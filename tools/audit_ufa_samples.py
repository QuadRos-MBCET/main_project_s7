import json
import pandas as pd

def main():
    with open("results/real_pipeline_baseline/saved_detector_outputs.json", "r", encoding="utf-8") as f:
        d = json.load(f)
    cat = pd.read_csv(r"C:\Users\hello\Videos\sourav\datasets\safead-dataset-hub\splits\repaired_benchmark\development_set.csv").set_index("sample_id")

    ufa_sids = [sid for sid, rec in d.items() if rec["true_label"] == "UNSAFE_FOR_ALL"]
    print(f"Total UFA samples in clean dev: {len(ufa_sids)}\n")

    for sid in ufa_sids:
        rec = d[sid]
        ev = rec.get("raw_detector_evidence", {})
        vis = ev.get("visual", {})
        vid = ev.get("video", {})
        ocr = rec.get("extracted_ocr", "")
        aud = ev.get("audio", {}).get("transcript", "")
        cat_row = cat.loc[sid] if sid in cat.index else None
        reason = str(cat_row["label_reason"] if cat_row is not None else "")
        mtype = rec["media_type"].upper()
        
        print("=" * 80)
        print(f"Sample: {sid} ({mtype})")
        print(f"Catalog Reason : {reason[:80]}...")
        print(f"Baseline Pred  : {rec.get('predicted_label')} (Score: {rec.get('risk_score')})")
        print(f"Visual Unsafe  : {vis.get('unsafe')} | Evidence: {vis.get('evidence')} | Adult: {vis.get('adult')}")
        print(f"Video Violence : {vid.get('violence')} | Adult: {vid.get('adult')}")
        if rec["media_type"] == "video":
            print(f"Top Video Segs : {vid.get('sampled_segments', [])[:3]}")
        print(f"OCR Text       : {repr(ocr[:70])}")
        print(f"Audio Transcript: {repr(aud[:70])}")

if __name__ == "__main__":
    main()
