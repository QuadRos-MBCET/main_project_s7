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

# Set page config
st.set_page_config(
    page_title="SafeAd AI — Trust & Safety Platform",
    layout="wide",
    page_icon="🛡️",
    initial_sidebar_state="collapsed"
)

# Custom Glassmorphic & Modern Modern CSS
st.markdown("""
    <style>
    /* Global Styles & Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Hero Header */
    .hero-container {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 40%, #4338ca 100%);
        border-radius: 16px;
        padding: 28px 36px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(49, 46, 129, 0.3);
    }
    .hero-title {
        font-size: 32px;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
        color: #ffffff;
    }
    .hero-subtitle {
        font-size: 15px;
        color: #c7d2fe;
        margin-top: 6px;
        font-weight: 400;
    }

    /* Cards & Containers */
    .card {
        background: #ffffff;
        border: 1px solid #e0e7ff;
        border-radius: 14px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
        margin-bottom: 20px;
    }
    
    /* Result Badges */
    .badge {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 13px;
        letter-spacing: 0.3px;
    }
    .badge-child {
        background-color: #fef2f2;
        color: #dc2626;
        border: 1px solid #fecaca;
    }
    .badge-adult {
        background-color: #ecfdf5;
        color: #059669;
        border: 1px solid #a7f3d0;
    }
    .badge-teen {
        background-color: #eff6ff;
        color: #2563eb;
        border: 1px solid #bfdbfe;
    }
    
    /* Metric Cards */
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
    
    /* Hide empty padding */
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Top Hero Section
st.markdown("""
    <div class="hero-container">
        <div class="hero-title">🛡️ SafeAd AI</div>
        <div class="hero-subtitle">Multimodal Content Moderation & AI Face Age Estimation Platform</div>
    </div>
""", unsafe_allow_html=True)

# Main Navigation Tabs
tabs = st.tabs([
    "👤 Age Verification",
    "📢 Advertiser Portal",
    "🛡️ Admin Audit Panel",
    "📱 Social Reels Feed"
])

# =====================================================================
# TAB 1: FACIAL & BEHAVIORAL AGE ESTIMATION
# =====================================================================
with tabs[0]:
    st.subheader("Facial & Behavioral Age Estimation")
    
    sub_tab1, sub_tab2 = st.tabs(["📸 Facial AI Classifier (MTCNN + ViT)", "📊 Behavioral Profiler"])
    
    with sub_tab1:
        c_left, c_right = st.columns([1, 1.1], gap="medium")
        
        with c_left:
            st.markdown("#### 1. Input Face Photo")
            input_type = st.radio(
                "Choose Input Source",
                ["Webcam Snapshot", "Upload Image", "Preset Profile"],
                horizontal=True,
                key="t1_input_type"
            )
            
            image_np = None
            
            if input_type == "Webcam Snapshot":
                cam_img = st.camera_input("Take a photo", key="t1_cam")
                if cam_img:
                    image_np = np.array(Image.open(cam_img).convert("RGB"))
            elif input_type == "Upload Image":
                up_file = st.file_uploader("Upload face photo", type=["jpg", "jpeg", "png"], key="t1_file")
                if up_file:
                    image_np = np.array(Image.open(up_file).convert("RGB"))
            else:
                preset = st.selectbox("Select Preset Face", ["Child Profile (Round)", "Adult Profile (Oval)"], key="t1_preset")
                dummy = np.ones((128, 128, 3), dtype=np.uint8) * 240
                if preset == "Child Profile (Round)":
                    cv2.ellipse(dummy, (64, 64), (45, 45), 0, 0, 360, (255, 200, 180), -1)
                    cv2.circle(dummy, (49, 69), 7, (40, 40, 40), -1)
                    cv2.circle(dummy, (79, 69), 7, (40, 40, 40), -1)
                else:
                    cv2.ellipse(dummy, (64, 64), (36, 54), 0, 0, 360, (245, 190, 160), -1)
                    cv2.circle(dummy, (49, 54), 4, (40, 40, 40), -1)
                    cv2.circle(dummy, (79, 54), 4, (40, 40, 40), -1)
                image_np = dummy
                
            if image_np is not None:
                st.image(image_np, caption="Input Image", use_container_width=True)
                
        with c_right:
            st.markdown("#### 2. AI Verdict & Face Detection")
            if image_np is not None:
                cropped_face, bbox = detect_and_crop_face(image_np)
                detailed = estimate_detailed_age_from_face(image_np)
                
                age_range = detailed["age_range"]
                norm_group = detailed["normalized_group"]
                confidence = detailed["confidence"]
                category = detailed["category"]
                
                # Render Clean Verdict Box
                if category == "Less than 14":
                    b_class = "badge-child"
                    b_icon = "🚨"
                elif category == "14 to 17":
                    b_class = "badge-teen"
                    b_icon = "⚠️"
                else:
                    b_class = "badge-adult"
                    b_icon = "✅"
                
                st.markdown(f"""
                <div style="background-color:#f8fafc; padding:18px; border-radius:12px; border:1px solid #e2e8f0; margin-bottom:16px;">
                    <div style="display:flex; justify-between; align-items:center;">
                        <span style="font-size:18px; font-weight:700; color:#1e293b;">ViT Age Group: {age_range} years</span>
                        <span class="badge {b_class}">{b_icon} {category}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Face Crop & Confidence Side-by-Side
                fc1, fc2 = st.columns([1, 2])
                with fc1:
                    st.image(cropped_face, caption="Cropped Face (128x128)", width=130)
                with fc2:
                    st.markdown(f"**Model Confidence Score**: `{confidence:.1%}`")
                    st.progress(float(confidence))
                    if bbox is not None:
                        st.caption(f"Bounding Box: `{bbox}`")
                
                if detailed.get("pipeline_result"):
                    with st.expander("🔍 Detailed ViT Probabilities & Raw Data"):
                        st.json(detailed["pipeline_result"])
            else:
                st.info("👈 Snap or upload a photo to perform facial age estimation.")
                
        # Optional Desktop OpenCV Camera Launcher
        with st.expander("🎥 Open Real-Time Desktop Camera Window (OpenCV)"):
            st.caption("Launches the standalone OpenCV python window for real-time bounding boxes.")
            if st.button("Launch Desktop OpenCV Camera App"):
                try:
                    subprocess.Popen([sys.executable, "camera_app.py"])
                    st.success("OpenCV Camera Window opened on your desktop!")
                except Exception as e:
                    st.error(f"Error launching desktop camera window: {e}")

    with sub_tab2:
        st.markdown("#### Behavioral Profile Analysis")
        b_col1, b_col2 = st.columns(2)
        with b_col1:
            search_queries = st.text_input("Recent Search Terms", "minecraft speedrun, cartoon videos, fun games", key="t1_queries")
            gk_watch = st.slider("Educational / GK Watch Time (s)", 0, 60, 45, key="t1_gk")
            adult_watch = st.slider("Adult / Ad Watch Time (s)", 0, 100, 10, key="t1_adult")
            
            if st.button("Analyze Behavioral Pattern", key="t1_beh_btn"):
                queries_list = [q.strip() for q in search_queries.split(",") if q.strip()]
                gk_watches = [{"duration_watched": gk_watch, "total_duration": 60}]
                adult_watches = [{"duration_watched": adult_watch, "total_duration": 100}]
                
                category, confidence = estimate_age_from_behavior(queries_list, gk_watches, adult_watches)
                st.session_state["beh_res"] = (category, confidence)
                
        with b_col2:
            if "beh_res" in st.session_state:
                cat, conf = st.session_state["beh_res"]
                st.markdown("#### Behavioral Score Verdict")
                if cat == "Child":
                    st.warning(f"🚨 **Behavior Profile**: **{cat}** (Confidence: {conf:.1%})")
                else:
                    st.success(f"✅ **Behavior Profile**: **{cat}** (Confidence: {conf:.1%})")
                st.progress(float(conf))
            else:
                st.info("Fill out user behavior traits to estimate age profile.")

# =====================================================================
# TAB 2: ADVERTISER PORTAL
# =====================================================================
with tabs[1]:
    st.subheader("Ad Campaign Submission & Multimodal Safety Audit")
    
    col_ad1, col_ad2 = st.columns([1, 1.2], gap="medium")
    
    with col_ad1:
        st.markdown("#### Submit Ad Creative")
        with st.form("ad_form", clear_on_submit=False):
            title = st.text_input("Campaign Title", "Mega Jackpot Offer")
            caption = st.text_area("Caption & Keywords", "Earn cash fast! Satta khelne ke liye link pe click karein.", height=80)
            up_media = st.file_uploader("Upload Creative (Image / Video)", type=["png", "jpg", "jpeg", "mp4"])
            submit_ad = st.form_submit_button("Run Multimodal Audit", use_container_width=True)
            
        if submit_ad:
            if not up_media:
                st.error("Please select a media file.")
            else:
                os.makedirs("website/uploads", exist_ok=True)
                fpath = os.path.join("website/uploads", up_media.name)
                with open(fpath, "wb") as f:
                    f.write(up_media.getbuffer())
                    
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO Advertisements (title, advertiser_id, caption, file_path, status) VALUES (?, 1, ?, ?, 'under_review')", (title, caption, fpath))
                ad_id = cursor.lastrowid
                conn.commit()
                conn.close()
                
                with st.spinner("Analyzing Visual (MobileNet), OCR Text, and Speech Audio..."):
                    res = run_multimodal_moderation(ad_id)
                    time.sleep(0.4)
                st.session_state["latest_mod"] = res
                st.success(f"Ad Campaign #{ad_id} processed!")

    with col_ad2:
        st.markdown("#### Audit Results")
        if "latest_mod" in st.session_state:
            res = st.session_state["latest_mod"]
            st_status = res["status"].upper()
            status_color = "#059669" if res["status"] == "approved" else "#dc2626" if res["status"] == "rejected" else "#d97706"
            
            st.markdown(f"### Status: <span style='color:{status_color}; font-weight:700;'>{st_status}</span>", unsafe_allow_html=True)
            
            # Risk Gauge Cards
            m1, m2, m3, m4 = st.columns(4)
            m1.markdown(f"<div class='metric-card'><div class='metric-val'>{res['final_score']:.2f}</div><div class='metric-lbl'>Overall Risk</div></div>", unsafe_allow_html=True)
            m2.markdown(f"<div class='metric-card'><div class='metric-val'>{res['visual_score']:.2f}</div><div class='metric-lbl'>Visual Risk</div></div>", unsafe_allow_html=True)
            m3.markdown(f"<div class='metric-card'><div class='metric-val'>{res['ocr_score']:.2f}</div><div class='metric-lbl'>OCR Risk</div></div>", unsafe_allow_html=True)
            m4.markdown(f"<div class='metric-card'><div class='metric-val'>{res['speech_score']:.2f}</div><div class='metric-lbl'>Speech Risk</div></div>", unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.info(f"💡 **AI Explainability Note**: {res['explanation']}")
            
            m_path = res.get("file_path", "")
            if m_path and os.path.exists(m_path):
                if m_path.lower().endswith('.mp4'):
                    st.video(m_path)
                else:
                    st.image(m_path, caption="Ad Creative Preview", width=260)
        else:
            st.info("Submit an ad campaign to trigger instant Safety Audit.")

# =====================================================================
# TAB 3: ADMIN AUDIT PANEL
# =====================================================================
with tabs[2]:
    st.subheader("Admin Moderation & Policy Governance")
    
    adm_t1, adm_t2 = st.tabs(["Pending Queue", "Safety Policies"])
    
    with adm_t1:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, caption, file_path, status, created_at FROM Advertisements WHERE status = 'under_review'")
        pending_ads = cursor.fetchall()
        conn.close()
        
        if not pending_ads:
            st.success("✨ Human review queue is clean! No pending items.")
        else:
            for ad in pending_ads:
                ad_id, ad_title, ad_caption, ad_file_path, ad_status, ad_time = ad
                with st.expander(f"Campaign #{ad_id}: '{ad_title}' ({ad_time})"):
                    col_p1, col_p2 = st.columns([1, 1.2])
                    with col_p1:
                        if ad_file_path and os.path.exists(ad_file_path):
                            if ad_file_path.lower().endswith('.mp4'):
                                st.video(ad_file_path)
                            else:
                                st.image(ad_file_path, width=220)
                        else:
                            st.caption(f"Path: `{ad_file_path}`")
                    with col_p2:
                        st.markdown(f"**Caption**: {ad_caption}")
                        notes = st.text_input("Audit Note", key=f"n_{ad_id}")
                        ac1, ac2, ac3 = st.columns(3)
                        
                        if ac1.button("✅ Approve", key=f"ap_{ad_id}"):
                            conn = get_connection()
                            c = conn.cursor()
                            c.execute("UPDATE Advertisements SET status = 'approved' WHERE id = ?", (ad_id,))
                            c.execute("INSERT INTO AuditLogs (ad_id, trigger_user_id, model_version, final_decision, log_details) VALUES (?, 2, 'Human_Override', 'approved', ?)", (ad_id, f"Approved: {notes}"))
                            conn.commit()
                            conn.close()
                            st.success(f"Ad #{ad_id} Approved")
                            time.sleep(0.3)
                            st.rerun()
                            
                        if ac2.button("❌ Reject", key=f"rj_{ad_id}"):
                            conn = get_connection()
                            c = conn.cursor()
                            c.execute("UPDATE Advertisements SET status = 'rejected' WHERE id = ?", (ad_id,))
                            c.execute("INSERT INTO AuditLogs (ad_id, trigger_user_id, model_version, final_decision, log_details) VALUES (?, 2, 'Human_Override', 'rejected', ?)", (ad_id, f"Rejected: {notes}"))
                            conn.commit()
                            conn.close()
                            st.error(f"Ad #{ad_id} Rejected")
                            time.sleep(0.3)
                            st.rerun()

                        if ac3.button("⚠️ Restrict 18+", key=f"rs_{ad_id}"):
                            conn = get_connection()
                            c = conn.cursor()
                            c.execute("UPDATE Advertisements SET status = 'approved' WHERE id = ?", (ad_id,))
                            c.execute("INSERT INTO AuditLogs (ad_id, trigger_user_id, model_version, final_decision, log_details) VALUES (?, 2, 'Human_Override', 'restricted_18', ?)", (ad_id, f"Restricted 18+: {notes}"))
                            conn.commit()
                            conn.close()
                            st.warning(f"Ad #{ad_id} Restricted to 18+")
                            time.sleep(0.3)
                            st.rerun()

    with adm_t2:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, description, age_restriction FROM PolicyRules")
        policies = cursor.fetchall()
        conn.close()
        dict_p = [{"ID": p[0], "Policy": p[1], "Description": p[2], "Min Age": p[3]} for p in policies]
        st.dataframe(dict_p, use_container_width=True)

# =====================================================================
# TAB 4: SOCIAL USER REELS FEED
# =====================================================================
with tabs[3]:
    st.subheader("Age-Aware Content & Ad Feed")
    
    col_u1, col_u2 = st.columns([1, 1.5], gap="medium")
    
    with col_u1:
        st.markdown("#### User Verification Mode")
        username = st.text_input("Handle", "guest_user", key="t4_user")
        auth_mode = st.radio("Verification Engine", ["Facial Camera Scan", "Behavior Tracking"], key="t4_auth")
        
        user_category = "Not a Child"
        user_confidence = 1.0
        
        if auth_mode == "Facial Camera Scan":
            f_mode = st.radio("Source", ["Webcam", "Preset Face"], horizontal=True, key="t4_fmode")
            img_np = None
            if f_mode == "Webcam":
                c_img = st.camera_input("Verify face", key="t4_cam")
                if c_img:
                    img_np = np.array(Image.open(c_img).convert("RGB"))
            else:
                sim = st.selectbox("Simulate Profile", ["Child Face", "Adult Face"], key="t4_sim")
                dummy = np.ones((128, 128, 3), dtype=np.uint8) * 240
                if sim == "Child Face":
                    cv2.ellipse(dummy, (64, 64), (45, 45), 0, 0, 360, (255, 200, 180), -1)
                else:
                    cv2.ellipse(dummy, (64, 64), (36, 54), 0, 0, 360, (245, 190, 160), -1)
                img_np = dummy
                
            if img_np is not None:
                user_category, user_confidence = estimate_age_from_face(img_np)
        else:
            search_input = st.text_input("Search history", "minecraft speedrun, cartoon videos", key="t4_srch")
            queries_list = [q.strip() for q in search_input.split(",")]
            user_category, user_confidence = estimate_age_from_behavior(queries_list, [{"duration_watched": 45, "total_duration": 60}], [])
            
        st.markdown("---")
        st.markdown("#### Active Profile Status")
        if user_category == "Less than 14":
            st.markdown("""
            <div style="background-color:#fef2f2; border:1px solid #fecaca; padding:14px; border-radius:10px;">
                <span style="color:#dc2626; font-weight:700;">🚨 LESS THAN 14 (Child Profile)</span><br>
                <span style="font-size:12px; color:#991b1b;">Restricted & gambling ads blocked. Educational content prioritized.</span>
            </div>
            """, unsafe_allow_html=True)
        elif user_category == "14 to 17":
            st.markdown("""
            <div style="background-color:#eff6ff; border:1px solid #bfdbfe; padding:14px; border-radius:10px;">
                <span style="color:#2563eb; font-weight:700;">⚠️ 14 TO 17 (Teen Profile)</span><br>
                <span style="font-size:12px; color:#1e40af;">Restricted & 18+ adult ads blocked. General interest feed active.</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background-color:#ecfdf5; border:1px solid #a7f3d0; padding:14px; border-radius:10px;">
                <span style="color:#059669; font-weight:700;">✅ 18 AND ABOVE (Adult Profile)</span><br>
                <span style="font-size:12px; color:#065f46;">Full ad delivery active.</span>
            </div>
            """, unsafe_allow_html=True)

    with col_u2:
        st.markdown("#### Personalized Feed Output")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, caption, file_path, status FROM Advertisements WHERE status = 'approved'")
        approved_ads = cursor.fetchall()
        
        GK_REELS = [
            {"title": "Fun Science: Why is the Sky Blue?", "desc": "Light scattering explanation for curious minds."},
            {"title": "Math Tricks: Multiply by 11 Mentally", "desc": "Quick mental arithmetic calculation steps."}
        ]
        
        feed_items = []
        if user_category in ["Less than 14", "14 to 17"]:
            for ad in approved_ads:
                ad_id, ad_title, ad_caption, ad_file_path, status = ad
                cursor.execute("SELECT final_decision FROM AuditLogs WHERE ad_id = ? ORDER BY id DESC LIMIT 1", (ad_id,))
                log = cursor.fetchone()
                is_restricted = (log and log[0] == 'restricted_18') or any(kw in (ad_title + " " + ad_caption).lower() for kw in ['casino', 'betting', 'gambling', 'satta', 'alcohol', 'poker'])
                if not is_restricted:
                    feed_items.append({"title": f"📢 [Age-Safe Ad] {ad_title}", "desc": ad_caption, "file": ad_file_path})
            for gk in GK_REELS:
                feed_items.append({"title": f"🎓 [Educational Reel] {gk['title']}", "desc": gk['desc'], "file": None})
        else:
            for ad in approved_ads:
                ad_id, ad_title, ad_caption, ad_file_path, status = ad
                feed_items.append({"title": f"📢 [Sponsored] {ad_title}", "desc": ad_caption, "file": ad_file_path})
            for gk in GK_REELS:
                feed_items.append({"title": f"🎓 {gk['title']}", "desc": gk['desc'], "file": None})
        conn.close()
        
        for item in feed_items:
            with st.container():
                st.markdown(f"**{item['title']}**")
                st.caption(item['desc'])
                if item.get('file') and os.path.exists(item['file']):
                    if item['file'].lower().endswith('.mp4'):
                        st.video(item['file'])
                    else:
                        st.image(item['file'], width=220)
                st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)

# Collapsible Audit Logs
st.markdown("<br>", unsafe_allow_html=True)
with st.expander("📋 View Real-Time System Audit Logs"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, ad_id, timestamp, model_version, final_decision, log_details FROM AuditLogs ORDER BY id DESC LIMIT 10")
    logs = cursor.fetchall()
    conn.close()
    if logs:
        dict_l = [{"Log ID": l[0], "Ad ID": l[1], "Timestamp": l[2], "Decision": l[4], "Audit Details": l[5]} for l in logs]
        st.dataframe(dict_l, use_container_width=True)
    else:
        st.caption("No audit logs recorded yet.")
