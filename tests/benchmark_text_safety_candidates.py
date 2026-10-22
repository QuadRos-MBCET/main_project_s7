"""
SafeAd AI (SAFE-VISION) — Phase 5A Task 2: Comparative Text Safety Classifier Benchmark.

Compares:
1. Production Baseline: Multilingual Keyword Rules
2. Zero-Shot NLI: DeBERTa-v3-base
3. Experimental: Domain-Specific Ad Fraud & Deceptive Marketing Classifier

Evaluated on the 14 real extracted ad text cases from Dev OCR & Whisper.
Reports Precision, Recall, F1, False Positives, False Negatives, and Latency.
"""

import sys
import os
import time
import json
from typing import Dict, Any, List
import pandas as pd
import numpy as np

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
B2JB_DIR = os.path.join(ROOT_DIR, "joseph_safead_core", "backend2jb")
for p in [ROOT_DIR, B2JB_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

from tests.evaluate_deberta_on_real_extracted_text import REAL_EXTRACTED_TEXT_BENCHMARK
from tests.experimental_ad_text_classifier import ExperimentalDomainAdTextClassifier
from models.text_safety import SafeAdTextSafetyDetector
from tests.experiment_deberta_text_safety import IsolatedDebertaClassifier


def run_text_benchmark():
    print("=" * 80)
    print("      SAFEAD AI: COMPARATIVE TEXT SAFETY CLASSIFIER BENCHMARK (PHASE 5A)     ")
    print("=" * 80)

    # Initialize candidates
    baseline_detector = SafeAdTextSafetyDetector()
    deberta = IsolatedDebertaClassifier().load()
    domain_clf = ExperimentalDomainAdTextClassifier(use_local_toxic_bert=True)

    candidates = {
        "Baseline (Keyword Rules)": {"preds": [], "latencies": [], "tp": 0, "fp": 0, "fn": 0, "tn": 0},
        "DeBERTa-v3-base (Zero-Shot)": {"preds": [], "latencies": [], "tp": 0, "fp": 0, "fn": 0, "tn": 0},
        "Experimental Domain Classifier": {"preds": [], "latencies": [], "tp": 0, "fp": 0, "fn": 0, "tn": 0}
    }

    per_sample_audit = []

    for item in REAL_EXTRACTED_TEXT_BENCHMARK:
        sid = item["id"]
        text = item["text"]
        gt = item["gt_prohibited"]

        # 1. Baseline
        t0 = time.time()
        res_base = baseline_detector.predict_text(text)
        lat_base = (time.time() - t0) * 1000.0
        # In baseline, overall_text_risk >= 0.85 indicates prohibited violation
        pred_base = bool(res_base["overall_text_risk"] >= 0.85 or "Misleading Advertisement" in res_base["detected_categories"])

        # 2. DeBERTa
        t1 = time.time()
        if text.strip():
            res_deb = deberta.predict(text)
            pred_deb = bool(res_deb["is_flagged_prohibited"])
        else:
            pred_deb = False
        lat_deb = (time.time() - t1) * 1000.0

        # 3. Experimental Domain Classifier
        t2 = time.time()
        res_exp = domain_clf.predict(text)
        lat_exp = (time.time() - t2) * 1000.0
        pred_exp = bool(res_exp["is_flagged_prohibited"])

        # Record confusion
        for c_name, pred, lat in [
            ("Baseline (Keyword Rules)", pred_base, lat_base),
            ("DeBERTa-v3-base (Zero-Shot)", pred_deb, lat_deb),
            ("Experimental Domain Classifier", pred_exp, lat_exp)
        ]:
            c_dict = candidates[c_name]
            c_dict["preds"].append(pred)
            c_dict["latencies"].append(lat)
            if gt and pred:
                c_dict["tp"] += 1
            elif not gt and pred:
                c_dict["fp"] += 1
            elif gt and not pred:
                c_dict["fn"] += 1
            else:
                c_dict["tn"] += 1

        per_sample_audit.append({
            "id": sid,
            "type": item["type"],
            "gt_prohibited": gt,
            "pred_baseline": pred_base,
            "pred_deberta": pred_deb,
            "pred_experimental": pred_exp,
            "exp_violations": res_exp["violation_types"]
        })

    # Compute comparative metrics
    print(f"\nTotal Evaluated Cases: {len(REAL_EXTRACTED_TEXT_BENCHMARK)}")
    print(f"{'Metric':<32} | {'Baseline (Keywords)':<20} | {'DeBERTa-v3 (NLI)':<18} | {'Experimental Domain Classifier':<25}")
    print("-" * 32 + "-+-" + "-" * 20 + "-+-" + "-" * 18 + "-+-" + "-" * 30)

    summary_results = {}
    for c_name, c_dict in candidates.items():
        tp = c_dict["tp"]
        fp = c_dict["fp"]
        fn = c_dict["fn"]
        tn = c_dict["tn"]
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0
        avg_lat = float(np.mean(c_dict["latencies"]))

        summary_results[c_name] = {
            "tp": tp, "fp": fp, "fn": fn, "tn": tn,
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1": round(f1, 4),
            "avg_latency_ms": round(avg_lat, 2)
        }

    s_base = summary_results["Baseline (Keyword Rules)"]
    s_deb = summary_results["DeBERTa-v3-base (Zero-Shot)"]
    s_exp = summary_results["Experimental Domain Classifier"]

    print(f"{'True Positives (TP)':<32} | {s_base['tp']:>18} | {s_deb['tp']:>16} | {s_exp['tp']:>28}")
    print(f"{'False Negatives (FN - Misses)':<32} | {s_base['fn']:>18} | {s_deb['fn']:>16} | {s_exp['fn']:>28}")
    print(f"{'False Positives (FP - Alarms)':<32} | {s_base['fp']:>18} | {s_deb['fp']:>16} | {s_exp['fp']:>28}")
    print(f"{'Precision':<32} | {s_base['precision']*100:>17.2f}% | {s_deb['precision']*100:>15.2f}% | {s_exp['precision']*100:>27.2f}%")
    print(f"{'Recall':<32} | {s_base['recall']*100:>17.2f}% | {s_deb['recall']*100:>15.2f}% | {s_exp['recall']*100:>27.2f}%")
    print(f"{'F1-Score':<32} | {s_base['f1']:>18.4f} | {s_deb['f1']:>16.4f} | {s_exp['f1']:>28.4f}")
    print(f"{'Average Latency per Text':<32} | {s_base['avg_latency_ms']:>15.2f} ms | {s_deb['avg_latency_ms']:>13.2f} ms | {s_exp['avg_latency_ms']:>25.2f} ms")
    print("=" * 80)

    # Save artifact report
    output_path = "results/real_pipeline_baseline/phase5a_text_safety_benchmark.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"summary": summary_results, "per_sample": per_sample_audit}, f, indent=2)
    print(f"Detailed benchmark saved to: {output_path}")

    return summary_results


if __name__ == "__main__":
    run_text_benchmark()
