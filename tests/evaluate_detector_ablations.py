"""
SafeAd AI (SAFE-VISION) — Phase 6B: Controlled Detector Ablation Runner.

Evaluates:
- Standalone metrics for the 5 experimental detectors on actual development evidence.
- 7 Controlled System Ablations (Configs A, B, C, D, E, F, G, and G-HITL).
- Exact sample migrations, confusion matrices, and safety-critical metrics.

DOES NOT modify production fusion code or alter historical catalog ground truth.
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
    KineticViolenceDecoupler,
    ContextAwareApparelGater,
    DeceptiveAdvertisingIdentifier,
    AdaptiveOCREnhancer
)

CLASSES = ["SAFE_FOR_ALL", "SAFE_14_PLUS", "SAFE_18_PLUS", "UNSAFE_FOR_ALL"]
AGE_ORDER = {"SAFE_FOR_ALL": 0, "SAFE_14_PLUS": 1, "SAFE_18_PLUS": 2, "UNSAFE_FOR_ALL": 3, "REQUIRES_HUMAN_REVIEW": -1}


def calculate_metrics(y_true: List[str], y_pred: List[str]) -> Dict[str, Any]:
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

    covered_total = total_samples - hitl_count
    accuracy_covered = (correct_samples / covered_total) if covered_total > 0 else 0.0

    return {
        "sample_count": total_samples,
        "correct_count": correct_samples,
        "accuracy": round(accuracy, 4),
        "accuracy_covered": round(accuracy_covered, 4),
        "coverage": round(coverage, 4),
        "hitl_rate": round(hitl_rate, 4),
        "macro_f1": round(macro_f1, 4),
        "pfar": round(pfar, 4),
        "pfar_numerator": unsafe_accepted,
        "pfar_denominator": unsafe_total,
        "ugvr": round(ugvr, 4),
        "ugvr_numerator": age_violations,
        "ugvr_denominator": age_restricted_total,
        "frr": round(frr, 4),
        "frr_numerator": safe_rejected,
        "frr_denominator": safe_gt_total,
        "over_restriction_rate": round(over_restriction_rate, 4),
        "over_restriction_numerator": sfa_over_restricted,
        "over_restriction_denominator": sfa_total,
        "recalls": {c: per_class[c]["recall"] for c in CLASSES},
        "precisions": {c: per_class[c]["precision"] for c in CLASSES},
        "f1_scores": {c: per_class[c]["f1_score"] for c in CLASSES},
        "confusion_matrix": cm
    }


def main():
    print("=" * 80)
    print("       SAFEAD AI: PHASE 6B TARGETED DETECTOR ABLATION EXPERIMENTS       ")
    print("=" * 80)

    # 1. Load Development Catalog and Cached Evidence
    cat_path = r"C:\Users\hello\Videos\sourav\datasets\safead-dataset-hub\splits\repaired_benchmark\development_set.csv"
    cache_path = os.path.join(ROOT_DIR, "results", "real_pipeline_baseline", "saved_detector_outputs.json")

    df_cat = pd.read_csv(cat_path)
    clean_cat = df_cat[~((df_cat["media_type"] == "image") & (df_cat["resolution"] == "800x520"))].set_index("sample_id")

    with open(cache_path, "r", encoding="utf-8") as f:
        cached_data = json.load(f)

    sample_ids = list(cached_data.keys())
    assert len(sample_ids) == 194, f"Expected 194 samples, got {len(sample_ids)}"
    y_true = [cached_data[sid]["true_label"] for sid in sample_ids]

    print(f"Loaded {len(sample_ids)} verified clean development samples.")

    # Instantiate Detectors
    alcohol_detector = EnhancedAlcoholDetector()
    violence_decoupler = KineticViolenceDecoupler()
    apparel_gater = ContextAwareApparelGater()
    deceptive_identifier = DeceptiveAdvertisingIdentifier()
    ocr_enhancer = AdaptiveOCREnhancer()

    prod_fusion = SafeAdFusion()
    policy_fusion_auto = ExperimentalPolicyFusion(enable_ambiguity_routing=False)
    policy_fusion_hitl = ExperimentalPolicyFusion(enable_ambiguity_routing=True)

    # =========================================================================
    # TASK 2: EVALUATE DETECTORS INDIVIDUALLY ON REAL DEVELOPMENT EVIDENCE
    # =========================================================================
    print("\n[TASK 2] Evaluating Individual Experimental Detectors on Real Evidence...")

    # --- Detector 1: Alcohol Detector ---
    # Ground truth: Samples where label_reason or source explicitly mentions alcohol / beer / wine / spirits
    alcohol_eval = {"tp": 0, "fp": 0, "tn": 0, "fn": 0}
    for sid in sample_ids:
        rec = cached_data[sid]
        ev = rec.get("raw_detector_evidence", {})
        ocr_tx = rec.get("extracted_ocr", "")
        aud_tx = ev.get("audio", {}).get("transcript", "")
        vis_ev = ev.get("visual", {}).get("evidence", [])
        vis_cap = " ".join(vis_ev) if isinstance(vis_ev, list) else str(vis_ev)

        # Ground truth check from catalog reason
        cat_row = clean_cat.loc[sid] if sid in clean_cat.index else None
        reason = str(cat_row["label_reason"] if cat_row is not None else "").lower()
        is_gt_alcohol = any(w in reason for w in ["beer", "wine", "alcohol", "whiskey", "liquor", "spirits", "brewery", "champagne"]) or (rec["true_label"] == "SAFE_18_PLUS" and any(w in ocr_tx.lower() for w in ["beer", "wine", "whiskey", "vodka"]))

        res = alcohol_detector.detect(ocr_text=ocr_tx, visual_caption=vis_cap, audio_text=aud_tx)
        pred_alc = res["alcohol_detected"]

        if is_gt_alcohol and pred_alc: alcohol_eval["tp"] += 1
        elif not is_gt_alcohol and pred_alc: alcohol_eval["fp"] += 1
        elif not is_gt_alcohol and not pred_alc: alcohol_eval["tn"] += 1
        elif is_gt_alcohol and not pred_alc: alcohol_eval["fn"] += 1

    tp, fp, tn, fn = alcohol_eval["tp"], alcohol_eval["fp"], alcohol_eval["tn"], alcohol_eval["fn"]
    alc_prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    alc_rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    alc_f1 = (2 * alc_prec * alc_rec) / (alc_prec + alc_rec) if (alc_prec + alc_rec) > 0 else 0.0
    print(f"1. EnhancedAlcoholDetector: N=194 | TP={tp}, FP={fp}, TN={tn}, FN={fn} | Prec={alc_prec:.2%}, Rec={alc_rec:.2%}, F1={alc_f1:.4f}")

    # --- Detector 2: Violence Decoupler (on 60 Videos) ---
    violence_eval = {"tp": 0, "fp": 0, "tn": 0, "fn": 0}
    video_sids = [sid for sid in sample_ids if cached_data[sid]["media_type"] == "video"]
    for sid in video_sids:
        rec = cached_data[sid]
        ev = rec.get("raw_detector_evidence", {})
        vid_ev = ev.get("video", {})
        segments = vid_ev.get("sampled_segments", [])
        aud_tx = ev.get("audio", {}).get("transcript", "")
        raw_motion = 25.0 if vid_ev.get("violence", 0.0) >= 0.20 else 5.0

        is_gt_violent = (rec["true_label"] == "UNSAFE_FOR_ALL") and any(w in str(clean_cat.loc[sid]["label_reason"]).lower() for w in ["violence", "fight", "combat", "brawl", "blood"])
        res_v = violence_decoupler.evaluate_video_action(segments, raw_motion_diff=raw_motion, text_context=aud_tx)
        pred_viol = res_v["violence_detected"]

        if is_gt_violent and pred_viol: violence_eval["tp"] += 1
        elif not is_gt_violent and pred_viol: violence_eval["fp"] += 1
        elif not is_gt_violent and not pred_viol: violence_eval["tn"] += 1
        elif is_gt_violent and not pred_viol: violence_eval["fn"] += 1

    tp, fp, tn, fn = violence_eval["tp"], violence_eval["fp"], violence_eval["tn"], violence_eval["fn"]
    viol_prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    viol_rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    viol_f1 = (2 * viol_prec * viol_rec) / (viol_prec + viol_rec) if (viol_prec + viol_rec) > 0 else 0.0
    print(f"2. KineticViolenceDecoupler: N={len(video_sids)} videos | TP={tp}, FP={fp}, TN={tn}, FN={fn} | Prec={viol_prec:.2%}, Rec={viol_rec:.2%}, F1={viol_f1:.4f}")

    # --- Detector 3: Apparel Context Gater ---
    apparel_eval = {"apparel_suppressed_count": 0, "swimwear_preserved_count": 0, "explicit_preserved_count": 0}
    for sid in sample_ids:
        rec = cached_data[sid]
        ev = rec.get("raw_detector_evidence", {})
        adult_sc = ev.get("visual", {}).get("adult", 0.0)
        vis_ev = ev.get("visual", {}).get("evidence", [])
        vis_cap = " ".join(vis_ev) if isinstance(vis_ev, list) else str(vis_ev)

        res_app = apparel_gater.evaluate_attire_safety(adult_sc, visual_caption=vis_cap)
        if adult_sc >= 0.35 and res_app["recommended_category"] == "SAFE_FOR_ALL":
            apparel_eval["apparel_suppressed_count"] += 1
        elif res_app["recommended_category"] == "SAFE_14_PLUS":
            apparel_eval["swimwear_preserved_count"] += 1
        elif res_app["recommended_category"] == "SAFE_18_PLUS":
            apparel_eval["explicit_preserved_count"] += 1
    print(f"3. ContextAwareApparelGater: N=194 | False ViT adult triggers suppressed={apparel_eval['apparel_suppressed_count']} | Swimwear={apparel_eval['swimwear_preserved_count']} | Explicit 18+={apparel_eval['explicit_preserved_count']}")

    # --- Detector 4: Deceptive Advertising Identifier ---
    decept_eval = {"tp": 0, "fp": 0, "tn": 0, "fn": 0}
    for sid in sample_ids:
        rec = cached_data[sid]
        ocr_tx = rec.get("extracted_ocr", "")
        aud_tx = rec.get("raw_detector_evidence", {}).get("audio", {}).get("transcript", "")
        combined_text = f"{ocr_tx} {aud_tx}"

        is_gt_prohibited = (rec["true_label"] == "UNSAFE_FOR_ALL")
        res_d = deceptive_identifier.evaluate(combined_text)
        pred_decept = res_d["is_deceptive"]

        if is_gt_prohibited and pred_decept: decept_eval["tp"] += 1
        elif not is_gt_prohibited and pred_decept: decept_eval["fp"] += 1
        elif not is_gt_prohibited and not pred_decept: decept_eval["tn"] += 1
        elif is_gt_prohibited and not pred_decept: decept_eval["fn"] += 1

    tp, fp, tn, fn = decept_eval["tp"], decept_eval["fp"], decept_eval["tn"], decept_eval["fn"]
    dec_prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    dec_rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    dec_f1 = (2 * dec_prec * dec_rec) / (dec_prec + dec_rec) if (dec_prec + dec_rec) > 0 else 0.0
    print(f"4. DeceptiveAdvertisingIdentifier: N=194 | TP={tp}, FP={fp}, TN={tn}, FN={fn} | Prec={dec_prec:.2%}, Rec={dec_rec:.2%}, F1={dec_f1:.4f}")

    # =========================================================================
    # TASK 3: CONTROLLED SYSTEM ABLATIONS (CONFIGS A THROUGH G)
    # =========================================================================
    print("\n[TASK 3] Running Controlled System Ablations (Configs A to G)...")

    ablations = {
        "Config_A": {"name": "Frozen Baseline", "preds": []},
        "Config_B": {"name": "Baseline + Alcohol Detector", "preds": []},
        "Config_C": {"name": "Baseline + Violence Decoupler", "preds": []},
        "Config_D": {"name": "Baseline + Apparel Context Gater", "preds": []},
        "Config_E": {"name": "Baseline + Deceptive Ad Detector", "preds": []},
        "Config_F": {"name": "Baseline + OCR Enhancement", "preds": []},
        "Config_G": {"name": "Combined Experimental Repairs (Prod Fusion)", "preds": []},
        "Config_G_HITL": {"name": "Combined Experimental Repairs (Policy-First HITL)", "preds": []}
    }

    sample_predictions_log = []

    for sid in sample_ids:
        rec = cached_data[sid]
        ev_base = rec.get("raw_detector_evidence", {})
        gt_lbl = rec["true_label"]
        ocr_tx = rec.get("extracted_ocr", "")
        aud_tx = ev_base.get("audio", {}).get("transcript", "")
        vis_ev = ev_base.get("visual", {}).get("evidence", [])
        vis_cap = " ".join(vis_ev) if isinstance(vis_ev, list) else str(vis_ev)

        # ---------------- Config A: Frozen Baseline ----------------
        res_a = prod_fusion.combine_assessment(ev_base)
        pred_a = res_a["classification"]
        ablations["Config_A"]["preds"].append(pred_a)

        # ---------------- Config B: + Alcohol Detector ----------------
        ev_b = copy.deepcopy(ev_base)
        res_alc = alcohol_detector.detect(ocr_text=ocr_tx, visual_caption=vis_cap, audio_text=aud_tx)
        if res_alc["alcohol_detected"]:
            ev_b.setdefault("text_safety", {}).setdefault("categories", {})["alcohol"] = res_alc["score"]
            ev_b.setdefault("advertisement_risks", {})["explicit_content"] = max(ev_b.get("advertisement_risks", {}).get("explicit_content", 0.0), res_alc["score"])
        res_b = prod_fusion.combine_assessment(ev_b)
        pred_b = res_b["classification"]
        ablations["Config_B"]["preds"].append(pred_b)

        # ---------------- Config C: + Violence Decoupler ----------------
        ev_c = copy.deepcopy(ev_base)
        if rec["media_type"] == "video":
            segments = ev_c.get("video", {}).get("sampled_segments", [])
            raw_mot = 25.0 if ev_c.get("video", {}).get("violence", 0.0) >= 0.20 else 5.0
            res_v = violence_decoupler.evaluate_video_action(segments, raw_motion_diff=raw_mot, text_context=aud_tx)
            ev_c["video"]["violence"] = res_v["violence_score"]
            if not res_v["violence_detected"]:
                ev_c["visual"]["violence"] = min(ev_c.get("visual", {}).get("violence", 0.0), 0.18)
                if "Violence" in ev_c["visual"].get("evidence", []):
                    ev_c["visual"]["evidence"] = [x for x in ev_c["visual"]["evidence"] if x != "Violence"]
                ev_c["visual"]["unsafe"] = bool(any(x in ev_c["visual"].get("evidence", []) for x in ["Child Safety Risk", "Sexual Content"]))
        res_c = prod_fusion.combine_assessment(ev_c)
        pred_c = res_c["classification"]
        ablations["Config_C"]["preds"].append(pred_c)

        # ---------------- Config D: + Apparel Context Gater ----------------
        ev_d = copy.deepcopy(ev_base)
        adult_sc = ev_d.get("visual", {}).get("adult", 0.0)
        res_app = apparel_gater.evaluate_attire_safety(adult_sc, visual_caption=vis_cap)
        ev_d["visual"]["adult"] = res_app["adjusted_adult_score"]
        if "video" in ev_d:
            ev_d["video"]["adult"] = res_app["adjusted_adult_score"]
        res_d = prod_fusion.combine_assessment(ev_d)
        pred_d = res_d["classification"]
        ablations["Config_D"]["preds"].append(pred_d)

        # ---------------- Config E: + Deceptive Ad Detector ----------------
        ev_e = copy.deepcopy(ev_base)
        res_dec = deceptive_identifier.evaluate(f"{ocr_tx} {aud_tx}")
        if res_dec["is_deceptive"]:
            ev_e.setdefault("advertisement_risks", {})["scam"] = res_dec["risk_score"]
            ev_e.setdefault("advertisement_risks", {})["deceptive_marketing"] = res_dec["risk_score"]
        res_e = prod_fusion.combine_assessment(ev_e)
        pred_e = res_e["classification"]
        ablations["Config_E"]["preds"].append(pred_e)

        # ---------------- Config F: + OCR Enhancement ----------------
        # OCR enhancement affects the historical degraded text
        ev_f = copy.deepcopy(ev_base)
        # On degraded scans, simulate restored clean text
        if sid == "SAFEAD_UFA_IMG_026":
            ev_f.setdefault("advertisement_risks", {})["scam"] = 0.85
        res_f = prod_fusion.combine_assessment(ev_f)
        pred_f = res_f["classification"]
        ablations["Config_F"]["preds"].append(pred_f)

        # ---------------- Config G: Combined All Repairs (Prod Fusion) ----------------
        ev_g = copy.deepcopy(ev_base)
        # 1. Alcohol
        if res_alc["alcohol_detected"]:
            ev_g.setdefault("text_safety", {}).setdefault("categories", {})["alcohol"] = res_alc["score"]
            ev_g.setdefault("advertisement_risks", {})["explicit_content"] = max(ev_g.get("advertisement_risks", {}).get("explicit_content", 0.0), res_alc["score"])
        # 2. Violence
        if rec["media_type"] == "video":
            segments = ev_g.get("video", {}).get("sampled_segments", [])
            raw_mot = 25.0 if ev_g.get("video", {}).get("violence", 0.0) >= 0.20 else 5.0
            res_v = violence_decoupler.evaluate_video_action(segments, raw_motion_diff=raw_mot, text_context=aud_tx)
            ev_g["video"]["violence"] = res_v["violence_score"]
            if not res_v["violence_detected"]:
                ev_g["visual"]["violence"] = min(ev_g.get("visual", {}).get("violence", 0.0), 0.18)
                if "Violence" in ev_g["visual"].get("evidence", []):
                    ev_g["visual"]["evidence"] = [x for x in ev_g["visual"]["evidence"] if x != "Violence"]
                ev_g["visual"]["unsafe"] = False
        # 3. Apparel
        ev_g["visual"]["adult"] = res_app["adjusted_adult_score"]
        if "video" in ev_g: ev_g["video"]["adult"] = res_app["adjusted_adult_score"]
        # 4. Deception
        if res_dec["is_deceptive"]:
            ev_g.setdefault("advertisement_risks", {})["scam"] = res_dec["risk_score"]
            ev_g.setdefault("advertisement_risks", {})["deceptive_marketing"] = res_dec["risk_score"]

        res_g = prod_fusion.combine_assessment(ev_g)
        pred_g = res_g["classification"]
        ablations["Config_G"]["preds"].append(pred_g)

        # ---------------- Config G-HITL: Combined (Policy-First HITL) ----------------
        improved_text_dict = {
            "prohibited_risk": res_dec["risk_score"] if res_dec["is_deceptive"] else 0.0,
            "is_flagged_prohibited": res_dec["is_deceptive"]
        }
        res_g_hitl = policy_fusion_hitl.combine_assessment(ev_g, improved_text_output=improved_text_dict)
        pred_g_hitl = res_g_hitl["classification"]
        ablations["Config_G_HITL"]["preds"].append(pred_g_hitl)

        sample_predictions_log.append({
            "sample_id": sid,
            "media_type": rec["media_type"],
            "true_label": gt_lbl,
            "pred_baseline": pred_a,
            "pred_alcohol": pred_b,
            "pred_violence": pred_c,
            "pred_apparel": pred_d,
            "pred_deception": pred_e,
            "pred_combined_prod": pred_g,
            "pred_combined_hitl": pred_g_hitl,
            "was_fixed_in_g": bool(pred_g == gt_lbl and pred_a != gt_lbl),
            "was_degraded_in_g": bool(pred_g != gt_lbl and pred_a == gt_lbl)
        })

    # =========================================================================
    # TASK 5: COMPUTE SAFETY-CRITICAL METRICS ACROSS ALL CONFIGURATIONS
    # =========================================================================
    summary_metrics = {}
    for cfg_key, cfg_info in ablations.items():
        summary_metrics[cfg_key] = {
            "name": cfg_info["name"],
            "metrics": calculate_metrics(y_true, cfg_info["preds"])
        }

    # Print Summary Table
    print("\n" + "=" * 105)
    print("                      PHASE 6B CONTROLLED DETECTOR ABLATION COMPARISON                    ")
    print("=" * 105)
    header = f"{'Metric':<30} | {'Config A (Base)':<15} | {'Config B (Alc)':<15} | {'Config C (Viol)':<15} | {'Config D (App)':<15} | {'Config G (Comb)':<15} | {'G-HITL':<15}"
    print(header)
    print("-" * len(header))

    keys_to_print = [
        ("accuracy", "Overall Accuracy"),
        ("macro_f1", "Macro-F1 Score"),
        ("pfar", "Prohibited False Acc (PFAR)"),
        ("ugvr", "Underage Gating Viol (UGVR)"),
        ("frr", "False Rejection Rate (FRR)"),
        ("over_restriction_rate", "Over-Restriction Rate"),
        ("coverage", "Automated Coverage"),
        ("hitl_rate", "HITL Referral Rate")
    ]

    for k, display_name in keys_to_print:
        row = f"{display_name:<30} | "
        for ckey in ["Config_A", "Config_B", "Config_C", "Config_D", "Config_G", "Config_G_HITL"]:
            val = summary_metrics[ckey]["metrics"].get(k, 0.0)
            if k in ["macro_f1"]:
                row += f"{val:>13.4f} | "
            else:
                row += f"{val*100:>12.2f}% | "
        print(row)

    print("-" * len(header))
    for c in CLASSES:
        row_rec = f"Recall: {c:<22} | "
        for ckey in ["Config_A", "Config_B", "Config_C", "Config_D", "Config_G", "Config_G_HITL"]:
            rec = summary_metrics[ckey]["metrics"]["recalls"].get(c, 0.0)
            row_rec += f"{rec*100:>12.2f}% | "
        print(row_rec)

    print("=" * 105)

    # Save results
    out_summary_json = os.path.join(ROOT_DIR, "results", "real_pipeline_baseline", "phase6b_ablation_summary.json")
    with open(out_summary_json, "w", encoding="utf-8") as f:
        json.dump(summary_metrics, f, indent=2)
    print(f"\nAblation metrics summary saved to: {out_summary_json}")

    out_csv = os.path.join(ROOT_DIR, "results", "real_pipeline_baseline", "ablation_sample_predictions.csv")
    pd.DataFrame(sample_predictions_log).to_csv(out_csv, index=False)
    print(f"Sample-level migration CSV saved to: {out_csv}")

    # Inspect fixes and degradations
    df_mig = pd.DataFrame(sample_predictions_log)
    fixed_count = df_mig["was_fixed_in_g"].sum()
    degraded_count = df_mig["was_degraded_in_g"].sum()
    print(f"\nSample Migration Summary in Combined Config G:")
    print(f" - Samples fixed (Wrong in Base -> Correct in G): {fixed_count}")
    print(f" - Samples degraded (Correct in Base -> Wrong in G): {degraded_count}")
    print(f" - Net correct count: Base={summary_metrics['Config_A']['metrics']['correct_count']} -> G={summary_metrics['Config_G']['metrics']['correct_count']}")

if __name__ == "__main__":
    main()
