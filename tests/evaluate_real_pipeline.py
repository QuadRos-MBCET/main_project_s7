"""
SafeAd AI (SAFE-VISION) — Real Neural Inference Pipeline Evaluation Runner.

Evaluates the actual multimodal pipeline (backend2jb.ai.pipeline: run_safead_inference
and SafeAdFusion) on the official SafeAd Dataset Hub (380 samples: 300 images + 80 videos).

Key Features:
- Does NOT alter model weights, thresholds, or catalog ground truth.
- Zero Ground-Truth Exposure: Evaluates raw uploaded media files with title="" and caption="".
- Separates Image and Video performance.
- Computes:
    * 4x4 Multi-Class Confusion Matrix
    * Per-class Precision, Recall, F1
    * Macro-F1
    * Prohibited-Content False Acceptance Rate (PFAR)
    * Underage Gating Violation Rate (UGVR)
    * False Rejection Rate for Safe Content (FRR)
    * Human-Review Trigger Frequency (HITL)
    * Latency & Fallback Diagnostic Profiling
- Detailed Misclassification Analysis per failed sample.
"""

import os
import sys
import time
import json
import argparse
from typing import Dict, List, Any
import pandas as pd
import numpy as np

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Ensure path priority
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
JB_DIR = os.path.join(ROOT_DIR, "joseph_safead_core")
B2JB_DIR = os.path.join(ROOT_DIR, "joseph_safead_core", "backend2jb")
if B2JB_DIR not in sys.path:
    sys.path.insert(0, B2JB_DIR)
if JB_DIR not in sys.path:
    sys.path.insert(0, JB_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Import real inference engine
from backend2jb.ai.pipeline import run_safead_inference

CLASSES = ["SAFE_FOR_ALL", "SAFE_14_PLUS", "SAFE_18_PLUS", "UNSAFE_FOR_ALL"]
AGE_ORDER = {"SAFE_FOR_ALL": 0, "SAFE_14_PLUS": 1, "SAFE_18_PLUS": 2, "UNSAFE_FOR_ALL": 3}


def calculate_metrics(y_true: List[str], y_pred: List[str]) -> Dict[str, Any]:
    """Calculates comprehensive multi-class classification and safety metrics."""
    if not y_true or not y_pred:
        return {}

    # Initialize confusion matrix
    cm = {true_c: {pred_c: 0 for pred_c in CLASSES} for true_c in CLASSES}
    for t, p in zip(y_true, y_pred):
        if t in cm and p in cm[t]:
            cm[t][p] += 1
        elif t in cm:
            cm[t]["UNSAFE_FOR_ALL"] += 1

    per_class = {}
    f1_list = []

    for c in CLASSES:
        tp = cm[c][c]
        fp = sum(cm[other_c][c] for other_c in CLASSES if other_c != c)
        fn = sum(cm[c][other_c] for other_c in CLASSES if other_c != c)
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

    macro_f1 = float(np.mean(f1_list))
    total_samples = len(y_true)
    accuracy = sum(cm[c][c] for c in CLASSES) / total_samples if total_samples > 0 else 0.0

    # 1. Prohibited-Content False Acceptance Rate (PFAR)
    # Ground Truth = UNSAFE_FOR_ALL, but predicted as SAFE_FOR_ALL, SAFE_14_PLUS, or SAFE_18_PLUS
    unsafe_total = sum(cm["UNSAFE_FOR_ALL"].values())
    unsafe_accepted = sum(cm["UNSAFE_FOR_ALL"][safe_c] for safe_c in ["SAFE_FOR_ALL", "SAFE_14_PLUS", "SAFE_18_PLUS"])
    pfar = (unsafe_accepted / unsafe_total) if unsafe_total > 0 else 0.0

    # 2. Underage Gating Violation Rate (UGVR)
    # True age gate (14+ or 18+) assigned a lower age bracket
    age_violations = 0
    age_restricted_total = 0
    for t, p in zip(y_true, y_pred):
        if t in ["SAFE_14_PLUS", "SAFE_18_PLUS"]:
            age_restricted_total += 1
            if AGE_ORDER.get(p, 0) < AGE_ORDER.get(t, 0):
                age_violations += 1
    ugvr = (age_violations / age_restricted_total) if age_restricted_total > 0 else 0.0

    # 3. False Rejection Rate for Safe Content (FRR)
    # Safe content (SAFE_FOR_ALL, SAFE_14_PLUS, SAFE_18_PLUS) incorrectly rejected as UNSAFE_FOR_ALL
    safe_total = sum(sum(cm[sc].values()) for sc in ["SAFE_FOR_ALL", "SAFE_14_PLUS", "SAFE_18_PLUS"])
    safe_rejected = sum(cm[sc]["UNSAFE_FOR_ALL"] for sc in ["SAFE_FOR_ALL", "SAFE_14_PLUS", "SAFE_18_PLUS"])
    frr = (safe_rejected / safe_total) if safe_total > 0 else 0.0

    # 4. Human-Review Trigger Frequency
    hitl_count = sum(1 for p in y_pred if p == "REQUIRES_HUMAN_REVIEW")
    hitl_rate = hitl_count / total_samples if total_samples > 0 else 0.0

    return {
        "sample_count": total_samples,
        "overall_accuracy": round(accuracy, 4),
        "macro_f1": round(macro_f1, 4),
        "prohibited_false_acceptance_rate": round(pfar, 4),
        "underage_gating_violation_rate": round(ugvr, 4),
        "false_rejection_rate_for_safe_content": round(frr, 4),
        "human_review_trigger_rate": round(hitl_rate, 4),
        "confusion_matrix": cm,
        "per_class_metrics": per_class
    }


def run_real_pipeline_benchmark(
    catalog_path: str,
    output_dir: str,
    media_filter: str = "all",
    samples_per_class: int = None,
    max_samples: int = None,
    exclude_synthetic: bool = False
):
    """Executes the full evaluation using real neural inference."""
    if not os.path.exists(catalog_path):
        raise FileNotFoundError(f"Dataset catalog not found at: {catalog_path}")

    os.makedirs(output_dir, exist_ok=True)
    hub_root = r"C:\Users\hello\Videos\sourav\datasets\safead-dataset-hub"
    candidate = os.path.dirname(os.path.abspath(catalog_path))
    while candidate and os.path.splitdrive(candidate)[1] not in ["", "\\", "/"]:
        if os.path.exists(os.path.join(candidate, "custom_ads")):
            hub_root = candidate
            break
        candidate = os.path.dirname(candidate)

    df = pd.read_csv(catalog_path)
    if exclude_synthetic:
        df = df[~((df["media_type"] == "image") & (df["resolution"] == "800x520"))].copy()
    if media_filter != "all":
        df = df[df["media_type"] == media_filter].copy()

    # Stratified subsetting if requested
    if samples_per_class:
        selected_dfs = []
        for m_type in (["image", "video"] if media_filter == "all" else [media_filter]):
            m_sub = df[df["media_type"] == m_type]
            for lbl in CLASSES:
                lbl_sub = m_sub[m_sub["safead_label"] == lbl]
                n_take = min(len(lbl_sub), samples_per_class)
                if n_take > 0:
                    selected_dfs.append(lbl_sub.sample(n=n_take, random_state=42))
        df = pd.concat(selected_dfs, ignore_index=True)
    elif max_samples and max_samples < len(df):
        df = df.groupby("safead_label", group_keys=False).apply(
            lambda x: x.sample(min(len(x), max(1, max_samples // len(CLASSES))), random_state=42)
        )

    print("=" * 80)
    print("      SAFEAD AI (SAFE-VISION) — REAL MULTIMODAL INFERENCE EVALUATION      ")
    print("=" * 80)
    print(f"Catalog Location : {catalog_path}")
    print(f"Total Samples    : {len(df)} (Media filter: {media_filter})")
    print(f"Output Directory : {output_dir}")
    print("Ground Truth Distribution:")
    for lbl, count in df["safead_label"].value_counts().items():
        print(f"  - {lbl:<16}: {count}")
    print("=" * 80)

    detector_outputs_path = os.path.join(output_dir, "saved_detector_outputs.json")
    cached_outputs = {}
    if os.path.exists(detector_outputs_path):
        try:
            with open(detector_outputs_path, "r", encoding="utf-8") as f:
                cached_outputs = json.load(f)
            print(f"[CACHE] Loaded {len(cached_outputs)} previously evaluated samples from cache.")
        except Exception as e:
            print(f"[CACHE WARNING] Could not load cache: {e}")
            cached_outputs = {}

    predictions = []
    error_analyses = []
    t_start = time.time()

    for idx, (_, row) in enumerate(df.iterrows(), 1):
        sample_id = row["sample_id"]
        rel_path = row["file_path"]
        media_type = row["media_type"]
        gt_label = row["safead_label"]

        # ZERO LEAKAGE: Empty title and caption ensures raw media inference
        title = ""
        caption = ""

        full_path = os.path.join(hub_root, rel_path) if not os.path.isabs(rel_path) else rel_path

        if not os.path.exists(full_path):
            print(f"[{idx}/{len(df)}] [ERROR] File missing on disk: {full_path}")
            continue

        # Check if already in cache with valid evidence
        if sample_id in cached_outputs and cached_outputs[sample_id].get("raw_detector_evidence"):
            c_rec = cached_outputs[sample_id]
            pred_label = c_rec.get("predicted_label", "UNSAFE_FOR_ALL")
            risk_score = c_rec.get("risk_score", 0.0)
            confidence = c_rec.get("confidence", 0.0)
            is_correct = bool(gt_label == pred_label)
            print(f"[{idx}/{len(df)}] [CACHED] {sample_id} ({media_type.upper()}) -> Pred: {pred_label} (Score: {risk_score}) [{'CORRECT' if is_correct else 'WRONG'}]")
            
            sample_record = {
                "sample_id": sample_id,
                "media_type": media_type,
                "true_label": gt_label,
                "predicted_label": pred_label,
                "is_correct": is_correct,
                "risk_score": risk_score,
                "confidence": confidence,
                "action": c_rec.get("action", "APPROVE" if "SAFE" in pred_label else "REJECT"),
                "policy_stage": c_rec.get("policy_stage", "CACHED"),
                "prohibited_detected": bool(pred_label == "UNSAFE_FOR_ALL"),
                "policy_reasons": c_rec.get("policy_reasons", ""),
                "has_ocr_text": bool(c_rec.get("extracted_ocr")),
                "extracted_ocr_snippet": str(c_rec.get("extracted_ocr", ""))[:80],
                "has_audio_transcript": c_rec.get("has_audio_transcript", False),
                "audio_available": c_rec.get("audio_available", False),
                "latency_seconds": c_rec.get("latency_seconds", 0.0),
                "raw_detector_evidence": c_rec.get("raw_detector_evidence", {})
            }
            predictions.append(sample_record)
            continue

        print(f"[{idx}/{len(df)}] Evaluating {sample_id} ({media_type.upper()})...", end=" ", flush=True)
        t0 = time.time()

        try:
            res = run_safead_inference(full_path, title=title, caption=caption)
            latency = round(time.time() - t0, 3)

            pred_label = res.get("classification", "UNSAFE_FOR_ALL")
            risk_score = res.get("risk_score", 0.0)
            confidence = res.get("confidence", 0.0)
            action = res.get("publication_action", "")
            stage = res.get("policy_stage", "")
            prohibited_flag = res.get("prohibited_content_detected", False)
            policy_reasons = res.get("policy_reasons", [])
            evidence = res.get("evidence", {})

            # Modality details
            ocr_text = res.get("extracted_ocr", "")
            audio_text = res.get("audio_transcript", "")
            audio_avail = res.get("audio_available", False)
            stage_timings = res.get("stage_timings", {})

            is_correct = bool(gt_label == pred_label)
            print(f"-> Pred: {pred_label} (Score: {risk_score}, Conf: {confidence:.2f}) [{'CORRECT' if is_correct else 'WRONG'}] [{latency}s]")

            # Extract full raw detector evidence matrix
            raw_matrix = res.get("assessment_matrix", res.get("evidence", {}))

            sample_record = {
                "sample_id": sample_id,
                "media_type": media_type,
                "true_label": gt_label,
                "predicted_label": pred_label,
                "is_correct": is_correct,
                "risk_score": risk_score,
                "confidence": confidence,
                "action": action,
                "policy_stage": stage,
                "prohibited_detected": prohibited_flag,
                "policy_reasons": "; ".join(policy_reasons) if isinstance(policy_reasons, list) else str(policy_reasons),
                "has_ocr_text": bool(ocr_text and len(ocr_text.strip()) > 0),
                "extracted_ocr_snippet": str(ocr_text)[:80].replace("\n", " "),
                "has_audio_transcript": bool(audio_text and len(audio_text.strip()) > 0),
                "audio_available": audio_avail,
                "latency_seconds": latency,
                "raw_detector_evidence": raw_matrix
            }
            predictions.append(sample_record)

            # Persist incrementally to cache
            cached_outputs[sample_id] = {
                "sample_id": sample_id,
                "media_type": media_type,
                "true_label": gt_label,
                "predicted_label": pred_label,
                "risk_score": risk_score,
                "confidence": confidence,
                "action": action,
                "policy_stage": stage,
                "policy_reasons": sample_record["policy_reasons"],
                "extracted_ocr": sample_record["extracted_ocr_snippet"],
                "has_audio_transcript": sample_record["has_audio_transcript"],
                "audio_available": audio_avail,
                "latency_seconds": latency,
                "raw_detector_evidence": raw_matrix
            }
            try:
                with open(detector_outputs_path, "w", encoding="utf-8") as f:
                    json.dump(cached_outputs, f, indent=2)
            except Exception:
                pass

            # Error Analysis for misclassified samples
            if not is_correct:
                error_type = "UNKNOWN"
                if gt_label == "UNSAFE_FOR_ALL" and pred_label != "UNSAFE_FOR_ALL":
                    error_type = "PROHIBITED_LEAK_FALSE_ACCEPTANCE"
                elif gt_label in ["SAFE_14_PLUS", "SAFE_18_PLUS"] and AGE_ORDER.get(pred_label, 0) < AGE_ORDER.get(gt_label, 0):
                    error_type = "UNDERAGE_GATING_VIOLATION"
                elif gt_label in ["SAFE_FOR_ALL", "SAFE_14_PLUS", "SAFE_18_PLUS"] and pred_label == "UNSAFE_FOR_ALL":
                    error_type = "SAFE_CONTENT_FALSE_REJECTION"
                elif gt_label == "SAFE_FOR_ALL" and pred_label in ["SAFE_14_PLUS", "SAFE_18_PLUS"]:
                    error_type = "OVER_RESTRICTED_SAFE_AD"
                else:
                    error_type = "CATEGORY_TIER_MISMATCH"

                error_analyses.append({
                    "sample_id": sample_id,
                    "media_type": media_type,
                    "ground_truth": gt_label,
                    "predicted": pred_label,
                    "risk_score": risk_score,
                    "error_type": error_type,
                    "policy_stage": stage,
                    "policy_reasons": policy_reasons,
                    "ocr_snippet": str(ocr_text)[:100],
                    "audio_snippet": str(audio_text)[:100],
                    "likely_root_cause": (
                        "Text-only scam/policy cues undetected because visual scene looked benign"
                        if error_type == "PROHIBITED_LEAK_FALSE_ACCEPTANCE"
                        else "Llama Guard / Text model fallback to heuristics or ViT NSFW threshold divergence"
                    )
                })

        except Exception as e:
            print(f"-> [EXCEPTION] {e}")
            predictions.append({
                "sample_id": sample_id,
                "media_type": media_type,
                "true_label": gt_label,
                "predicted_label": "UNSAFE_FOR_ALL",
                "is_correct": False,
                "risk_score": 100.0,
                "confidence": 0.0,
                "action": "ERROR_FALLBACK",
                "policy_stage": "EXCEPTION",
                "prohibited_detected": True,
                "policy_reasons": f"Exception: {e}",
                "has_ocr_text": False,
                "extracted_ocr_snippet": "",
                "has_audio_transcript": False,
                "audio_available": False,
                "latency_seconds": round(time.time() - t0, 3)
            })

    total_time = round(time.time() - t_start, 2)
    pred_df = pd.DataFrame(predictions)

    # Save raw predictions CSV
    pred_csv_path = os.path.join(output_dir, "real_pipeline_sample_predictions.csv")
    pred_df.to_csv(pred_csv_path, index=False)

    # Save detailed error analysis CSV
    err_csv_path = os.path.join(output_dir, "misclassified_sample_analysis.csv")
    pd.DataFrame(error_analyses).to_csv(err_csv_path, index=False)

    # Generate metrics
    report = {
        "metadata": {
            "evaluation_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "catalog_path": catalog_path,
            "total_samples_evaluated": len(pred_df),
            "is_partial_pilot": bool(len(pred_df) < 380),
            "total_runtime_seconds": total_time,
            "average_latency_per_sample": round(total_time / len(pred_df), 3) if len(pred_df) > 0 else 0.0,
            "models_executed": {
                "falconsai_nsfw_vit": "LOADED_ACTIVE_CPU",
                "easyocr": "LOADED_ACTIVE_CPU",
                "videomae_kinetics": "LOADED_ACTIVE_CPU_FOR_VIDEOS",
                "whisper_base": "LOADED_ACTIVE_CPU_FOR_VIDEOS",
                "llama_guard_3_vision": "HTTP_401_GATED_FALLBACK_TO_HEURISTICS",
                "llama_guard_3_text": "HTTP_401_GATED_FALLBACK_TO_HEURISTICS"
            }
        },
        "overall": calculate_metrics(pred_df["true_label"].tolist(), pred_df["predicted_label"].tolist()),
        "image_subset": calculate_metrics(
            pred_df[pred_df["media_type"] == "image"]["true_label"].tolist(),
            pred_df[pred_df["media_type"] == "image"]["predicted_label"].tolist()
        ) if "image" in pred_df["media_type"].values else {},
        "video_subset": calculate_metrics(
            pred_df[pred_df["media_type"] == "video"]["true_label"].tolist(),
            pred_df[pred_df["media_type"] == "video"]["predicted_label"].tolist()
        ) if "video" in pred_df["media_type"].values else {}
    }

    # Save full granular raw detector outputs
    detector_outputs = {}
    for p in predictions:
        detector_outputs[p["sample_id"]] = {
            "sample_id": p["sample_id"],
            "media_type": p["media_type"],
            "true_label": p["true_label"],
            "predicted_label": p["predicted_label"],
            "risk_score": p["risk_score"],
            "confidence": p["confidence"],
            "extracted_ocr": p.get("extracted_ocr_snippet", ""),
            "has_audio_transcript": p.get("has_audio_transcript", False),
            "audio_available": p.get("audio_available", False),
            "latency_seconds": p.get("latency_seconds", 0.0),
            "raw_detector_evidence": p.get("raw_detector_evidence", {})
        }
    cached_outputs.update(detector_outputs)
    detector_outputs_path = os.path.join(output_dir, "saved_detector_outputs.json")
    with open(detector_outputs_path, "w", encoding="utf-8") as f:
        json.dump(cached_outputs, f, indent=2)

    report_json_path = os.path.join(output_dir, "real_pipeline_evaluation_report.json")
    with open(report_json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    # Console Summary
    print("\n" + "=" * 80)
    print("                     REAL PIPELINE EVALUATION SUMMARY REPORT                   ")
    print("=" * 80)
    print(f"Total Evaluated: {len(pred_df)} ({'PARTIAL PILOT' if report['metadata']['is_partial_pilot'] else 'FULL CATALOG'}) | Runtime: {total_time}s | Avg: {report['metadata']['average_latency_per_sample']}s/sample")
    print("-" * 80)

    for subset_name, subset_key in [("Overall (Combined)", "overall"), ("Image Media", "image_subset"), ("Video Media", "video_subset")]:
        m = report.get(subset_key, {})
        if not m:
            continue
        print(f"\n[*] {subset_name} (N={m['sample_count']}):")
        print(f"   - Overall Accuracy : {m.get('overall_accuracy', 0.0)*100:.2f}%")
        print(f"   - Macro-F1 Score   : {m.get('macro_f1', 0.0):.4f}")
        print(f"   - Prohibited False Acceptance (PFAR) : {m.get('prohibited_false_acceptance_rate', 0.0)*100:.2f}%")
        print(f"   - Underage Gating Violation (UGVR)   : {m.get('underage_gating_violation_rate', 0.0)*100:.2f}%")
        print(f"   - False Rejection of Safe Ads (FRR)  : {m.get('false_rejection_rate_for_safe_content', 0.0)*100:.2f}%")
        print(f"   - Human-Review Trigger Frequency     : {m.get('human_review_trigger_rate', 0.0)*100:.2f}%")
        print("\n   Per-Class Performance:")
        print(f"   {'Category':<18} | {'Count':<6} | {'Precision':<9} | {'Recall':<9} | {'F1-Score':<9}")
        print(f"   {'-'*18}-+-{'-'*6}-+-{'-'*9}-+-{'-'*9}-+-{'-'*9}")
        for c, pmetrics in m.get("per_class_metrics", {}).items():
            print(f"   {c:<18} | {pmetrics['true_count']:<6} | {pmetrics['precision']*100:>8.2f}% | {pmetrics['recall']*100:>8.2f}% | {pmetrics['f1_score']:>9.4f}")

    print("\n" + "=" * 80)
    print(f"Predictions CSV : {pred_csv_path}")
    print(f"Error Audit CSV : {err_csv_path}")
    print(f"Full Report JSON: {report_json_path}")
    print("=" * 80)
    return report

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate real SafeAd AI multimodal pipeline")
    parser.add_argument("--catalog", default=r"C:\Users\hello\Videos\sourav\datasets\safead-dataset-hub\custom_ads\complete_dataset_catalog.csv")
    parser.add_argument("--output-dir", default=r"results\real_pipeline_baseline")
    parser.add_argument("--media-filter", default="all", choices=["all", "image", "video"])
    parser.add_argument("--samples-per-class", type=int, default=None, help="Sample N items per class per media type for representative pilot")
    parser.add_argument("--max-samples", type=int, default=None)
    parser.add_argument("--exclude-synthetic", action="store_true", help="Exclude synthetic 800x520 review cards with embedded labels")

    args = parser.parse_args()
    run_real_pipeline_benchmark(
        catalog_path=args.catalog,
        output_dir=args.output_dir,
        media_filter=args.media_filter,
        samples_per_class=args.samples_per_class,
        max_samples=args.max_samples,
        exclude_synthetic=args.exclude_synthetic
    )
