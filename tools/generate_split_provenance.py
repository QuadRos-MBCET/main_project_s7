"""
SafeAd AI (SAFE-VISION) — Phase 7C Split Provenance Report Generator.

Analyzes all 414 assets in safead_master_manifest_v2_reconstructed.json and traces:
- Sample ID
- SHA-256
- Media type
- Original split (in v1/Phase 5B)
- Reconstructed split (in v2)
- Previous benchmark membership
- Whether the sample was ever in a held-out partition (was_in_held_out_partition)
- Whether it has been used in prior model selection (used_in_prior_model_selection)
- Current label and review status
- Content format type (commercial_advertisement vs archival_hazard_footage vs scam)
- Benchmark inclusion status
"""

import os
import sys
import json
import pandas as pd

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATASET_ROOT = r"C:\Users\hello\Videos\sourav\datasets\safead-dataset-hub"


def main():
    print("=" * 85)
    print("      SAFEAD AI: PHASE 7C SPLIT PROVENANCE GENERATOR       ")
    print("=" * 85)

    # 1. Load Phase 5B evaluated 194 samples
    dev_path = os.path.join(ROOT_DIR, "results", "real_pipeline_baseline", "saved_detector_outputs.json")
    with open(dev_path, "r", encoding="utf-8") as f:
        dev_194 = json.load(f)

    # 2. Load V1 frozen manifest
    v1_path = os.path.join(DATASET_ROOT, "manifests", "safead_master_manifest_v1_frozen.json")
    with open(v1_path, "r", encoding="utf-8") as f:
        v1_records = {r["sample_id"]: r for r in json.load(f)["records"]}

    # 3. Load V2 reconstructed manifest
    v2_path = os.path.join(DATASET_ROOT, "manifests", "safead_master_manifest_v2_reconstructed.json")
    with open(v2_path, "r", encoding="utf-8") as f:
        v2_records = {r["sample_id"]: r for r in json.load(f)["records"]}

    # 4. Load S14P review table
    s14p_path = os.path.join(DATASET_ROOT, "docs", "s14p_review_table.json")
    with open(s14p_path, "r", encoding="utf-8") as f:
        s14p_reviews = {r["sample_id"]: r for r in json.load(f)}

    rows = []
    
    summary = {
        "total_assets_v2": len(v2_records),
        "genuine_benchmark_samples": 0,
        "quarantined_synthetic_cards": 0,
        "used_in_prior_model_selection_194": 0,
        "historical_held_out_candidates_88": 0,
        "new_v2_scam_supplementary_14": 0,
        "cross_split_leakage_risks": {
            "prior_dev_samples_in_v2_test": 0,
            "historical_held_out_in_v2_train": 0,
            "historical_held_out_in_v2_val": 0,
            "historical_held_out_in_v2_test": 0,
            "new_scam_in_v2_train": 0,
            "new_scam_in_v2_val": 0,
            "new_scam_in_v2_test": 0
        },
        "non_ad_controls_count": 0,
        "commercial_ads_count": 0
    }

    for sid in sorted(list(v2_records.keys())):
        r2 = v2_records[sid]
        r1 = v1_records.get(sid)
        
        sha256 = r2.get("content_hash", "")
        media_type = r2.get("media_type", "")
        reconstructed_split = r2.get("split", "")
        safead_label = r2.get("safead_label", "")
        review_status = r2.get("review_status", "")
        is_synthetic = r2.get("is_synthetic", False)
        benchmark_inc = r2.get("benchmark_inclusion", "")
        content_format = r2.get("content_format_type", "commercial_advertisement")
        
        # Categorize benchmark membership and partition history
        if is_synthetic:
            prev_membership = "v1_synthetic_review_card"
            original_split = "quarantined_synthetic_v1"
            was_in_held_out = False
            used_in_prior_model_selection = False
            summary["quarantined_synthetic_cards"] += 1
        elif sid in dev_194:
            prev_membership = "phase5b_clean_development_194"
            original_split = "phase5b_dev_train_val"
            was_in_held_out = False
            used_in_prior_model_selection = True
            summary["used_in_prior_model_selection_194"] += 1
            summary["genuine_benchmark_samples"] += 1
            if reconstructed_split == "test":
                summary["cross_split_leakage_risks"]["prior_dev_samples_in_v2_test"] += 1
        elif r1 is not None:
            prev_membership = "v1_genuine_held_out_candidate"
            original_split = "v1_held_out_test_partition"
            was_in_held_out = True
            used_in_prior_model_selection = False
            summary["historical_held_out_candidates_88"] += 1
            summary["genuine_benchmark_samples"] += 1
            if reconstructed_split == "train":
                summary["cross_split_leakage_risks"]["historical_held_out_in_v2_train"] += 1
            elif reconstructed_split == "val":
                summary["cross_split_leakage_risks"]["historical_held_out_in_v2_val"] += 1
            elif reconstructed_split == "test":
                summary["cross_split_leakage_risks"]["historical_held_out_in_v2_test"] += 1
        else:
            prev_membership = "new_v2_scam_supplement"
            original_split = "unassigned_new_asset"
            was_in_held_out = False
            used_in_prior_model_selection = False
            summary["new_v2_scam_supplementary_14"] += 1
            summary["genuine_benchmark_samples"] += 1
            if reconstructed_split == "train":
                summary["cross_split_leakage_risks"]["new_scam_in_v2_train"] += 1
            elif reconstructed_split == "val":
                summary["cross_split_leakage_risks"]["new_scam_in_v2_val"] += 1
            elif reconstructed_split == "test":
                summary["cross_split_leakage_risks"]["new_scam_in_v2_test"] += 1

        is_non_ad = (content_format != "commercial_advertisement")
        if is_non_ad:
            summary["non_ad_controls_count"] += 1
        else:
            summary["commercial_ads_count"] += 1

        # Check human review documentation
        has_review_doc = (sid in s14p_reviews) or (review_status == "ACCEPTED" and not is_synthetic)
        reviewer_id = r2.get("reviewer_id", "none")
        reviewer_decision = r2.get("reviewer_decision", "")

        rows.append({
            "sample_id": sid,
            "sha256": sha256,
            "media_type": media_type,
            "original_split": original_split,
            "reconstructed_split": reconstructed_split,
            "previous_benchmark_membership": prev_membership,
            "was_in_held_out_partition": was_in_held_out,
            "used_in_prior_model_selection": used_in_prior_model_selection,
            "current_safead_label": safead_label,
            "current_review_status": review_status,
            "reviewer_id": reviewer_id,
            "reviewer_decision": reviewer_decision,
            "content_format_type": content_format,
            "is_non_ad_control": is_non_ad,
            "benchmark_inclusion": benchmark_inc
        })

    df_out = pd.DataFrame(rows)
    csv_path = os.path.join(ROOT_DIR, "docs", "PHASE_7C_SPLIT_PROVENANCE_REPORT.csv")
    df_out.to_csv(csv_path, index=False)
    print(f"[OK] Wrote split provenance CSV ({len(df_out)} rows): {csv_path}")

    json_path = os.path.join(ROOT_DIR, "docs", "PHASE_7C_SPLIT_PROVENANCE_SUMMARY.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"[OK] Wrote split provenance summary JSON: {json_path}")

    print("\nProvenance Summary Highlights:")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
