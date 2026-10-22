"""
SafeAd AI (SAFE-VISION) — Phase 5B Task 4: Ad Text Classifier Generalization Benchmark.

Tests the ExperimentalDomainAdTextClassifier on 30 diverse ad text samples:
- 10 Prohibited Scams, Phishing, Quackery, and Fraud (including unseen paraphrased copy).
- 12 Legitimate Commercial Ads (banking, retail, OTC pharma, automotive, food).
- 8 Complex Edge Cases (unverifiable puffery, noisy OCR, multilingual Spanish/Portuguese, textless).

Verifies whether the classifier overfits to specific keywords or generalizes to varied deceptive advertising topologies.
"""

import sys
import os
import time
import json
import numpy as np

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
B2JB_DIR = os.path.join(ROOT_DIR, "joseph_safead_core", "backend2jb")
for p in [ROOT_DIR, B2JB_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

from tests.experimental_ad_text_classifier import ExperimentalDomainAdTextClassifier

GENERALIZATION_TEXT_CORPUS = [
    # --- Group 1: Financial & Yield Scams (Prohibited) ---
    {
        "id": "UNSEEN_SCAM_01",
        "category": "financial_scam",
        "text": "Copy my proprietary algorithmic trading bot and secure $1,500 daily on autopilot with zero risk.",
        "gt_prohibited": True
    },
    {
        "id": "UNSEEN_SCAM_02",
        "category": "financial_scam",
        "text": "Secret wealth formula: Turn 500 dollars into 15,000 in 30 days guaranteed profit. Passive income system.",
        "gt_prohibited": True
    },
    {
        "id": "UNSEEN_CRYPTO_01",
        "category": "crypto_scam",
        "text": "Official Elon Musk Bitcoin doubling giveaway! Send 0.1 BTC to receive back 0.2 BTC instantly.",
        "gt_prohibited": True
    },
    {
        "id": "UNSEEN_PHISH_01",
        "category": "phishing_fraud",
        "text": "Federal Grant Disbursement Notice: Unclaimed government funds of $25,000 ready for release. Pay administrative fee.",
        "gt_prohibited": True
    },
    {
        "id": "UNSEEN_PRIZE_01",
        "category": "prize_scam",
        "text": "Congratulations winner! You have won a $1,000 Amazon gift card. Claim your reward now.",
        "gt_prohibited": True
    },

    # --- Group 2: Deceptive Health & Quack Cures (Prohibited) ---
    {
        "id": "UNSEEN_QUACK_01",
        "category": "quack_cure",
        "text": "Miracle Himalayan root cures diabetes, arthritis, and chronic pain in 48 hours without prescription drugs.",
        "gt_prohibited": True
    },
    {
        "id": "UNSEEN_QUACK_02",
        "category": "quack_cure",
        "text": "Electric belt restores youthful vitality and cures paralysis. 100% guaranteed medical miracle.",
        "gt_prohibited": True
    },
    {
        "id": "UNSEEN_QUACK_03",
        "category": "quack_cure",
        "text": "Authentic snake oil liniment instantly banishes backache and rheumatism.",
        "gt_prohibited": True
    },

    # --- Group 3: Multilingual Violence & Illegal Contraband (Prohibited) ---
    {
        "id": "UNSEEN_MULTI_01",
        "category": "multilingual_violence",
        "text": "Transmissão ao vivo de tiroteio com armas pesadas e combate mortal na favela.",
        "gt_prohibited": True
    },
    {
        "id": "UNSEEN_MULTI_02",
        "category": "multilingual_violence",
        "text": "Brutal combat fight scene with knife attack and blood on full display.",
        "gt_prohibited": True
    },

    # --- Group 4: Legitimate Financial Promotions (Safe / Permitted) ---
    {
        "id": "LEGIT_FINANCE_01",
        "category": "legitimate_banking",
        "text": "Chase Freedom Unlimited: Earn 1.5% cash back on all everyday purchases with no annual fee. Member FDIC.",
        "gt_prohibited": False
    },
    {
        "id": "LEGIT_FINANCE_02",
        "category": "legitimate_banking",
        "text": "Open a High Yield Savings Account with Vanguard. 4.60% APY variable rate. Capital at risk.",
        "gt_prohibited": False
    },

    # --- Group 5: Legitimate Medical & OTC Pharma (Safe / Permitted) ---
    {
        "id": "LEGIT_PHARMA_01",
        "category": "legitimate_health",
        "text": "Tylenol Extra Strength: Temporarily relieves minor aches, muscular pain, and fever. Use only as directed.",
        "gt_prohibited": False
    },
    {
        "id": "LEGIT_PHARMA_02",
        "category": "legitimate_health",
        "text": "Colgate Total Toothpaste: Fights plaque bacteria on teeth, tongue, cheeks, and gums for 12 hours.",
        "gt_prohibited": False
    },

    # --- Group 6: Legitimate FMCG, Retail & Food Advertising (Safe / Permitted) ---
    {
        "id": "LEGIT_RETAIL_01",
        "category": "legitimate_fmcg",
        "text": "Kellogg's Frosted Flakes: They're Gr-r-reat! Fuel your morning with wholesome energy.",
        "gt_prohibited": False
    },
    {
        "id": "LEGIT_RETAIL_02",
        "category": "legitimate_fmcg",
        "text": "Coca-Cola Zero Sugar: Real Coca-Cola taste with zero calories. Best served chilled.",
        "gt_prohibited": False
    },
    {
        "id": "LEGIT_RETAIL_03",
        "category": "legitimate_retail",
        "text": "Nike Air Zoom Pegasus: Engineered for daily runners with responsive foam cushioning and breathable mesh.",
        "gt_prohibited": False
    },
    {
        "id": "LEGIT_RETAIL_04",
        "category": "legitimate_automotive",
        "text": "The all-new Ford F-150: Built tough with high-strength military-grade aluminum-alloy body.",
        "gt_prohibited": False
    },
    {
        "id": "LEGIT_RETAIL_05",
        "category": "legitimate_travel",
        "text": "Fly Emirates to Dubai and beyond. Experience award-winning inflight entertainment and gourmet dining.",
        "gt_prohibited": False
    },
    {
        "id": "LEGIT_RETAIL_06",
        "category": "legitimate_dining",
        "text": "Starbucks Rewards: Buy one iced caramel macchiato and earn 50 bonus stars this Friday.",
        "gt_prohibited": False
    },
    {
        "id": "LEGIT_ALCOHOL_01",
        "category": "regulated_alcohol_18p",
        "text": "Guinness Extra Stout: Distinctively black with a rich creamy head. Brewed with roasted barley since 1759.",
        "gt_prohibited": False  # Regulated adult content, but NOT prohibited
    },
    {
        "id": "LEGIT_ALCOHOL_02",
        "category": "regulated_alcohol_18p",
        "text": "Heineken 0.0: Great taste, zero alcohol. Enjoy Heineken anytime, anywhere.",
        "gt_prohibited": False
    },

    # --- Group 7: Edge Cases, Ambiguity, OCR Noise & Multilingual Safe ---
    {
        "id": "EDGE_PUFFERY_01",
        "category": "commercial_puffery",
        "text": "Red Bull gives you wings! Vitalizes body and mind for athletes and gamers.",
        "gt_prohibited": False
    },
    {
        "id": "EDGE_PUFFERY_02",
        "category": "unverifiable_claim",
        "text": "Our Dyson air purifier captures 99.97% of allergens and fine particles as small as 0.3 microns. Certified HEPA.",
        "gt_prohibited": False
    },
    {
        "id": "EDGE_GAMING_01",
        "category": "gaming_metaphor",
        "text": "Secretlab Titan Evo: Destroy the competition with brutal ergonomic precision and cold-cure foam.",
        "gt_prohibited": False
    },
    {
        "id": "EDGE_NOISE_01",
        "category": "ocr_noise",
        "text": "XxX 290192 &&! %%% LLL P-R-0-D-U-C-T === 99.0",
        "gt_prohibited": False
    },
    {
        "id": "EDGE_NOISE_02",
        "category": "ocr_noise",
        "text": "The 100 200 12/10/2026 Page 1 of 4",
        "gt_prohibited": False
    },
    {
        "id": "EDGE_EMPTY_01",
        "category": "empty_input",
        "text": "",
        "gt_prohibited": False
    },
    {
        "id": "EDGE_MULTI_SAFE_01",
        "category": "multilingual_safe",
        "text": "Descubre las mejores ofertas de viajes a Cancún con vuelos directos y hoteles todo incluido.",
        "gt_prohibited": False
    },
    {
        "id": "EDGE_MULTI_SAFE_02",
        "category": "multilingual_safe",
        "text": "Compre café fresco em grãos torrado artesanalmente nas montanhas de Minas Gerais.",
        "gt_prohibited": False
    }
]


def run_generalization_test():
    print("=" * 80)
    print("   SAFEAD AI: DOMAIN AD TEXT CLASSIFIER 30-SAMPLE GENERALIZATION BENCHMARK   ")
    print("=" * 80)

    clf = ExperimentalDomainAdTextClassifier(use_local_toxic_bert=False)

    y_true = []
    y_pred = []
    audit_records = []
    latencies = []

    for item in GENERALIZATION_TEXT_CORPUS:
        t0 = time.time()
        res = clf.predict(item["text"])
        lat = (time.time() - t0) * 1000.0
        latencies.append(lat)

        gt = item["gt_prohibited"]
        pred = res["is_flagged_prohibited"]
        y_true.append(gt)
        y_pred.append(pred)

        is_correct = (gt == pred)
        audit_records.append({
            "id": item["id"],
            "category": item["category"],
            "gt": gt,
            "pred": pred,
            "correct": is_correct,
            "violations": res["violation_types"],
            "latency_ms": round(lat, 2)
        })

    tp = sum(1 for t, p in zip(y_true, y_pred) if t and p)
    fp = sum(1 for t, p in zip(y_true, y_pred) if not t and p)
    fn = sum(1 for t, p in zip(y_true, y_pred) if t and not p)
    tn = sum(1 for t, p in zip(y_true, y_pred) if not t and not p)

    prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0
    acc = (tp + tn) / len(y_true)

    print(f"Total Evaluated Test Cases : {len(GENERALIZATION_TEXT_CORPUS)}")
    print(f"  - Prohibited Cases       : {sum(y_true)}")
    print(f"  - Permitted/Edge Cases   : {len(y_true) - sum(y_true)}")
    print("-" * 80)
    print(f"True Positives (TP)        : {tp:>4} / {sum(y_true)}")
    print(f"False Negatives (FN)       : {fn:>4} / {sum(y_true)}")
    print(f"False Positives (FP)       : {fp:>4} / {len(y_true) - sum(y_true)}")
    print(f"True Negatives (TN)        : {tn:>4} / {len(y_true) - sum(y_true)}")
    print("-" * 80)
    print(f"Classification Accuracy    : {acc*100:>6.2f}%")
    print(f"Precision                  : {prec*100:>6.2f}%")
    print(f"Recall                     : {rec*100:>6.2f}%")
    print(f"F1-Score                   : {f1:>6.4f}")
    print(f"Average Execution Latency  : {np.mean(latencies):>6.2f} ms")
    print("=" * 80)

    # Save artifact
    out_file = "results/real_pipeline_baseline/phase5b_text_generalization_report.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump({
            "metrics": {
                "total": len(y_true),
                "accuracy": round(acc, 4),
                "precision": round(prec, 4),
                "recall": round(rec, 4),
                "f1": round(f1, 4),
                "tp": tp, "fp": fp, "fn": fn, "tn": tn,
                "avg_latency_ms": round(float(np.mean(latencies)), 2)
            },
            "audit": audit_records
        }, f, indent=2)

    print(f"Generalization report saved to: {out_file}")
    return acc, prec, rec, f1


if __name__ == "__main__":
    run_generalization_test()
