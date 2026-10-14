import streamlit as st
import sqlite3
import os
import time
import sys
import subprocess
from pathlib import Path

# Ensure parent directory is in sys.path for website package imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import cv2
from PIL import Image
from website.database import get_connection, init_database
from website.classifier import (
    estimate_age_from_face,
    estimate_detailed_age_from_face,
    detect_and_crop_face,
    verify_id_card_and_live_face,
    process_pdf_id_document,
    extract_dob_and_age_from_id,
    extract_arcface_embedding,
    compute_similarity_from_embeddings,
    detect_photo_spoof,
    annotate_live_frame
)

init_database()

# Set page config
st.set_page_config(
    page_title="SafeAd AI — ID Card & Face Verification",
    layout="wide",
    page_icon="🛡️",
    initial_sidebar_state="collapsed"
)

# Custom Glassmorphic & Modern CSS
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.hero-container {
    background: linear-gradient(135deg, #1e1b4b 0%, #312e81 40%, #4338ca 100%);
    border-radius: 16px;
    padding: 24px 30px;
    color: white;
    margin-bottom: 24px;
    box-shadow: 0 10px 25px -5px rgba(49, 46, 129, 0.3);
}
.hero-title {
    font-size: 30px;
    font-weight: 700;
    margin: 0;
    color: #ffffff;
}
.hero-subtitle {
    font-size: 15px;
    color: #c7d2fe;
    margin-top: 6px;
}

.card {
    background: #ffffff;
    border: 1px solid #e0e7ff;
    border-radius: 14px;
    padding: 20px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
    margin-bottom: 20px;
}

.metric-card {
    background: #f8fafc;
    border-radius: 12px;
    padding: 14px;
    border: 1px solid #e2e8f0;
    text-align: center;
}
.metric-val {
    font-size: 24px;
    font-weight: 700;
    color: #0f172a;
}
.metric-lbl {
    font-size: 12px;
    color: #64748b;
    font-weight: 500;
    margin-top: 2px;
}

.block-container {
    padding-top: 1.8rem;
    padding-bottom: 2rem;
}
</style>""", unsafe_allow_html=True)

# Top Hero Section
st.markdown("""
    <div class="hero-container">
        <div class="hero-title">🛡️ SafeAd AI — Identity Verification Platform</div>
        <div class="hero-subtitle">ID Card Biometric Verification & Live Face Cross-Matching</div>
    </div>
""", unsafe_allow_html=True)

st.markdown("### 🆔 ID Card Verification & Live Face Cross-Matching")
c_id, c_live = st.columns([1, 1], gap="medium")

with c_id:
    st.markdown("#### 1. Upload Official ID Card")
    up_id = st.file_uploader("Upload ID (Image or PDF Document)", type=["jpg", "jpeg", "png", "pdf"], key="t1_id_file")
    id_manual_dob = st.text_input("Optional DOB override if text blurry (DD/MM/YYYY)", "", key="t1_dob_override")
    
    id_image_np = None
    id_pdf_text = None
    
    if up_id:
        if up_id.name.lower().endswith('.pdf'):
            with st.spinner("Rendering PDF page and extracting document text..."):
                id_image_np, id_pdf_text = process_pdf_id_document(up_id.getvalue())
            if id_image_np is not None:
                st.success(f"📄 PDF Loaded: '{up_id.name}' (First page rendered)")
            else:
                st.error(f"Failed to process PDF: {id_pdf_text}")
        else:
            id_image_np = np.array(Image.open(up_id).convert("RGB"))
            
    if id_image_np is not None:
        st.image(id_image_np, caption="Scanned ID Card / PDF Page", use_container_width=True)

with c_live:
    st.markdown("#### 2. Live Face Camera Video Stream")
    cam_active = st.toggle("🎥 Start Live Camera Feed", value=False, key="t1_cam_toggle")
    
    col_c1, col_c2 = st.columns([1, 1])
    with col_c1:
        lock_frame = st.button("📸 Freeze Current Frame", key="freeze_btn", help="Lock current live frame for analysis & report")
    with col_c2:
        clear_frozen = st.button("🔄 Clear Frozen Frame", key="clear_frozen_btn")

    if clear_frozen and "frozen_live_frame" in st.session_state:
        del st.session_state["frozen_live_frame"]
        st.rerun()

    if lock_frame and "latest_live_frame" in st.session_state:
        st.session_state["frozen_live_frame"] = st.session_state["latest_live_frame"]
        st.session_state["t1_cam_toggle"] = False
        st.rerun()

    live_image_np = st.session_state.get("frozen_live_frame", None)
    
    video_placeholder = st.empty()
    status_placeholder = st.empty()
    
    if cam_active:
        st.caption("🟢 Live Front Camera Video Active — ArcFace Real-Time Face Verification")
        
        # Precompute ID embedding once if ID card is uploaded
        id_face = None
        id_emb = None
        if id_image_np is not None:
            id_face, _ = detect_and_crop_face(id_image_np)
            id_emb = extract_arcface_embedding(id_face)
            
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        frame_idx = 0
        t0 = time.time()
        cached_age_cat = None
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    status_placeholder.error("Could not capture frame from camera.")
                    break
                    
                frame_idx += 1
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Fast downscale for real-time MTCNN tracking
                h_f, w_f = frame_rgb.shape[:2]
                scale = 400.0 / float(w_f) if w_f > 400 else 1.0
                small_rgb = cv2.resize(frame_rgb, (400, int(h_f * scale))) if scale < 1.0 else frame_rgb
                
                live_face, small_bbox = detect_and_crop_face(small_rgb)
                
                live_bbox = None
                if small_bbox is not None:
                    sx, sy, sw, sh = small_bbox
                    live_bbox = (int(sx / scale), int(sy / scale), int(sw / scale), int(sh / scale))
                    
                match_score = None
                is_match = None
                if id_emb is not None and live_face is not None:
                    live_emb = extract_arcface_embedding(live_face)
                    if live_emb is not None:
                        match_score = compute_similarity_from_embeddings(id_emb, live_emb)
                        is_match = match_score >= 0.65
                        
                is_spoof, spoof_score, spoof_reason = (False, 0.0, None)
                if live_face is not None:
                    is_spoof, spoof_score, spoof_reason = detect_photo_spoof(frame_rgb, live_face)
                    
                if frame_idx % 8 == 1 and live_face is not None:
                    try:
                        det = estimate_detailed_age_from_face(live_face)
                        cached_age_cat = det.get("category", "")
                    except Exception:
                        pass
                        
                fps = frame_idx / max(0.001, time.time() - t0)
                
                annotated = annotate_live_frame(
                    frame_rgb,
                    live_bbox=live_bbox,
                    match_score=match_score,
                    is_match=is_match,
                    is_spoof=is_spoof,
                    spoof_reason=spoof_reason,
                    age_category=cached_age_cat,
                    fps=fps
                )
                
                video_placeholder.image(annotated, caption="Live Front Camera Video Feed (ArcFace Real-Time)", use_container_width=True)
                
                if is_spoof:
                    status_placeholder.markdown("""
                    <div style="background:#fee2e2; border:1px solid #ef4444; border-radius:10px; padding:10px; margin-top:6px;">
                        <b style="color:#b91c1c;">🛑 DONT TRY TO PLAY A FOOL WITH ME NIGESH</b><br>
                        <span style="color:#991b1b; font-size:12px;">Photo/Screen Spoof Detected!</span>
                    </div>
                    """, unsafe_allow_html=True)
                elif match_score is not None:
                    color = "#16a34a" if is_match else "#dc2626"
                    tag = "✅ BIOMETRICS MATCH" if is_match else "❌ BIOMETRIC MISMATCH"
                    status_placeholder.markdown(f"""
                    <div style="background:#f8fafc; border:1px solid #cbd5e1; border-radius:10px; padding:10px; margin-top:6px; display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <span style="font-weight:700; color:{color};">{tag}</span><br>
                            <span style="font-size:12px; color:#64748b;">ArcFace MS1MV3 Confidence</span>
                        </div>
                        <div style="font-size:22px; font-weight:800; color:{color};">{match_score:.1%}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    status_placeholder.caption("Face detected. Upload an ID Card on the left to cross-match.")
                    
                st.session_state["latest_live_frame"] = frame_rgb
                live_image_np = frame_rgb
                
                time.sleep(0.02)
        finally:
            cap.release()
            
    else:
        if live_image_np is not None:
            video_placeholder.image(live_image_np, caption="Frozen Live Camera Snapshot", use_container_width=True)
        else:
            video_placeholder.markdown("""
            <div style="border:2px dashed #cbd5e1; border-radius:14px; padding:32px; text-align:center; background:#f8fafc; margin-bottom:12px;">
                <div style="font-size:36px; margin-bottom:8px;">🎥</div>
                <div style="font-size:16px; font-weight:600; color:#334155;">Live Camera Feed is Off</div>
                <div style="font-size:13px; color:#64748b;">Toggle <b>'Start Live Camera Feed'</b> above for real-time ArcFace video comparison.</div>
            </div>
            """, unsafe_allow_html=True)

# =====================================================================
# STEP 3: REAL-TIME VERIFICATION & CROSS-MATCH VERDICT
# =====================================================================
st.markdown("---")
st.markdown("### 📊 ID vs Live Face Cross-Matching Verdict")
if live_image_np is None and "latest_live_frame" in st.session_state:
    live_image_np = st.session_state["latest_live_frame"]

if id_image_np is not None and live_image_np is not None:
    res = verify_id_card_and_live_face(id_image_np, live_image_np, id_manual_dob, id_pdf_text)
    
    # Status & Anti-Spoof Warning
    if res["is_spoof"]:
        st.error("🛑 **DONT TRY TO PLAY A FOOL WITH ME NIGESH**")
        st.warning(f"⚠️ Photo/Screen Spoof Detected! ({res['spoof_reason']})")
    elif res["status"] == "VERIFIED_SUCCESS":
        st.success(f"### {res['message']}")
    elif res["status"] == "FAILED_FACE_MISMATCH":
        st.error(f"### {res['message']}")
    else:
        st.warning(f"### {res['message']}")

    # Side-by-side face comparison & DOB metrics
    vm1, vm2, vm3 = st.columns(3)
    with vm1:
        st.markdown("##### ID Card Face Photo")
        st.image(res["id_face"], width=130)
        st.caption(f"ID Card DOB: **{res['id_dob_str']}**")
        st.caption(f"Extracted ID Age: **{res['id_age']} yrs** (`{res['id_age_category']}`)")
        
    with vm2:
        st.markdown("##### Live Captured Face")
        st.image(res["live_face"], width=130)
        st.caption(f"Live ViT Predicted Age: **`{res['live_age_category']}`**")
        
    with vm3:
        st.markdown("##### Face Similarity Score")
        st.metric("Face Match Confidence", f"{res['face_similarity']:.1%}")
        st.progress(float(res['face_similarity']))
        st.caption(f"Biometric Model: **{res.get('model_used', 'ArcFace (MS1MV3)')}**")
        
        if res["face_match"]:
            st.success("✅ Facial Biometrics Match!")
        else:
            st.error("❌ Facial Mismatch Detected!")
            
        if res["dob_age_match"]:
            st.success("✅ ID DOB matches Live Face Age!")
        else:
            st.warning("⚠️ ID DOB does not match Live Face Age!")
else:
    st.info("👈 Upload an ID Card AND capture/upload a Live Face to execute real-time cross-matching verification.")
