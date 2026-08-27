import streamlit as st
import sqlite3
import os
import time
import numpy as np
import cv2
from PIL import Image
from safead_system.database import get_connection, init_database
from safead_system.pipeline import run_multimodal_moderation, MULTILINGUAL_KEYWORDS
from safead_system.classifier import estimate_age_from_face, estimate_age_from_behavior

init_database()

st.set_page_config(page_title="SafeAd AI: Trust & Safety Framework", layout="wide")

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
st.markdown("<div class='subtitle'>Multimodal Trust & Safety Framework for Social Media Advertisement Moderation</div>", unsafe_allow_html=True)

# Navigation
tabs = st.tabs(["Advertiser Portal", "Admin Auditing Dashboard", "Social User Feed (Age-Aware)"])

# =====================================================================
# TAB 1: ADVERTISER PORTAL
# =====================================================================
with tabs[0]:
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
                os.makedirs("safead_system/uploads", exist_ok=True)
                file_path = os.path.join("safead_system/uploads", uploaded_file.name)
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
            fused_score = res["final_score"]
            status = res["status"].upper()
            
            # Status Indicator card
            if status == "APPROVED":
                st.success(f"✅ AD APPROVED (Safety Decision: {status})")
            elif status == "REJECTED":
                st.error(f"❌ AD BLOCKED / REJECTED (Safety Decision: {status})")
            else:
                st.warning(f"⚠️ HELD FOR HUMAN AUDIT (Safety Decision: {status})")
                
            # Score Metrics
            mcol1, mcol2, mcol3, mcol4 = st.columns(4)
            mcol1.metric("Unified Risk", f"{fused_score:.1f}%")
            mcol2.metric("Visual Risk", f"{res['visual_score']:.1f}%")
            mcol3.metric("OCR/Text Risk", f"{res['ocr_score']:.1f}%")
            mcol4.metric("Speech Risk", f"{res['speech_score']:.1f}%")
            
            # Explanation details
            st.markdown("### Modality-specific Findings")
            st.write(f"**Violated Policies**: {', '.join(res['violations']) if res['violations'] else 'None'}")
            st.info(f"**Explainable AI Reason**: {res['explanation']}")
            
            # Display uploaded media
            if os.path.exists(res.get("file_path", "")):
                st.markdown("### Uploaded Creative Preview")
                if res["file_path"].lower().endswith(('.mp4')):
                    st.video(res["file_path"])
                else:
                    st.image(res["file_path"], width=300)
        else:
            st.info("Upload an advertisement and submit to see audit predictions here.")

# =====================================================================
# TAB 2: ADMIN AUDITING DASHBOARD
# =====================================================================
with tabs[1]:
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
                        if ad_file_path.lower().endswith('.mp4'):
                            st.video(ad_file_path)
                        else:
                            st.image(ad_file_path, width=250)
                            
                    with col_b:
                        # Get AI scores
                        conn = get_connection()
                        cursor = conn.cursor()
                        cursor.execute("SELECT final_score, visual_score, ocr_score, speech_score FROM RiskScores WHERE ad_id = ?", (ad_id,))
                        scores = cursor.fetchone()
                        
                        cursor.execute("SELECT explanation FROM ModerationResults WHERE ad_id = ?", (ad_id,))
                        expl = cursor.fetchone()
                        conn.close()
                        
                        if scores:
                            st.markdown(f"**AI Risk Score**: `{scores[0]:.1f}%` (Visual: {scores[1]}%, OCR: {scores[2]}%, Speech: {scores[3]}%)")
                        if expl:
                            st.markdown(f"**AI Prediction Reason**: *{expl[0]}*")
                            
                        st.markdown(f"**Description/Caption**: {ad_caption}")
                        
                        # Admin Actions
                        st.markdown("#### Auditing Override Actions")
                        action_col1, action_col2, action_col3 = st.columns(3)
                        
                        notes = st.text_input("Manual Audit Action Notes", placeholder="Reason for action...", key=f"notes_{ad_id}")
                        
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
                            cursor.execute("UPDATE Advertisements SET status = 'approved' WHERE id = ?", (ad_id,))  # Mark as approved but restriction noted in audit logs
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
        
        df_p = pd.DataFrame(policies, columns=["ID", "Policy Name", "Description", "Min Age Allowed"])
        st.dataframe(df_p, use_container_width=True)

# =====================================================================
# TAB 3: SOCIAL USER FEED (AGE-AWARE DELIVERY SIMULATION)
# =====================================================================
with tabs[2]:
    st.header("Simulated Social User Reels Feed")
    
    col_u1, col_u2 = st.columns([1.2, 2])
    
    with col_u1:
        st.subheader("1. User Profile Setup")
        username = st.text_input("Social User Handle", "guest_user")
        
        # User Age Authentication Options
        auth_mode = st.radio("Age Assessment Method", ["Behavioral History Tracker", "Facial Verification Camera Scan"])
        
        user_category = "Not a Child"
        user_confidence = 1.0
        
        if auth_mode == "Facial Verification Camera Scan":
            st.info("Simulate age prediction from camera input.")
            face_sim = st.selectbox("Simulate Face Profile Camera Input", ["Round Baby Face (Child Profile)", "Oval Beard Face (Adult Profile)"])
            
            # Draw synthetic images representing selected profile
            dummy_img = np.ones((128, 128, 3), dtype=np.uint8) * 240
            if face_sim == "Round Baby Face (Child Profile)":
                cv2.ellipse(dummy_img, (64, 64), (45, 45), 0, 0, 360, (255, 200, 180), -1)
                cv2.circle(dummy_img, (49, 69), 7, (40, 40, 40), -1)
                cv2.circle(dummy_img, (79, 69), 7, (40, 40, 40), -1)
            else:
                cv2.ellipse(dummy_img, (64, 64), (36, 54), 0, 0, 360, (245, 190, 160), -1)
                cv2.circle(dummy_img, (49, 54), 4, (40, 40, 40), -1)
                cv2.circle(dummy_img, (79, 54), 4, (40, 40, 40), -1)
                
            st.image(dummy_img, width=120, caption="Simulated Scan")
            user_category, user_confidence = estimate_age_from_face(dummy_img)
            
        else:
            st.info("Track age dynamically from recent searches & watch traces.")
            search_input = st.text_area("Recent User Search Terms (comma separated)", "minecraft speedrun, cartoon videos, school drawing")
            gk_retention = st.slider("GK/Educational Video Retention Ratio", 0.0, 1.0, 0.90)
            adult_retention = st.slider("Adult/Gambling Video Retention Ratio", 0.0, 1.0, 0.05)
            
            queries_list = [q.strip() for q in search_input.split(",")]
            gk_watches = [{"duration_watched": gk_retention * 60, "total_duration": 60}]
            adult_watches = [{"duration_watched": adult_retention * 120, "total_duration": 120}]
            
            user_category, user_confidence = estimate_age_from_behavior(queries_list, gk_watches, adult_watches)
            
        # Log Age Profile prediction in DB
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
        
        # UI Card for profile results
        if user_category == "Child":
            st.error(f"🔴 CLASSIFIED ROLE: {user_category} (Score: {user_confidence:.1%})")
            st.caption("Safety policy rule applies: Content restricted for children under 18 will be filtered out.")
        else:
            st.success(f"🟢 CLASSIFIED ROLE: {user_category} (Adult Score: {1.0 - user_confidence:.1%})")
            st.caption("Standard browsing profile. Eligible for general and restricted advertisements.")
            
    with col_u2:
        st.subheader("2. Personalized Age-Aware Media Feed")
        
        # Query approved ads from database
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT A.id, A.title, A.caption, A.file_path, R.final_score 
            FROM Advertisements A
            LEFT JOIN RiskScores R ON A.id = R.ad_id
            WHERE A.status = 'approved'
        """)
        approved_ads = cursor.fetchall()
        conn.close()
        
        # General Knowledge reels database
        GK_REELS = [
            {"title": "The Solar System for Kids", "topic": "Space Science", "desc": "Explore planets, stars, and galaxies in this fun guide.", "gk": True},
            {"title": "Why is the Sky Blue?", "topic": "Physics Experiments", "desc": "Understanding sunlight scattering and atmosphere molecules.", "gk": True},
            {"title": "How Do Plants Make Food?", "topic": "Biology Class", "desc": "Learn all about photosynthesis, water, and sunlight.", "gk": True}
        ]
        
        feed_items = []
        
        # Build feed content based on user age category
        if user_category == "Child":
            st.warning("Child Protection Mode is ACTIVE. Filtering unsafe/age-restricted advertisements...")
            
            # Filter ads: only keep ads that are safe and do not trigger safety violations
            for ad in approved_ads:
                ad_id, ad_title, ad_caption, ad_file_path, score = ad
                # Exclude ads containing keywords triggers (Alcohol, Casino, Vegas, Dating, Combat, Satta)
                lower_text = f"{ad_title} {ad_caption or ''} {ad_file_path}".lower()
                is_restricted = any(w in lower_text for langs in MULTILINGUAL_KEYWORDS.values() for lang in langs.values() for w in lang)
                if not is_restricted:
                    feed_items.append({"title": f"[Safe Ad] {ad_title}", "desc": ad_caption, "file": ad_file_path, "gk": False})
                    
            # Inject GK reels
            for gk in GK_REELS:
                feed_items.append({"title": f"[GK Reel] {gk['title']}", "desc": f"Topic: {gk['topic']} - {gk['desc']}", "file": None, "gk": True})
        else:
            st.success("Adult Feed Active. Delivery includes general and age-appropriate advertisements.")
            for ad in approved_ads:
                ad_id, ad_title, ad_caption, ad_file_path, score = ad
                feed_items.append({"title": f"[Ad Campaign] {ad_title}", "desc": ad_caption, "file": ad_file_path, "gk": False})
            for gk in GK_REELS:
                feed_items.append({"title": f"[GK Reel] {gk['title']}", "desc": f"Topic: {gk['topic']} - {gk['desc']}", "file": None, "gk": True})
                
        # Render Feed
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
    df_l = pd.DataFrame(logs, columns=["Log ID", "Ad ID", "Timestamp", "Framework Version", "Decision", "AI Audit Notes"])
    st.dataframe(df_l, use_container_width=True)
else:
    st.caption("No audit logs recorded yet.")
