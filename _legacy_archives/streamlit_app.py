import streamlit as st
import requests
import os
import json
from PIL import Image
import numpy as np

# FastAPI Backend Base URL
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000/api/v1")

st.set_page_config(
    page_title="SafeAd AI - Multimodal Trust & Safety Framework",
    page_icon="🛡️",
    layout="wide"
)

# Custom Styling
st.markdown("""
    <style>
    .main-header {
        font-size: 36px;
        color: #1e3a8a;
        font-weight: bold;
        text-align: center;
        margin-bottom: 5px;
    }
    .sub-header {
        font-size: 16px;
        color: #4b5563;
        text-align: center;
        margin-bottom: 25px;
    }
    .card-box {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #e5e7eb;
        margin-bottom: 15px;
    }
    .workflow-step {
        background-color: #1e293b;
        color: #f8fafc !important;
        padding: 14px 18px;
        border-left: 4px solid #3b82f6;
        border-radius: 6px;
        margin-bottom: 12px;
        font-size: 14px;
    }
    .workflow-step b {
        color: #60a5fa !important;
    }
    .workflow-step i {
        color: #cbd5e1 !important;
    }
    .workflow-step code {
        background-color: #334155 !important;
        color: #38bdf8 !important;
        padding: 2px 6px;
        border-radius: 4px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-header'>🛡️ SafeAd AI (SAFE-VISION)</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>A Multimodal Trust and Safety Framework for Early Detection of Harmful Advertisements & Age-Aware Content Moderation</div>", unsafe_allow_html=True)

# Session State Initialization
if "user_token" not in st.session_state:
    st.session_state["user_token"] = None
if "user_id" not in st.session_state:
    st.session_state["user_id"] = 1
if "username" not in st.session_state:
    st.session_state["username"] = "GuestUser"
if "verified_age_group" not in st.session_state:
    st.session_state["verified_age_group"] = "AGE_18_PLUS"

# Sidebar Backend Health Check
st.sidebar.title("SafeAd System Portal")
try:
    health_resp = requests.get(f"{BACKEND_URL.replace('/api/v1', '')}/health", timeout=3)
    if health_resp.status_code == 200:
        st.sidebar.success(f"🟢 Backend Status: Online ({health_resp.json().get('database', 'DB')})")
    else:
        st.sidebar.error("🔴 Backend Error")
except Exception:
    st.sidebar.warning("⚠️ FastAPI Backend Offline! Start backend server on port 8000.")

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Logged In User**: `{st.session_state['username']}`")
st.sidebar.markdown(f"**Verified Age Profile**: `{st.session_state['verified_age_group']}`")
if st.sidebar.button("Log Out"):
    st.session_state["user_token"] = None
    st.session_state["user_id"] = 1
    st.session_state["username"] = "GuestUser"
    st.session_state["verified_age_group"] = "AGE_18_PLUS"
    st.rerun()

tabs = st.tabs([
    "📢 Advertiser Moderation Portal",
    "👤 Registration & Age Verification",
    "📱 Age-Aware Social User Feed",
    "🛡️ Admin Auditing & Policy Control"
])

# =====================================================================
# TAB 1: ADVERTISER PORTAL
# =====================================================================
with tabs[0]:
    st.header("Upload Advertisement Creative for Safety Audit")
    
    col1, col2 = st.columns([1, 1.2])
    
    with col1:
        st.subheader("1. Submission Parameters")
        with st.form("ad_submit_form"):
            ad_title = st.text_input("Creative Title", placeholder="e.g. Grand Casino Offer / Python Coding Tutorial")
            ad_caption = st.text_area("Caption / Copy", placeholder="e.g. Win cash online / Learn programming step by step")
            uploaded_file = st.file_uploader("Upload Creative Media (Image or MP4 Video)", type=["jpg", "jpeg", "png", "mp4"])
            submit_btn = st.form_submit_button("Submit for AI Safety Audit")
            
        if submit_btn:
            if not ad_title or not uploaded_file:
                st.error("Please provide both a Creative Title and upload a media file.")
            else:
                with st.spinner("Executing Multimodal AI Detection Pipeline (OCR + YOLO + BLIP + NLP + FAISS + CoT)..."):
                    try:
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                        data = {"title": ad_title, "caption": ad_caption, "user_id": st.session_state["user_id"]}
                        
                        resp = requests.post(f"{BACKEND_URL}/advertisements/check", files=files, data=data, timeout=90)
                        if resp.status_code == 200:
                            st.session_state["latest_result"] = resp.json()
                            st.success("Safety Audit Completed Successfully!")
                        else:
                            st.error(f"Backend Submission Error: {resp.text}")
                    except Exception as e:
                        st.error(f"Failed to connect to backend API: {e}")

    with col2:
        st.subheader("2. Standardized AI Audit Report & Detection Workflow")
        if "latest_result" in st.session_state:
            res = st.session_state["latest_result"]
            
            classification = res.get("classification", "UNKNOWN")
            action = res.get("action", "REJECT")
            risk_score = res.get("risk_score")
            risk_score_avail = res.get("risk_score_available", False)
            
            # Action Banner
            if action == "APPROVE":
                st.success(f"✅ APPROVED FOR GENERAL AUDIENCE (Classification: {classification})")
            elif action == "RESTRICT":
                st.warning(f"⚠️ AGE RESTRICTED ({res.get('age_restriction', 18)}+ ONLY) (Classification: {classification})")
            else:
                st.error(f"❌ PUBLICATION REJECTED (Classification: {classification})")
                
            # Metrics Row
            mcol1, mcol2, mcol3 = st.columns(3)
            if risk_score_avail and risk_score is not None:
                mcol1.metric("Risk Score", f"{risk_score:.1f}%")
            else:
                mcol1.metric("Risk Score", "N/A")
                
            mcol2.metric("Risk Category", res.get("risk_category", "general"))
            mcol3.metric("Publishable", "Yes" if res.get("publishable") else "No")
            
            # Chain-of-Thought Explanation
            st.markdown("### Chain-of-Thought Explanation")
            st.info(res.get("explanation", "No explanation available."))
            
            if res.get("violations"):
                st.markdown(f"**Policy Infractions Detected**: `{', '.join(res['violations'])}`")
                
            # Multimodal Detection Workflow Visualizer
            st.markdown("---")
            st.markdown("### 🔍 SafeAd AI Multimodal Detection Workflow")
            
            with st.expander("Show Step-by-Step AI Pipeline Detection Workflow", expanded=True):
                st.markdown(f"""
                <div class='workflow-step'>
                    <b>Step 1: Media Ingestion & Sampling</b><br>
                    File validated. Extracted media keyframe / image representation.
                </div>
                <div class='workflow-step'>
                    <b>Step 2: OCR & Speech Transcript Extraction</b><br>
                    Parsed embedded text overlay: <i>"{res.get('extracted_ocr', 'OCR completed')}"</i>
                </div>
                <div class='workflow-step'>
                    <b>Step 3: Visual Feature Analysis (YOLO & BLIP)</b><br>
                    Detected Objects: <code>{', '.join(res.get('detected_objects', ['Object scanning complete']))}</code><br>
                    Generated Visual Caption: <i>"{res.get('generated_caption', 'Visual caption generated')}"</i>
                </div>
                <div class='workflow-step'>
                    <b>Step 4: Multilingual NLP Risk Scoring (English, Hinglish, Manglish)</b><br>
                    Triggered Policy Flags: <code>{', '.join(res.get('violations', ['None']))}</code>
                </div>
                <div class='workflow-step'>
                    <b>Step 5: FAISS Vector Nearest Case Retrieval</b><br>
                    Matched Historical Exemplar: <b>{res.get('faiss_match', {}).get('title', 'Vector Exemplar Index Searched')}</b> 
                    (Distance: {res.get('faiss_match', {}).get('distance', 0.0)})
                </div>
                <div class='workflow-step'>
                    <b>Step 6: Policy Engine & Final Classification</b><br>
                    Mapped Target Classification: <b>{classification}</b> | Platform Action: <b>{action}</b>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Submit an advertisement on the left panel to run the safety pipeline and view the workflow.")

# =====================================================================
# TAB 2: USER REGISTRATION & AGE VERIFICATION
# =====================================================================
with tabs[1]:
    st.header("User Authentication & Age Verification System")
    
    col_reg1, col_reg2 = st.columns([1, 1])
    
    with col_reg1:
        st.subheader("1. Register New User Account")
        reg_username = st.text_input("Username", value="alice_user")
        reg_email = st.text_input("Email Address", value="alice@example.com")
        reg_password = st.text_input("Password", value="password123", type="password")
        
        # Default date set to 1999-05-15 (Adult age 27)
        import datetime
        reg_dob = st.date_input("Date of Birth", value=datetime.date(1999, 5, 15), min_value=datetime.date(1940, 1, 1), max_value=datetime.date(2025, 1, 1))
        
        st.markdown("#### Facial Verification Scan Options")
        face_scan_profile = st.selectbox(
            "Select Face Scan Verification Profile",
            ["Adult Profile (18+ Oval Face Scan)", "Child Profile (< 14 Round Face Scan)", "Use Live Webcam Camera"]
        )
        
        cam_image = None
        if face_scan_profile == "Use Live Webcam Camera":
            cam_image = st.camera_input("Capture Profile Face Photo")
            
        if st.button("Register Account & Verify Age Profile"):
            if not reg_username or not reg_email or not reg_password:
                st.error("Please fill in all registration fields.")
            else:
                try:
                    payload = {
                        "username": reg_username,
                        "email": reg_email,
                        "password": reg_password,
                        "date_of_birth": str(reg_dob)
                    }
                    resp = requests.post(f"{BACKEND_URL}/auth/register", json=payload, timeout=10)
                    if resp.status_code == 200:
                        user_data = resp.json()
                        st.session_state["user_id"] = user_data["id"]
                        st.session_state["username"] = user_data["username"]
                        st.session_state["verified_age_group"] = user_data.get("verified_age_group", "AGE_18_PLUS")
                        st.success(f"Registered successfully! User: **{user_data['username']}** | Verified Age Category: **{st.session_state['verified_age_group']}**")
                        st.rerun()
                    else:
                        st.error(f"Registration Error: {resp.text}")
                except Exception as e:
                    st.error(f"API Connection Failure: {e}")

    with col_reg2:
        st.subheader("2. Login to Account")
        login_user = st.text_input("Login Username", value="alice_user")
        login_pass = st.text_input("Login Password", value="password123", type="password")
        
        if st.button("Login"):
            if not login_user or not login_pass:
                st.error("Please enter username and password.")
            else:
                try:
                    resp = requests.post(f"{BACKEND_URL}/auth/login", json={"username": login_user, "password": login_pass}, timeout=10)
                    if resp.status_code == 200:
                        token_data = resp.json()
                        st.session_state["user_token"] = token_data["access_token"]
                        st.session_state["user_id"] = token_data["user_id"]
                        st.session_state["username"] = token_data["username"]
                        st.session_state["verified_age_group"] = token_data["verified_age_group"]
                        st.success(f"Welcome back, **{token_data['username']}**! Stored Verified Age Profile: **{token_data['verified_age_group']}**")
                        st.rerun()
                    else:
                        st.error("Invalid username or password. Please verify credentials.")
                except Exception as e:
                    st.error(f"Login Failure: {e}")

# =====================================================================
# TAB 3: AGE-AWARE SOCIAL USER FEED
# =====================================================================
with tabs[2]:
    st.header("Personalized Social Media Feed (Age-Aware Delivery)")
    st.markdown(f"Current Viewer Profile: **{st.session_state['username']}** | Verified Age Category: **{st.session_state['verified_age_group']}**")
    
    col_f1, col_f2 = st.columns([1, 4])
    with col_f1:
        if st.button("🔄 Refresh Social Feed"):
            st.rerun()
            
    with col_f2:
        st.info("Policy Protection Active: Ads classified as 'UNSAFE_FOR_ALL' are NEVER displayed to any user. Minors (< 18) only receive safe content.")

    try:
        resp = requests.get(f"{BACKEND_URL}/advertisements/user_feed?user_age_group={st.session_state['verified_age_group']}", timeout=10)
        if resp.status_code == 200:
            feed_items = resp.json()
            
            if not feed_items:
                st.info("No advertisements currently eligible for your age profile.")
            else:
                for item in feed_items:
                    with st.container():
                        st.markdown(f"### 📢 {item['title']}")
                        if item.get("caption"):
                            st.write(item["caption"])
                            
                        rating_badge = "General Audience" if item['classification'] == "SAFE_FOR_ALL" else f"{item.get('age_restriction', 18)}+ Only"
                        st.caption(f"Safety Tag: `{item['classification']}` | Rating: `{rating_badge}`")
                        
                        fpath = item.get("file_path", "")
                        if os.path.exists(fpath):
                            if fpath.lower().endswith(".mp4"):
                                st.video(fpath)
                            else:
                                st.image(fpath, width=450)
                        st.markdown("---")
        else:
            st.error(f"Error retrieving feed: {resp.text}")
    except Exception as e:
        st.error(f"Could not connect to FastAPI Backend: {e}")

# =====================================================================
# TAB 4: ADMIN AUDITING & POLICY CONTROL
# =====================================================================
with tabs[3]:
    st.header("Admin Policy Control & Audit Panel")
    
    admin_sub_tabs = st.tabs(["Pending Human Review Queue", "System Audit Logs"])
    
    with admin_sub_tabs[0]:
        try:
            resp = requests.get(f"{BACKEND_URL}/admin/pending", timeout=10)
            if resp.status_code == 200:
                pending_list = resp.json()
                if not pending_list:
                    st.success("No advertisements currently holding for manual human review.")
                else:
                    for ad in pending_list:
                        with st.expander(f"Review Ad ID #{ad['id']}: '{ad['title']}' (Status: {ad['status']})"):
                            col_a, col_b = st.columns([1, 1])
                            with col_a:
                                if os.path.exists(ad['file_path']):
                                    if ad['file_path'].lower().endswith(".mp4"):
                                        st.video(ad['file_path'])
                                    else:
                                        st.image(ad['file_path'], width=300)
                            with col_b:
                                st.markdown(f"**Title**: {ad['title']}")
                                st.markdown(f"**Caption**: {ad['caption']}")
                                st.markdown(f"**AI Reason**: *{ad['explanation']}*")
                                
                                notes = st.text_input("Override Notes", key=f"notes_{ad['id']}")
                                
                                ocol1, ocol2, ocol3 = st.columns(3)
                                if ocol1.button("✅ Approve", key=f"app_{ad['id']}"):
                                    requests.post(f"{BACKEND_URL}/admin/override", json={"ad_id": ad['id'], "action": "APPROVE", "notes": notes})
                                    st.success("Approved!")
                                    st.rerun()
                                if ocol2.button("⚠️ Age Restrict", key=f"rest_{ad['id']}"):
                                    requests.post(f"{BACKEND_URL}/admin/override", json={"ad_id": ad['id'], "action": "RESTRICT", "notes": notes})
                                    st.warning("Restricted!")
                                    st.rerun()
                                if ocol3.button("❌ Reject", key=f"rej_{ad['id']}"):
                                    requests.post(f"{BACKEND_URL}/admin/override", json={"ad_id": ad['id'], "action": "REJECT", "notes": notes})
                                    st.error("Rejected!")
                                    st.rerun()
        except Exception as e:
            st.error(f"Failed to fetch review queue: {e}")

    with admin_sub_tabs[1]:
        try:
            resp = requests.get(f"{BACKEND_URL}/moderation/logs", timeout=10)
            if resp.status_code == 200:
                logs = resp.json()
                st.dataframe(logs, use_container_width=True)
            else:
                st.error("Could not fetch audit logs.")
        except Exception as e:
            st.error(f"Audit log query error: {e}")
