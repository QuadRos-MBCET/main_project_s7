import os
import json
import pandas as pd

def main():
    df_dev = pd.read_csv(r"C:\Users\hello\Videos\sourav\datasets\safead-dataset-hub\splits\repaired_benchmark\development_set.csv")
    clean_dev = df_dev[~((df_dev["media_type"] == "image") & (df_dev["resolution"] == "800x520"))]
    s14p = clean_dev[clean_dev["safead_label"] == "SAFE_14_PLUS"].copy()

    cache_path = os.path.join("results", "real_pipeline_baseline", "saved_detector_outputs.json")
    with open(cache_path, "r", encoding="utf-8") as f:
        cached = json.load(f)

    manifest_rows = []
    for _, row in s14p.iterrows():
        sid = row["sample_id"]
        mtype = row["media_type"]
        c_rec = cached.get(sid, {})
        evidence = c_rec.get("raw_detector_evidence", {})
        
        ocr_text = c_rec.get("extracted_ocr", "")
        audio_text = evidence.get("audio", {}).get("transcript", "")
        adult_score = evidence.get("visual", {}).get("adult", 0.0)
        violence_score = evidence.get("video", {}).get("violence", 0.0)
        
        # Observable content summary
        observable = []
        if mtype == "video":
            if audio_text:
                observable.append(f"Audio: '{audio_text[:50]}...'")
            if violence_score > 0.15:
                observable.append(f"Action/Motion: {violence_score:.2f}")
        if ocr_text:
            observable.append(f"Text: '{ocr_text[:40]}'")
        if adult_score > 0.25:
            observable.append(f"Adult/Attire score: {adult_score:.2f}")
        obs_summary = "; ".join(observable) if observable else "General consumer product creative"

        # Demographic vs safety diagnosis
        reason_str = str(row["label_reason"]).lower()
        is_demographic = any(w in reason_str for w in ["youth", "streetwear", "gaming", "teen", "drivers", "rock-band", "muscle car", "automobile", "sports car", "toy"])
        has_harm_signal = (adult_score >= 0.35 or violence_score >= 0.40)
        
        if has_harm_signal and adult_score >= 0.35:
            suggested = "SAFE_18_PLUS"
            demo_desc = "Safety Restriction: Swimwear/adult attire detected"
        elif has_harm_signal and violence_score >= 0.40:
            suggested = "SAFE_14_PLUS"
            demo_desc = "Safety Restriction: Mild combat/action violence"
        elif is_demographic:
            suggested = "SAFE_FOR_ALL"
            demo_desc = "Demographic Appeal (Teen/Youth target market, 0.0 safety risk)"
        else:
            suggested = "REQUIRES_HUMAN_REVIEW"
            demo_desc = "Ambiguous / Unclear safety justification"

        manifest_rows.append({
            "media_id": sid,
            "media_type": mtype,
            "existing_label": "SAFE_14_PLUS",
            "existing_rationale": row["label_reason"],
            "actual_observable_content": obs_summary,
            "demographic_vs_safety_finding": demo_desc,
            "is_demographic_label": is_demographic and not has_harm_signal,
            "suggested_harmonized_label": suggested,
            "needs_independent_human_review": True,
            "reviewer_notes": (
                "General youth demographic product (streetwear/gaming/auto). Recommend SAFE_FOR_ALL if no safety violation."
                if suggested == "SAFE_FOR_ALL"
                else ("Suggestive attire/swimwear detected by visual ViT. Harmonize with 18+ policy." if suggested == "SAFE_18_PLUS" else "Verify action sequence.")
            )
        })

    manifest_df = pd.DataFrame(manifest_rows)
    out_csv = os.path.join("docs", "SAFE_14_PLUS_LABEL_REVIEW_MANIFEST.csv")
    os.makedirs("docs", exist_ok=True)
    manifest_df.to_csv(out_csv, index=False)
    print(f"Manifest generated: {out_csv} ({len(manifest_df)} rows)")
    print(manifest_df["suggested_harmonized_label"].value_counts())

if __name__ == "__main__":
    main()
