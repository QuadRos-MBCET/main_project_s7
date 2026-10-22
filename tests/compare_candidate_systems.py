#!/usr/bin/env python3
"""
SafeAd AI (SAFE-VISION) — Phase 5B: Five-System Architectural Comparison Runner.

Evaluates and compares the 5 candidate architectures across clean development data:
System A: Original Baseline: Current Production Fusion + Keyword Rules
System B: Repaired Detector Infrastructure + Current Production Fusion
System C: Repaired Detector Infrastructure + Policy-First Fusion (No HITL)
System D1: Repaired Detectors + Policy-First Fusion + Domain Ad Text Classifier (No HITL)
System D2: Repaired Detectors + Policy-First Fusion + Domain Ad Text Classifier (With HITL)
"""

import os
import sys
import json
import time
from typing import Dict, Any, List
import pandas as pd
import numpy as np

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
JB_DIR = os.path.join(ROOT_DIR, "joseph_safead_core")
B2JB_DIR = os.path.join(ROOT_DIR, "joseph_safead_core", "backend2jb")
for p in [ROOT_DIR, JB_DIR, B2JB_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

from models.fusion.safead_fusion import SafeAdFusion
from models.fusion.experimental_policy_fusion import ExperimentalPolicyFusion
from tests.experimental_ad_text_classifier import ExperimentalDomainAdTextClassifier

CLASSES = ["SAFE_FOR_ALL", "SAFE_14_PLUS", "SAFE_18_PLUS", "UNSAFE_FOR_ALL"]
AGE_ORDER = {"SAFE_FOR_ALL": 0, "SAFE_14_PLUS": 1, "SAFE_18_PLUS": 2, "UNSAFE_FOR_ALL": 3, "REQUIRES_HUMAN_REVIEW": -1}


def calculate_system_metrics(y_true: List[str], y_pred: List[str]) -> Dict[str, Any]:
    if not y_true or not y_pred:
        return {}

    cm = {true_c: {pred_c: 0 for pred_c in CLASSES + ["REQUIRES_HUMAN_REVIEW"]} for true_c in CLASSES}
    for t, p in zip(y_true, y_pred):
        if t in cm:
            if p in cm[t]:
                cm[t][p] += 1
            else:
                cm[t]["UNSAFE_FOR_ALL"] += 1

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
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4)
        }
        f1_list.append(f1)

    macro_f1 = float(np.mean(f1_list))
    total_samples = len(y_true)
    correct_samples = sum(cm[c][c] for c in CLASSES)
    accuracy = correct_samples / total_samples if total_samples > 0 else 0.0

    # 1. Prohibited False Acceptance Rate (PFAR)
    unsafe_total = sum(cm["UNSAFE_FOR_ALL"].values())
    unsafe_accepted = sum(cm["UNSAFE_FOR_ALL"][safe_c] for safe_c in ["SAFE_FOR_ALL", "SAFE_14_PLUS", "SAFE_18_PLUS"])
    pfar = (unsafe_accepted / unsafe_total) if unsafe_total > 0 else 0.0

    # 2. Underage Gating Violation Rate (UGVR)
    age_violations = 0
    age_restricted_total = 0
    for t, p in zip(y_true, y_pred):
        if t in ["SAFE_14_PLUS", "SAFE_18_PLUS"]:
            age_restricted_total += 1
            if AGE_ORDER.get(p, 0) < AGE_ORDER.get(t, 0) and p != "REQUIRES_HUMAN_REVIEW":
                age_violations += 1
    ugvr = (age_violations / age_restricted_total) if age_restricted_total > 0 else 0.0

    # 3. False Rejection Rate for Safe Content (FRR)
    # Ground truth in [SAFE_FOR_ALL, SAFE_14_PLUS, SAFE_18_PLUS], but predicted as UNSAFE_FOR_ALL
    safe_gt_total = sum(cm[c][p] for c in ["SAFE_FOR_ALL", "SAFE_14_PLUS", "SAFE_18_PLUS"] for p in cm[c])
    safe_rejected = sum(cm[c]["UNSAFE_FOR_ALL"] for c in ["SAFE_FOR_ALL", "SAFE_14_PLUS", "SAFE_18_PLUS"])
    frr = (safe_rejected / safe_gt_total) if safe_gt_total > 0 else 0.0

    # 4. Over-Restriction Rate for General Safe Ads
    # Ground truth SAFE_FOR_ALL, but predicted as SAFE_14_PLUS or SAFE_18_PLUS
    sfa_total = sum(cm["SAFE_FOR_ALL"].values())
    sfa_over_restricted = cm["SAFE_FOR_ALL"]["SAFE_14_PLUS"] + cm["SAFE_FOR_ALL"]["SAFE_18_PLUS"]
    over_restriction_rate = (sfa_over_restricted / sfa_total) if sfa_total > 0 else 0.0

    # 5. Human Review Frequency & Coverage
    hitl_count = sum(1 for p in y_pred if p == "REQUIRES_HUMAN_REVIEW")
    hitl_rate = hitl_count / total_samples if total_samples > 0 else 0.0
    coverage = (total_samples - hitl_count) / total_samples if total_samples > 0 else 1.0

    # Accuracy on covered slice
    covered_total = total_samples - hitl_count
    accuracy_covered = (correct_samples / covered_total) if covered_total > 0 else 0.0

    return {
        "sample_count": total_samples,
        "accuracy": round(accuracy, 4),
        "accuracy_covered": round(accuracy_covered, 4),
        "coverage": round(coverage, 4),
        "hitl_rate": round(hitl_rate, 4),
        "macro_f1": round(macro_f1, 4),
        "pfar": round(pfar, 4),
        "ugvr": round(ugvr, 4),
        "frr": round(frr, 4),
        "over_restriction_rate": round(over_restriction_rate, 4),
        "recalls": {c: per_class[c]["recall"] for c in CLASSES},
        "precisions": {c: per_class[c]["precision"] for c in CLASSES},
        "f1_scores": {c: per_class[c]["f1_score"] for c in CLASSES},
        "confusion_matrix": cm
    }


def run_four_system_comparison():
    print("=" * 80)
    print("       SAFEAD AI: 5-CANDIDATE ARCHITECTURE COMPARISON EXPERIMENT (PHASE 5B)    ")
    print("=" * 80)

    cache_path = os.path.join(ROOT_DIR, "results", "real_pipeline_baseline", "saved_detector_outputs.json")
    if not os.path.exists(cache_path):
        raise FileNotFoundError(f"Detector cache not found at: {cache_path}")

    with open(cache_path, "r", encoding="utf-8") as f:
        cached_data = json.load(f)

    print(f"Loaded {len(cached_data)} cached development samples with raw detector outputs.")

    prod_fusion = SafeAdFusion()
    exp_policy_fusion_no_hitl = ExperimentalPolicyFusion(enable_ambiguity_routing=False)
    exp_policy_fusion_with_hitl = ExperimentalPolicyFusion(enable_ambiguity_routing=True)
    domain_text_clf = ExperimentalDomainAdTextClassifier(use_local_toxic_bert=False)

    print("Evaluating domain-specific ad text classifier on extracted OCR/audio transcripts...")
    domain_scores = {}
    for sid, record in cached_data.items():
        text = str(record.get("extracted_ocr", ""))
        domain_scores[sid] = domain_text_clf.predict(text)

    y_true = [record["true_label"] for record in cached_data.values()]
    systems = {
        "System_A": {"name": "Current Prod Fusion + Keyword Rules", "preds": []},
        "System_B": {"name": "Current Prod Fusion + Repaired Detectors", "preds": []},
        "System_C": {"name": "Policy-First Fusion + Keyword Rules", "preds": []},
        "System_D1": {"name": "Policy-First + Domain Text (No HITL)", "preds": []},
        "System_D2": {"name": "Policy-First + Domain Text (With HITL)", "preds": []}
    }

    paired_comparisons = []

    for sid, record in cached_data.items():
        evidence = record.get("raw_detector_evidence", {})
        domain_out = domain_scores[sid]

        # System A: Original baseline production fusion
        res_a = prod_fusion.combine_assessment(evidence)
        systems["System_A"]["preds"].append(res_a["classification"])

        # System B: Repaired detector evidence in production fusion
        evidence_b = json.loads(json.dumps(evidence))
        if domain_out["is_flagged_prohibited"]:
            evidence_b.setdefault("advertisement_risks", {})["scam"] = max(
                evidence_b.get("advertisement_risks", {}).get("scam", 0.0),
                domain_out["prohibited_risk"]
            )
        res_b = prod_fusion.combine_assessment(evidence_b)
        systems["System_B"]["preds"].append(res_b["classification"])

        # System C: Policy-First + Keyword rules (No HITL)
        res_c = exp_policy_fusion_no_hitl.combine_assessment(evidence, improved_text_output=None)
        systems["System_C"]["preds"].append(res_c["classification"])

        # System D1: Policy-First + Domain Text (No HITL)
        res_d1 = exp_policy_fusion_no_hitl.combine_assessment(evidence, improved_text_output=domain_out)
        systems["System_D1"]["preds"].append(res_d1["classification"])

        # System D2: Policy-First + Domain Text (With HITL)
        res_d2 = exp_policy_fusion_with_hitl.combine_assessment(evidence, improved_text_output=domain_out)
        systems["System_D2"]["preds"].append(res_d2["classification"])

        paired_comparisons.append({
            "sample_id": sid,
            "true_label": record["true_label"],
            "pred_sys_a": res_a["classification"],
            "pred_sys_b": res_b["classification"],
            "pred_sys_c": res_c["classification"],
            "pred_sys_d1": res_d1["classification"],
            "pred_sys_d2": res_d2["classification"],
            "domain_violations": domain_out["violation_types"],
            "ocr_snippet": str(record.get("extracted_ocr", ""))[:60]
        })

    summary_results = {}
    for sys_key, sys_info in systems.items():
        m = calculate_system_metrics(y_true, sys_info["preds"])
        summary_results[sys_key] = {
            "name": sys_info["name"],
            "metrics": m
        }

    # Print Table
    print("\n" + "=" * 90)
    print("                     FIVE-SYSTEM ARCHITECTURAL COMPARISON (PHASE 5B)           ")
    print("=" * 90)
    print(f"{'Metric':<32} | {'Sys A (Base)':<12} | {'Sys B (Rep)':<12} | {'Sys C (Pol1)':<12} | {'Sys D1 (Dom)':<12} | {'Sys D2 (HITL)':<12}")
    print("-" * 32 + "-+-" + "-" * 12 + "-+-" + "-" * 12 + "-+-" + "-" * 12 + "-+-" + "-" * 12 + "-+-" + "-" * 12)

    for k in ["accuracy", "accuracy_covered", "coverage", "macro_f1", "pfar", "ugvr", "frr", "over_restriction_rate", "hitl_rate"]:
        row = f"{k.replace('_', ' ').title():<32} | "
        for s_key in ["System_A", "System_B", "System_C", "System_D1", "System_D2"]:
            val = summary_results[s_key]["metrics"].get(k, 0.0)
            if k in ["macro_f1"]:
                row += f"{val:>10.4f} | "
            else:
                row += f"{val*100:>9.2f}% | "
        print(row)

    print("-" * 32 + "-+-" + "-" * 12 + "-+-" + "-" * 12 + "-+-" + "-" * 12 + "-+-" + "-" * 12 + "-+-" + "-" * 12)
    for c in CLASSES:
        # Precision
        row_p = f"Precision: {c:<21} | "
        for s_key in ["System_A", "System_B", "System_C", "System_D1", "System_D2"]:
            prec = summary_results[s_key]["metrics"]["precisions"].get(c, 0.0)
            row_p += f"{prec*100:>9.2f}% | "
        print(row_p)
        # Recall
        row_r = f"Recall: {c:<24} | "
        for s_key in ["System_A", "System_B", "System_C", "System_D1", "System_D2"]:
            rec = summary_results[s_key]["metrics"]["recalls"].get(c, 0.0)
            row_r += f"{rec*100:>9.2f}% | "
        print(row_r)
        # F1
        row_f = f"F1-Score: {c:<22} | "
        for s_key in ["System_A", "System_B", "System_C", "System_D1", "System_D2"]:
            f1 = summary_results[s_key]["metrics"]["f1_scores"].get(c, 0.0)
            row_f += f"{f1:>10.4f} | "
        print(row_f)
        print("." * 32 + "-+-" + "." * 12 + "-+-" + "." * 12 + "-+-" + "." * 12 + "-+-" + "." * 12 + "-+-" + "." * 12)
    print("=" * 90)

    out_path = os.path.join(ROOT_DIR, "results", "real_pipeline_baseline", "phase5b_four_system_comparison.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"systems": summary_results, "paired": paired_comparisons}, f, indent=2)
    print(f"\nComparison report saved to: {out_path}")

    return summary_results


if __name__ == "__main__":
    run_four_system_comparison()
