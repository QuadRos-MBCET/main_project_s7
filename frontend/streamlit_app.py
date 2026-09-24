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
    .badge-hitl {
        background-color: #8b5cf6;
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
    .matrix-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 14px;
        margin-bottom: 10px;
    }
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
    st.sidebar.warning("⚠️ Standalone Local Pipeline Active")

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Logged User**: `{st.session_state['username']}`")
st.sidebar.markdown(f"**Verified Age**: `{st.session_state['verified_age_group']}`")

tabs = st.tabs([
    "📢 Advertiser Moderation Portal",
    "👤 User Age-Confidence Analytics",
    "📱 Age-Aware Feed Preview",
    "🛡️ Human Moderator Review Dashboard",
    "📊 Audit History & Logs"
])

# =====================================================================
# TAB 1: ADVERTISER MODERATION PORTAL
# =====================================================================
with tabs[0]:
    st.header("Upload Advertisement Creative for Safety Audit")
    
    col1, col2 = st.columns([1, 1.2])
    
    with col1:
        st.subheader("1. Submission Options")
        with st.form("ad_upload_form"):
            ad_title = st.text_input("Creative Title", placeholder="e.g. Organic Apple Juice / Casino Slot Promo / Get Rich Quick")
            ad_caption = st.text_area("Ad Copy / Caption", placeholder="e.g. Double your money guaranteed / Pure natural ingredients")
            uploaded_file = st.file_uploader("Upload Image or Video Advertisement", type=["jpg", "jpeg", "png", "webp", "mp4", "avi", "mov"])
            submit_btn = st.form_submit_button("Analyze Advertisement")
            
        if submit_btn:
            if not ad_title or not uploaded_file:
                st.error("Please provide a title and upload a media file.")
            else:
                progress_bar = st.progress(0)
                status_text = st.empty()

                progress_bar.progress(15)
                status_text.info("[1 & 2] Validating File & Extracting Adaptive Keyframes...")

                progress_bar.progress(35)
                status_text.info("[3 & 4] Running Multilingual OCR & Visual Safety (Llama Guard Vision)...")

                progress_bar.progress(60)
                status_text.info("[5 & 6] VideoMAE Violence, Falconsai NSFW, & Whisper Speech Transcription...")

                progress_bar.progress(80)
                status_text.info("[7 & 8] Synthesizing Central SafeAdAssessment Matrix & Ad Risk Analysis...")

                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    data = {"title": ad_title, "caption": ad_caption, "user_id": st.session_state["user_id"]}
                    
                    resp = requests.post(f"{BACKEND_URL}/advertisements/analyze", files=files, data=data, timeout=120)

                    progress_bar.progress(100)
                    status_text.success("Central SafeAdAssessment Matrix & Policy Decision Completed!")
                    
                    if resp.status_code == 200:
                        st.session_state["moderation_report"] = resp.json()
                    else:
                        from ai.pipeline import run_safead_inference
                        temp_path = os.path.join("uploads", uploaded_file.name)
                        os.makedirs("uploads", exist_ok=True)
                        with open(temp_path, "wb") as f:
                            f.write(uploaded_file.getvalue())
                        st.session_state["moderation_report"] = run_safead_inference(temp_path, ad_title, ad_caption)
                except Exception:
                    from ai.pipeline import run_safead_inference
                    temp_path = os.path.join("uploads", uploaded_file.name)
                    os.makedirs("uploads", exist_ok=True)
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getvalue())
                    st.session_state["moderation_report"] = run_safead_inference(temp_path, ad_title, ad_caption)
                    progress_bar.progress(100)
                    status_text.success("Central SafeAdAssessment Matrix & Policy Decision Completed!")

    with col2:
        st.subheader("2. SafeAd AI Moderation Result")
        if "moderation_report" in st.session_state:
            rep = st.session_state["moderation_report"]
            
            classification = rep.get("classification", "UNSAFE_FOR_ALL")
            action = rep.get("publication_action", "REJECT")
            risk_score = rep.get("risk_score", 0.0)
            confidence = rep.get("confidence", 0.85)
            requires_hitl = rep.get("requires_human_review", False) or action == "HUMAN_REVIEW"
            
            # Action Badge Display
            if requires_hitl or classification == "REQUIRES_HUMAN_REVIEW":
                st.markdown("<div class='badge-hitl'>REQUIRES HUMAN REVIEW — MODERATOR QUEUED</div>", unsafe_allow_html=True)
            elif classification == "UNSAFE_FOR_ALL" or action == "REJECT":
                st.markdown("<div class='badge-reject'>REJECT — UNSAFE FOR ALL</div>", unsafe_allow_html=True)
            elif classification == "SAFE_18_PLUS":
                st.markdown("<div class='badge-18'>AGE RESTRICTED — 18+</div>", unsafe_allow_html=True)
            elif classification == "SAFE_14_PLUS":
                st.markdown("<div class='badge-14'>AGE RESTRICTED — 14+</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='badge-approve'>APPROVED — SAFE FOR ALL</div>", unsafe_allow_html=True)
                
            # Metrics Row
            mcol1, mcol2, mcol3, mcol4 = st.columns(4)
            mcol1.metric("Risk Score", f"{risk_score:.1f} / 100")
            mcol2.metric("Confidence", f"{int(confidence * 100)}%")
            mcol3.metric("Human Review", "Queued" if requires_hitl else "No")
            mcol4.metric("Latency", f"{rep.get('total_processing_time_seconds', 0.0):.2f}s")
            
            # Central SafeAdAssessment Matrix Card
            st.markdown("### 📊 Central SafeAdAssessment Matrix")
            ev = rep.get("evidence", {})
            matrix = ev if "visual" in ev else rep.get("assessment_matrix", {})
            
            with st.container():
                st.markdown("<div class='matrix-card'>", unsafe_allow_html=True)
                m_col1, m_col2 = st.columns(2)
                with m_col1:
                    st.markdown(f"• **Visual Safety**: `{'UNSAFE' if matrix.get('visual', {}).get('unsafe') else 'SAFE'}`")
                    st.markdown(f"• **Video Violence**: `{matrix.get('video', {}).get('violence', 0.0):.2f}`")
                    st.markdown(f"• **Adult / NSFW**: `{matrix.get('visual', {}).get('adult', 0.0):.2f}`")
                    st.markdown(f"• **OCR Risk**: `{matrix.get('ocr', {}).get('scam', 0.0) or matrix.get('ocr', {}).get('adult', 0.0):.2f}`")
                with m_col2:
                    st.markdown(f"• **Audio Stream**: `{'YES' if rep.get('audio_available') else 'NO'}` ({matrix.get('audio', {}).get('language', 'N/A')})")
                    st.markdown(f"• **Speech Transcript**: *\"{rep.get('audio_transcript', '') or 'No speech'}\"*")
                    st.markdown(f"• **Scam / Deceptive**: `{matrix.get('advertisement_risks', {}).get('scam', 0.0):.2f}`")
                    st.markdown(f"• **Explicit Content**: `{matrix.get('advertisement_risks', {}).get('explicit_content', 0.0):.2f}`")
                st.markdown("</div>", unsafe_allow_html=True)

            # Explanation
            st.markdown("### Decision Explanation & Rationale")
            st.info(rep.get("explanation", "Completed safety evaluation."))

            # Full Transparency Workflow & Latency Breakdown
            with st.expander("🔍 Complete End-to-End Multimodal Workflow & Latency Breakdown", expanded=True):
                st.markdown("**SafeAd AI 10-Step Execution Pipeline**")
                timings = rep.get("stage_timings", {})
                
                t_col1, t_col2 = st.columns(2)
                with t_col1:
                    st.write(f"1. **Input Validation**: `{timings.get('step1_validation', 0.001):.4f}s`")
                    st.write(f"2. **Adaptive Keyframe Extraction**: `{timings.get('step2_extraction', 0.001):.4f}s`")
                    st.write(f"3. **PaddleOCR Overlay Text**: `{timings.get('step3_ocr', 0.001):.4f}s`")
                    st.write(f"4. **Visual Safety (Falconsai ViT)**: `{timings.get('step4_visual_nsfw', 0.001):.4f}s`")
                    st.write(f"5. **VideoMAE Action Violence**: `{timings.get('step5_violence', 0.001):.4f}s`")
                with t_col2:
                    st.write(f"6. **Whisper Speech Transcription**: `{timings.get('step6_audio', 0.001):.4f}s`")
                    st.write(f"7. **Proactive Ad Risk Analyzer**: `{timings.get('step7_ad_risk_analysis', 0.001):.4f}s`")
                    st.write(f"8. **Assessment Matrix Assembly**: `{timings.get('step8_matrix_assembly', 0.001):.4f}s`")
                    st.write(f"9. **SafeAdFusion Policy Engine**: `{timings.get('step9_fusion', 0.001):.4f}s`")
                    st.write(f"10. **Database & Audit Trail**: `{timings.get('step10_decision', 0.001):.4f}s`")

                st.markdown("---")
                ocr_extracted = rep.get('extracted_ocr', '') or rep.get('evidence', {}).get('ocr', {}).get('text', '')
                transcript_extracted = rep.get('audio_transcript', '') or rep.get('evidence', {}).get('audio', {}).get('transcript', '')
                
                st.markdown(f"**Extracted Keyframe OCR Text**: *\"{ocr_extracted.strip() if ocr_extracted and ocr_extracted.strip() else 'No text overlay detected on video keyframes'}\"*")
                st.markdown(f"**Whisper Audio Speech Transcript**: *\"{transcript_extracted.strip() if transcript_extracted and transcript_extracted.strip() else 'No spoken speech detected in audio track'}\"*")


        else:
            st.info("Upload an advertisement creative on the left panel to execute the SafeAd safety pipeline.")


# =====================================================================
# TAB 2: USER AGE-CONFIDENCE ANALYTICS
# =====================================================================
with tabs[1]:
    st.header("User Age-Confidence Analytics System")
    st.markdown("Automates user age verification using Date of Birth (DOB), facial feature detection, estimated age, age difference calculation, and age confidence scoring.")
    
    col_reg1, col_reg2 = st.columns([1, 1])
    with col_reg1:
        st.subheader("1. New User Age Analytics Verification")
        import datetime
        reg_username = st.text_input("Username", value="alice_user")
        reg_dob = st.date_input("Entered Date of Birth (DOB)", value=datetime.date(1999, 5, 15), min_value=datetime.date(1940, 1, 1), max_value=datetime.date(2025, 1, 1))
        profile_selection = st.selectbox("Select Facial Age Estimation Scan Profile", ["Adult Profile (18+ Oval Face Scan)", "Child Profile (< 14 Round Face Scan)", "Teen Profile (14-17 Face Scan)"])
        
        if st.button("Run Age-Confidence Verification"):
            from backend.app.services.age_service import AgeVerificationService
            res = AgeVerificationService.verify_user_age(reg_dob, profile_selection=profile_selection)
            
            st.session_state["age_res"] = res
            st.session_state["verified_age_group"] = res["verified_age_group"].value
            st.success(f"Verification Status: **{res['verification_status']}** | Verified Category: **{res['verified_age_group'].value}**")

    with col_reg2:
        st.subheader("2. Age-Confidence Analytics Dashboard")
        if "age_res" in st.session_state:
            ares = st.session_state["age_res"]
            ac1, ac2, ac3 = st.columns(3)
            ac1.metric("DOB Age", f"{ares['chronological_age']} yrs")
            ac2.metric("Estimated Age", f"{ares['estimated_age']} yrs")
            ac3.metric("Age Difference", f"Δ {ares['age_difference']} yrs")
            
            st.metric("Age Verification Confidence", f"{int(ares['age_confidence'] * 100)}%")
            st.info(f"Verified Age Group: `{ares['verified_age_group'].value}` (Status: {ares['verification_status']})")
        else:
            st.info("Run age verification on the left panel to display confidence analytics.")

# =====================================================================
# TAB 3: AGE-AWARE FEED PREVIEW
# =====================================================================
with tabs[2]:
    st.header("Personalized User Ad Feed")
    st.markdown(f"Current Viewer Profile: **{st.session_state['username']}** | Verified Age Profile: **{st.session_state['verified_age_group']}**")
    st.info("Policy Protection: Advertisements classified as 'UNSAFE_FOR_ALL' or 'REQUIRES_HUMAN_REVIEW' are NEVER displayed to general users.")

# =====================================================================
# TAB 4: HUMAN MODERATOR REVIEW DASHBOARD (HITL)
# =====================================================================
with tabs[3]:
    st.header("Human Moderator Review Queue (Human-in-the-Loop)")
    st.markdown("Advertisements flagged for **low model confidence**, **conflicting modality evidence**, or **borderline risk scores** are held here for manual human moderator review.")
    
    try:
        resp = requests.get(f"{BACKEND_URL.replace('/api/v1', '')}/api/admin/pending", timeout=5)
        if resp.status_code == 200:
            pending_items = resp.json()
            if not pending_items:
                st.success("🎉 No advertisements currently waiting for human moderator review.")
            else:
                for ad in pending_items:
                    with st.expander(f"Review Pending Ad ID #{ad['id']}: '{ad['title']}' (Status: {ad['status']})"):
                        pcol1, pcol2 = st.columns([1, 1.2])
                        with pcol1:
                            if os.path.exists(ad.get("file_path", "")):
                                if ad["file_path"].lower().endswith(".mp4"):
                                    st.video(ad["file_path"])
                                else:
                                    st.image(ad["file_path"], width=350)
                        with pcol2:
                            st.markdown(f"**Title**: {ad['title']}")
                            st.markdown(f"**Caption**: {ad['caption']}")
                            st.markdown(f"**AI Risk Score**: `{ad.get('risk_score', 0.0):.1f} / 100` | **Confidence**: `{int(ad.get('confidence', 0.5)*100)}%`")
                            st.markdown(f"**AI Trigger Reason**: *{ad['explanation']}*")
                            
                            notes = st.text_input("Moderator Notes", key=f"mod_notes_{ad['id']}")
                            
                            m_btn1, m_btn2, m_btn3, m_btn4 = st.columns(4)
                            if m_btn1.button("✅ Safe for All", key=f"safe_{ad['id']}"):
                                requests.post(f"{BACKEND_URL.replace('/api/v1', '')}/api/admin/override", json={"ad_id": ad['id'], "action": "APPROVE", "final_classification": "SAFE_FOR_ALL", "moderator_notes": notes})
                                st.success("Approved Safe for All!")
                                st.rerun()
                            if m_btn2.button("⚠️ 14+ Only", key=f"r14_{ad['id']}"):
                                requests.post(f"{BACKEND_URL.replace('/api/v1', '')}/api/admin/override", json={"ad_id": ad['id'], "action": "AGE_RESTRICT", "final_classification": "SAFE_14_PLUS", "moderator_notes": notes})
                                st.warning("Restricted to 14+!")
                                st.rerun()
                            if m_btn3.button("⚠️ 18+ Only", key=f"r18_{ad['id']}"):
                                requests.post(f"{BACKEND_URL.replace('/api/v1', '')}/api/admin/override", json={"ad_id": ad['id'], "action": "AGE_RESTRICT", "final_classification": "SAFE_18_PLUS", "moderator_notes": notes})
                                st.warning("Restricted to 18+!")
                                st.rerun()
                            if m_btn4.button("❌ Reject Ad", key=f"rej_{ad['id']}"):
                                requests.post(f"{BACKEND_URL.replace('/api/v1', '')}/api/admin/override", json={"ad_id": ad['id'], "action": "REJECT", "final_classification": "UNSAFE_FOR_ALL", "moderator_notes": notes})
                                st.error("Rejected Ad!")
                                st.rerun()
        else:
            st.info("Start FastAPI backend server (`uvicorn backend.app.main:app --reload`) to activate live Moderator Review Queue.")
    except Exception:
        st.info("Start FastAPI backend server (`uvicorn backend.app.main:app --reload`) to activate live Moderator Review Queue.")

# =====================================================================
# TAB 5: AUDIT HISTORY & LOGS
# =====================================================================
with tabs[4]:
    st.header("System Audit Logs & Moderation History")
    try:
        resp = requests.get(f"{BACKEND_URL}/moderation/history", timeout=5)
        if resp.status_code == 200:
            st.dataframe(resp.json(), use_container_width=True)
    except Exception:
        st.info("Local database active. Moderation history will display upon running API backend.")
