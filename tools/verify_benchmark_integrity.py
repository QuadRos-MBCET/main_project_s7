"""
Comprehensive Dataset Integrity & Leakage Verification for SAFE-VISION (SafeAd AI).
Validates:
1. Unique Sample IDs and Exact SHA-256 hashes.
2. File accessibility on disk.
3. Class distribution per split (train, val, test).
4. Near-duplicate image check across splits (pHash/dHash).
5. Cross-split campaign / brand token contamination check.
6. Rule-tuning contamination audit (checking if dataset tokens are hardcoded into production policy heuristics).
"""

import os
import sys
import hashlib
import json
import pandas as pd
import numpy as np
from PIL import Image

def compute_dhash(image_path, hash_size=8):
    """Computes difference hash for perceptual image near-duplicate detection."""
    try:
        with Image.open(image_path) as img:
            img = img.convert('L').resize((hash_size + 1, hash_size), Image.Resampling.LANCZOS)
            pixels = np.array(img)
            diff = pixels[:, 1:] > pixels[:, :-1]
            return diff.flatten()
    except Exception:
        return None

def verify_dataset_integrity(splits_dir, hub_root):
    print("=" * 80)
    print("      SAFEAD DATASET-HUB — BENCHMARK INTEGRITY & LEAKAGE AUDIT          ")
    print("=" * 80)

    train_path = os.path.join(splits_dir, "train.csv")
    val_path = os.path.join(splits_dir, "val.csv")
    test_path = os.path.join(splits_dir, "test.csv")

    splits = {}
    for name, p in [("train", train_path), ("val", val_path), ("test", test_path)]:
        if os.path.exists(p):
            splits[name] = pd.read_csv(p)
            print(f"[+] Loaded {name} split: {len(splits[name])} samples")
        else:
            print(f"[-] Missing split file: {p}")

    total_df = pd.concat(splits.values(), ignore_index=True)
    total_samples = len(total_df)
    print(f"\n1. Sample ID & Exact Duplicate Hash Audit (Total: {total_samples} samples):")

    # Sample ID uniqueness
    unique_ids = total_df["sample_id"].nunique()
    print(f"   - Unique Sample IDs: {unique_ids}/{total_samples} " + ("(PASS)" if unique_ids == total_samples else "(FAIL: Duplicate IDs)"))

    # SHA256 Exact Duplicates
    unique_hashes = total_df["sha256"].nunique()
    print(f"   - Unique SHA-256 Hashes: {unique_hashes}/{total_samples} " + ("(PASS: 0 Exact Duplicates)" if unique_hashes == total_samples else "(WARN: Exact Duplicates Present)"))

    # File Availability
    print("\n2. Media File On-Disk Accessibility Check:")
    missing_files = []
    for idx, row in total_df.iterrows():
        fpath = os.path.join(hub_root, row["file_path"]) if not os.path.isabs(row["file_path"]) else row["file_path"]
        if not os.path.exists(fpath):
            missing_files.append((row["sample_id"], fpath))
    print(f"   - Files Accessible: {total_samples - len(missing_files)}/{total_samples} " + ("(PASS: 100% Accessible)" if not missing_files else f"(FAIL: {len(missing_files)} missing)"))

    # Class Distributions
    print("\n3. Class Distribution Across Splits:")
    dist_table = {}
    for name, s_df in splits.items():
        dist_table[name] = s_df["safead_label"].value_counts().to_dict()
    dist_df = pd.DataFrame(dist_table).fillna(0).astype(int)
    print(dist_df.to_string())

    # Shared Brands / Campaign Domains Cross-Contamination
    print("\n4. Cross-Split Campaign & Brand Token Contamination Audit:")
    split_brands = {}
    split_urls = {}
    for name, s_df in splits.items():
        brands = set(b.strip().lower() for b in s_df["key_brand_tokens"].dropna() if b.strip().lower() != "nan")
        urls = set(u.strip().lower() for u in s_df["source_url"].dropna() if u.strip().lower() != "nan")
        split_brands[name] = brands
        split_urls[name] = urls

    brand_leak_tv = split_brands.get("train", set()) & split_brands.get("val", set())
    brand_leak_tt = split_brands.get("train", set()) & split_brands.get("test", set())
    brand_leak_vt = split_brands.get("val", set()) & split_brands.get("test", set())

    print(f"   - Shared Brand Tokens between Train and Val : {len(brand_leak_tv)} {list(brand_leak_tv)[:3]}")
    print(f"   - Shared Brand Tokens between Train and Test: {len(brand_leak_tt)} {list(brand_leak_tt)[:3]}")
    print(f"   - Shared Brand Tokens between Val and Test  : {len(brand_leak_vt)} {list(brand_leak_vt)[:3]}")
    
    brand_leakage_status = (len(brand_leak_tt) == 0 and len(brand_leak_tv) == 0 and len(brand_leak_vt) == 0)
    print("   -> Brand Isolation: " + ("PASS (Zero Brand Leakage)" if brand_leakage_status else "WARN: Cross-Split Brands Present"))

    # Near-Duplicate Image pHash Analysis
    print("\n5. Near-Duplicate Perceptual Hash (dHash) Audit across Image Splits:")
    hashes_by_split = {}
    for name, s_df in splits.items():
        img_df = s_df[s_df["media_type"] == "image"]
        split_h = {}
        for _, row in img_df.iterrows():
            fpath = os.path.join(hub_root, row["file_path"]) if not os.path.isabs(row["file_path"]) else row["file_path"]
            h = compute_dhash(fpath)
            if h is not None:
                split_h[row["sample_id"]] = h
        hashes_by_split[name] = split_h
        print(f"   - Computed dHash for {len(split_h)} images in {name}")

    # Check hamming distance between train and test
    near_dupe_pairs = []
    if "train" in hashes_by_split and "test" in hashes_by_split:
        for tr_id, tr_h in hashes_by_split["train"].items():
            for te_id, te_h in hashes_by_split["test"].items():
                ham_dist = np.count_nonzero(tr_h != te_h)
                if ham_dist <= 2:  # Extremely close perceptual near-duplicate
                    near_dupe_pairs.append((tr_id, te_id, ham_dist))

    print(f"   - Cross-Split Near-Duplicate Pairs (Hamming dist <= 2): {len(near_dupe_pairs)}")
    if near_dupe_pairs:
        for p in near_dupe_pairs[:5]:
            print(f"     * Train {p[0]} vs Test {p[1]} (Hamming dist: {p[2]})")
    else:
        print("   -> Perceptual Image Isolation: PASS (No near-duplicates found between train and test)")

    # 6. Rule-Tuning Contamination Audit
    print("\n6. Rule-Tuning Contamination Audit:")
    # Check if dataset brand tokens or Malayalam/Hindi slang are in ad_risk_analyzer or evaluate_hub_dataset
    try:
        from backend2jb.models.ad_risk_analyzer import AdRiskAnalyzer
        analyzer = AdRiskAnalyzer()
        # Extract keywords
        analyzer_keywords = set()
        for pat_list in analyzer.policy_patterns.values():
            analyzer_keywords.update([p.lower() for p in pat_list])

        dataset_tokens = set()
        for t in total_df["key_brand_tokens"].dropna():
            dataset_tokens.update([tok.strip().lower() for tok in str(t).split() if len(tok.strip()) > 3])

        matched_tokens = analyzer_keywords.intersection(dataset_tokens)
        print(f"   - Total unique rules in AdRiskAnalyzer: {len(analyzer_keywords)}")
        print(f"   - Tokens from custom catalog appearing in production rules: {len(matched_tokens)} {list(matched_tokens)[:8]}")
        if matched_tokens:
            print("   -> Limitation Identified: Catalog tokens appear in heuristic rule catalogs.")
            print("      This confirms evaluation samples were partially used for rule-crafting/tuning.")
    except Exception as e:
        print(f"   - Rule audit exception: {e}")

    print("\n" + "=" * 80)
    print("Audit Complete.")

if __name__ == "__main__":
    splits_dir = r"C:\Users\hello\Videos\sourav\datasets\safead-dataset-hub\splits\benchmark_380"
    hub_root = r"C:\Users\hello\Videos\sourav\datasets\safead-dataset-hub"
    verify_dataset_integrity(splits_dir, hub_root)
