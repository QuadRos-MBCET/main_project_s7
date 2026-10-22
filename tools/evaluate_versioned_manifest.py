"""
SafeAd AI (SAFE-VISION) — Reproducible Versioned Manifest Evaluation Workflow.

Executes a controlled evaluation run over a specified versioned development manifest.

Enforces:
1. Test Partition Inaccessibility (Rejects test_held_out manifests during model selection).
2. Manifest and Media File Existence Verification.
3. Explicit Recording of Detector and Fusion Configuration.
4. Incremental Resumption of Interrupted Runs.
5. Four-Class Multi-Class Confusion Matrix Generation.
6. Safety-Critical Metrics: PFAR, Prohibited Exposure, UGVR, FRR, and HITL Abstention.
"""

import os
import sys
import time
import json
import argparse
from datetime import datetime
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

# Ensure path resolution
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
JB_DIR = os.path.join(ROOT_DIR, "joseph_safead_core")
B2JB_DIR = os.path.join(ROOT_DIR, "joseph_safead_core", "backend2jb")
for p in [B2JB_DIR, JB_DIR, ROOT_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

from backend2jb.ai.pipeline import run_safead_inference
from models.fusion.safead_fusion import SafeAdFusion

CLASSES = ["SAFE_FOR_ALL", "SAFE_14_PLUS", "SAFE_18_PLUS", "UNSAFE_FOR_ALL"]


def calculate_metrics(y_true: List[str], y_pred: List[str]) -> Dict[str, Any]:
    """Calculates four-class multi-class confusion matrix and safety-critical metrics."""
    cm = {true_c: {pred_c: 0 for pred_c in CLASSES + ["REQUIRES_HUMAN_REVIEW"]} for true_c in CLASSES}
    for t, p in zip(y_true, y_pred):
        if t in cm:
            if p in cm[t]:
                cm[t][p] += 1
            else:
                cm[t]["UNSAFE_FOR_ALL"] += 1

    total_samples = len(y_true)
    hitl_count = sum(1 for p in y_pred if p == "REQUIRES_HUMAN_REVIEW")
    hitl_rate = round(hitl_count / total_samples, 4) if total_samples > 0 else 0.0
    coverage = round(1.0 - hitl_rate, 4)

    # Covered slice accuracy (ignoring abstentions)
    covered_indices = [i for i, p in enumerate(y_pred) if p != "REQUIRES_HUMAN_REVIEW"]
    covered_total = len(covered_indices)
    covered_correct = sum(1 for i in covered_indices if y_pred[i] == y_true[i])
    accuracy_covered = round(covered_correct / covered_total, 4) if covered_total > 0 else 0.0

    # Overall dataset accuracy
    overall_correct = sum(1 for t, p in zip(y_true, y_pred) if t == p)
    overall_acc = round(overall_correct / total_samples, 4) if total_samples > 0 else 0.0

    per_class = {}
    f1_list = []
    for c in CLASSES:
        tp = cm[c][c]
        fp = sum(cm[other_c][c] for other_c in CLASSES if other_c != c)
        fn = sum(cm[c][other_c] for other_c in CLASSES + ["REQUIRES_HUMAN_REVIEW"] if other_c != c)
        total_true = sum(cm[c].values())

        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0

        per_class[c] = {
            "true_count": total_true,
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4)
        }
        f1_list.append(f1)

    macro_f1 = round(float(np.mean(f1_list)), 4)

    # 1. Prohibited False Acceptance Rate (PFAR)
    ufa_total = sum(cm["UNSAFE_FOR_ALL"].values())
    ufa_false_accepted = sum(cm["UNSAFE_FOR_ALL"][c] for c in ["SAFE_FOR_ALL", "SAFE_14_PLUS", "SAFE_18_PLUS"])
    pfar = round(ufa_false_accepted / ufa_total, 4) if ufa_total > 0 else 0.0

    # 2. Prohibited Exposure Rate (among released ads)
    prohibited_exposure_rate = round(ufa_false_accepted / covered_total, 4) if covered_total > 0 else 0.0

    # 3. Underage Gating Violation Rate (UGVR)
    s18p_leaked_underage = cm["SAFE_18_PLUS"]["SAFE_FOR_ALL"] + cm["SAFE_18_PLUS"]["SAFE_14_PLUS"]
    s14p_leaked_underage = cm["SAFE_14_PLUS"]["SAFE_FOR_ALL"]
    ugvr_den = sum(cm["SAFE_18_PLUS"].values()) + sum(cm["SAFE_14_PLUS"].values())
    ugvr = round((s18p_leaked_underage + s14p_leaked_underage) / ugvr_den, 4) if ugvr_den > 0 else 0.0

    # 4. False Rejection Rate (FRR)
    safe_total = sum(cm["SAFE_FOR_ALL"].values()) + sum(cm["SAFE_14_PLUS"].values()) + sum(cm["SAFE_18_PLUS"].values())
    safe_rejected = cm["SAFE_FOR_ALL"]["UNSAFE_FOR_ALL"] + cm["SAFE_14_PLUS"]["UNSAFE_FOR_ALL"] + cm["SAFE_18_PLUS"]["UNSAFE_FOR_ALL"]
    frr = round(safe_rejected / safe_total, 4) if safe_total > 0 else 0.0

    return {
        "sample_count": total_samples,
        "overall_accuracy": overall_acc,
        "accuracy_covered_slice": accuracy_covered,
        "coverage": coverage,
        "hitl_count": hitl_count,
        "hitl_rate": hitl_rate,
        "macro_f1": macro_f1,
        "pfar": pfar,
        "pfar_numerator": ufa_false_accepted,
        "pfar_denominator": ufa_total,
        "prohibited_exposure_rate": prohibited_exposure_rate,
        "ugvr": ugvr,
        "frr": frr,
        "per_class_metrics": per_class,
        "confusion_matrix": cm
    }


def main():
    parser = argparse.ArgumentParser(description="Reproducible Versioned Manifest Evaluation Workflow")
    parser.add_argument("--manifest", type=str, required=True, help="Path to versioned development manifest CSV or JSON")
    parser.add_argument("--dataset-root", type=str, default=r"C:\Users\hello\Videos\sourav\datasets\safead-dataset-hub", help="Root directory of dataset hub")
    parser.add_argument("--pipeline-config", type=str, default="production", choices=["production", "candidate_b", "candidate_c", "candidate_d"], help="Selectable inference configuration")
    parser.add_argument("--split", type=str, default="", help="Optional split filter: train, val, or dev")
    parser.add_argument("--benchmark-inclusion-only", action="store_true", default=True, help="Filter out EXCLUDED_SYNTHETIC_CARD items (default: True)")
    parser.add_argument("--limit", type=int, default=0, help="Optional limit on number of samples to evaluate (for smoke testing)")
    parser.add_argument("--cache-dir", type=str, default="", help="Directory to save/resume incremental detector cache")
    parser.add_argument("--output-dir", type=str, default="", help="Directory to save evaluation results and report")
    parser.add_argument("--allow-test", action="store_true", help="Explicit override required to evaluate held-out test data (Strictly barred during model selection)")

    args = parser.parse_args()

    # 1. Gate Check: Test Partition Isolation
    manifest_name = os.path.basename(args.manifest).lower()
    if ("test" in manifest_name or args.split == "test") and not args.allow_test:
        print("\n" + "!" * 80)
        print("CRITICAL GOVERNANCE VIOLATION: HELD-OUT TEST MANIFEST DETECTED!")
        print("Model selection and experimental benchmarking MUST NEVER execute against held-out test data.")
        print("Aborting evaluation immediately to preserve test split integrity.")
        print("!" * 80 + "\n")
        sys.exit(1)

    if not os.path.exists(args.manifest):
        print(f"Error: Manifest file not found: {args.manifest}")
        sys.exit(1)

    if args.manifest.endswith(".json"):
        with open(args.manifest, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
        samples = raw_data.get("samples", raw_data.get("records", [])) if isinstance(raw_data, dict) else raw_data
        df_manifest = pd.DataFrame(samples)
        # Standardize column names if needed
        if "safead_label" in df_manifest.columns and "ground_truth_label" not in df_manifest.columns:
            df_manifest["ground_truth_label"] = df_manifest["safead_label"]
    else:
        df_manifest = pd.read_csv(args.manifest)

    # 2. Immutable Metadata-Based Held-Out Isolation:
    # If not explicitly evaluating test, filter out ANY historical held-out partition sample!
    if not args.allow_test:
        prov_path = os.path.join(ROOT_DIR, "docs", "PHASE_7C_SPLIT_PROVENANCE_REPORT.csv")
        if os.path.exists(prov_path):
            df_prov = pd.read_csv(prov_path)
            held_out_sids = set(df_prov[df_prov["was_in_held_out_partition"] == True]["sample_id"])
            initial_count = len(df_manifest)
            df_manifest = df_manifest[~df_manifest["sample_id"].isin(held_out_sids)].copy()
            removed_held_out = initial_count - len(df_manifest)
            if removed_held_out > 0:
                print(f"[GATE PASS] Metadata Partition Guard: Filtered out {removed_held_out} historical held-out samples to prevent split contamination.")

    if args.benchmark_inclusion_only and "benchmark_inclusion" in df_manifest.columns:
        initial_len = len(df_manifest)
        df_manifest = df_manifest[df_manifest["benchmark_inclusion"].isin(["GENUINE_BENCHMARK", "INCLUDED_GENUINE_BENCHMARK"])].copy()
        print(f"Benchmark Inclusion Filter: Retained {len(df_manifest)} / {initial_len} genuine samples (quarantined {initial_len - len(df_manifest)} synthetic cards).")

    if args.split and "split" in df_manifest.columns:
        initial_len = len(df_manifest)
        df_manifest = df_manifest[df_manifest["split"] == args.split].copy()
        print(f"Split Filter ({args.split}): Retained {len(df_manifest)} / {initial_len} samples.")

    if args.limit > 0 and len(df_manifest) > args.limit:
        df_manifest = df_manifest.head(args.limit).copy()
        print(f"[INFO] Applied sample limit: Evaluating first {len(df_manifest)} samples.")

    print("=" * 85)
    print("      SAFEAD AI: REPRODUCIBLE VERSIONED MANIFEST EVALUATION WORKFLOW       ")
    print("=" * 85)
    print(f"Manifest: {args.manifest} ({len(df_manifest)} entries)")
    print(f"Selected Configuration: {args.pipeline_config}")
    print(f"Dataset Root: {args.dataset_root}")

    # Set up directories
    output_dir = args.output_dir or os.path.join(ROOT_DIR, "results", "versioned_evaluations", f"{args.pipeline_config}_{int(time.time())}")
    cache_dir = args.cache_dir or os.path.join(ROOT_DIR, "results", "versioned_evaluations", "cache")
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(cache_dir, exist_ok=True)

    cache_file = os.path.join(cache_dir, f"eval_cache_{args.pipeline_config}.json")
    cached_predictions: Dict[str, Any] = {}
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                cached_predictions = json.load(f)
            print(f"Resuming run: Loaded {len(cached_predictions)} cached predictions from: {cache_file}")
        except Exception:
            cached_predictions = {}

    # Set global pipeline configuration mode
    os.environ["SAFEAD_PIPELINE_MODE"] = args.pipeline_config

    run_meta = {
        "timestamp": datetime.now().isoformat(),
        "manifest_path": args.manifest,
        "sample_count": len(df_manifest),
        "pipeline_config": args.pipeline_config,
        "env_pipeline_mode": os.getenv("SAFEAD_PIPELINE_MODE"),
        "hardware": "Single-thread deterministic CPU inference",
        "fusion_engine": "SafeAdFusion (Production Frozen)"
    }

    results = []
    y_true = []
    y_pred = []

    print("\nExecuting evaluation loop...")
    for idx, row in df_manifest.iterrows():
        sid = str(row["sample_id"])
        gt = str(row["ground_truth_label"])
        rel_path = str(row["file_path"])
        full_path = os.path.join(args.dataset_root, rel_path) if not os.path.isabs(rel_path) else rel_path

        sha256_hash = str(row.get("sha256") or row.get("content_hash") or "")
        fmt_type = str(row.get("content_format_type") or "commercial_advertisement")
        is_non_ad = (fmt_type != "commercial_advertisement")

        if sid in cached_predictions:
            pred = cached_predictions[sid]["predicted_label"]
            res_entry = cached_predictions[sid]
        else:
            if not os.path.exists(full_path):
                print(f"  [WARNING] File missing on disk for {sid}: {full_path}. Marking UNSAFE_FOR_ALL.")
                pred = "UNSAFE_FOR_ALL"
                res_entry = {
                    "sample_id": sid,
                    "sha256": sha256_hash,
                    "ground_truth_label": gt,
                    "predicted_label": pred,
                    "model_version": f"SafeAd_{args.pipeline_config}_v2",
                    "content_format_type": fmt_type,
                    "is_non_ad_control": is_non_ad,
                    "error": "File missing"
                }
            else:
                out = run_safead_inference(file_path=full_path, title="", caption="", pipeline_mode=args.pipeline_config)
                pred = out["classification"]
                res_entry = {
                    "sample_id": sid,
                    "sha256": sha256_hash,
                    "ground_truth_label": gt,
                    "predicted_label": pred,
                    "model_version": f"SafeAd_{args.pipeline_config}_v2",
                    "content_format_type": fmt_type,
                    "is_non_ad_control": is_non_ad,
                    "risk_score": out.get("risk_score"),
                    "confidence": out.get("confidence"),
                    "action": out.get("publication_action") or out.get("action"),
                    "publishable": out.get("publishable"),
                    "pipeline_mode": out.get("pipeline_mode"),
                    "experimental_audit": out.get("experimental_audit")
                }

            cached_predictions[sid] = res_entry
            # Incremental save every 5 samples
            if idx % 5 == 0:
                with open(cache_file, "w", encoding="utf-8") as f:
                    json.dump(cached_predictions, f, indent=2)

        results.append(res_entry)
        y_true.append(gt)
        y_pred.append(pred)

    # Save final cache
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(cached_predictions, f, indent=2)

    # Calculate overall metrics
    metrics_overall = calculate_metrics(y_true, y_pred)

    # Separate commercial ads vs non-ad controls
    comm_indices = [i for i, r in enumerate(results) if not r.get("is_non_ad_control", False)]
    non_ad_indices = [i for i, r in enumerate(results) if r.get("is_non_ad_control", False)]

    metrics_commercial = calculate_metrics(
        [y_true[i] for i in comm_indices],
        [y_pred[i] for i in comm_indices]
    ) if comm_indices else None

    metrics_non_ad = calculate_metrics(
        [y_true[i] for i in non_ad_indices],
        [y_pred[i] for i in non_ad_indices]
    ) if non_ad_indices else None

    # Save outputs
    predictions_df = pd.DataFrame(results)
    predictions_csv = os.path.join(output_dir, "sample_predictions.csv")
    predictions_df.to_csv(predictions_csv, index=False)

    summary_file = os.path.join(output_dir, "evaluation_summary.json")
    final_report = {
        "metadata": run_meta,
        "metrics_overall": metrics_overall,
        "metrics_commercial_ads": metrics_commercial,
        "metrics_non_ad_controls": metrics_non_ad
    }
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(final_report, f, indent=2)

    print("\n" + "=" * 85)
    print("                         EVALUATION SUMMARY REPORT                        ")
    print("=" * 85)
    print(f"Total Evaluated Samples     : {metrics_overall['sample_count']}")
    print(f"Overall Accuracy            : {metrics_overall['overall_accuracy'] * 100:.2f}%")
    print(f"Covered Slice Accuracy      : {metrics_overall['accuracy_covered_slice'] * 100:.2f}%")
    print(f"Macro-F1 Score              : {metrics_overall['macro_f1']:.4f}")
    print(f"Automatic Decision Coverage : {metrics_overall['coverage'] * 100:.2f}%")
    print(f"Human-Review Rate (HITL)    : {metrics_overall['hitl_rate'] * 100:.2f}% ({metrics_overall['hitl_count']} samples)")
    print(f"Prohibited False Acceptance : {metrics_overall['pfar'] * 100:.2f}% ({metrics_overall['pfar_numerator']}/{metrics_overall['pfar_denominator']})")
    print(f"Underage Gating Violations  : {metrics_overall['ugvr'] * 100:.2f}%")

    if metrics_commercial:
        print("-" * 85)
        print("  PRIMARY COMMERCIAL ADVERTISEMENTS METRICS:")
        print(f"  Commercial Ad Count       : {metrics_commercial['sample_count']}")
        print(f"  Commercial Ad Accuracy    : {metrics_commercial['overall_accuracy'] * 100:.2f}%")
        print(f"  Commercial PFAR           : {metrics_commercial['pfar'] * 100:.2f}%")

    if metrics_non_ad:
        print("-" * 85)
        print("  DIAGNOSTIC NON-AD CONTROLS METRICS:")
        print(f"  Non-Ad Control Count      : {metrics_non_ad['sample_count']}")
        print(f"  Non-Ad Control Accuracy   : {metrics_non_ad['overall_accuracy'] * 100:.2f}%")
        print(f"  Non-Ad PFAR               : {metrics_non_ad['pfar'] * 100:.2f}%")

    print("=" * 85)
    print(f"\nArtifacts saved to: {output_dir}")
    print(f"Predictions CSV: {predictions_csv}")
    print(f"Summary JSON:    {summary_file}")


if __name__ == "__main__":
    main()
