import streamlit as st
import sqlite3
import os
import time
import numpy as np
import cv2
from PIL import Image
from website.database import get_connection, init_database
from website.pipeline import run_multimodal_moderation, MULTILINGUAL_KEYWORDS
from website.classifier import estimate_age_from_face, estimate_age_from_behavior

init_database()

st.set_page_config(page_title="Instagram Clone - SafeAd AI", layout="wide")

# Instagram Theme CSS Styling
st.markdown("""
    <style>
    /* Global Styles */
    .stApp {
        background-color: #fafafa;
        color: #262626;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Instagram Header */
    .insta-header {
        font-family: "Georgia", serif;
        font-size: 32px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
        color: #262626;
        border-bottom: 1px solid #dbdbdb;
        padding-bottom: 10px;
    }
    
    /* Post Cards */
    .post-card {
        background-color: #ffffff;
        border: 1px solid #dbdbdb;
        border-radius: 8px;
        margin-bottom: 24px;
        padding: 0px;
    }
    .post-header {
        display: flex;
        align-items: center;
        padding: 12px;
        border-bottom: 1px solid #efefef;
    }
    .post-username {
        font-weight: 600;
        font-size: 14px;
        margin-left: 10px;
        color: #262626;
    }
    .post-caption {
        padding: 12px;
        font-size: 14px;
        color: #262626;
    }
    
    /* Profile Grid */
    .profile-header {
        display: flex;
        align-items: center;
        padding: 24px 0px;
        border-bottom: 1px solid #dbdbdb;
        margin-bottom: 20px;
    }
    .profile-username {
        font-size: 28px;
        font-weight: 300;
        margin-right: 20px;
    }
    .profile-stats {
        display: flex;
        gap: 30px;
        margin-top: 10px;
        font-size: 16px;
    }
    .stat-number {
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize Session States
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""
if "age_category" not in st.session_state:
    st.session_state["age_category"] = "Not a Child"
if "age_confidence" not in st.session_state:
    st.session_state["age_confidence"] = 1.0
if "current_tab" not in st.session_state:
    st.session_state["current_tab"] = "🏠 Feed"

# =====================================================================
# LOGIN & AGE ASSESSMENT PORTAL
# =====================================================================
if not st.session_state["logged_in"]:
    st.markdown("<div class='insta-header'>Instagram</div>", unsafe_allow_html=True)
    
    col_l1, col_l2, col_l3 = st.columns([1, 1.2, 1])
    
    with col_l2:
        st.subheader("Login to your account")
        user_input = st.text_input("Username / Email", "RD_Sourav")
        password_input = st.text_input("Password", type="password")
        
        st.markdown("---")
        st.markdown("#### Trust & Safety Age Check Verification")
        auth_mode = st.radio("Choose Verification Method", ["Facial Face Scan (Webcam Camera)", "Behavioral Search Survey"])
        
        category, conf = None, None
        
        if auth_mode == "Facial Face Scan (Webcam Camera)":
            st.info("Snap a photo to verify your age category using real-time facial feature roundness estimation.")
            cam_image = st.camera_input("Capture Profile Face Photo")
            
            st.markdown("**(Optional Fallback)** If camera permissions are blocked, select face type:")
            face_sim = st.selectbox("Simulate Face Shape", ["Select shape...", "Adult Face Profile (Oval shape)", "Baby/Child Face Profile (Round shape)"])
            
            if cam_image:
                # Capture real face photo
                try:
                    image = Image.open(cam_image)
                    image_np = np.array(image)
                    category, conf = estimate_age_from_face(image_np)
                except Exception as e:
                    st.error(f"Camera analysis error: {e}")
            elif face_sim != "Select shape...":
                dummy_face = np.ones((128, 128, 3), dtype=np.uint8) * 240
                if face_sim == "Baby/Child Face Profile (Round shape)":
                    cv2.ellipse(dummy_face, (64, 64), (45, 45), 0, 0, 360, (255, 200, 180), -1)
                    cv2.circle(dummy_face, (49, 69), 7, (40, 40, 40), -1)
                    cv2.circle(dummy_face, (79, 69), 7, (40, 40, 40), -1)
                else:
                    cv2.ellipse(dummy_face, (64, 64), (36, 54), 0, 0, 360, (245, 190, 160), -1)
                    cv2.circle(dummy_face, (49, 54), 4, (40, 40, 40), -1)
                    cv2.circle(dummy_face, (79, 54), 4, (40, 40, 40), -1)
                category, conf = estimate_age_from_face(dummy_face)
                
        else: # Behavioral Search Survey
            survey_q1 = st.text_input("Search query simulation (e.g. 'roblox, toys' vs 'stocks, ML')", "python coding, machine learning jobs")
            survey_q2 = st.slider("GK Reels View Time (seconds out of 60)", 0, 60, 15)
            survey_q3 = st.slider("Adult/Ad Reels View Time (seconds out of 100)", 0, 100, 85)
            
            if st.button("Analyze Search Behavior"):
                queries = [q.strip() for q in survey_q1.split(",")]
                gk_watches = [{"duration_watched": survey_q2, "total_duration": 60}]
                adult_watches = [{"duration_watched": survey_q3, "total_duration": 100}]
                category, conf = estimate_age_from_behavior(queries, gk_watches, adult_watches)
        
        if category is not None:
            st.success(f"Age scan complete: **{category}** detected (Confidence: {conf:.1%})!")
            
            if st.button("Confirm & Enter Instagram Feed"):
                if not user_input:
                    st.error("Please enter a username.")
                else:
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = user_input
                    st.session_state["age_category"] = category
                    st.session_state["age_confidence"] = conf
                    
                    # Check / Insert User in DB
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("SELECT id FROM Users WHERE username = ?", (user_input,))
                    usr = cursor.fetchone()
                    if not usr:
                        cursor.execute("INSERT INTO Users (username, password_hash, role) VALUES (?, 'mock_hash', 'social_user')", (user_input,))
                        user_id = cursor.lastrowid
                    else:
                        user_id = usr[0]
                        
                    cursor.execute("""
                        INSERT INTO AgeProfiles (user_id, method, prediction_class, confidence)
                        VALUES (?, ?, ?, ?)
                    """, (user_id, "facial" if "Facial" in auth_mode else "behavioral", category, conf))
                    conn.commit()
                    conn.close()
                    
                    st.success(f"Logged in successfully as {user_input}!")
                    time.sleep(0.5)
                    st.rerun()


# =====================================================================
# MAIN INSTAGRAM SYSTEM FEED & INTERFACE
# =====================================================================
else:
    # Header bar
    st.markdown("<div class='insta-header'>Instagram</div>", unsafe_allow_html=True)
    
    # Top navbar / Tab selector
    tabs_sel = st.radio(
        "Navigation",
        ["🏠 Feed", "🎬 Reels", "➕ Create Post", "👤 Profile (Personal Page)", "🛡️ Safety Logs"],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    st.session_state["current_tab"] = tabs_sel
    
    # Helper to check if a text contains restricted safety words
    def is_age_restricted(text: str) -> bool:
        text_lower = text.lower()
        for policy, langs in MULTILINGUAL_KEYWORDS.items():
            for lang, words in langs.items():
                for w in words:
                    if w in text_lower:
                        return True
        return False

    # Get User Details
    username = st.session_state["username"]
    age_category = st.session_state["age_category"]
    age_conf = st.session_state["age_confidence"]

    # =================================================================
    # TAB A: PHOTO FEED
    # =================================================================
    if st.session_state["current_tab"] == "🏠 Feed":
        st.subheader("Photo Ingestion Timeline")
        
        # Load posts from DB
        conn = get_connection()
        cursor = conn.cursor()
        # Query approved photo posts (which are not videos)
        cursor.execute("""
            SELECT A.id, A.title, A.caption, A.file_path, U.username 
            FROM Advertisements A
            JOIN Users U ON A.advertiser_id = U.id
            WHERE A.status = 'approved' AND A.file_path NOT LIKE '%.mp4'
            ORDER BY A.id DESC
        """)
        posts = cursor.fetchall()
        conn.close()
        
        # Filter feed based on age check
        filtered_posts = []
        for post in posts:
            pid, ptitle, pcap, pfile, puser = post
            full_txt = f"{ptitle} {pcap or ''} {pfile}"
            
            # If viewer is a child, filter out any restricted terms
            if age_category == "Child" and is_age_restricted(full_txt):
                continue
            filtered_posts.append(post)
            
        if not filtered_posts:
            st.info("No photo posts found in feed.")
        else:
            for pid, ptitle, pcap, pfile, puser in filtered_posts:
                # Render Instagram-style Card
                st.markdown(f"""
                <div class="post-card">
                    <div class="post-header">
                        <div style="width: 32px; height: 32px; background-color: #dbdbdb; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 12px; color: #555;">
                            {puser[0].upper()}
                        </div>
                        <div class="post-username">{puser}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Image Content
                if os.path.exists(pfile):
                    st.image(pfile, use_container_width=True)
                else:
                    # Draw a fallback safe placeholder card
                    placeholder_img = np.ones((400, 600, 3), dtype=np.uint8) * 240
                    cv2.putText(placeholder_img, ptitle, (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (40, 40, 40), 2)
                    st.image(placeholder_img, use_container_width=True)
                    
                st.markdown(f"<div class='post-caption'><b>{puser}</b> {pcap or ''}</div>", unsafe_allow_html=True)
                st.markdown("<hr style='margin: 0px 0px 20px 0px; border: 0; border-top: 1px solid #dbdbdb;'>", unsafe_allow_html=True)

    # =================================================================
    # TAB B: REELS FEED (VIDEOS)
    # =================================================================
    elif st.session_state["current_tab"] == "🎬 Reels":
        st.subheader("Short-Video Reels Feed")
        
        # General Knowledge Reels Database
        GK_REELS = [
            {"id": "gk1", "title": "The Solar System for Kids", "topic": "Space Science", "desc": "Explore planets, stars, and galaxies in this fun guide.", "gk": True, "restricted": False, "username": "SystemGK"},
            {"id": "gk2", "title": "Why is the Sky Blue?", "topic": "Physics Experiments", "desc": "Understanding sunlight scattering and atmosphere molecules.", "gk": True, "restricted": False, "username": "SystemGK"},
            {"id": "gk3", "title": "How Do Plants Make Food?", "topic": "Biology Class", "desc": "Learn all about photosynthesis, water, and sunlight.", "gk": True, "restricted": False, "username": "SystemGK"}
        ]
        
        # 10 Video Safety Datasets from Python settings
        VIDEO_SAFETY_DATASETS = [
            {"id": "ds_01", "title": "SAFEWATCH-BENCH Dataset Split", "topic": "General Video Safety", "desc": "Large-scale video safety guardrail benchmark containing Real-world splits across 6 safety categories.", "restricted": False, "gk": False, "username": "SafeWatchTeam"},
            {"id": "ds_02", "title": "KuaiMod Short Video Dataset Split", "topic": "Short Video Governance", "desc": "SVP content governance dataset from Kuaishou covering 15 categories of policy violations.", "restricted": True, "gk": False, "username": "KuaishouTeam"},
            {"id": "ds_03", "title": "XD-Violence Dataset Split", "topic": "Audio-Visual Violence Detection", "desc": "Surveillance crime, combat, explosion, and weapon fights containing both video and audio tracks.", "restricted": True, "gk": False, "username": "XDViolenceTeam"},
            {"id": "ds_04", "title": "UCF-Crime Dataset Split", "topic": "Crime Anomaly Detection", "desc": "Surveillance videos capturing real-world anomalies, crimes, and platform safety hazards.", "restricted": True, "gk": False, "username": "UCFCrimeTeam"},
            {"id": "ds_05", "title": "FakeSV Fake News Dataset Split", "topic": "Fake News Verification", "desc": "Multimodal fake news detection split containing social media video visual and transcript cues.", "restricted": True, "gk": False, "username": "FakeSVTeam"},
            {"id": "ds_06", "title": "Autoshot Dataset Split", "topic": "Shot Boundary Detection", "desc": "Standard normal short-video transitions used to analyze shot boundary cuts.", "restricted": False, "gk": False, "username": "AutoShotTeam"},
            {"id": "ds_07", "title": "VHD11K Dataset Split", "topic": "Video Harmfulness Recognition", "desc": "11,000 video samples for training and verifying toxic and harmful visual filters.", "restricted": True, "gk": False, "username": "VHD11KTeam"},
            {"id": "ds_08", "title": "Violent Scenes Dataset (VSD) Split", "topic": "Violence Scene Recognition", "desc": "Contains movie clips and video segments labeled for action violence and acoustic screams.", "restricted": True, "gk": False, "username": "VSDTeam"},
            {"id": "ds_09", "title": "BLM-Guard Dataset Split", "topic": "Commercial Ad Policy Violations", "desc": "Real-world commercial short-video ads dataset structured across seven safety risk tiers.", "restricted": True, "gk": False, "username": "BLMGuardTeam"},
            {"id": "ds_10", "title": "LSPD Dataset Split", "topic": "Pornography and Age Restricted Detection", "desc": "Large-scale pornographic dataset for verifying adult content management filters.", "restricted": True, "gk": False, "username": "LSPDTeam"}
        ]
        
        # Load Video posts from DB
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT A.id, A.title, A.caption, A.file_path, U.username 
            FROM Advertisements A
            JOIN Users U ON A.advertiser_id = U.id
            WHERE A.status = 'approved' AND A.file_path LIKE '%.mp4'
            ORDER BY A.id DESC
        """)
        db_reels = cursor.fetchall()
        conn.close()
        
        reels_feed = []
        
        # Build feed content based on user age category
        if age_category == "Child":
            st.warning("Child Mode Active: Filtering restricted datasets and ads...")
            # Inject GK reels
            for gk in GK_REELS:
                reels_feed.append(gk)
            # Inject safe datasets
            for ds in VIDEO_SAFETY_DATASETS:
                if not ds["restricted"]:
                    reels_feed.append(ds)
            # Inject safe database uploads
            for r in db_reels:
                rid, rtitle, rcap, rfile, ruser = r
                full_txt = f"{rtitle} {rcap or ''} {rfile}"
                if not is_age_restricted(full_txt):
                    reels_feed.append({"title": rtitle, "desc": rcap, "file_path": rfile, "gk": False, "restricted": False, "username": ruser})
        else:
            st.success("Adult Reels Feed Active. Showing all datasets and ads.")
            # Inject all DB uploads
            for r in db_reels:
                rid, rtitle, rcap, rfile, ruser = r
                reels_feed.append({"title": rtitle, "desc": rcap, "file_path": rfile, "gk": False, "restricted": is_age_restricted(f"{rtitle} {rcap}"), "username": ruser})
            # Inject all datasets
            for ds in VIDEO_SAFETY_DATASETS:
                reels_feed.append(ds)
            # Inject GK reels
            for gk in GK_REELS:
                reels_feed.append(gk)
                
        if not reels_feed:
            st.info("No video reels available.")
        else:
            for item in reels_feed:
                is_gk = item.get("gk", False)
                is_restricted = item.get("restricted", False)
                u = item.get("username", "System")
                
                # Tag display info
                tag_label = "Ad Creative"
                if is_gk:
                    tag_label = "GK Lesson"
                elif "Dataset" in item["title"]:
                    tag_label = "Dataset Video Source"
                    
                st.markdown(f"""
                <div class="post-card" style="border: 2px solid {'#f87171' if is_restricted else '#dbdbdb'};">
                    <div class="post-header" style="background-color: {'#fef2f2' if is_restricted else '#ffffff'};">
                        <div style="width: 32px; height: 32px; background-color: {'#ef4444' if is_restricted else '#4a90e2'}; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 12px; color: #fff;">
                            {u[0].upper()}
                        </div>
                        <div class="post-username">
                            {u} 
                            <span style="color:#8e8e8e; font-weight:300;">• {tag_label}</span>
                            {f'<span style="color:#ef4444; font-weight:600; margin-left: 10px;">[RESTRICTED 18+]</span>' if is_restricted else ''}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Render video file or mock placeholder
                file_path = item.get("file_path", None)
                if file_path and os.path.exists(file_path):
                    st.video(file_path)
                else:
                    # Draw visual block for dataset videos / educational videos
                    ph_img = np.ones((250, 500, 3), dtype=np.uint8) * 40
                    cv2.putText(ph_img, f"Video Stream: {item['title']}", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
                    cv2.putText(ph_img, f"Topic: {item.get('topic', 'Content Safety')}", (20, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1)
                    cv2.putText(ph_img, "Dataset Video Feed Active", (20, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 200, 100), 1)
                    st.image(ph_img, use_container_width=True)
                    
                st.write(f"**{item['title']}**: {item.get('desc', '')}")
                st.markdown("<hr style='margin: 20px 0px;'>", unsafe_allow_html=True)


    # =================================================================
    # TAB C: NEW POST UPLOAD WITH REAL-TIME AI MODERATION
    # =================================================================
    elif st.session_state["current_tab"] == "➕ Create Post":
        st.subheader("Publish a New Creative / Post")
        
        col_c1, col_c2 = st.columns([1, 1.2])
        
        with col_c1:
            with st.form("new_post_form", clear_on_submit=True):
                post_title = st.text_input("Creative Title", "Organic Fruit Basket")
                post_caption = st.text_area("Caption / Hashtags", "Fresh healthy apples and organic grapes for diet.")
                post_type = st.radio("Creative Modality Type", ["Photo (Image)", "Reel (Video)"])
                post_file = st.file_uploader("Upload Creative File", type=["png", "jpg", "jpeg", "mp4"])
                share_btn = st.form_submit_button("Publish to Instagram")
                
            if share_btn:
                if not post_file:
                    st.error("Please select a file to upload.")
                else:
                    # Save locally
                    os.makedirs("website/uploads", exist_ok=True)
                    ext = ".mp4" if post_type == "Reel (Video)" else ".jpg"
                    f_name = f"user_{username}_{int(time.time())}{ext}"
                    file_path = os.path.join("website/uploads", f_name)
                    with open(file_path, "wb") as f:
                        f.write(post_file.getbuffer())
                        
                    # Insert in DB under logged-in user context
                    conn = get_connection()
                    cursor = conn.cursor()
                    # Resolve user ID
                    cursor.execute("SELECT id FROM Users WHERE username = ?", (username,))
                    usr_row = cursor.fetchone()
                    uid = usr_row[0] if usr_row else 1
                    
                    cursor.execute("""
                        INSERT INTO Advertisements (title, advertiser_id, caption, file_path, status)
                        VALUES (?, ?, ?, ?, 'under_review')
                    """, (post_title, uid, post_caption, file_path))
                    ad_id = cursor.lastrowid
                    conn.commit()
                    conn.close()
                    
                    # Run safety engine checks instantly!
                    with st.spinner("Analyzing upload content safety policies..."):
                        mod_res = run_multimodal_moderation(ad_id)
                        
                    st.session_state["latest_post_mod"] = mod_res
                    st.success("Analysis complete!")
                    
        with col_c2:
            st.subheader("Trust & Safety Feedback")
            if "latest_post_mod" in st.session_state:
                mr = st.session_state["latest_post_mod"]
                status = mr["status"].upper()
                score = mr["final_score"]
                
                if status == "APPROVED":
                    st.success(f"✅ Published successfully! Status: APPROVED (Risk: {score:.1f}%)")
                    st.info("Your post is now live and visible to compliant feeds.")
                elif status == "REJECTED":
                    st.error(f"❌ Upload Blocked: REJECTED (Risk: {score:.1f}%)")
                    st.markdown(f"**Policy Infractions Detected**: `{', '.join(mr['violations'])}`")
                    st.markdown(f"**AI Rejection Rationale**: *{mr['explanation']}*")
                else:
                    st.warning(f"⚠️ Held for Audit: UNDER REVIEW (Risk: {score:.1f}%)")
                    st.markdown("Your upload contains borderline signals. It will become visible on feeds once manual administrators audit and approve the content.")

    # =================================================================
    # TAB D: PROFILE PAGE (GRID VIEW OF USER'S POSTS)
    # =================================================================
    elif st.session_state["current_tab"] == "👤 Profile (Personal Page)":
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM Users WHERE username = ?", (username,))
        usr_row = cursor.fetchone()
        uid = usr_row[0] if usr_row else 1
        
        # Load user posts
        cursor.execute("""
            SELECT id, title, caption, file_path, status 
            FROM Advertisements 
            WHERE advertiser_id = ?
            ORDER BY id DESC
        """, (uid,))
        user_posts = cursor.fetchall()
        conn.close()
        
        # Profile Header
        st.markdown(f"""
        <div class="profile-header">
            <div style="width: 90px; height: 90px; background-color: #dbdbdb; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 32px; font-weight: bold; color: #555; margin-right: 30px;">
                {username[0].upper()}
            </div>
            <div>
                <div style="display:flex; align-items:center;">
                    <div class="profile-username">{username}</div>
                    <div style="background-color:#efefef; padding:5px 10px; border-radius:4px; font-size:14px; font-weight:600;">{age_category} Profile</div>
                </div>
                <div class="profile-stats">
                    <div><span class="stat-number">{len(user_posts)}</span> posts</div>
                    <div><span class="stat-number">234</span> followers</div>
                    <div><span class="stat-number">412</span> following</div>
                </div>
                <div style="margin-top: 15px; font-size:14px;">
                    <b>{username}</b><br>
                    SafeAd AI test profile. Verified Safety Status: <i>{age_category}</i> (Confidence: {age_conf:.1%})
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Profile Grid
        st.subheader("Your Posts Grid")
        if not user_posts:
            st.info("You haven't posted anything yet. Go to 'Create Post' to publish your first content.")
        else:
            # Create a 3-column grid
            cols = st.columns(3)
            for idx, post in enumerate(user_posts):
                pid, ptitle, pcap, pfile, pstatus = post
                col_idx = idx % 3
                
                with cols[col_idx]:
                    # Render small card with Status Tag
                    st.markdown(f"**{ptitle}**")
                    if pstatus == "approved":
                        st.caption("🟢 Approved")
                    elif pstatus == "rejected":
                        st.caption("🔴 Rejected")
                    else:
                        st.caption("🟡 In Review Queue")
                        
                    if os.path.exists(pfile):
                        if pfile.lower().endswith('.mp4'):
                            # Thumbnail for video
                            st.caption("🎥 Reel Video")
                            st.video(pfile)
                        else:
                            st.image(pfile, use_container_width=True)
                    else:
                        # Fallback image block
                        st.caption("Creative Media Not Found")
                    st.markdown("---")

    # =================================================================
    # TAB E: SAFETY CENTER LOGS
    # =================================================================
    elif st.session_state["current_tab"] == "🛡️ Safety Logs":
        st.subheader("SafeAd AI System Audit Logs")
        st.markdown(f"**Current Viewer Age Category**: `{age_category}` (Confidence: {age_conf:.2%})")
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT A.id, A.ad_id, A.timestamp, A.model_version, A.final_decision, A.log_details 
            FROM AuditLogs A
            ORDER BY A.id DESC LIMIT 15
        """)
        logs = cursor.fetchall()
        conn.close()
        
        if logs:
            dict_logs = [{"Log ID": l[0], "Ad ID": l[1], "Timestamp": l[2], "Framework Version": l[3], "Decision": l[4], "AI Audit Notes": l[5]} for l in logs]
            st.dataframe(dict_logs, use_container_width=True)
        else:

            st.info("No audit logs recorded in database.")
            
        st.markdown("### SafeAd System Information")
        st.info("SafeAd AI operates a unified multimodal fusion pipeline scoring policy compliance across visual, textual, and acoustic layers. Non-compliant, high-risk, or restricted postings are automatically held or blocked from minor streams.")
        
        # Add Logout button
        st.markdown("---")
        if st.button("Log Out of Session"):
            st.session_state["logged_in"] = False
            st.session_state["username"] = ""
            st.session_state["age_category"] = "Not a Child"
            st.rerun()
