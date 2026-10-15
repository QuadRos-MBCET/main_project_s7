import os
import sys
import time
import numpy as np
import pandas as pd

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Add project root and joseph_safead_core to sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
jb_dir = os.path.join(root_dir, "joseph_safead_core")
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
if jb_dir not in sys.path:
    sys.path.insert(0, jb_dir)

from website.database import get_connection, init_database
from website.pipeline import (
    extract_video_keyframes,
    extract_ocr_text,
    extract_audio_transcript,
    analyze_text_risk,
    run_multimodal_moderation
)

VIDEO_POLICY_BENCHMARK = [
    # 1. Safe & Educational Videos (SAFE_FOR_ALL / APPROVE)
    {
        "id": "VID-01",
        "title": "Online Coding Lessons for Beginners",
        "caption": "Learn Python, HTML, and CSS step by step with easy lessons.",
        "filename": "coding_lessons.mp4",
        "category": "Educational",
        "expected_action": "approved",
        "expected_bracket": "SAFE_FOR_ALL"
    },
    {
        "id": "VID-02",
        "title": "Geometry Tutorial for Kids",
        "caption": "Simple geometric shapes and math formulas explained in a fun way.",
        "filename": "geometry_class.mp4",
        "category": "Educational",
        "expected_action": "approved",
        "expected_bracket": "SAFE_FOR_ALL"
    },
    # 2. Gambling & Online Betting (AGE_18_PLUS / RESTRICT or REJECT)
    {
        "id": "VID-03",
        "title": "Grand Casino Vegas Promo",
        "caption": "Bet online, win real cash! Play blackjack and poker slot machine satta.",
        "filename": "casino_ad.mp4",
        "category": "Gambling",
        "expected_action": "rejected",
        "expected_bracket": "AGE_18_PLUS"
    },
    # 3. Violence & Weapons (UNSAFE_FOR_ALL / REJECT)
    {
        "id": "VID-04",
        "title": "Action Thriller Movie: Blood & Combat Guns",
        "caption": "Watch the ultimate combat fight with weapons, blood and shooting.",
        "filename": "violence_ad.mp4",
        "category": "Violence",
        "expected_action": "rejected",
        "expected_bracket": "UNSAFE_FOR_ALL"
    },
    # 4. Misleading Claims & Fast Cash Scam (UNSAFE_FOR_ALL / REJECT)
    {
        "id": "VID-05",
        "title": "Get Rich Fast Scheme Giveaway",
        "caption": "Paisa double in 24 hours guaranteed! Click here to win instant cash prize.",
        "filename": "scam_giveaway.mp4",
        "category": "Misleading Advertisement",
        "expected_action": "rejected",
        "expected_bracket": "UNSAFE_FOR_ALL"
    }
]

def evaluate_video_policy_accuracy():
    init_database()
    conn = get_connection()
    cursor = conn.cursor()

    print("=" * 80)
    print("      SAFEAD AI — VIDEO CONTENT POLICY ACCURACY EVALUATION SUITE      ")
    print("=" * 80)

    results = []
    
    for item in VIDEO_POLICY_BENCHMARK:
        file_path = os.path.join(root_dir, "sample_ad_media", item["filename"])
        if not os.path.exists(file_path):
            file_path = os.path.join(root_dir, "website", "uploads", item["filename"])

        if not os.path.exists(file_path):
            print(f"[SKIP] Video file not found: {item['filename']}")
            continue

        t_start = time.time()

        # Insert ad into DB for pipeline execution
        cursor.execute("""
            INSERT INTO Advertisements (title, caption, file_path, status)
            VALUES (?, ?, ?, 'under_review')
        """, (item["title"], item["caption"], file_path))
        ad_id = cursor.lastrowid
        conn.commit()

        # Run full multimodal video moderation pipeline
        res = run_multimodal_moderation(ad_id)
        latency_ms = (time.time() - t_start) * 1000

        pred_action = res.get("status", "unknown")
        
        # Fetch fused risk score & detected violations
        cursor.execute("SELECT final_score, visual_score, ocr_score, speech_score FROM RiskScores WHERE ad_id = ?", (ad_id,))
        scores = cursor.fetchone()
        final_score, vis_score, ocr_score, sp_score = scores if scores else (0, 0, 0, 0)

        cursor.execute("SELECT explanation FROM ModerationResults WHERE ad_id = ?", (ad_id,))
        reason_row = cursor.fetchone()
        reason = reason_row[0] if reason_row else ""

        # Determine binary match
        is_correct = (pred_action == item["expected_action"])

        results.append({
            "ID": item["id"],
            "Video": item["filename"],
            "Policy Category": item["category"],
            "Expected": item["expected_action"].upper(),
            "Predicted": pred_action.upper(),
            "Risk Score": f"{final_score:.1f}%",
            "Latency (ms)": f"{latency_ms:.1f}",
            "Verdict": "PASS" if is_correct else "FAIL"
        })

    conn.close()

    df = pd.DataFrame(results)
    print("\n### 📋 Per-Video Evaluation Results Table:\n")
    print(df.to_string(index=False))

    # Compute aggregate metrics
    total = len(results)
    if total == 0:
        print("No test videos evaluated.")
        return

    passes = sum(1 for r in results if r["Verdict"] == "PASS")
    accuracy = (passes / total) * 100.0

    # Binary classification (Safe=Approved vs Unsafe=Rejected/Review)
    y_true = [1 if r["Expected"] == "APPROVED" else 0 for r in results]
    y_pred = [1 if r["Predicted"] == "APPROVED" else 0 for r in results]

    tp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 1 and yp == 1)
    fp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 0 and yp == 1)
    fn = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 1 and yp == 0)
    tn = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 0 and yp == 0)

    precision = (tp / (tp + fp)) * 100.0 if (tp + fp) > 0 else 100.0
    recall = (tp / (tp + fn)) * 100.0 if (tp + fn) > 0 else 100.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    far = (fp / (fp + tn)) * 100.0 if (fp + tn) > 0 else 0.0
    frr = (fn / (tp + fn)) * 100.0 if (tp + fn) > 0 else 0.0

    print("\n" + "=" * 80)
    print("                    AGGREGATE PERFORMANCE METRICS                     ")
    print("=" * 80)
    print(f"Total Video Test Samples Evaluated : {total}")
    print(f"Policy Decision Accuracy           : {accuracy:.2f}% ({passes}/{total} Passed)")
    print(f"Safe Content Precision             : {precision:.2f}%")
    print(f"Safe Content Recall (Sensitivity)  : {recall:.2f}%")
    print(f"F1-Score                           : {f1 / 100.0:.3f}")
    print(f"False Acceptance Rate (FAR)        : {far:.2f}% (Harmful videos passed as safe)")
    print(f"False Rejection Rate (FRR)         : {frr:.2f}% (Safe videos blocked)")
    print("-" * 80)
    print(f"Confusion Matrix:")
    print(f"                       Predicted Safe     Predicted Unsafe")
    print(f"  Actual Safe (Pos)          {tp:<18} {fn:<18}")
    print(f"  Actual Unsafe (Neg)        {fp:<18} {tn:<18}")
    print("=" * 80)

if __name__ == "__main__":
    evaluate_video_policy_accuracy()
