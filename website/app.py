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
from website.classifier import estimate_age_from_face, estimate_detailed_age_from_face, detect_and_crop_face, verify_id_card_and_live_face, process_pdf_id_document

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
    st.markdown("#### 2. Live Face Camera Scan")
    live_type = st.radio("Live Input Source", ["Webcam Snapshot", "Upload Live Face Photo"], horizontal=True, key="t1_live_type")
    
    live_image_np = None
    if live_type == "Webcam Snapshot":
        cam_active = st.toggle("📸 Enable Front Camera Feed", value=False, key="t1_cam_toggle")
        if cam_active:
            st.caption("🟢 Live Front Camera Feed Active — Tap 'Take Photo' below")
            cam_img = st.camera_input("Live Camera Feed", key="t1_cam")
            if cam_img:
                live_image_np = np.array(Image.open(cam_img).convert("RGB"))
        else:
            st.markdown("""
            <div style="border:2px dashed #cbd5e1; border-radius:14px; padding:24px; text-align:center; background:#f8fafc; margin-bottom:12px;">
                <div style="font-size:32px; margin-bottom:6px;">📷</div>
                <div style="font-size:15px; font-weight:600; color:#334155;">Camera is Currently Off</div>
                <div style="font-size:12px; color:#64748b;">Toggle 'Enable Front Camera Feed' above to view feed.</div>
            </div>
            """, unsafe_allow_html=True)
    elif live_type == "Upload Live Face Photo":
        up_live = st.file_uploader("Upload Live Face Photo", type=["jpg", "jpeg", "png"], key="t1_live_file")
        if up_live:
            live_image_np = np.array(Image.open(up_live).convert("RGB"))
            
    if live_image_np is not None:
        st.image(live_image_np, caption="Live Captured Face", use_container_width=True)

# =====================================================================
# STEP 3: REAL-TIME VERIFICATION & CROSS-MATCH VERDICT
# =====================================================================
st.markdown("---")
st.markdown("### 📊 ID vs Live Face Cross-Matching Verdict")
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
