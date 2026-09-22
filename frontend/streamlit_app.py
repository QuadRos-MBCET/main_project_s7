import sys
import os

# Ensure project root is in Python module search path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st
import requests
import json
import time
from PIL import Image

# FastAPI Backend Base URL
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000/api/v1")

st.set_page_config(
    page_title="SafeAd AI - Multimodal Trust & Safety Framework",
    page_icon="🛡️",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 34px;
        color: #1e3a8a;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2px;
    }
    .sub-header {
        font-size: 15px;
        color: #4b5563;
        text-align: center;
        margin-bottom: 20px;
    }
    .badge-reject {
        background-color: #ef4444;
        color: #ffffff;
        padding: 12px 20px;
        border-radius: 8px;
        font-size: 20px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 15px;
    }
    .badge-18 {
        background-color: #f59e0b;
        color: #ffffff;
        padding: 12px 20px;
        border-radius: 8px;
        font-size: 20px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 15px;
    }
    .badge-14 {
        background-color: #3b82f6;
        color: #ffffff;
        padding: 12px 20px;
        border-radius: 8px;
        font-size: 20px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 15px;
    }
    .badge-approve {
        background-color: #10b981;
        color: #ffffff;
        padding: 12px 20px;
        border-radius: 8px;
        font-size: 20px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 15px;
    }
    .workflow-step {
        background-color: #0f172a;
        color: #f8fafc !important;
        padding: 12px 16px;
        border-left: 4px solid #38bdf8;
        border-radius: 6px;
        margin-bottom: 10px;
        font-size: 14px;
    }
    .workflow-step b { color: #38bdf8 !important; }
    .workflow-step i { color: #cbd5e1 !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-header'>🛡️ SAFEAD AI (SAFE-VISION)</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Multimodal Pre-Publication Advertisement Safety Moderation & Policy Decision Framework</div>", unsafe_allow_html=True)

# Session state initialization
if "user_token" not in st.session_state:
    st.session_state["user_token"] = None
if "user_id" not in st.session_state:
    st.session_state["user_id"] = 1
if "username" not in st.session_state:
    st.session_state["username"] = "GuestUser"
if "verified_age_group" not in st.session_state:
    st.session_state["verified_age_group"] = "AGE_18_PLUS"

# Sidebar System Health Status
st.sidebar.title("SafeAd Control Center")
try:
    health_resp = requests.get(f"{BACKEND_URL.replace('/api/v1', '')}/health", timeout=3)
    if health_resp.status_code == 200:
        st.sidebar.success(f"🟢 System Online ({health_resp.json().get('database', 'DB').upper()})")
    else:
        st.sidebar.error("🔴 Backend Error")
except Exception:
    st.sidebar.warning("⚠️ Local Backend Offline — Standalone Pipeline Active")

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Logged User**: `{st.session_state['username']}`")
st.sidebar.markdown(f"**Verified Age**: `{st.session_state['verified_age_group']}`")

tabs = st.tabs([
    "📢 Advertisement Moderation Portal",
    "👤 User Authentication & Age Policy",
    "📱 Age-Aware Feed Preview",
    "📊 Audit History & Logs"
])

# =====================================================================
# TAB 1: ADVERTISEMENT MODERATION PORTAL
# =====================================================================
with tabs[0]:
    st.header("Upload Advertisement Creative for Safety Audit")
    
    col1, col2 = st.columns([1, 1.2])
    
    with col1:
        st.subheader("1. Submission Options")
        with st.form("ad_upload_form"):
            ad_title = st.text_input("Creative Title", placeholder="e.g. Organic Apple Juice / Casino Slot Promo")
            ad_caption = st.text_area("Ad Copy / Caption", placeholder="e.g. Win instant prizes / Pure natural ingredients")
            uploaded_file = st.file_uploader("Upload Image or Video Advertisement", type=["jpg", "jpeg", "png", "webp", "mp4", "avi", "mov"])
            submit_btn = st.form_submit_button("Analyze Advertisement")
            
        if submit_btn:
            if not ad_title or not uploaded_file:
                st.error("Please provide a title and upload a media file.")
            else:
                progress_bar = st.progress(0)
                status_text = st.empty()

                progress_bar.progress(10)
                status_text.info("[1] Uploading Advertisement...")

                progress_bar.progress(25)
                status_text.info("[2] Extracting Content & Keyframes...")

                progress_bar.progress(40)
                status_text.info("[3] Running Visual Safety Analysis (Llama Guard Vision)...")

                progress_bar.progress(55)
                status_text.info("[4] Running Video Violence & NSFW Analysis (VideoMAE + Falconsai ViT)...")

                progress_bar.progress(70)
                status_text.info("[5] Running Multilingual OCR Text Extraction (PP-OCR / PaddleOCR)...")

                progress_bar.progress(85)
                status_text.info("[6] Extracting Audio & Transcribing Speech (OpenAI Whisper)...")

                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    data = {"title": ad_title, "caption": ad_caption, "user_id": st.session_state["user_id"]}
                    
                    resp = requests.post(f"{BACKEND_URL}/advertisements/check", files=files, data=data, timeout=120)
                    progress_bar.progress(100)
                    status_text.success("[7 & 8] Multimodal Safety Evidence Fusion Completed!")
                    
                    if resp.status_code == 200:
                        st.session_state["moderation_report"] = resp.json()
                    else:
                        # Standalone pipeline execution fallback
                        from ai.pipeline import run_safead_inference
                        # Save temp uploaded file
                        temp_path = os.path.join("uploads", uploaded_file.name)
                        os.makedirs("uploads", exist_ok=True)
                        with open(temp_path, "wb") as f:
                            f.write(uploaded_file.getvalue())
                        st.session_state["moderation_report"] = run_safead_inference(temp_path, ad_title, ad_caption)
                except Exception as e:
                    # Direct Python pipeline execution
                    from ai.pipeline import run_safead_inference
                    temp_path = os.path.join("uploads", uploaded_file.name)
                    os.makedirs("uploads", exist_ok=True)
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getvalue())
                    st.session_state["moderation_report"] = run_safead_inference(temp_path, ad_title, ad_caption)
                    progress_bar.progress(100)
                    status_text.success("[7 & 8] Multimodal Safety Evidence Fusion Completed!")

    with col2:
        st.subheader("2. SafeAd AI Moderation Result")
        if "moderation_report" in st.session_state:
            rep = st.session_state["moderation_report"]
            
            classification = rep.get("classification", "UNSAFE_FOR_ALL")
            display_label = rep.get("display_label", classification)
            action = rep.get("publication_action", "REJECT")
            risk_score = rep.get("risk_score", 0.0)
            confidence = rep.get("confidence", 0.85)
            
            # Action Badge Display
            if classification == "UNSAFE_FOR_ALL" or action == "REJECT":
                st.markdown("<div class='badge-reject'>REJECT — UNSAFE FOR ALL</div>", unsafe_allow_html=True)
            elif classification == "SAFE_18_PLUS":
                st.markdown("<div class='badge-18'>AGE RESTRICTED — 18+</div>", unsafe_allow_html=True)
            elif classification == "SAFE_14_PLUS":
                st.markdown("<div class='badge-14'>AGE RESTRICTED — 14+</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='badge-approve'>APPROVED — SAFE FOR ALL</div>", unsafe_allow_html=True)
                
            # Metrics
            mcol1, mcol2, mcol3 = st.columns(3)
            mcol1.metric("Risk Score", f"{risk_score:.1f} / 100")
            mcol2.metric("Confidence", f"{int(confidence * 100)}%")
            mcol3.metric("Total Latency", f"{rep.get('total_processing_time_seconds', 0.0):.2f}s")
            
            # Evidence Breakdown
            st.markdown("### Modality Evidence Summary")
            ev = rep.get("evidence", {})
            
            ev_col1, ev_col2 = st.columns(2)
            with ev_col1:
                st.markdown(f"**Visual Safety**: `{'UNSAFE' if ev.get('visual', {}).get('unsafe') else 'SAFE'}`")
                st.markdown(f"**Video Violence Score**: `{ev.get('video', {}).get('violence_score', 0.0):.2f}`")
                st.markdown(f"**Adult / NSFW Score**: `{ev.get('nsfw', {}).get('adult_score', 0.0):.2f}`")
            with ev_col2:
                st.markdown(f"**OCR Risk**: `{ev.get('ocr', {}).get('risk', 0.0):.2f}`")
                audio_tx = rep.get("audio_transcript", "") or ev.get("audio", {}).get("transcript", "")
                st.markdown(f"**Audio Available**: `{'YES' if rep.get('audio_available', ev.get('audio', {}).get('available')) else 'NO'}`")
                st.markdown(f"**Speech Transcript**: *\"{audio_tx if audio_tx else 'No spoken speech detected.'}\"*")

            # Explanation
            st.markdown("### Decision Explanation")
            st.info(rep.get("explanation", "Completed safety evaluation."))

            # Step Workflow Log
            with st.expander("Show 8-Step Multimodal Detection Workflow Log"):
                timings = rep.get("stage_timings", {})
                st.markdown(f"""
                <div class='workflow-step'><b>Step 1: Upload & File Validation</b> — Completed ({timings.get('step1_validation', 0.0)}s)</div>
                <div class='workflow-step'><b>Step 2: Keyframe & Audio Extraction</b> — Completed ({timings.get('step2_extraction', 0.0)}s)</div>
                <div class='workflow-step'><b>Step 3: Visual Safety Analysis (Llama Guard Vision)</b> — Completed ({timings.get('step3_visual_safety', 0.0)}s)</div>
                <div class='workflow-step'><b>Step 4: Video Violence & NSFW Analysis (VideoMAE + Falconsai)</b> — Completed ({timings.get('step4_video_nsfw', 0.0)}s)</div>
                <div class='workflow-step'><b>Step 5: OCR Text Analysis (PP-OCR / PaddleOCR)</b> — Extracted text: <i>"{rep.get('extracted_ocr', 'None')}"</i> ({timings.get('step5_ocr', 0.0)}s)</div>
                <div class='workflow-step'><b>Step 6: Audio Analysis (Whisper Speech-to-Text)</b> — Completed ({timings.get('step6_audio', 0.0)}s)</div>
                <div class='workflow-step'><b>Step 7: SafeAd Evidence Fusion</b> — Fused Score: {risk_score}/100 ({timings.get('step7_fusion', 0.0)}s)</div>
                <div class='workflow-step'><b>Step 8: Final Decision & Policy Action</b> — Classification: {classification} ({timings.get('step8_decision', 0.0)}s)</div>
                """, unsafe_allow_html=True)
        else:
            st.info("Upload an advertisement creative on the left panel to execute the SafeAd safety pipeline.")

# =====================================================================
# TAB 2: USER AUTHENTICATION & AGE VERIFICATION
# =====================================================================
with tabs[1]:
    st.header("User Age Verification & Access Policy Control")
    st.markdown("User age verification is strictly separated from advertisement classification. Advertisement classification remains objective: **Safe for All**, **14+**, **18+**, **Unsafe for All**.")

# =====================================================================
# TAB 3: AGE-AWARE FEED PREVIEW
# =====================================================================
with tabs[2]:
    st.header("Personalized User Ad Feed")
    st.markdown(f"Current Viewer Profile: **{st.session_state['username']}** | Verified Age Profile: **{st.session_state['verified_age_group']}**")
    st.info("Policy Protection: Advertisements classified as 'UNSAFE_FOR_ALL' are NEVER displayed to any user.")

# =====================================================================
# TAB 4: AUDIT HISTORY & LOGS
# =====================================================================
with tabs[3]:
    st.header("System Audit Logs & Moderation History")
    try:
        resp = requests.get(f"{BACKEND_URL}/moderation/history", timeout=5)
        if resp.status_code == 200:
            st.dataframe(resp.json(), use_container_width=True)
    except Exception as e:
        st.info("Local database active. Moderation history will display upon running API backend.")
