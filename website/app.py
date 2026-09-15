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
from website.pipeline import run_multimodal_moderation, MULTILINGUAL_KEYWORDS
from website.classifier import estimate_age_from_face, estimate_detailed_age_from_face, estimate_age_from_behavior, detect_and_crop_face

init_database()

st.set_page_config(page_title="SafeAd AI: Trust & Safety Framework", layout="wide", page_icon="🛡️")

st.markdown("""
    <style>
    .main-title {
        font-size: 38px;
        color: #1e3a8a;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2px;
    }
    .subtitle {
        font-size: 16px;
        color: #4b5563;
        text-align: center;
        margin-bottom: 25px;
    }
    .metric-box {
        background-color: #f3f4f6;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        border: 1px solid #e5e7eb;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-title'>SafeAd AI (SAFE-VISION)</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Multimodal Trust & Safety Framework & MTCNN + ViT Deep Learning Face Age Estimation</div>", unsafe_allow_html=True)

# Navigation Tabs
tabs = st.tabs([
    "👤 Facial & Behavioral Age Classifier",
    "📢 Advertiser Portal",
    "🛡️ Admin Auditing Dashboard",
    "📱 Social User Feed (Age-Aware)"
])

# =====================================================================
# TAB 1: FACIAL & BEHAVIORAL AGE ESTIMATION FRAMEWORK
# =====================================================================
with tabs[0]:
    st.header("👤 Face Age Estimation & Behavioral Profiling System")
    st.markdown("Early detection of age categories (Child vs. Not a Child / Adult) using MTCNN face detection and HuggingFace ViT age classification.")
    
    sub_tab1, sub_tab2 = st.tabs(["📸 Facial Age Classifier (MTCNN + ViT)", "📊 Behavioral Age Classifier"])
    
    with sub_tab1:
        st.subheader("Facial Age Classification")
        input_type = st.radio("Select Input Method:", ["Use Webcam Camera", "Upload Image File", "Simulated Face Preset"], key="tab1_input_type")
        
        image_np = None
        
        if input_type == "Use Webcam Camera":
            cam_image = st.camera_input("Capture Profile Face Photo", key="tab1_webcam")
            if cam_image is not None:
                image = Image.open(cam_image).convert("RGB")
                image_np = np.array(image)
                
        elif input_type == "Upload Image File":
            uploaded_file = st.file_uploader("Choose a photo with a face...", type=["jpg", "jpeg", "png"], key="tab1_file")
            if uploaded_file is not None:
                image = Image.open(uploaded_file).convert("RGB")
                image_np = np.array(image)
                
        elif input_type == "Simulated Face Preset":
            face_choice = st.selectbox("Select Preset Face Profile", ["Child Face (Round)", "Adult Face (Oval)"], key="tab1_preset")
            dummy_face = np.ones((128, 128, 3), dtype=np.uint8) * 240
            if face_choice == "Child Face (Round)":
                cv2.ellipse(dummy_face, (64, 64), (45, 45), 0, 0, 360, (255, 200, 180), -1)
                cv2.circle(dummy_face, (49, 69), 7, (40, 40, 40), -1)
                cv2.circle(dummy_face, (79, 69), 7, (40, 40, 40), -1)
            else:
                cv2.ellipse(dummy_face, (64, 64), (36, 54), 0, 0, 360, (245, 190, 160), -1)
                cv2.circle(dummy_face, (49, 54), 4, (40, 40, 40), -1)
                cv2.circle(dummy_face, (79, 54), 4, (40, 40, 40), -1)
            image_np = dummy_face
            
        if image_np is not None:
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Original Input Image")
                st.image(image_np, width=350)
                
            with col2:
                st.subheader("Face Detection & ViT Age Analysis")
                cropped_face, bbox = detect_and_crop_face(image_np)
                
                st.image(cropped_face, width=160, caption="Cropped 128x128 Face")
                if bbox is not None:
                    st.caption(f"Bounding Box Coordinates: `{bbox}`")
                
                detailed = estimate_detailed_age_from_face(image_np)
                age_range = detailed["age_range"]
                norm_group = detailed["normalized_group"]
                confidence = detailed["confidence"]
                category = detailed["category"]
                
                st.markdown("### 📊 ViT Age Prediction Results")
                st.info(f"🎯 **Predicted Age Range**: **{age_range}**")
                
                if category == "Child":
                    st.warning(f"🏷️ **Category**: **{norm_group}** (`Child Profile`)")
                else:
                    st.success(f"🏷️ **Category**: **{norm_group}** (`Adult / Non-Child Profile`)")
                    
                st.metric("ViT Model Confidence", f"{confidence:.1%}")
                st.progress(float(confidence))
                
                if detailed.get("pipeline_result"):
                    with st.expander("🔍 View Raw Pipeline JSON Output"):
                        st.json(detailed["pipeline_result"])

        st.markdown("---")
        st.markdown("### 🎥 Open Live Desktop Camera Window")
        st.caption("Click below to open the real-time OpenCV window (`camera_app.py`) for live bounding box drawing and continuous webcam age detection.")
        if st.button("Launch Desktop OpenCV Camera Window"):
            try:
                subprocess.Popen([sys.executable, "camera_app.py"])
                st.success("OpenCV Camera Window opened! Check your desktop window.")
            except Exception as e:
                st.error(f"Error launching camera window: {e}")

    with sub_tab2:
        st.header("Behavioral Age Profiling")
        st.markdown("Analyze user search queries and reel watch duration to classify age group.")
        
        search_queries = st.text_input("Enter Search Queries (comma-separated):", "minecraft speedrun, cartoon videos, fun games", key="tab1_queries")
        gk_watch = st.slider("Educational / GK Video Watch Time (seconds):", 0, 60, 45, key="tab1_gk")
        adult_watch = st.slider("Adult / Ad Video Watch Time (seconds):", 0, 100, 10, key="tab1_adult")
        
        if st.button("Run Behavioral Classification", key="tab1_beh_btn"):
            queries_list = [q.strip() for q in search_queries.split(",") if q.strip()]
            gk_watches = [{"duration_watched": gk_watch, "total_duration": 60}]
            adult_watches = [{"duration_watched": adult_watch, "total_duration": 100}]
            
            category, confidence = estimate_age_from_behavior(queries_list, gk_watches, adult_watches)
            
            st.subheader("Behavioral Analysis Results")
            if category == "Child":
                st.warning(f"🚨 Predicted Category: **{category}**")
            else:
                st.success(f"✅ Predicted Category: **{category}**")
                
            st.metric("Child Behavioral Score", f"{confidence:.1%}")
            st.progress(float(confidence))

# =====================================================================
# TAB 2: ADVERTISER PORTAL
# =====================================================================
with tabs[1]:
    st.header("Upload & Moderate Advertisements")
    
    col1, col2 = st.columns([1, 1.2])
    
    with col1:
        st.subheader("Ad Campaign Parameters")
        with st.form("ad_upload_form", clear_on_submit=False):
            title = st.text_input("Ad Title", "Mega Jackpot Offer")
            caption = st.text_input("Ad Caption/Description", "Earn cash fast! Satta khelne ke liye link pe click karein.")
            uploaded_file = st.file_uploader("Upload Ad Media (Image/Video)", type=["png", "jpg", "jpeg", "mp4"])
            submit_btn = st.form_submit_button("Submit for Moderation")
            
        if submit_btn:
            if not uploaded_file:
                st.error("Please upload a media file.")
            else:
                # Save uploaded file locally
                os.makedirs("website/uploads", exist_ok=True)
                file_path = os.path.join("website/uploads", uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                    
                # Insert into DB
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO Advertisements (title, advertiser_id, caption, file_path, status)
                    VALUES (?, 1, ?, ?, 'under_review')
                """, (title, caption, file_path))
                ad_id = cursor.lastrowid
                conn.commit()
                conn.close()
                
                # Execute moderation pipeline
                with st.spinner("Processing multimodal safety indicators (Vision + OCR + Speech)..."):
                    res = run_multimodal_moderation(ad_id)
                    time.sleep(0.5)
                    
                st.session_state["latest_mod"] = res
                st.success(f"Ad Campaign submitted successfully! Mod ID: {ad_id}")

    with col2:
        st.subheader("Real-time Safety Audit Report")
        if "latest_mod" in st.session_state:
            res = st.session_state["latest_mod"]
            
            status_color = "#10b981" if res["status"] == "approved" else "#ef4444" if res["status"] == "rejected" else "#f59e0b"
            st.markdown(f"### Status: <span style='color:{status_color}; font-weight:bold;'>{res['status'].upper()}</span>", unsafe_allow_html=True)
            
            # Metric Columns
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Overall Risk Score", f"{res['final_score']:.2f}")
            m2.metric("Visual Risk", f"{res['visual_score']:.2f}")
            m3.metric("NLP / OCR Risk", f"{res['ocr_score']:.2f}")
            m4.metric("Speech Risk", f"{res['speech_score']:.2f}")
            
            st.markdown("---")
            st.markdown("### Modality-specific Findings")
            st.write(f"**Violated Policies**: {', '.join(res['violations']) if res['violations'] else 'None'}")
            st.info(f"**Explainable AI Reason**: {res['explanation']}")
            
            # Display uploaded media safely
            media_path = res.get("file_path", "")
            if media_path and os.path.exists(media_path):
                st.markdown("### Uploaded Creative Preview")
                if media_path.lower().endswith('.mp4'):
                    st.video(media_path)
                else:
                    st.image(media_path, width=300)
            elif media_path:
                st.info(f"Uploaded Media Path: `{media_path}`")
        else:
            st.info("Upload an advertisement and submit to see audit predictions here.")

# =====================================================================
# TAB 3: ADMIN AUDITING DASHBOARD
# =====================================================================
with tabs[2]:
    st.header("Admin Policy & Audit Panel")
    
    adm_tab1, adm_tab2 = st.tabs(["Pending Human Review Queue", "Configure Policy Rules"])
    
    with adm_tab1:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, caption, file_path, status, created_at 
            FROM Advertisements 
            WHERE status = 'under_review'
        """)
        pending_ads = cursor.fetchall()
        conn.close()
        
        if not pending_ads:
            st.success("Human review queue is currently empty!")
        else:
            st.write(f"Found {len(pending_ads)} advertisements holding for manual audit:")
            
            for ad in pending_ads:
                ad_id, ad_title, ad_caption, ad_file_path, ad_status, ad_time = ad
                
                with st.expander(f"Review ID {ad_id}: '{ad_title}' (Submitted {ad_time})"):
                    col_a, col_b = st.columns([1, 1.2])
                    
                    with col_a:
                        if ad_file_path and os.path.exists(ad_file_path):
                            if ad_file_path.lower().endswith('.mp4'):
                                st.video(ad_file_path)
                            else:
                                st.image(ad_file_path, width=250)
                        else:
                            st.info(f"Ad File: `{ad_file_path}` (No preview available)")
                            
                    with col_b:
                        conn = get_connection()
                        cursor = conn.cursor()
                        cursor.execute("SELECT final_score, visual_score, ocr_score, speech_score FROM RiskScores WHERE ad_id = ?", (ad_id,))
                        scores = cursor.fetchone()
                        conn.close()
                        
                        if scores:
                            st.write(f"**AI Risk Score**: {scores[0]:.2f} (Visual: {scores[1]:.2f}, OCR: {scores[2]:.2f}, Speech: {scores[3]:.2f})")
                        st.write(f"**Ad Caption**: {ad_caption}")
                        
                        notes = st.text_input("Reviewer Audit Notes", key=f"notes_{ad_id}")
                        action_col1, action_col2, action_col3 = st.columns(3)
                        
                        if action_col1.button("✅ Approve", key=f"app_{ad_id}"):
                            conn = get_connection()
                            cursor = conn.cursor()
                            cursor.execute("UPDATE Advertisements SET status = 'approved' WHERE id = ?", (ad_id,))
                            cursor.execute("INSERT INTO HumanReviews (ad_id, reviewer_id, action, notes) VALUES (?, 2, 'approve', ?)", (ad_id, notes))
                            cursor.execute("INSERT INTO AuditLogs (ad_id, trigger_user_id, model_version, final_decision, log_details) VALUES (?, 2, 'Human_Override', 'approved', ?)", (ad_id, f"Override: Approved. Notes: {notes}"))
                            conn.commit()
                            conn.close()
                            st.success(f"Ad {ad_id} Approved manually!")
                            time.sleep(0.5)
                            st.rerun()
                            
                        if action_col2.button("❌ Reject", key=f"rej_{ad_id}"):
                            conn = get_connection()
                            cursor = conn.cursor()
                            cursor.execute("UPDATE Advertisements SET status = 'rejected' WHERE id = ?", (ad_id,))
                            cursor.execute("INSERT INTO HumanReviews (ad_id, reviewer_id, action, notes) VALUES (?, 2, 'reject', ?)", (ad_id, notes))
                            cursor.execute("INSERT INTO AuditLogs (ad_id, trigger_user_id, model_version, final_decision, log_details) VALUES (?, 2, 'Human_Override', 'rejected', ?)", (ad_id, f"Override: Rejected. Notes: {notes}"))
                            conn.commit()
                            conn.close()
                            st.error(f"Ad {ad_id} Rejected manually!")
                            time.sleep(0.5)
                            st.rerun()
                            
                        if action_col3.button("⚠️ Age-Restrict", key=f"rest_{ad_id}"):
                            conn = get_connection()
                            cursor = conn.cursor()
                            cursor.execute("UPDATE Advertisements SET status = 'approved' WHERE id = ?", (ad_id,))
                            cursor.execute("INSERT INTO HumanReviews (ad_id, reviewer_id, action, notes) VALUES (?, 2, 'restrict', ?)", (ad_id, notes))
                            cursor.execute("INSERT INTO AuditLogs (ad_id, trigger_user_id, model_version, final_decision, log_details) VALUES (?, 2, 'Human_Override', 'restricted_18', ?)", (ad_id, f"Override: Restricted to Adults (18+). Notes: {notes}"))
                            conn.commit()
                            conn.close()
                            st.warning(f"Ad {ad_id} marked as Age-Restricted (18+)!")
                            time.sleep(0.5)
                            st.rerun()
                            
    with adm_tab2:
        st.subheader("Edit Safety Policies")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, description, age_restriction FROM PolicyRules")
        policies = cursor.fetchall()
        conn.close()
        
        dict_p = [{"ID": p[0], "Policy Name": p[1], "Description": p[2], "Min Age Allowed": p[3]} for p in policies]
        st.dataframe(dict_p, use_container_width=True)

# =====================================================================
# TAB 4: SOCIAL USER FEED (AGE-AWARE DELIVERY SIMULATION)
# =====================================================================
with tabs[3]:
    st.header("Simulated Social User Reels Feed")
    
    col_u1, col_u2 = st.columns([1.2, 2])
    
    with col_u1:
        st.subheader("1. User Profile Setup")
        username = st.text_input("Social User Handle", "guest_user", key="tab4_username")
        
        auth_mode = st.radio("Age Assessment Method", ["Facial Verification Camera Scan", "Behavioral History Tracker"], key="tab4_auth")
        
        user_category = "Not a Child"
        user_confidence = 1.0
        
        if auth_mode == "Facial Verification Camera Scan":
            st.info("Snap or upload a face photo to verify your age category using MTCNN + ViT deep learning age estimation.")
            input_mode = st.radio("Choose Input Method:", ["Live Webcam Camera", "Upload Image File", "Simulated Preset Profile"], key="tab4_face_mode")
            
            image_np = None
            if input_mode == "Live Webcam Camera":
                cam_image = st.camera_input("Capture Profile Face Photo", key="tab4_cam_input")
                if cam_image:
                    image_np = np.array(Image.open(cam_image).convert("RGB"))
            elif input_mode == "Upload Image File":
                uploaded = st.file_uploader("Upload Profile Image", type=["jpg", "jpeg", "png"], key="tab4_file_upload")
                if uploaded:
                    image_np = np.array(Image.open(uploaded).convert("RGB"))
            else:
                face_sim = st.selectbox("Simulate Face Profile Camera Input", ["Round Baby Face (Child Profile)", "Oval Face (Adult Profile)"], key="tab4_sim")
                dummy_img = np.ones((128, 128, 3), dtype=np.uint8) * 240
                if face_sim == "Round Baby Face (Child Profile)":
                    cv2.ellipse(dummy_img, (64, 64), (45, 45), 0, 0, 360, (255, 200, 180), -1)
                    cv2.circle(dummy_img, (49, 69), 7, (40, 40, 40), -1)
                    cv2.circle(dummy_img, (79, 69), 7, (40, 40, 40), -1)
                else:
                    cv2.ellipse(dummy_img, (64, 64), (36, 54), 0, 0, 360, (245, 190, 160), -1)
                    cv2.circle(dummy_img, (49, 54), 4, (40, 40, 40), -1)
                    cv2.circle(dummy_img, (79, 54), 4, (40, 40, 40), -1)
                image_np = dummy_img
                
            if image_np is not None:
                st.image(image_np, width=160, caption="Input Face")
                user_category, user_confidence = estimate_age_from_face(image_np)
            else:
                user_category, user_confidence = "Not a Child", 1.0
            
        else:
            st.info("Track age dynamically from recent searches & watch traces.")
            search_input = st.text_area("Recent User Search Terms (comma separated)", "minecraft speedrun, cartoon videos, school drawing", key="tab4_search")
            gk_retention = st.slider("GK/Educational Video Retention Ratio", 0.0, 1.0, 0.90, key="tab4_gk_ret")
            adult_retention = st.slider("Adult/Gambling Video Retention Ratio", 0.0, 1.0, 0.05, key="tab4_ad_ret")
            
            queries_list = [q.strip() for q in search_input.split(",")]
            gk_watches = [{"duration_watched": gk_retention * 60, "total_duration": 60}]
            adult_watches = [{"duration_watched": adult_retention * 120, "total_duration": 120}]
            
            user_category, user_confidence = estimate_age_from_behavior(queries_list, gk_watches, adult_watches)
            
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM Users WHERE username = ?", (username,))
        usr = cursor.fetchone()
        if usr:
            cursor.execute("""
                INSERT INTO AgeProfiles (user_id, method, prediction_class, confidence)
                VALUES (?, ?, ?, ?)
            """, (usr[0], "facial" if auth_mode == "Facial Verification Camera Scan" else "behavioral", user_category, user_confidence))
            conn.commit()
        conn.close()
        
        st.markdown("---")
        st.markdown("### 📊 Active Profile Classification")
        if user_category == "Child":
            st.error(f"🚨 **PROFILE CLASSIFIED AS CHILD** (Score: {user_confidence:.1%})")
            st.warning("Age-Restricted Advertisements (Gambling, Alcohol, Adult content) will be blocked from your feed.")
        else:
            st.success(f"✅ **PROFILE CLASSIFIED AS ADULT / NON-CHILD** (Score: {user_confidence:.1%})")
            st.info("Standard ad delivery active.")

    with col_u2:
        st.subheader("2. Age-Filtered Feed Output")
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, caption, file_path, status FROM Advertisements WHERE status = 'approved'")
        approved_ads = cursor.fetchall()
        
        GK_REELS = [
            {"title": "Fun Science: Why is the Sky Blue?", "topic": "Physics for Kids", "desc": "Light scattering explanation in simple words."},
            {"title": "Quick Math Trick: Multiply by 11", "topic": "Educational Math", "desc": "Easy mental math trick for school students."},
            {"title": "Space Exploration: Mars Rover Discoveries", "topic": "Astronomy", "desc": "What Perseverance found on the Red Planet."}
        ]
        
        feed_items = []
        
        if user_category == "Child":
            st.caption("🔒 Filtered Mode: Restricted Ads are omitted from feed.")
            for ad in approved_ads:
                ad_id, ad_title, ad_caption, ad_file_path, status = ad
                cursor.execute("SELECT final_decision FROM AuditLogs WHERE ad_id = ? ORDER BY id DESC LIMIT 1", (ad_id,))
                log = cursor.fetchone()
                is_restricted = (log and log[0] == 'restricted_18') or any(kw in (ad_title + " " + ad_caption).lower() for kw in ['casino', 'betting', 'gambling', 'satta', 'alcohol', 'poker'])
                
                if not is_restricted:
                    feed_items.append({"title": f"[Safe Ad] {ad_title}", "desc": ad_caption, "file": ad_file_path, "gk": False})
                    
            for gk in GK_REELS:
                feed_items.append({"title": f"[GK Reel] {gk['title']}", "desc": f"Topic: {gk['topic']} - {gk['desc']}", "file": None, "gk": True})
        else:
            st.success("Adult Feed Active. Delivery includes general and age-appropriate advertisements.")
            for ad in approved_ads:
                ad_id, ad_title, ad_caption, ad_file_path, status = ad
                feed_items.append({"title": f"[Ad Campaign] {ad_title}", "desc": ad_caption, "file": ad_file_path, "gk": False})
            for gk in GK_REELS:
                feed_items.append({"title": f"[GK Reel] {gk['title']}", "desc": f"Topic: {gk['topic']} - {gk['desc']}", "file": None, "gk": True})
                
        conn.close()
        
        if not feed_items:
            st.info("No content available for your feed profile.")
        else:
            for idx, item in enumerate(feed_items):
                with st.chat_message("user" if item["gk"] else "assistant"):
                    st.markdown(f"### {item['title']}")
                    st.write(item["desc"])
                    
                    if not item["gk"] and item["file"]:
                        if os.path.exists(item["file"]):
                            if item["file"].lower().endswith('.mp4'):
                                st.video(item["file"])
                            else:
                                st.image(item["file"], width=200)
                        else:
                            st.info(f"Ad Creative: `{item['file']}`")

# =====================================================================
# SYSTEM AUDIT LOG VIEWER (PERSISTENT ON BOTTOM)
# =====================================================================
st.markdown("---")
st.subheader("🛡️ Unified SafeAd AI Audit Logs")
conn = get_connection()
cursor = conn.cursor()
cursor.execute("SELECT id, ad_id, timestamp, model_version, final_decision, log_details FROM AuditLogs ORDER BY id DESC LIMIT 10")
logs = cursor.fetchall()
conn.close()

if logs:
    dict_l = [{"Log ID": l[0], "Ad ID": l[1], "Timestamp": l[2], "Framework Version": l[3], "Decision": l[4], "AI Audit Notes": l[5]} for l in logs]
    st.dataframe(dict_l, use_container_width=True)
else:
    st.caption("No audit logs recorded yet.")
