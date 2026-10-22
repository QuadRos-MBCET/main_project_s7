#!/usr/bin/env python3
"""Isolated Experiment for Alternative Text Safety & Deceptive Ad Detectors.

Compares:
1. Baseline (Current Keyword Fallback in SafeAdTextSafetyDetector & AdRiskAnalyzer)
2. Candidate 1: unitary/toxic-bert (Toxicity / Abuse Classifier)
3. Candidate 2: MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli (Zero-Shot Deceptive / Scam Classifier)

Evaluates on a development subset of text samples representing:
- Prohibited Scams & Deceptive Offers (un-gated real ads)
- Permissible Adult / Regulated Ads (beer, dating)
- Benign Consumer Ads (electronics, food, household)
"""

import os
import sys
import time
import json
from typing import Dict, Any, List

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
JB_DIR = os.path.join(ROOT_DIR, "joseph_safead_core")
B2JB_DIR = os.path.join(ROOT_DIR, "joseph_safead_core", "backend2jb")
for p in [ROOT_DIR, JB_DIR, B2JB_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

from models.text_safety import SafeAdTextSafetyDetector
from models.ad_risk_analyzer import AdRiskAnalyzer

# Test corpus taken directly from development dataset text and realistic ad copy
DEV_TEXT_CORPUS = [
    {
        "id": "TEXT_DEV_UFA_01",
        "category": "UNSAFE_FOR_ALL",
        "subcategory": "Financial Scam (No keyword match)",
        "text": "Exclusive pre-market allocation available now. Deposit 250 USD and our proprietary automated quantum arbitrage algorithm will generate 4,800 USD within 48 hours directly into your banking wallet. Act before the window closes.",
        "expected_flag": "SCAM / DECEPTIVE"
    },
    {
        "id": "TEXT_DEV_UFA_02",
        "category": "UNSAFE_FOR_ALL",
        "subcategory": "Phishing / Prize Fraud",
        "text": "Notice of Unclaimed Delivery: Package tracking #US94821 is held at regional sorting facility. Pay 1.95 USD redelivery verification fee immediately or parcel will be returned to sender.",
        "expected_flag": "SCAM / DECEPTIVE"
    },
    {
        "id": "TEXT_DEV_UFA_03",
        "category": "UNSAFE_FOR_ALL",
        "subcategory": "Historical Patent Medicine (Clark Stanley Snake Oil)",
        "text": "Clark Stanley's Snake Oil Liniment cures rheumatism, neuralgia, sciatica, lame back, contracted muscles, frost bites, chill blains, bruises, sore throat, and bites of animals. Good for man and beast.",
        "expected_flag": "PROHIBITED MEDICAL CURE"
    },
    {
        "id": "TEXT_DEV_S18P_01",
        "category": "SAFE_18_PLUS",
        "subcategory": "Regulated Alcohol Print Ad (Schlitz Beer)",
        "text": "Schlitz - The Beer That Made Milwaukee Famous. Enjoy the pure, clean taste of master-brewed draught beer. Please drink responsibly. Must be 21 or older to purchase.",
        "expected_flag": "ALCOHOL / 18+"
    },
    {
        "id": "TEXT_DEV_S14P_01",
        "category": "SAFE_14_PLUS",
        "subcategory": "Teen Action Video Game Ad",
        "text": "Unleash extreme combat tactics in Shadow Warzone 4. Battle through intense urban operations with advanced weapon customisation. Rated Teen for Violence and Blood.",
        "expected_flag": "TEEN ACTION / 14+"
    },
    {
        "id": "TEXT_DEV_SFA_01",
        "category": "SAFE_FOR_ALL",
        "subcategory": "Everyday Household Appliance",
        "text": "Start your morning fresh with the AeroPress Compact Coffee Maker. Rapid immersion brewing produces rich, smooth coffee in under 60 seconds with zero bitterness.",
        "expected_flag": "SAFE_FOR_ALL"
    }
]

def run_baseline_pipeline(text: str) -> Dict[str, Any]:
    detector = SafeAdTextSafetyDetector()
    analyzer = AdRiskAnalyzer()
    
    # Run keyword-based text safety
    ts_res = detector.predict_text(text)
    ad_res = analyzer.analyze_ad_risks(ocr_text=text, text_safety_output=ts_res)
    
    return {
        "text_safety": ts_res,
        "ad_risk": ad_res,
        "scam_score": ad_res.get("scam", 0.0),
        "deceptive_score": ad_res.get("deceptive_marketing", 0.0),
        "alcohol_score": ts_res.get("alcohol", 0.0),
        "violence_score": ts_res.get("violent", 0.0),
        "detected_categories": ts_res.get("detected_categories", []) + ad_res.get("detected_risks", [])
    }

def main():
    print("=" * 80)
    print(" SAFE-VISION: ISOLATED TEXT SAFETY DETECTOR EXPERIMENT (DEV ONLY) ")
    print("=" * 80)

    # 1. Baseline Evaluation
    print("\n--- 1. Evaluating Current Baseline (Keyword Fallback) ---")
    baseline_results = []
    for item in DEV_TEXT_CORPUS:
        t0 = time.time()
        res = run_baseline_pipeline(item["text"])
        lat = round(time.time() - t0, 4)
        print(f"[{item['id']}] Cat: {item['category']} | Expected: {item['expected_flag']}")
        print(f"   Detected: {res['detected_categories']} | Scam: {res['scam_score']} | Alcohol: {res['alcohol_score']} ({lat}s)")
        baseline_results.append({
            "id": item["id"],
            "expected": item["expected_flag"],
            "detected": res["detected_categories"],
            "scam_score": res["scam_score"],
            "deceptive_score": res["deceptive_score"],
            "alcohol_score": res["alcohol_score"]
        })

    # 2. Check Candidate 1: unitary/toxic-bert availability & performance
    print("\n--- 2. Evaluating Candidate 1: unitary/toxic-bert ---")
    toxic_bert_status = "NOT_INSTALLED"
    toxic_results = []
    try:
        from transformers import pipeline
        t0 = time.time()
        toxic_pipe = pipeline("text-classification", model="unitary/toxic-bert", return_all_scores=True)
        print(f"   [LOAD SUCCESS] Loaded unitary/toxic-bert in {time.time() - t0:.2f}s")
        toxic_bert_status = "ACTIVE"
        for item in DEV_TEXT_CORPUS:
            scores = toxic_pipe(item["text"][:512])[0]
            # Find max toxic label
            max_score = max(scores, key=lambda x: x["score"])
            print(f"[{item['id']}] -> Top Label: {max_score['label']} ({max_score['score']:.4f})")
            toxic_results.append({
                "id": item["id"],
                "top_label": max_score["label"],
                "score": round(max_score["score"], 4)
            })
    except Exception as e:
        print(f"   [NOTICE] toxic-bert evaluation status: {e}")
        toxic_bert_status = f"FAILED: {e}"

    # Summary
    output = {
        "experiment_name": "isolated_text_safety_comparison",
        "tested_samples_count": len(DEV_TEXT_CORPUS),
        "baseline_summary": baseline_results,
        "toxic_bert_status": toxic_bert_status,
        "toxic_bert_results": toxic_results
    }
    
    out_path = os.path.join(ROOT_DIR, "results", "real_pipeline_baseline", "text_safety_experiment_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    print(f"\nExperiment results saved to: {out_path}")

if __name__ == "__main__":
    main()
