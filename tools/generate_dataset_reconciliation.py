"""
SafeAd AI (SAFE-VISION) — Phase 7B Dataset Reconciliation Generator.

Compares:
A. The frozen 194-sample Phase 5B development benchmark.
B. The reconstructed dataset v2 containing 414 total assets (296 non-synthetic media samples + 118 quarantined synthetic cards).

Produces:
1. docs/PHASE_7B_DATASET_RECONCILIATION.csv
2. docs/PHASE_7B_DATASET_RECONCILIATION_SUMMARY.json
"""

import os
import sys
import json
import pandas as pd
from typing import Dict, Any, List

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATASET_ROOT = r"C:\Users\hello\Videos\sourav\datasets\safead-dataset-hub"


def main():
    print("=" * 80)
    print("      SAFEAD AI: PHASE 7B DATASET RECONCILIATION GENERATOR       ")
    print("=" * 80)

    # 1. Load Frozen 194 Dev Benchmark
    dev_path = os.path.join(ROOT_DIR, "results", "real_pipeline_baseline", "saved_detector_outputs.json")
    with open(dev_path, "r", encoding="utf-8") as f:
        dev_194 = json.load(f)

    # 2. Load V2 Reconstructed Master Manifest
    v2_path = os.path.join(DATASET_ROOT, "manifests", "safead_master_manifest_v2_reconstructed.json")
    with open(v2_path, "r", encoding="utf-8") as f:
        v2_data = json.load(f)
    v2_records = {r["sample_id"]: r for r in v2_data.get("records", [])}

    # 3. Load V1 Frozen Master Manifest
    v1_path = os.path.join(DATASET_ROOT, "manifests", "safead_master_manifest_v1_frozen.json")
    with open(v1_path, "r", encoding="utf-8") as f:
        v1_data = json.load(f)
    v1_records = {r["sample_id"]: r for r in v1_data.get("records", [])}

    # 4. Load Synthetic Manifest
    syn_path = os.path.join(DATASET_ROOT, "manifests", "synthetic_benchmark_manifest.json")
    with open(syn_path, "r", encoding="utf-8") as f:
        syn_data = json.load(f)
    syn_records = {r["sample_id"]: r for r in syn_data.get("samples", [])}

    # 5. Load S14P Review Table
    s14p_path = os.path.join(DATASET_ROOT, "docs", "s14p_review_table.json")
    with open(s14p_path, "r", encoding="utf-8") as f:
        s14p_reviews = {r["sample_id"]: r for r in json.load(f)}

    rows = []
    reconciliation_summary = {
        "frozen_benchmark_count": len(dev_194),
        "v2_total_assets": len(v2_records),
        "v2_primary_benchmark_samples": v2_data.get("primary_benchmark_samples", 296),
        "v2_quarantined_synthetic_samples": v2_data.get("quarantined_synthetic_samples", 118),
        "counts_by_category_all": v2_data.get("counts_by_category_all_assets", {}),
        "counts_by_category_genuine": v2_data.get("counts_by_category_genuine_benchmark", {}),
        "label_changes_in_194_dev": 0,
        "label_changes_in_all_414": 0,
        "s14p_total_reviewed": len(s14p_reviews),
        "s14p_reclassified_safe_for_all": 0,
        "s14p_overruled_18p_safe_for_all": 0,
        "s14p_retained_14_plus": 0,
        "s14p_overruled_review_safe_for_all": 0
    }

    all_sample_ids = sorted(list(v2_records.keys()))

    for sid in all_sample_ids:
        v2_rec = v2_records[sid]
        v1_rec = v1_records.get(sid, {})
        dev_rec = dev_194.get(sid)

        # Baseline Label (from 194 dev if present, else from v1 frozen)
        if dev_rec:
            old_label = dev_rec["true_label"]
            old_split = "phase5b_clean_development_194"
        elif sid in syn_records:
            old_label = syn_records[sid]["safead_label"]
            old_split = "v1_synthetic_card_excluded"
        elif v1_rec:
            old_label = v1_rec["safead_label"]
            old_split = v1_rec.get("split", "v1_frozen")
        else:
            old_label = "NOT_IN_V1 (NEW_ASSET)"
            old_split = "none"

        new_label = v2_rec.get("safead_label")
        new_split = v2_rec.get("split")
        is_synthetic = v2_rec.get("is_synthetic", False)
        benchmark_inc = v2_rec.get("benchmark_inclusion", "UNKNOWN")
        fmt_type = v2_rec.get("content_format_type", "commercial_advertisement")
        is_genuine_ad = (fmt_type == "commercial_advertisement")

        # Human Review documentation
        human_review_doc = False
        review_details = ""
        if sid in s14p_reviews:
            human_review_doc = True
            rev = s14p_reviews[sid]
            review_details = f"Dec: {rev.get('reviewer_decision')} | By: {rev.get('reviewer_id')} on {rev.get('review_date')}"
            dec = rev.get("reviewer_decision")
            if dec == "ACCEPTED_RECLASSIFIED_SAFE_FOR_ALL":
                reconciliation_summary["s14p_reclassified_safe_for_all"] += 1
            elif dec == "DISAGREEMENT_RESOLVED_OVERRULE_18_PLUS":
                reconciliation_summary["s14p_overruled_18p_safe_for_all"] += 1
            elif dec == "ACCEPTED_RETAINED_14_PLUS":
                reconciliation_summary["s14p_retained_14_plus"] += 1
            elif dec == "DISAGREEMENT_RESOLVED_OVERRULE_REVIEW":
                reconciliation_summary["s14p_overruled_review_safe_for_all"] += 1
        elif v2_rec.get("reviewer_decision"):
            human_review_doc = True
            review_details = f"Dec: {v2_rec.get('reviewer_decision')} | By: {v2_rec.get('reviewer_id')}"

        label_changed = (old_label != new_label) and (old_label != "NOT_IN_V1 (NEW_ASSET)")
        if label_changed:
            reconciliation_summary["label_changes_in_all_414"] += 1
            if dev_rec:
                reconciliation_summary["label_changes_in_194_dev"] += 1

        row = {
            "sample_id": sid,
            "media_type": v2_rec.get("media_type"),
            "old_label": old_label,
            "new_label": new_label,
            "label_changed": label_changed,
            "media_hash_sha256": v2_rec.get("content_hash"),
            "resolution": v2_rec.get("resolution"),
            "file_size_kb": v2_rec.get("file_size_kb"),
            "source_name": v2_rec.get("source_name"),
            "source_url": v2_rec.get("source_url"),
            "license": v2_rec.get("license"),
            "is_genuine_ad": is_genuine_ad,
            "content_format_type": fmt_type,
            "is_synthetic": is_synthetic,
            "benchmark_inclusion": benchmark_inc,
            "old_split": old_split,
            "new_split": new_split,
            "human_review_documented": human_review_doc,
            "review_details": review_details,
            "in_phase5b_clean_dev_194": dev_rec is not None
        }
        rows.append(row)

    df_out = pd.DataFrame(rows)
    csv_path = os.path.join(ROOT_DIR, "docs", "PHASE_7B_DATASET_RECONCILIATION.csv")
    df_out.to_csv(csv_path, index=False)
    print(f"Reconciliation CSV written: {csv_path} ({len(df_out)} rows)")

    json_path = os.path.join(ROOT_DIR, "docs", "PHASE_7B_DATASET_RECONCILIATION_SUMMARY.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(reconciliation_summary, f, indent=2)
    print(f"Reconciliation Summary JSON written: {json_path}")

    print("\nSummary Statistics:")
    for k, v in reconciliation_summary.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
