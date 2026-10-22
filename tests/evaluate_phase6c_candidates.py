"""
SafeAd AI (SAFE-VISION) — Phase 6C: Safety Regression Repair and Candidate Selection Runner.

Compares:
- Candidate A: Frozen Phase 5B Baseline.
- Candidate B: Baseline + EnhancedAlcoholDetector.
- Candidate C: Baseline + Safeguarded KineticViolenceDecoupler.
- Candidate D: Baseline + Both Improvements (Alcohol + Safeguarded Violence Decoupler).
- Candidate D-HITL: Both Improvements + Policy-First Ambiguity Routing.

Prioritizes prevention of prohibited-content exposure over raw accuracy.
DOES NOT modify production fusion code in safead_fusion.py.
DOES NOT modify catalog ground-truth labels.
DOES NOT access the held-out test set.
"""

import os
import sys
import json
import copy
from typing import Dict, Any, List, Tuple
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
from tests.experimental_repaired_detectors import (
    EnhancedAlcoholDetector,
    KineticViolenceDecoupler
)

CLASSES = ["SAFE_FOR_ALL", "SAFE_14_PLUS", "SAFE_18_PLUS", "UNSAFE_FOR_ALL"]
AGE_ORDER = {"SAFE_FOR_ALL": 0, "SAFE_14_PLUS": 1, "SAFE_18_PLUS": 2, "UNSAFE_FOR_ALL": 3, "REQUIRES_HUMAN_REVIEW": -1}


def calculate_safety_metrics(y_true: List[str], y_pred: List[str]) -> Dict[str, Any]:
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
            "fp": fp,
            "fn": fn,
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

    # 3. False Rejection Rate (FRR)
    safe_gt_total = sum(cm[c][p] for c in ["SAFE_FOR_ALL", "SAFE_14_PLUS", "SAFE_18_PLUS"] for p in cm[c])
    safe_rejected = sum(cm[c]["UNSAFE_FOR_ALL"] for c in ["SAFE_FOR_ALL", "SAFE_14_PLUS", "SAFE_18_PLUS"])
    frr = (safe_rejected / safe_gt_total) if safe_gt_total > 0 else 0.0

    # 4. Over-Restriction Rate (Safe Ads)
    sfa_total = sum(cm["SAFE_FOR_ALL"].values())
    sfa_over_restricted = cm["SAFE_FOR_ALL"]["SAFE_14_PLUS"] + cm["SAFE_FOR_ALL"]["SAFE_18_PLUS"]
    over_restriction_rate = (sfa_over_restricted / sfa_total) if sfa_total > 0 else 0.0

    # 5. Human Review Frequency & Coverage
    hitl_count = sum(1 for p in y_pred if p == "REQUIRES_HUMAN_REVIEW")
    hitl_rate = hitl_count / total_samples if total_samples > 0 else 0.0
    coverage = (total_samples - hitl_count) / total_samples if total_samples > 0 else 1.0

    # 6. Prohibited Exposure Among Automatically Released Ads
    released_count = total_samples - hitl_count
    prohibited_exposure_rate = (unsafe_accepted / released_count) if released_count > 0 else 0.0

    # 7. Accuracy on Covered Subset
    accuracy_covered = (correct_samples / released_count) if released_count > 0 else 0.0

    return {
        "sample_count": total_samples,
        "correct_count": correct_samples,
        "accuracy": round(accuracy, 4),
        "accuracy_covered": round(accuracy_covered, 4),
        "coverage": round(coverage, 4),
        "hitl_count": hitl_count,
        "hitl_rate": round(hitl_rate, 4),
        "macro_f1": round(macro_f1, 4),
        "pfar": round(pfar, 4),
        "pfar_num": unsafe_accepted,
        "pfar_den": unsafe_total,
        "ugvr": round(ugvr, 4),
        "ugvr_num": age_violations,
        "ugvr_den": age_restricted_total,
        "frr": round(frr, 4),
        "frr_num": safe_rejected,
        "frr_den": safe_gt_total,
        "over_restriction_rate": round(over_restriction_rate, 4),
        "over_restriction_num": sfa_over_restricted,
        "over_restriction_den": sfa_total,
        "prohibited_exposure_rate": round(prohibited_exposure_rate, 4),
        "prohibited_exposure_num": unsafe_accepted,
        "prohibited_exposure_den": released_count,
        "recalls": {c: per_class[c]["recall"] for c in CLASSES},
        "precisions": {c: per_class[c]["precision"] for c in CLASSES},
        "f1_scores": {c: per_class[c]["f1_score"] for c in CLASSES},
        "confusion_matrix": cm
    }


def main():
    print("=" * 85)
    print("      SAFEAD AI: PHASE 6C SAFETY REGRESSION REPAIR & CANDIDATE SELECTION       ")
    print("=" * 85)

    cache_path = os.path.join(ROOT_DIR, "results", "real_pipeline_baseline", "saved_detector_outputs.json")
    with open(cache_path, "r", encoding="utf-8") as f:
        cached_data = json.load(f)

    cat_path = r"C:\Users\hello\Videos\sourav\datasets\safead-dataset-hub\splits\repaired_benchmark\development_set.csv"
    df_cat = pd.read_csv(cat_path)
    clean_cat = df_cat[~((df_cat["media_type"] == "image") & (df_cat["resolution"] == "800x520"))].set_index("sample_id")

    sample_ids = list(cached_data.keys())
    assert len(sample_ids) == 194
    y_true = [cached_data[sid]["true_label"] for sid in sample_ids]

    alcohol_detector = EnhancedAlcoholDetector()
    violence_decoupler = KineticViolenceDecoupler()

    prod_fusion = SafeAdFusion()
    policy_fusion_hitl = ExperimentalPolicyFusion(enable_ambiguity_routing=True)

    candidates = {
        "Candidate_A": {"name": "Frozen Phase 5B Baseline", "preds": []},
        "Candidate_B": {"name": "Baseline + EnhancedAlcoholDetector", "preds": []},
        "Candidate_C": {"name": "Baseline + Safeguarded Violence Decoupler", "preds": []},
        "Candidate_D": {"name": "Baseline + Both Improvements (Alcohol + Safeguarded Violence)", "preds": []},
        "Candidate_D_HITL": {"name": "Candidate D + Policy-First HITL Ambiguity Routing", "preds": []}
    }

    sample_logs = []

    for sid in sample_ids:
        rec = cached_data[sid]
        ev_base = rec.get("raw_detector_evidence", {})
        gt_lbl = rec["true_label"]
        ocr_tx = rec.get("extracted_ocr", "")
        aud_tx = ev_base.get("audio", {}).get("transcript", "")
        vis_ev = ev_base.get("visual", {}).get("evidence", [])
        vis_cap = " ".join(vis_ev) if isinstance(vis_ev, list) else str(vis_ev)
        vis_violence_flag = bool(ev_base.get("visual", {}).get("unsafe", False) or "Violence" in ev_base.get("visual", {}).get("evidence", []))

        # ---------------- Candidate A: Frozen Phase 5B Baseline ----------------
        res_a = prod_fusion.combine_assessment(ev_base)
        pred_a = res_a["classification"]
        candidates["Candidate_A"]["preds"].append(pred_a)

        # ---------------- Candidate B: Baseline + Alcohol Detector ----------------
        ev_b = copy.deepcopy(ev_base)
        res_alc = alcohol_detector.detect(ocr_text=ocr_tx, visual_caption=vis_cap, audio_text=aud_tx)
        if res_alc["alcohol_detected"]:
            ev_b.setdefault("text_safety", {}).setdefault("categories", {})["alcohol"] = res_alc["score"]
            ev_b.setdefault("advertisement_risks", {})["explicit_content"] = max(ev_b.get("advertisement_risks", {}).get("explicit_content", 0.0), res_alc["score"])
        res_b = prod_fusion.combine_assessment(ev_b)
        pred_b = res_b["classification"]
        candidates["Candidate_B"]["preds"].append(pred_b)

        # ---------------- Candidate C: Baseline + Safeguarded Violence Decoupler ----------------
        ev_c = copy.deepcopy(ev_base)
        route_c_hitl = False
        c_reasons = []

        if rec["media_type"] == "video":
            segments = ev_c.get("video", {}).get("sampled_segments", [])
            raw_mot = 25.0 if ev_c.get("video", {}).get("violence", 0.0) >= 0.20 else 5.0
            res_v = violence_decoupler.evaluate_video_action(
                sampled_segments=segments,
                raw_motion_diff=raw_mot,
                text_context=aud_tx,
                visual_violence_flag=vis_violence_flag
            )
            ev_c["video"]["violence"] = res_v["violence_score"]

            if res_v["requires_human_review"]:
                # Fail-safe: Route to Human Review and WITHHOLD publication
                route_c_hitl = True
                c_reasons.extend(res_v["policy_reasons"])
            elif not res_v["violence_detected"] and not vis_violence_flag:
                # Confirmed non-violent: suppress frame difference motion
                ev_c["visual"]["violence"] = min(ev_c.get("visual", {}).get("violence", 0.0), 0.18)

        if route_c_hitl:
            pred_c = "REQUIRES_HUMAN_REVIEW"
        else:
            res_c = prod_fusion.combine_assessment(ev_c)
            pred_c = res_c["classification"]
        candidates["Candidate_C"]["preds"].append(pred_c)

        # ---------------- Candidate D: Baseline + Both Improvements ----------------
        ev_d = copy.deepcopy(ev_base)
        route_d_hitl = False
        d_reasons = []

        # 1. Apply Alcohol Detector
        if res_alc["alcohol_detected"]:
            ev_d.setdefault("text_safety", {}).setdefault("categories", {})["alcohol"] = res_alc["score"]
            ev_d.setdefault("advertisement_risks", {})["explicit_content"] = max(ev_d.get("advertisement_risks", {}).get("explicit_content", 0.0), res_alc["score"])

        # 2. Apply Safeguarded Violence Decoupler
        if rec["media_type"] == "video":
            segments = ev_d.get("video", {}).get("sampled_segments", [])
            raw_mot = 25.0 if ev_d.get("video", {}).get("violence", 0.0) >= 0.20 else 5.0
            res_vd = violence_decoupler.evaluate_video_action(
                sampled_segments=segments,
                raw_motion_diff=raw_mot,
                text_context=aud_tx,
                visual_violence_flag=vis_violence_flag
            )
            ev_d["video"]["violence"] = res_vd["violence_score"]

            if res_vd["requires_human_review"]:
                route_d_hitl = True
                d_reasons.extend(res_vd["policy_reasons"])
            elif not res_vd["violence_detected"] and not vis_violence_flag:
                ev_d["visual"]["violence"] = min(ev_d.get("visual", {}).get("violence", 0.0), 0.18)

        if route_d_hitl:
            pred_d = "REQUIRES_HUMAN_REVIEW"
        else:
            res_d = prod_fusion.combine_assessment(ev_d)
            pred_d = res_d["classification"]
        candidates["Candidate_D"]["preds"].append(pred_d)

        # ---------------- Candidate D-HITL: Policy-First Fusion with Ambiguity Routing ----------------
        res_d_hitl = policy_fusion_hitl.combine_assessment(ev_d)
        if route_d_hitl:
            pred_d_hitl = "REQUIRES_HUMAN_REVIEW"
        else:
            pred_d_hitl = res_d_hitl["classification"]
        candidates["Candidate_D_HITL"]["preds"].append(pred_d_hitl)

        sample_logs.append({
            "sample_id": sid,
            "media_type": rec["media_type"],
            "true_label": gt_lbl,
            "pred_cand_a": pred_a,
            "pred_cand_b": pred_b,
            "pred_cand_c": pred_c,
            "pred_cand_d": pred_d,
            "pred_cand_d_hitl": pred_d_hitl,
            "is_cand_d_correct": bool(pred_d == gt_lbl),
            "is_withheld_review": bool(pred_d == "REQUIRES_HUMAN_REVIEW" or pred_d_hitl == "REQUIRES_HUMAN_REVIEW"),
            "alcohol_flagged": res_alc["alcohol_detected"],
            "violence_route_hitl": route_d_hitl
        })

    # =========================================================================
    # SUMMARY METRICS TABLE
    # =========================================================================
    summary_results = {}
    for c_key, c_info in candidates.items():
        summary_results[c_key] = {
            "name": c_info["name"],
            "metrics": calculate_safety_metrics(y_true, c_info["preds"])
        }

    print("\n" + "=" * 105)
    print("                     PHASE 6C CANDIDATE ARCHITECTURE COMPARISON TABLE                    ")
    print("=" * 105)
    header = f"{'Metric':<32} | {'Cand A (Base)':<13} | {'Cand B (+Alc)':<13} | {'Cand C (+Viol)':<13} | {'Cand D (+Both)':<13} | {'Cand D-HITL':<13}"
    print(header)
    print("-" * len(header))

    metrics_list = [
        ("accuracy", "Overall Accuracy"),
        ("accuracy_covered", "Accuracy (Covered Slice)"),
        ("macro_f1", "Macro-F1 Score"),
        ("pfar", "Prohibited False Acc (PFAR)"),
        ("prohibited_exposure_rate", "Prohibited Exposure Rate"),
        ("ugvr", "Underage Gating Viol (UGVR)"),
        ("frr", "False Rejection Rate (FRR)"),
        ("over_restriction_rate", "Over-Restriction Rate"),
        ("coverage", "Automatic Decision Coverage"),
        ("hitl_rate", "Human-Review Rate (HITL)")
    ]

    for k, display_name in metrics_list:
        row = f"{display_name:<32} | "
        for ckey in ["Candidate_A", "Candidate_B", "Candidate_C", "Candidate_D", "Candidate_D_HITL"]:
            val = summary_results[ckey]["metrics"].get(k, 0.0)
            if k in ["macro_f1"]:
                row += f"{val:>11.4f} | "
            else:
                row += f"{val*100:>10.2f}% | "
        print(row)

    print("-" * len(header))
    for c in CLASSES:
        row_rec = f"Recall: {c:<24} | "
        for ckey in ["Candidate_A", "Candidate_B", "Candidate_C", "Candidate_D", "Candidate_D_HITL"]:
            rec = summary_results[ckey]["metrics"]["recalls"].get(c, 0.0)
            row_rec += f"{rec*100:>10.2f}% | "
        print(row_rec)

    print("=" * 105)

    # Save summary json
    out_json = os.path.join(ROOT_DIR, "results", "real_pipeline_baseline", "phase6c_candidate_comparison.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(summary_results, f, indent=2)
    print(f"\nCandidate comparison saved to: {out_json}")

    # Save sample-level log
    out_csv = os.path.join(ROOT_DIR, "results", "real_pipeline_baseline", "phase6c_sample_predictions.csv")
    pd.DataFrame(sample_logs).to_csv(out_csv, index=False)
    print(f"Sample-level predictions saved to: {out_csv}")

    # =========================================================================
    # TASK 5: TARGETED REGRESSION AUDIT SUMMARY
    # =========================================================================
    print("\n" + "=" * 85)
    print("                    TASK 5: TARGETED REGRESSION SAMPLE AUDIT                    ")
    print("=" * 85)

    df_logs = pd.DataFrame(sample_logs).set_index("sample_id")

    # 1. Prohibited Samples (N=10)
    print("\n[Targeted Audit 1: All 10 Prohibited (UFA) Development Samples]")
    ufa_ids = [sid for sid in sample_ids if cached_data[sid]["true_label"] == "UNSAFE_FOR_ALL"]
    for sid in ufa_ids:
        r = df_logs.loc[sid]
        print(f"  - {sid:<20}: Base={r['pred_cand_a']:<15} -> Cand D={r['pred_cand_d']:<22} | Withheld={r['is_withheld_review']}")

    # 2. Previously False-Rejected Safe Videos
    print("\n[Targeted Audit 2: Previously False-Rejected Safe Commercial Videos]")
    false_rej_vids = ["SAFEAD_SFA_VID_006", "SAFEAD_SFA_VID_009", "SAFEAD_SFA_VID_011", "SAFEAD_SFA_VID_022", "SAFEAD_SFA_VID_024", "SAFEAD_S14P_VID_003"]
    for sid in false_rej_vids:
        if sid in df_logs.index:
            r = df_logs.loc[sid]
            print(f"  - {sid:<20}: Base={r['pred_cand_a']:<15} -> Cand D={r['pred_cand_d']:<22} | True={r['true_label']}")

    # 3. Previously Misclassified Alcohol Ads
    print("\n[Targeted Audit 3: Alcohol Advertisements (S18P)]")
    alcohol_test_ids = ["SAFEAD_S18P_IMG_002", "SAFEAD_S18P_IMG_006", "SAFEAD_S18P_IMG_031"]
    for sid in alcohol_test_ids:
        if sid in df_logs.index:
            r = df_logs.loc[sid]
            print(f"  - {sid:<20}: Base={r['pred_cand_a']:<15} -> Cand D={r['pred_cand_d']:<22} | True={r['true_label']}")

if __name__ == "__main__":
    main()
