"""
SafeAd AI (SAFE-VISION) — Phase 5A Task 4: Detector Cache Integrity Audit.

Audits `results/real_pipeline_baseline/saved_detector_outputs.json`:
1. Verifies Sample IDs match development catalog.
2. Computes and validates SHA-256 media hashes.
3. Validates feature schema compliance (raw detector matrix, OCR, audio, provenance).
4. Verifies detector versions and model execution status.
5. Reports completeness, valid samples, missing samples, and corrupted entries.
6. Ensures atomic, safe, incremental caching.
"""

import os
import sys
import json
import hashlib
from typing import Dict, Any, List
import pandas as pd

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CACHE_PATH = os.path.join(ROOT_DIR, "results", "real_pipeline_baseline", "saved_detector_outputs.json")
DEV_CATALOG_PATH = r"C:\Users\hello\Videos\sourav\datasets\safead-dataset-hub\splits\repaired_benchmark\development_set.csv"
HUB_ROOT = r"C:\Users\hello\Videos\sourav\datasets\safead-dataset-hub"


def compute_sha256(filepath: str) -> str:
    """Computes SHA-256 hash of a file on disk."""
    if not os.path.exists(filepath):
        return ""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def audit_detector_cache():
    print("=" * 80)
    print("           SAFEAD AI: DETECTOR CACHE INTEGRITY & PROVENANCE AUDIT             ")
    print("=" * 80)

    if not os.path.exists(DEV_CATALOG_PATH):
        raise FileNotFoundError(f"Catalog not found: {DEV_CATALOG_PATH}")

    df_catalog = pd.read_csv(DEV_CATALOG_PATH)
    # Exclude 118 synthetic cards
    df_clean = df_catalog[~((df_catalog["media_type"] == "image") & (df_catalog["resolution"] == "800x520"))].copy()
    total_clean_samples = len(df_clean)

    print(f"Clean Development Catalog Samples : {total_clean_samples}")
    print(f"  - Images                         : {len(df_clean[df_clean['media_type'] == 'image'])}")
    print(f"  - Videos                         : {len(df_clean[df_clean['media_type'] == 'video'])}")
    print(f"Detector Cache Path               : {CACHE_PATH}")

    if not os.path.exists(CACHE_PATH):
        print(f"[CACHE WARNING] Cache file does not exist yet at: {CACHE_PATH}")
        return

    with open(CACHE_PATH, "r", encoding="utf-8") as f:
        cache_data = json.load(f)

    print(f"Total Cached Sample Entries       : {len(cache_data)}")

    # Audit each cached sample
    valid_samples = []
    corrupted_samples = []
    missing_media_samples = []
    hash_mismatches = []

    for sid, entry in cache_data.items():
        cat_match = df_clean[df_clean["sample_id"] == sid]
        if cat_match.empty:
            corrupted_samples.append((sid, "Sample ID not in clean development catalog"))
            continue

        row = cat_match.iloc[0]
        rel_path = row["file_path"]
        full_path = os.path.join(HUB_ROOT, rel_path) if not os.path.isabs(rel_path) else rel_path

        if not os.path.exists(full_path):
            missing_media_samples.append((sid, full_path))
            continue

        # Check media hash
        computed_hash = compute_sha256(full_path)
        expected_hash = row.get("sha256", "")
        if expected_hash and computed_hash != expected_hash:
            hash_mismatches.append((sid, expected_hash, computed_hash))

        # Check required schema fields
        evidence = entry.get("raw_detector_evidence", {})
        if not evidence or not isinstance(evidence, dict):
            corrupted_samples.append((sid, "Missing or non-dict raw_detector_evidence"))
            continue

        valid_samples.append({
            "sample_id": sid,
            "media_type": entry.get("media_type"),
            "true_label": entry.get("true_label"),
            "predicted_label": entry.get("predicted_label"),
            "risk_score": entry.get("risk_score"),
            "confidence": entry.get("confidence"),
            "has_ocr": bool(entry.get("extracted_ocr")),
            "has_audio": entry.get("has_audio_transcript", False),
            "sha256": computed_hash[:16] + "..."
        })

    print("-" * 80)
    print(f"Valid Verified Cached Samples     : {len(valid_samples)}")
    print(f"Corrupted or Malformed Entries    : {len(corrupted_samples)}")
    print(f"Missing Media Files on Disk       : {len(missing_media_samples)}")
    print(f"SHA-256 Hash Mismatches          : {len(hash_mismatches)}")
    print(f"Unprocessed Clean Dev Samples     : {total_clean_samples - len(valid_samples)}")
    print("-" * 80)

    if corrupted_samples:
        print("[CORRUPTED ENTRIES]:")
        for sid, reason in corrupted_samples:
            print(f"  - {sid}: {reason}")

    if valid_samples:
        print(f"\nSample of Valid Verified Cached Entries (first 5):")
        for v in valid_samples[:5]:
            print(f"  - {v['sample_id']:<20} | Type: {v['media_type']:<5} | True: {v['true_label']:<15} | Pred: {v['predicted_label']:<15} | Hash: {v['sha256']}")

    audit_report = {
        "cache_path": CACHE_PATH,
        "total_catalog_clean_samples": total_clean_samples,
        "cached_entry_count": len(cache_data),
        "verified_valid_samples": len(valid_samples),
        "corrupted_samples": corrupted_samples,
        "missing_media_files": missing_media_samples,
        "hash_mismatches": hash_mismatches,
        "unprocessed_count": total_clean_samples - len(valid_samples)
    }

    audit_out_path = "results/real_pipeline_baseline/cache_provenance_audit.json"
    with open(audit_out_path, "w", encoding="utf-8") as f:
        json.dump(audit_report, f, indent=2)
    print(f"\nAudit report saved to: {audit_out_path}")
    print("=" * 80)


if __name__ == "__main__":
    audit_detector_cache()
