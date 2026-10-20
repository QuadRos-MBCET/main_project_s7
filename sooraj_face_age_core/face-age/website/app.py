import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import streamlit as st
import sqlite3
import time
import sys
import subprocess
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

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
    annotate_live_frame,
    Realtime30FPSVisionEngine
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
        try:
            if up_id.name.lower().endswith('.pdf'):
                with st.spinner("Rendering PDF page and extracting document text..."):
                    id_image_np, id_pdf_text = process_pdf_id_document(up_id.getvalue())
                if id_image_np is not None:
                    st.success(f"📄 PDF Loaded: '{up_id.name}' (First page rendered)")
                else:
                    st.error(f"Failed to process PDF: {id_pdf_text}")
            else:
                up_id.seek(0)
                id_image_np = np.array(Image.open(up_id).convert("RGB"))
        except Exception as e:
            st.error(f"Error loading uploaded ID: {e}")
            
    if id_image_np is not None:
        st.image(id_image_np, caption="Scanned ID Card / PDF Page", width="stretch")

with c_live:
    st.markdown("#### 2. Live Face Camera Video Stream")
    
    def _on_freeze_click():
        if "latest_live_frame" in st.session_state and st.session_state["latest_live_frame"] is not None:
            st.session_state["frozen_live_frame"] = st.session_state["latest_live_frame"]
            st.session_state["t1_cam_toggle"] = False
            if "vision_engine" in st.session_state:
                try:
                    st.session_state["vision_engine"].stop()
                except Exception:
                    pass
                del st.session_state["vision_engine"]

    def _on_clear_click():
        if "frozen_live_frame" in st.session_state:
            del st.session_state["frozen_live_frame"]

    col_c1, col_c2 = st.columns([1, 1])
    with col_c1:
        st.button("📸 Freeze Current Frame", key="freeze_btn", on_click=_on_freeze_click, help="Lock current live frame for analysis & report")
    with col_c2:
        st.button("🔄 Clear Frozen Frame", key="clear_frozen_btn", on_click=_on_clear_click)

    cam_active = st.toggle("🎥 Start Live Camera Feed", value=False, key="t1_cam_toggle")

    live_image_np = st.session_state.get("frozen_live_frame", None)
    
    video_placeholder = st.empty()
    status_placeholder = st.empty()
    
    if cam_active:
        st.caption("🟢 Live Front Camera Video Active — 30 FPS ArcFace Real-Time Verification")
        
        # Seamlessly reuse or initialize vision engine so that removing or replacing an ID card
        # does NOT recreate the camera hardware session or cause DirectShow COM collisions.
        if "vision_engine" not in st.session_state or not getattr(st.session_state["vision_engine"], "running", False):
            st.session_state["vision_engine"] = Realtime30FPSVisionEngine(id_image_np=id_image_np, target_fps=30.0)
        else:
            st.session_state["vision_engine"].update_id_image(id_image_np)

        engine = st.session_state["vision_engine"]
        target_interval = 1.0 / 30.0  # Strict 33.33ms pacing for 30 FPS
        
        while engine.running:
            t_frame_start = time.time()
            annotated, raw_rgb, info = engine.get_annotated_frame(target_fps=30.0)
            
            if annotated is not None:
                video_placeholder.image(annotated, caption="Live Front Camera Video (Locked 30 FPS | ArcFace)", width="stretch")
                
                is_spoof = info.get("is_spoof", False)
                match_score = info.get("match_score")
                is_match = info.get("is_match")
                
                if is_spoof:
                    score_html = ""
                    if match_score is not None:
                        score_color = "#16a34a" if is_match else "#dc2626"
                        score_tag = "✅ ArcFace Match" if is_match else "❌ ArcFace Mismatch"
                        score_html = f"""
                        <div style="border-top:1px dashed #fca5a5; margin-top:8px; padding-top:8px; display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                <span style="font-weight:700; color:#991b1b; font-size:13px;">{score_tag} (Cross-Matched):</span><br>
                                <span style="font-size:11px; color:#7f1d1d;">ArcFace Biometrics Computed Despite Spoof</span>
                            </div>
                            <div style="font-size:22px; font-weight:800; color:{score_color};">{match_score:.1%}</div>
                        </div>
                        """
                    spoof_detail = info.get("spoof_reason", "Screen/Photo Presentation Attack")
                    status_placeholder.markdown(f"""
                    <div style="background:#fee2e2; border:1px solid #ef4444; border-radius:10px; padding:12px; margin-top:6px;">
                        <b style="color:#b91c1c; font-size:15px;">🛑 YOU ARE A SCREEN</b><br>
                        <span style="color:#991b1b; font-size:12px;">Photo/Screen Spoof Detected! ({spoof_detail})</span>
                        {score_html.strip()}
                    </div>
                    """, unsafe_allow_html=True)
                elif match_score is not None:
                    color = "#16a34a" if is_match else "#dc2626"
                    tag = "✅ BIOMETRICS MATCH" if is_match else "❌ BIOMETRIC MISMATCH"
                    status_placeholder.markdown(f"""
                    <div style="background:#f8fafc; border:1px solid #cbd5e1; border-radius:10px; padding:10px; margin-top:6px; display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <span style="font-weight:700; color:{color};">{tag}</span><br>
                            <span style="font-size:12px; color:#64748b;">ArcFace MS1MV3 Confidence [30 FPS]</span>
                        </div>
                        <div style="font-size:22px; font-weight:800; color:{color};">{match_score:.1%}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    status_placeholder.caption("Face detected. Upload an ID Card on the left to cross-match.")
                    
                st.session_state["latest_live_frame"] = raw_rgb
                live_image_np = raw_rgb
                
            elapsed = time.time() - t_frame_start
            sleep_time = max(0.001, target_interval - elapsed)
            time.sleep(sleep_time)
            
    else:
        if "vision_engine" in st.session_state:
            try:
                st.session_state["vision_engine"].stop()
            except Exception:
                pass
            del st.session_state["vision_engine"]
            
        if live_image_np is not None:
            video_placeholder.image(live_image_np, caption="Frozen Live Camera Snapshot", width="stretch")
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
        st.error("🛑 **YOU ARE A SCREEN**")
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
