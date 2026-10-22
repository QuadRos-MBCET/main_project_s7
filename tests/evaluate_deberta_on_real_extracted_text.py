#!/usr/bin/env python3
"""
SafeAd AI (SAFE-VISION) — Phase 4B Task 5:
Evaluation of DeBERTa-v3-base Zero-Shot NLI on Real Extracted Advertisement Text.

Evaluates DeBERTa on:
1. Real OCR extracted text from historical print ads and images.
2. Real Whisper transcribed audio from TV/broadcast commercials.
3. Edge cases: Empty text, noisy OCR fragments, multilingual audio.
4. Factual truthfulness ambiguity analysis.

Compares against the current keyword detector baseline.
"""

import os
import sys
import time
import json
from typing import Dict, Any, List
import pandas as pd
import numpy as np

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
JB_DIR = os.path.join(ROOT_DIR, "joseph_safead_core")
B2JB_DIR = os.path.join(ROOT_DIR, "joseph_safead_core", "backend2jb")
for p in [ROOT_DIR, JB_DIR, B2JB_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

from models.text_safety import SafeAdTextSafetyDetector
from models.ad_risk_analyzer import AdRiskAnalyzer
from tests.experiment_deberta_text_safety import IsolatedDebertaClassifier

# Benchmark corpus compiled from actual extracted OCR / Whisper from Dev Ads + Edge Cases
REAL_EXTRACTED_TEXT_BENCHMARK = [
    # --- Real Prohibited Ad Texts ---
    {
        "id": "REAL_UFA_01",
        "source": "SAFEAD_UFA_IMG_021 (OCR)",
        "text": "21.43 X legitmarketingacademy com EXPERT Free Video Training reveals how complete beginners make $2,500 daily on autopilot using automated funnel loop.",
        "gt_prohibited": True,
        "type": "scam_marketing"
    },
    {
        "id": "REAL_UFA_02",
        "source": "SAFEAD_UFA_IMG_026 (OCR)",
        "text": "Royal Trust Beneficiary Notice: Unclaimed estate disbursement of $14,200,000 USD awaiting immediate identity clearance. Pay administrative filing charge to release legal deed.",
        "gt_prohibited": True,
        "type": "advance_fee_fraud"
    },
    {
        "id": "REAL_UFA_03",
        "source": "SAFEAD_UFA_IMG_054 (Historical Patent Medicine)",
        "text": "Clark Stanley's Snake Oil Liniment cures rheumatism, neuralgia, sciatica, lame back, contracted muscles, frost bites, chill blains, bruises, sore throat.",
        "gt_prohibited": True,
        "type": "quack_cure"
    },
    {
        "id": "REAL_UFA_04",
        "source": "SAFEAD_UFA_VID_005 (Whisper Audio)",
        "text": "Welcome to the official Ethereum doubling giveaway. Send any amount between 1 and 50 ETH to the contract on screen and receive back double immediately.",
        "gt_prohibited": True,
        "type": "crypto_scam"
    },

    # --- Real Legitimate Ad Texts ---
    {
        "id": "REAL_SFA_01",
        "source": "SAFEAD_SFA_VID_001 (Whisper Audio)",
        "text": "Now class, Mr. Tiger will show us how Kellogg's sugar-frosted flakes give you the secret vitality to be your best every morning.",
        "gt_prohibited": False,
        "type": "cereal_commercial"
    },
    {
        "id": "REAL_SFA_02",
        "source": "SAFEAD_SFA_VID_008 (Whisper Audio)",
        "text": "I say it's crackle the crispy sound you gotta have crackle on Kellogg's Rice Krispies. Snap, crackle and pop every breakfast.",
        "gt_prohibited": False,
        "type": "cereal_commercial"
    },
    {
        "id": "REAL_S14P_01",
        "source": "SAFEAD_S14P_VID_001 (Whisper Audio)",
        "text": "Groucho sent me to see the new De Soto Plymouth. Sleek aerodynamics, push-button transmission, and power-steering comfort for the open highway.",
        "gt_prohibited": False,
        "type": "automotive_commercial"
    },
    {
        "id": "REAL_S14P_02",
        "source": "SAFEAD_S14P_VID_010 (Whisper Audio)",
        "text": "The man, Carroll Shelby, engineer, racetrack, the car, the Shelby GT. Pure American muscle designed for the checkered flag.",
        "gt_prohibited": False,
        "type": "sports_automotive"
    },
    {
        "id": "REAL_S18P_01",
        "source": "SAFEAD_S18P_VID_001 (Whisper Audio + OCR)",
        "text": "Miller High Life Draft Beer. When it's time to relax with friends, choose the Champagne of Beers. Master-brewed draught beer since 1855.",
        "gt_prohibited": False,
        "type": "beer_commercial"
    },
    {
        "id": "REAL_S18P_02",
        "source": "SAFEAD_S18P_IMG_001 (Historical Beer Print Ad)",
        "text": "Bulimba Beer Brisbane 1900. Pure malt and hops brewed under golden sunshine. A refreshing tonic for colonial warmth.",
        "gt_prohibited": False,
        "type": "beer_print_ad"
    },

    # --- Edge Cases: Empty, Noisy OCR, and Multilingual Text ---
    {
        "id": "EDGE_EMPTY_01",
        "source": "Image with no text",
        "text": "",
        "gt_prohibited": False,
        "type": "empty_input"
    },
    {
        "id": "EDGE_NOISY_OCR_01",
        "source": "Low-confidence OCR artifact",
        "text": "Va 101 WR Wa VR QuFEC 24043",
        "gt_prohibited": False,
        "type": "noisy_ocr"
    },
    {
        "id": "EDGE_MULTILINGUAL_01",
        "source": "SAFEAD_UFA_VID_002 (Portuguese combat audio)",
        "text": "Ah ali eu não maneira pra replaced. Olha pra ali pra ver combate ao vivo com armas pesadas e tiroteio.",
        "gt_prohibited": True,
        "type": "multilingual_violence"
    },

    # --- Factual Truthfulness Ambiguity Test ---
    {
        "id": "AMBIGUITY_01",
        "source": "Puffery / Unverifiable Performance Claim",
        "text": "Our revolutionary ceramic ionic air purifier eliminates 99.99% of all airborne particles, dust mites, and bacteria within 30 minutes of operation. Lab certified.",
        "gt_prohibited": False,  # Benign puffery unless proven fraudulent
        "type": "unverifiable_claim"
    }
]


def run_text_benchmark():
    print("=" * 80)
    print("   PHASE 4B: DEBERTA VS KEYWORD EVALUATION ON REAL EXTRACTED AD TEXT   ")
    print("=" * 80)
    print(f"Total Evaluated Test Cases: {len(REAL_EXTRACTED_TEXT_BENCHMARK)}")
    print("-" * 80)

    # Initialize models
    detector = SafeAdTextSafetyDetector()
    analyzer = AdRiskAnalyzer()
    deberta = IsolatedDebertaClassifier().load()

    results = []

    for item in REAL_EXTRACTED_TEXT_BENCHMARK:
        tid = item["id"]
        text = item["text"]
        gt_prohib = item["gt_prohibited"]
        src = item["source"]

        # 1. Baseline Evaluation
        t0 = time.time()
        if not text.strip():
            base_prohib = False
            base_scam = 0.0
            base_lat = 0.0001
        else:
            ts_res = detector.predict_text(text)
            ad_res = analyzer.analyze_ad_risks(ocr_text=text, text_safety_output=ts_res)
            base_scam = max(ad_res.get("scam", 0.0), ad_res.get("deceptive_marketing", 0.0))
            base_prohib = bool(base_scam >= 0.50)
            base_lat = round(time.time() - t0, 4)

        # 2. DeBERTa Evaluation
        t0 = time.time()
        if not text.strip():
            deb_res = {
                "prohibited_risk": 0.0,
                "legit_score": 1.0,
                "is_flagged_prohibited": False,
                "latency": 0.0001
            }
        else:
            deb_res = deberta.predict(text)
        deb_prohib = deb_res["is_flagged_prohibited"]

        results.append({
            "id": tid,
            "source": src,
            "type": item["type"],
            "gt_prohibited": gt_prohib,
            "text_snippet": text[:60] if text else "<EMPTY>",
            "baseline_flagged": base_prohib,
            "baseline_score": base_scam,
            "baseline_latency_ms": round(base_lat * 1000, 1),
            "deberta_flagged": deb_prohib,
            "deberta_prohibited_score": deb_res["prohibited_risk"],
            "deberta_legit_score": deb_res["legit_score"],
            "deberta_latency_ms": round(deb_res["latency"] * 1000, 1)
        })

        print(f"[{tid:<20}] GT: {'PROHIBITED' if gt_prohib else 'SAFE':<10} | "
              f"Base: {'FLAGGED' if base_prohib else 'CLEARED':<7} | "
              f"DeBERTa: {'FLAGGED' if deb_prohib else 'CLEARED':<7} (p={deb_res['prohibited_risk']:.2f}, l={deb_res['legit_score']:.2f})")

    df_res = pd.DataFrame(results)

    # Standard metrics on non-empty samples
    valid_df = df_res[df_res["type"] != "empty_input"]
    y_true = valid_df["gt_prohibited"].tolist()

    def compute_metrics(preds):
        tp = sum(1 for t, p in zip(y_true, preds) if t and p)
        fp = sum(1 for t, p in zip(y_true, preds) if not t and p)
        fn = sum(1 for t, p in zip(y_true, preds) if t and not p)
        tn = sum(1 for t, p in zip(y_true, preds) if not t and not p)

        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        fnr = fn / (tp + fn) if (tp + fn) > 0 else 0.0

        return {
            "TP": tp, "FP": fp, "FN": fn, "TN": tn,
            "Precision": round(prec, 4),
            "Recall": round(rec, 4),
            "F1": round(f1, 4),
            "FPR": round(fpr, 4),
            "FNR": round(fnr, 4)
        }

    m_base = compute_metrics(valid_df["baseline_flagged"].tolist())
    m_deb = compute_metrics(valid_df["deberta_flagged"].tolist())

    print("\n" + "=" * 80)
    print("        DEBERTA VS KEYWORD BASELINE ON REAL AD TEXT (METRICS SUMMARY)          ")
    print("=" * 80)
    print(f"{'Metric':<30} | {'Baseline (Keyword Rules)':<24} | {'DeBERTa-v3-base NLI':<20}")
    print("-" * 30 + "-+-" + "-" * 24 + "-+-" + "-" * 20)
    print(f"{'Precision':<30} | {m_base['Precision']*100:>22.2f}% | {m_deb['Precision']*100:>18.2f}%")
    print(f"{'Recall':<30} | {m_base['Recall']*100:>22.2f}% | {m_deb['Recall']*100:>18.2f}%")
    print(f"{'F1-Score':<30} | {m_base['F1']:>24.4f} | {m_deb['F1']:>20.4f}")
    print(f"{'False Negative Rate (Misses)':<30} | {m_base['FNR']*100:>22.2f}% | {m_deb['FNR']*100:>18.2f}%")
    print(f"{'False Positive Rate (Alarms)':<30} | {m_base['FPR']*100:>22.2f}% | {m_deb['FPR']*100:>18.2f}%")
    print(f"{'True Positives (TP)':<30} | {m_base['TP']:>24} | {m_deb['TP']:>20}")
    print(f"{'False Positives (FP)':<30} | {m_base['FP']:>24} | {m_deb['FP']:>20}")
    print(f"{'False Negatives (FN)':<30} | {m_base['FN']:>24} | {m_deb['FN']:>20}")
    print(f"{'Average Latency per Text':<30} | {df_res['baseline_latency_ms'].mean():>21.1f} ms | {df_res['deberta_latency_ms'].mean():>17.1f} ms")
    print("=" * 80)

    # Save artifact
    out_path = os.path.join(ROOT_DIR, "results", "real_pipeline_baseline", "real_ad_text_deberta_report.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"summary_metrics": {"baseline": m_base, "deberta": m_deb}, "samples": results}, f, indent=2)
    print(f"Full report saved to: {out_path}")

    return m_deb

if __name__ == "__main__":
    run_text_benchmark()
