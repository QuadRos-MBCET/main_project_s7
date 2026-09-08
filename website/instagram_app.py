import streamlit as st
import sqlite3
import os
import time
import base64
import json
from datetime import datetime
import numpy as np
import cv2
from PIL import Image

# Import backend modules with fallback for both local and stlite execution
try:
    from website.database import get_connection, init_database
    from website.pipeline import run_multimodal_moderation, MULTILINGUAL_KEYWORDS
    from website.classifier import estimate_age_from_face, estimate_age_from_behavior
except ImportError:
    from database import get_connection, init_database
    from pipeline import run_multimodal_moderation, MULTILINGUAL_KEYWORDS
    from classifier import estimate_age_from_face, estimate_age_from_behavior

init_database()

st.set_page_config(
    page_title="Aura Social — Dark Mode Trust & Safety",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Helper to find media files across various working directory permutations
def resolve_media_path(file_path: str):
    if not file_path:
        return None
    if file_path.startswith("http://") or file_path.startswith("https://"):
        return file_path
    candidates = [
        file_path,
        os.path.join(os.path.dirname(__file__), file_path),
        os.path.join(os.path.dirname(__file__), "uploads", os.path.basename(file_path)),
        os.path.join("website", file_path),
        os.path.join("website", "uploads", os.path.basename(file_path)),
        os.path.basename(file_path)
    ]
    for c in candidates:
        if os.path.exists(c) and os.path.isfile(c):
            return c
    return None

def get_media_base64_data_uri(file_path: str):
    resolved = resolve_media_path(file_path)
    if not resolved or resolved.startswith("http"):
        return resolved
    try:
        with open(resolved, "rb") as f:
            data = f.read()
        ext = os.path.splitext(resolved)[1].lower().replace(".", "")
        mime = f"video/{ext}" if ext in ["mp4", "webm", "ogg"] else f"image/{ext if ext != 'jpg' else 'jpeg'}"
        b64 = base64.b64encode(data).decode("utf-8")
        return f"data:{mime};base64,{b64}"
    except Exception:
        return None

# =====================================================================
# GLOBAL IMMERSIVE DARK THEME (Aura Dark)
# =====================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    :root {
        --bg-dark: #090d16;
        --bg-dark-subtle: #030712;
        --surface-dark: #0f172a;
        --surface-card: #131d33;
        --surface-border: #1e293b;
        --surface-hover: #1e293b;
        --primary: #6366f1;
        --primary-glow: rgba(99, 102, 241, 0.4);
        --accent: #ec4899;
        --accent-gradient: linear-gradient(135deg, #6366f1 0%, #ec4899 100%);
        --text-primary: #f8fafc;
        --text-secondary: #94a3b8;
        --text-muted: #64748b;
        --safe-green: #10b981;
        --warn-amber: #f59e0b;
        --danger-red: #ef4444;
        --radius-lg: 20px;
        --radius-md: 14px;
        --shadow-glow: 0 10px 30px -5px rgba(99, 102, 241, 0.25);
    }

    * {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Full dark theme canvas */
    .stApp {
        background-color: var(--bg-dark);
        background-image: radial-gradient(at 15% 15%, rgba(99, 102, 241, 0.08) 0px, transparent 50%),
                          radial-gradient(at 85% 85%, rgba(236, 72, 153, 0.08) 0px, transparent 50%);
        color: var(--text-primary);
    }

    #MainMenu, footer, header {visibility: hidden;}
    .block-container {
        padding-top: 1.2rem !important;
        padding-bottom: 5rem !important;
        max-width: 1200px !important;
    }

    /* Dark Glassmorphic Navbar */
    .aura-navbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: rgba(15, 23, 42, 0.85);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid var(--surface-border);
        border-radius: var(--radius-lg);
        padding: 12px 24px;
        margin-bottom: 24px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
    }
    .aura-brand {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .aura-logo-icon {
        width: 40px;
        height: 40px;
        border-radius: 12px;
        background: var(--accent-gradient);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 800;
        font-size: 22px;
        box-shadow: var(--shadow-glow);
    }
    .aura-brand-title {
        font-size: 22px;
        font-weight: 800;
        letter-spacing: -0.5px;
        background: var(--accent-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .aura-badge-user {
        display: flex;
        align-items: center;
        gap: 10px;
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid var(--surface-border);
        padding: 6px 14px;
        border-radius: 999px;
        font-size: 13px;
        font-weight: 600;
        color: var(--text-primary);
    }

    /* Dark Mode Stories Highlights */
    .stories-container {
        display: flex;
        gap: 18px;
        overflow-x: auto;
        padding: 10px 6px 18px 6px;
        margin-bottom: 24px;
        scrollbar-width: none;
    }
    .stories-container::-webkit-scrollbar {
        display: none;
    }
    .story-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 6px;
        min-width: 72px;
        cursor: pointer;
    }
    .story-ring {
        width: 68px;
        height: 68px;
        border-radius: 50%;
        padding: 3px;
        background: var(--accent-gradient);
        display: flex;
        align-items: center;
        justify-content: center;
        transition: transform 0.2s ease;
    }
    .story-ring:hover {
        transform: scale(1.08);
    }
    .story-avatar {
        width: 100%;
        height: 100%;
        border-radius: 50%;
        background: var(--surface-dark);
        border: 2px solid var(--bg-dark);
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 20px;
    }
    .story-name {
        font-size: 12px;
        font-weight: 500;
        color: var(--text-secondary);
        max-width: 72px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    /* Dark Social Feed Cards */
    .aura-card {
        background: var(--surface-card);
        border: 1px solid var(--surface-border);
        border-radius: var(--radius-lg);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
        margin-bottom: 28px;
        overflow: hidden;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .aura-card:hover {
        border-color: rgba(99, 102, 241, 0.4);
    }
    .aura-card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 16px 20px;
        background: rgba(15, 23, 42, 0.6);
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }
    .card-user-info {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .user-avatar-sm {
        width: 42px;
        height: 42px;
        border-radius: 50%;
        background: var(--accent-gradient);
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 16px;
        color: white;
        box-shadow: var(--shadow-glow);
    }
    .user-meta-name {
        font-weight: 700;
        font-size: 15px;
        color: var(--text-primary);
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .user-meta-time {
        font-size: 12px;
        color: var(--text-muted);
    }

    /* Glowing Dark Badges */
    .badge-pill {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        padding: 4px 10px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.3px;
        text-transform: uppercase;
    }
    .badge-approved {
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.35);
    }
    .badge-review {
        background: rgba(245, 158, 11, 0.15);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.35);
    }
    .badge-rejected {
        background: rgba(239, 68, 68, 0.15);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.35);
    }
    .badge-sponsored {
        background: rgba(124, 58, 237, 0.15);
        color: #a78bfa;
        border: 1px solid rgba(124, 58, 237, 0.35);
    }

    .aura-card-caption {
        padding: 14px 20px;
        font-size: 14px;
        line-height: 1.55;
        color: var(--text-primary);
    }
    .aura-card-caption b {
        font-weight: 700;
        margin-right: 6px;
        color: #fff;
    }
    .aura-tag {
        color: #818cf8;
        font-weight: 600;
    }

    /* Explore & Discovery Dark Cards */
    .explore-card {
        background: var(--surface-card);
        border: 1px solid var(--surface-border);
        border-radius: var(--radius-md);
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .explore-card:hover {
        transform: translateY(-4px);
        border-color: var(--primary);
    }

    /* Profile Dark Banner */
    .profile-banner {
        background: var(--surface-card);
        border: 1px solid var(--surface-border);
        border-radius: var(--radius-lg);
        padding: 32px 28px;
        margin-bottom: 28px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
    }
    .profile-avatar-lg {
        width: 100px;
        height: 100px;
        border-radius: 50%;
        background: var(--accent-gradient);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 40px;
        font-weight: 800;
        box-shadow: 0 8px 30px rgba(99, 102, 241, 0.35);
    }
    .profile-stat-box {
        text-align: center;
        padding: 10px 20px;
        background: rgba(15, 23, 42, 0.7);
        border-radius: var(--radius-md);
        border: 1px solid var(--surface-border);
    }
    .profile-stat-val {
        font-size: 22px;
        font-weight: 800;
        color: #fff;
    }
    .profile-stat-lbl {
        font-size: 11px;
        color: var(--text-secondary);
        font-weight: 600;
        text-transform: uppercase;
    }

    /* Dark Safety Meter */
    .safety-radar-box {
        background: var(--surface-card);
        border: 1px solid var(--surface-border);
        border-radius: var(--radius-lg);
        padding: 22px;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
        margin-bottom: 20px;
    }
    .meter-label {
        display: flex;
        justify-content: space-between;
        font-size: 13px;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 6px;
    }
    .meter-bar {
        height: 8px;
        border-radius: 4px;
        background: #1e293b;
        overflow: hidden;
        margin-bottom: 14px;
    }
    .meter-fill {
        height: 100%;
        border-radius: 4px;
        transition: width 0.4s ease;
    }

    /* Dark Input Elements Override */
    div[data-testid="stTextInput"] input, div[data-testid="stTextArea"] textarea {
        background-color: #1e293b !important;
        color: #f8fafc !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
    }
    div[data-baseweb="select"] {
        background-color: #1e293b !important;
        color: #f8fafc !important;
        border-radius: 12px !important;
    }
    div[data-testid="stExpander"] {
        background-color: var(--surface-card) !important;
        border: 1px solid var(--surface-border) !important;
        border-radius: 14px !important;
    }
</style>
""", unsafe_allow_html=True)

# =====================================================================
# SESSION STATE INITIALIZATION
# =====================================================================
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""
if "age_category" not in st.session_state:
    st.session_state["age_category"] = "Not a Child"
if "age_confidence" not in st.session_state:
    st.session_state["age_confidence"] = 1.0
if "current_nav" not in st.session_state:
    st.session_state["current_nav"] = "🏠 Feed"
if "liked_posts" not in st.session_state:
    st.session_state["liked_posts"] = {20, 21, 30}
if "saved_posts" not in st.session_state:
    st.session_state["saved_posts"] = {21, 30}
if "post_comments" not in st.session_state:
    st.session_state["post_comments"] = {
        21: [
            {"user": "Elena_R", "text": "Crisp and totally organic! Loved the batch.", "time": "2h ago"},
            {"user": "Marcus_Dev", "text": "Great packaging! Arrived in 1 day.", "time": "1h ago"}
        ],
        30: [
            {"user": "Elena_R", "text": "Super fresh organic harvest.", "time": "3h ago"}
        ],
        20: [
            {"user": "CodeNinja", "text": "Super clear Python explanation for beginners.", "time": "5h ago"}
        ]
    }
if "posts_visible_limit" not in st.session_state:
    st.session_state["posts_visible_limit"] = 6
if "notifications" not in st.session_state:
    st.session_state["notifications"] = [
        {"icon": "🛡️", "title": "SafeAd AI Guard Active", "desc": "Multimodal visual and speech checks verified for current feed.", "time": "Just now"},
        {"icon": "🌟", "title": "Age Protection Verified", "desc": "Your profile safety protocols are dynamically enforced.", "time": "5m ago"},
        {"icon": "✅", "title": "Dataset Benchmark Synchronized", "desc": "10 video safety datasets updated across 6 risk categories.", "time": "1h ago"}
    ]

def is_age_restricted(text: str) -> bool:
    text_lower = (text or "").lower()
    for policy, langs in MULTILINGUAL_KEYWORDS.items():
        for lang, words in langs.items():
            for w in words:
                if w in text_lower:
                    return True
    return False

# =====================================================================
# AUTHENTICATION & AGE DETECTION ONBOARDING (DARK MODE)
# =====================================================================
if not st.session_state["logged_in"]:
    st.markdown("""
        <div style="text-align: center; margin-top: 40px; margin-bottom: 24px;">
            <div style="width: 60px; height: 60px; border-radius: 18px; background: linear-gradient(135deg, #6366f1 0%, #ec4899 100%); display: inline-flex; align-items: center; justify-content: center; color: white; font-weight: 800; font-size: 30px; box-shadow: 0 10px 30px rgba(99, 102, 241, 0.4);">✨</div>
            <h1 style="font-size: 34px; font-weight: 800; letter-spacing: -0.5px; margin-top: 14px; margin-bottom: 4px; color: #fff;">Aura Social</h1>
            <p style="color: #94a3b8; font-size: 15px;">Next-Gen Multimodal Trust & Safety Social Platform</p>
        </div>
    """, unsafe_allow_html=True)
    
    col_left, col_center, col_right = st.columns([1, 1.4, 1])
    
    with col_center:
        st.markdown("""
            <div style="background: #131d33; border: 1px solid #1e293b; border-radius: 20px; padding: 26px 24px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
                <h3 style="margin-top: 0; font-weight: 700; font-size: 18px; color: #fff; margin-bottom: 14px;">Sign In & Age Verification</h3>
            </div>
        """, unsafe_allow_html=True)
        
        user_input = st.text_input("Username or Handle", "RD_Sourav", placeholder="e.g. AlexMorgan")
        
        st.markdown("<p style='font-size:13px; font-weight:700; color:#cbd5e1; margin-top:14px; margin-bottom:6px;'>Select Verification Mode:</p>", unsafe_allow_html=True)
        auth_mode = st.radio(
            "Verification Mode",
            ["📷 Biometric Face Scan (Webcam)", "🧠 Behavioral Pattern Analysis"],
            label_visibility="collapsed"
        )
        
        category, conf = None, None
        
        if "Biometric" in auth_mode:
            st.info("A quick face photo calculates geometric contour ratios to establish child vs. adult safety guardrails.")
            cam_image = st.camera_input("Capture Face Snapshot")
            
            st.markdown("<p style='font-size:12px; color:#94a3b8; margin-top:6px;'>Simulate face geometry profile if camera is not enabled:</p>", unsafe_allow_html=True)
            face_sim = st.selectbox(
                "Face Geometry Profile",
                ["Choose simulation...", "Adult Profile (Mature Oval Features)", "Child Profile (Youth Round Features)"],
                label_visibility="collapsed"
            )
            
            if cam_image:
                try:
                    img = Image.open(cam_image)
                    img_np = np.array(img)
                    category, conf = estimate_age_from_face(img_np)
                except Exception as e:
                    st.error(f"Face scanner error: {e}")
            elif face_sim != "Choose simulation...":
                dummy_face = np.ones((128, 128, 3), dtype=np.uint8) * 240
                if "Child" in face_sim:
                    cv2.ellipse(dummy_face, (64, 64), (45, 45), 0, 0, 360, (255, 200, 180), -1)
                    cv2.circle(dummy_face, (49, 69), 7, (40, 40, 40), -1)
                    cv2.circle(dummy_face, (79, 69), 7, (40, 40, 40), -1)
                else:
                    cv2.ellipse(dummy_face, (64, 64), (36, 54), 0, 0, 360, (245, 190, 160), -1)
                    cv2.circle(dummy_face, (49, 54), 4, (40, 40, 40), -1)
                    cv2.circle(dummy_face, (79, 54), 4, (40, 40, 40), -1)
                category, conf = estimate_age_from_face(dummy_face)
                
        else:
            st.info("Analyzes simulated session query intent and watch retention metrics.")
            q_text = st.text_input("Sample search query stream", "python machine learning, computer vision tutorials")
            s_gk = st.slider("Educational Reel Retention (seconds / 60)", 0, 60, 20)
            s_adult = st.slider("General Ad Reel Retention (seconds / 100)", 0, 100, 75)
            
            if st.button("Evaluate Pattern Signature", use_container_width=True):
                queries = [q.strip() for q in q_text.split(",")]
                gk_w = [{"duration_watched": s_gk, "total_duration": 60}]
                ad_w = [{"duration_watched": s_adult, "total_duration": 100}]
                category, conf = estimate_age_from_behavior(queries, gk_w, ad_w)
                st.session_state["temp_eval"] = (category, conf)
            
            if "temp_eval" in st.session_state:
                category, conf = st.session_state["temp_eval"]

        if category is not None:
            is_child = (category == "Child")
            status_color = "#fbbf24" if is_child else "#34d399"
            st.markdown(f"""
                <div style="margin-top: 16px; padding: 14px 18px; border-radius: 12px; background: rgba(15, 23, 42, 0.8); border: 1px solid {status_color}; display: flex; align-items: center; justify-content: space-between;">
                    <div>
                        <div style="font-size: 12px; font-weight: 700; color: {status_color}; text-transform: uppercase;">Estimated Age Category</div>
                        <div style="font-size: 16px; font-weight: 800; color: #fff;">{category} <span style="font-size:13px; font-weight:600; color:#94a3b8;">({conf:.1%} confidence)</span></div>
                    </div>
                    <div style="font-size: 24px;">{'🛡️' if is_child else '🔓'}</div>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button("Enter Aura Social Feed ✨", type="primary", use_container_width=True):
                if not user_input.strip():
                    st.error("Please provide a valid username.")
                else:
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = user_input.strip()
                    st.session_state["age_category"] = category
                    st.session_state["age_confidence"] = conf
                    
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("SELECT id FROM Users WHERE username = ?", (user_input.strip(),))
                    usr = cursor.fetchone()
                    if not usr:
                        cursor.execute("INSERT INTO Users (username, password_hash, role) VALUES (?, 'demo_hash', 'social_user')", (user_input.strip(),))
                        uid = cursor.lastrowid
                    else:
                        uid = usr[0]
                        
                    cursor.execute("""
                        INSERT INTO AgeProfiles (user_id, method, prediction_class, confidence)
                        VALUES (?, ?, ?, ?)
                    """, (uid, "facial" if "Biometric" in auth_mode else "behavioral", category, conf))
                    conn.commit()
                    conn.close()
                    st.rerun()

# =====================================================================
# AUTHENTICATED PLATFORM EXPERIENCE (DARK THEME)
# =====================================================================
else:
    current_user = st.session_state["username"]
    age_category = st.session_state["age_category"]
    age_conf = st.session_state["age_confidence"]
    is_minor = (age_category == "Child")
    
    # -----------------------------------------------------------------
    # TOP AURA NAVBAR
    # -----------------------------------------------------------------
    status_bg = "rgba(245, 158, 11, 0.15)" if is_minor else "rgba(16, 185, 129, 0.15)"
    status_txt = "#fbbf24" if is_minor else "#34d399"
    status_icon = "🛡️" if is_minor else "✨"
    
    st.markdown(f"""
        <div class="aura-navbar">
            <div class="aura-brand">
                <div class="aura-logo-icon">A</div>
                <div class="aura-brand-title">AURA</div>
                <span style="background: linear-gradient(135deg, #6366f1, #ec4899); color: white; font-size: 10px; font-weight: 700; padding: 2px 8px; border-radius: 999px; letter-spacing: 0.5px;">SAFE-VISION</span>
            </div>
            <div class="aura-badge-user">
                <span style="font-size: 15px;">{status_icon}</span>
                <span style="color:#fff;">{current_user}</span>
                <span style="background: {status_bg}; color: {status_txt}; font-size: 11px; padding: 3px 9px; border-radius: 999px; font-weight: 700;">
                    {age_category} Guard
                </span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    nav_tabs = ["🏠 Feed", "🎬 Reels", "🔍 Explore", "➕ Create Post", "🔔 Alerts", "👤 Profile", "🛡️ Safety Hub"]
    selected_nav = st.radio(
        "Platform Navigation",
        nav_tabs,
        horizontal=True,
        label_visibility="collapsed",
        index=0 if st.session_state["current_nav"] not in nav_tabs else nav_tabs.index(st.session_state["current_nav"])
    )
    st.session_state["current_nav"] = selected_nav

    # -----------------------------------------------------------------
    # TAB 1: HOME SOCIAL FEED (UNLIMITED STREAMING & UNIQUE POSTS)
    # -----------------------------------------------------------------
    if selected_nav == "🏠 Feed":
        st.markdown("""
            <div class="stories-container">
                <div class="story-item"><div class="story-ring"><div class="story-avatar">🔭</div></div><div class="story-name">SpaceGK</div></div>
                <div class="story-item"><div class="story-ring"><div class="story-avatar">🌱</div></div><div class="story-name">EcoKids</div></div>
                <div class="story-item"><div class="story-ring"><div class="story-avatar">🤖</div></div><div class="story-name">AILab</div></div>
                <div class="story-item"><div class="story-ring"><div class="story-avatar">🍎</div></div><div class="story-name">OrganicFarm</div></div>
                <div class="story-item"><div class="story-ring"><div class="story-avatar">🎨</div></div><div class="story-name">ArtStudio</div></div>
                <div class="story-item"><div class="story-ring"><div class="story-avatar">⚡</div></div><div class="story-name">TechPulse</div></div>
                <div class="story-item"><div class="story-ring"><div class="story-avatar">🏔️</div></div><div class="story-name">AlpsExp</div></div>
                <div class="story-item"><div class="story-ring"><div class="story-avatar">☕</div></div><div class="story-name">CoffeeRoast</div></div>
            </div>
        """, unsafe_allow_html=True)
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT A.id, A.title, A.caption, A.file_path, COALESCE(U.username, 'AuraMember'), A.status, A.created_at 
            FROM Advertisements A
            LEFT JOIN Users U ON A.advertiser_id = U.id
            WHERE A.file_path NOT LIKE '%.mp4'
            ORDER BY A.id DESC
        """)
        all_db_posts = cursor.fetchall()
        conn.close()
        
        feed_posts = []
        seen_titles = set()
        for post in all_db_posts:
            pid, ptitle, pcap, pfile, puser, pstatus, pcreated = post
            if ptitle in seen_titles:
                continue
            seen_titles.add(ptitle)
            
            full_txt = f"{ptitle} {pcap or ''} {pfile}"
            is_flagged = (pstatus in ['rejected', 'under_review']) or is_age_restricted(full_txt)
            
            if is_minor and is_flagged:
                continue
                
            feed_posts.append({
                "id": pid,
                "title": ptitle,
                "caption": pcap or "",
                "file_path": pfile,
                "username": puser,
                "status": pstatus,
                "is_flagged": is_flagged,
                "created_at": pcreated or "Recently"
            })
            
        limit = st.session_state["posts_visible_limit"]
        visible_posts = feed_posts[:limit]
        
        col_feed_left, col_feed_mid, col_feed_right = st.columns([1, 1.8, 1])
        
        with col_feed_mid:
            for p in visible_posts:
                pid = p["id"]
                is_liked = pid in st.session_state["liked_posts"]
                is_saved = pid in st.session_state["saved_posts"]
                comments_list = st.session_state["post_comments"].get(pid, [])
                
                if p["is_flagged"]:
                    status_html = f'<span class="badge-pill badge-rejected">⚠️ Restricted: {p["status"].upper()}</span>'
                elif p["status"] == "approved":
                    status_html = '<span class="badge-pill badge-approved">✓ Verified Safe</span>'
                else:
                    status_html = '<span class="badge-pill badge-review">⏳ In Review</span>'
                    
                is_sponsored = "ad" in p["file_path"].lower() or "sponsor" in p["username"].lower() or p["status"] != "approved"
                sponsored_html = '<span class="badge-pill badge-sponsored">Sponsored</span>' if is_sponsored else ''

                st.markdown(f"""
                    <div class="aura-card">
                        <div class="aura-card-header">
                            <div class="card-user-info">
                                <div class="user-avatar-sm">{p['username'][0].upper()}</div>
                                <div>
                                    <div class="user-meta-name">{p['username']}</div>
                                    <div class="user-meta-time">{p['created_at']}</div>
                                </div>
                            </div>
                            <div style="display: flex; gap: 6px; align-items: center;">
                                {sponsored_html}
                                {status_html}
                            </div>
                        </div>
                """, unsafe_allow_html=True)
                
                resolved = resolve_media_path(p["file_path"])
                if resolved:
                    st.image(resolved, use_container_width=True)
                else:
                    st.caption("📷 Verified Visual Post")

                st.markdown(f"""
                    <div class="aura-card-caption">
                        <b>{p['username']}</b> {p['title']} — {p['caption']}
                        <div style="margin-top: 8px;">
                            <span class="aura-tag">#AuraSocial</span> <span class="aura-tag">#SafeAdAI</span> <span class="aura-tag">#VerifiedContent</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                c_act1, c_act2, c_act3, c_act4 = st.columns(4)
                with c_act1:
                    heart_icon = "❤️" if is_liked else "🤍"
                    like_count = 56 + (1 if is_liked else 0)
                    if st.button(f"{heart_icon} {like_count}", key=f"like_{pid}", use_container_width=True):
                        if is_liked:
                            st.session_state["liked_posts"].remove(pid)
                        else:
                            st.session_state["liked_posts"].add(pid)
                        st.rerun()
                with c_act2:
                    st.button(f"💬 {len(comments_list)}", key=f"cmt_btn_{pid}", use_container_width=True)
                with c_act3:
                    if st.button("↗️ Share", key=f"share_{pid}", use_container_width=True):
                        st.toast("Link copied to clipboard! 📋")
                with c_act4:
                    save_icon = "🔖 Saved" if is_saved else "🏷️ Save"
                    if st.button(save_icon, key=f"save_{pid}", use_container_width=True):
                        if is_saved:
                            st.session_state["saved_posts"].remove(pid)
                        else:
                            st.session_state["saved_posts"].add(pid)
                        st.rerun()
                        
                with st.expander(f"View comments ({len(comments_list)})", expanded=False):
                    if comments_list:
                        for c in comments_list:
                            st.markdown(f"<span style='color:#818cf8; font-weight:700;'>@{c['user']}</span>: <span style='color:#e2e8f0;'>{c['text']}</span>", unsafe_allow_html=True)
                    else:
                        st.caption("Be the first to comment!")
                    c_in1, c_in2 = st.columns([4, 1])
                    with c_in1:
                        new_comment_text = st.text_input("Add comment...", key=f"new_cmt_{pid}", label_visibility="collapsed", placeholder="Write a comment...")
                    with c_in2:
                        if st.button("Send", key=f"post_cmt_{pid}"):
                            if new_comment_text.strip():
                                if pid not in st.session_state["post_comments"]:
                                    st.session_state["post_comments"][pid] = []
                                st.session_state["post_comments"][pid].append({
                                    "user": current_user,
                                    "text": new_comment_text.strip(),
                                    "time": "Just now"
                                })
                                st.success("Comment posted!")
                                st.rerun()
                                
                st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                
            # Unlimited Infinite Feed Streamer
            if limit < len(feed_posts):
                if st.button("⚡ Load More Unique Posts", use_container_width=True):
                    st.session_state["posts_visible_limit"] += 4
                    st.rerun()
            else:
                st.markdown("<div style='text-align:center; padding:16px; color:#64748b; font-size:13px;'>✨ You've explored all current unique posts!</div>", unsafe_allow_html=True)

    # -----------------------------------------------------------------
    # TAB 2: CONTINUOUS VERTICAL SNAP-SCROLLING PORTRAIT REELS FEED
    # -----------------------------------------------------------------
    elif selected_nav == "🎬 Reels":
        # Expansive, diverse, verified non-repeating reels catalog
        ALL_REELS_CATALOG = [
            {"id": "reel_01", "title": "The Solar System for Kids", "topic": "Space Science", "desc": "Explore planets, stellar orbits, and galaxy wonders.", "gk": True, "restricted": False, "username": "CosmicGK", "video_url": "https://test-videos.co.uk/vids/bigbuckbunny/mp4/h264/360/Big_Buck_Bunny_360_10s_1MB.mp4"},
            {"id": "reel_02", "title": "Why is the Sky Blue?", "topic": "Physics & Optics", "desc": "Understanding sunlight Rayleigh scattering and atmospheric molecules.", "gk": True, "restricted": False, "username": "ScienceLab", "video_url": "https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4"},
            {"id": "reel_03", "title": "How Do Plants Make Food?", "topic": "Biology & Nature", "desc": "Photosynthesis process, chloroplasts, and solar energy capture.", "gk": True, "restricted": False, "username": "BioSphere", "video_url": "https://test-videos.co.uk/vids/jellyfish/mp4/h264/360/Jellyfish_360_10s_1MB.mp4"},
            {"id": "reel_04", "title": "SAFEWATCH-BENCH Benchmark Split", "topic": "General Video Safety", "desc": "Large-scale benchmark evaluating video guardrails across 6 policy tiers.", "restricted": False, "gk": False, "username": "SafeWatchTeam", "video_url": "https://www.w3schools.com/html/mov_bbb.mp4"},
            {"id": "reel_05", "title": "KuaiMod Short Video Split", "topic": "Content Governance", "desc": "SVP content governance dataset evaluating 15 violation categories.", "restricted": True, "gk": False, "username": "KuaishouTeam", "video_url": "https://media.w3.org/2010/05/sintel/trailer.mp4"},
            {"id": "reel_06", "title": "XD-Violence Audio-Visual Split", "topic": "Violence Detection", "desc": "Surveillance crime, physical combat, and acoustic impact cues.", "restricted": True, "gk": False, "username": "XDViolenceTeam", "video_url": "https://media.w3.org/2010/05/sintel/trailer.mp4"},
            {"id": "reel_07", "title": "UCF-Crime Anomaly Detection", "topic": "Crime Detection", "desc": "Surveillance tracking real-world hazards and incident triggers.", "restricted": True, "gk": False, "username": "UCFCrimeTeam", "video_url": "https://raw.githubusercontent.com/intel-iot-devkit/sample-videos/master/person-bicycle-car-detection.mp4"},
            {"id": "reel_08", "title": "FakeSV Fake News Split", "topic": "Fact Verification", "desc": "Multimodal fake news detection analyzing visual and speech cues.", "restricted": True, "gk": False, "username": "FakeSVTeam", "video_url": "https://www.w3schools.com/html/movie.mp4"},
            {"id": "reel_09", "title": "Autoshot Boundary Transitions", "topic": "Shot Detection", "desc": "Standard normal video transitions analyzing camera cuts.", "restricted": False, "gk": False, "username": "AutoShotTeam", "video_url": "https://media.w3.org/2010/05/bunny/trailer.mp4"},
            {"id": "reel_10", "title": "VHD11K Video Harmfulness Split", "topic": "Harm Recognition", "desc": "Evaluating algorithmic models for toxic and harmful visual filters.", "restricted": True, "gk": False, "username": "VHD11KTeam", "video_url": "https://test-videos.co.uk/vids/bigbuckbunny/mp4/h264/360/Big_Buck_Bunny_360_10s_1MB.mp4"},
            {"id": "reel_11", "title": "Violent Scenes Dataset (VSD)", "topic": "Scene Recognition", "desc": "Acoustic scream and violent combat scene recognition benchmarks.", "restricted": True, "gk": False, "username": "VSDTeam", "video_url": "https://media.w3.org/2010/05/sintel/trailer.mp4"},
            {"id": "reel_12", "title": "BLM-Guard Commercial Split", "topic": "Ad Policy Guard", "desc": "Commercial ad compliance across multiple risk tiers.", "restricted": True, "gk": False, "username": "BLMGuardTeam", "video_url": "https://test-videos.co.uk/vids/jellyfish/mp4/h264/360/Jellyfish_360_10s_1MB.mp4"},
            {"id": "reel_13", "title": "LSPD Mature Content Split", "topic": "Age Restriction", "desc": "Benchmark verifying age-restricted content management filters.", "restricted": True, "gk": False, "username": "LSPDTeam", "video_url": "https://media.w3.org/2010/05/video/movie_300.mp4"},
            {"id": "reel_14", "title": "Online Coding Lessons for Beginners", "topic": "Python & Web3", "desc": "Learn Python, data structures, and algorithms step by step.", "restricted": False, "gk": True, "username": "CodeNinja", "local_file": "coding_lessons.mp4"},
            {"id": "reel_15", "title": "Geometry Tutorial for Kids", "topic": "Visual Math", "desc": "Geometric shapes, angles, and 3D solids explained playfully.", "restricted": False, "gk": True, "username": "MathLab", "local_file": "geometry_class.mp4"},
            {"id": "reel_16", "title": "Grand Casino Vegas", "topic": "Casino & Betting", "desc": "Bet online, win cash jackpots, and spin slot machines.", "restricted": True, "gk": False, "username": "VegasSlots", "local_file": "casino_ad.mp4"},
            {"id": "reel_17", "title": "Action Thriller Movie: Blood & Guns", "topic": "Cinematic Action", "desc": "Combat sword choreography and high-stakes thriller scenes.", "restricted": True, "gk": False, "username": "ActionStudio", "local_file": "violence_ad.mp4"},
            {"id": "reel_18", "title": "Get Rich Fast Scheme", "topic": "Financial Warning", "desc": "Paisa double in 24 hours guaranteed with no investment.", "restricted": True, "gk": False, "username": "ScamAlert", "local_file": "scam_giveaway.mp4"},
            {"id": "reel_19", "title": "Deep Ocean Marine Biome", "topic": "Oceanography", "desc": "Bioluminescent jellyfish and deep oceanic ecosystems.", "restricted": False, "gk": True, "username": "OceanLife", "video_url": "https://test-videos.co.uk/vids/jellyfish/mp4/h264/360/Jellyfish_360_10s_1MB.mp4"},
            {"id": "reel_20", "title": "Microscopic Botanical Wonders", "topic": "Botany & Science", "desc": "Macro cellular petal structures and plant pollination.", "restricted": False, "gk": True, "username": "MicroWorld", "video_url": "https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4"}
        ]
        
        # Filter non-repeating reels by viewer age status
        active_reels = []
        for r in ALL_REELS_CATALOG:
            if is_minor and r.get("restricted", False):
                continue
            active_reels.append(r)
            
        st.markdown(f"""
            <div style="text-align: center; margin-bottom: 12px;">
                <span style="background: rgba(99, 102, 241, 0.15); color: #818cf8; border: 1px solid rgba(99, 102, 241, 0.35); padding: 4px 14px; border-radius: 999px; font-size: 12px; font-weight: 700;">
                    📱 {len(active_reels)} Unique Reels • Continuous Vertical Snap-Scroll
                </span>
            </div>
        """, unsafe_allow_html=True)
        
        # Build HTML slides
        slides_html = ""
        for idx, r in enumerate(active_reels):
            v_src = r.get("video_url")
            local_candidate = r.get("local_file")
            if local_candidate:
                resolved_local = resolve_media_path(local_candidate)
                if resolved_local:
                    v_src = get_media_base64_data_uri(resolved_local) or v_src
            if not v_src:
                v_src = "https://www.w3schools.com/html/mov_bbb.mp4"
                
            is_restr = r.get("restricted", False)
            status_tag = '<span class="status-pill status-restr">⚠️ RESTRICTED</span>' if is_restr else '<span class="status-pill status-safe">✓ SAFE STREAM</span>'
            topic = r.get("topic", "Reels")
            creator = r.get("username", "AuraCreator")
            title = r.get("title", "")
            desc = r.get("desc", "")
            
            slides_html += f"""
            <div class="reel-slide" data-index="{idx}">
                <div class="reel-top-bar">
                    <div class="audio-badge">🎵 {topic}</div>
                    <div>{status_tag}</div>
                </div>
                
                <video src="{v_src}" loop playsinline preload="metadata" onclick="togglePlay(this)"></video>
                <div class="play-indicator" onclick="togglePlayFromParent(this)">▶</div>
                
                <div class="reel-actions-column">
                    <div class="action-btn-wrap" onclick="toggleLike(this)">
                        <div class="action-btn">❤️</div>
                        <div class="action-lbl">3.{idx+1}k</div>
                    </div>
                    <div class="action-btn-wrap">
                        <div class="action-btn">💬</div>
                        <div class="action-lbl">{120 + idx * 7}</div>
                    </div>
                    <div class="action-btn-wrap" onclick="copyReelShare(this)">
                        <div class="action-btn">↗️</div>
                        <div class="action-lbl">Share</div>
                    </div>
                    <div class="action-btn-wrap" onclick="toggleSave(this)">
                        <div class="action-btn">🔖</div>
                        <div class="action-lbl">Save</div>
                    </div>
                    <div class="music-disc-wrap">
                        <div class="music-disc">🎵</div>
                    </div>
                </div>
                
                <div class="reel-bottom-meta">
                    <div class="creator-row">
                        <div class="creator-avatar">{creator[0].upper()}</div>
                        <div class="creator-handle">@{creator}</div>
                        <div class="follow-tag">Follow</div>
                    </div>
                    <div class="reel-title">{title}</div>
                    <div class="reel-desc">{desc}</div>
                </div>
            </div>
            """
            
        # Continuous Snap-Scroll Video Feed Component
        reels_feed_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                * {{ box-sizing: border-box; margin: 0; padding: 0; }}
                body {{
                    background: transparent;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                }}
                .reels-feed-container {{
                    width: 380px;
                    height: 700px;
                    overflow-y: scroll;
                    scroll-snap-type: y mandatory;
                    -webkit-overflow-scrolling: touch;
                    scrollbar-width: none;
                    border-radius: 28px;
                    background: #000;
                    box-shadow: 0 25px 60px rgba(0, 0, 0, 0.7);
                    border: 2px solid #1e293b;
                    position: relative;
                }}
                .reels-feed-container::-webkit-scrollbar {{
                    display: none;
                }}
                .reel-slide {{
                    position: relative;
                    width: 100%;
                    height: 100%;
                    min-height: 700px;
                    scroll-snap-align: start;
                    scroll-snap-stop: always;
                    overflow: hidden;
                    background: #000;
                }}
                video {{
                    width: 100%;
                    height: 100%;
                    object-fit: cover;
                    display: block;
                    cursor: pointer;
                }}
                .play-indicator {{
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%) scale(0.8);
                    width: 64px;
                    height: 64px;
                    border-radius: 50%;
                    background: rgba(0, 0, 0, 0.65);
                    color: white;
                    display: none;
                    align-items: center;
                    justify-content: center;
                    font-size: 28px;
                    pointer-events: none;
                    z-index: 30;
                    backdrop-filter: blur(8px);
                }}
                .reel-top-bar {{
                    position: absolute;
                    top: 14px;
                    left: 14px;
                    right: 14px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    z-index: 20;
                }}
                .audio-badge {{
                    background: rgba(15, 23, 42, 0.75);
                    backdrop-filter: blur(8px);
                    color: #fff;
                    padding: 5px 12px;
                    border-radius: 999px;
                    font-size: 11px;
                    font-weight: 600;
                }}
                .status-pill {{
                    padding: 4px 10px;
                    border-radius: 999px;
                    font-size: 10px;
                    font-weight: 800;
                    letter-spacing: 0.5px;
                }}
                .status-safe {{
                    background: rgba(16, 185, 129, 0.85);
                    color: #fff;
                }}
                .status-restr {{
                    background: rgba(239, 68, 68, 0.85);
                    color: #fff;
                }}
                .reel-actions-column {{
                    position: absolute;
                    right: 14px;
                    bottom: 75px;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    gap: 16px;
                    z-index: 20;
                }}
                .action-btn-wrap {{
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    cursor: pointer;
                }}
                .action-btn {{
                    background: rgba(15, 23, 42, 0.65);
                    backdrop-filter: blur(8px);
                    color: #fff;
                    width: 44px;
                    height: 44px;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 19px;
                    border: 1px solid rgba(255, 255, 255, 0.15);
                    transition: transform 0.15s ease, background 0.15s ease;
                }}
                .action-btn:hover {{
                    transform: scale(1.12);
                    background: rgba(99, 102, 241, 0.7);
                }}
                .action-lbl {{
                    font-size: 10px;
                    color: #fff;
                    font-weight: 700;
                    margin-top: 3px;
                    text-shadow: 0 1px 4px rgba(0,0,0,0.8);
                }}
                .music-disc-wrap {{
                    margin-top: 4px;
                }}
                .music-disc {{
                    width: 38px;
                    height: 38px;
                    border-radius: 50%;
                    background: radial-gradient(circle, #334155 30%, #0f172a 70%);
                    border: 2px solid rgba(255, 255, 255, 0.4);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 14px;
                    animation: spinDisc 3.5s linear infinite;
                }}
                @keyframes spinDisc {{
                    100% {{ transform: rotate(360deg); }}
                }}
                .reel-bottom-meta {{
                    position: absolute;
                    bottom: 0;
                    left: 0;
                    right: 70px;
                    padding: 24px 16px 18px 16px;
                    background: linear-gradient(180deg, transparent 0%, rgba(0,0,0,0.88) 100%);
                    color: #fff;
                    z-index: 20;
                }}
                .creator-row {{
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    margin-bottom: 8px;
                }}
                .creator-avatar {{
                    width: 36px;
                    height: 36px;
                    border-radius: 50%;
                    background: linear-gradient(135deg, #6366f1, #ec4899);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-weight: bold;
                    font-size: 15px;
                    border: 2px solid #fff;
                }}
                .creator-handle {{
                    font-weight: 700;
                    font-size: 14px;
                    color: #fff;
                    text-shadow: 0 1px 3px rgba(0,0,0,0.8);
                }}
                .follow-tag {{
                    background: rgba(255,255,255,0.22);
                    backdrop-filter: blur(4px);
                    border: 1px solid rgba(255,255,255,0.4);
                    color: #fff;
                    padding: 2px 10px;
                    border-radius: 999px;
                    font-size: 11px;
                    font-weight: 700;
                    cursor: pointer;
                }}
                .reel-title {{
                    font-weight: 700;
                    font-size: 14px;
                    margin-bottom: 4px;
                    text-shadow: 0 1px 3px rgba(0,0,0,0.8);
                }}
                .reel-desc {{
                    font-size: 12px;
                    color: rgba(255,255,255,0.88);
                    line-height: 1.35;
                    text-shadow: 0 1px 3px rgba(0,0,0,0.8);
                }}
                .toast-msg {{
                    position: fixed;
                    bottom: 24px;
                    left: 50%;
                    transform: translateX(-50%);
                    background: rgba(15, 23, 42, 0.95);
                    border: 1px solid rgba(255,255,255,0.2);
                    color: white;
                    padding: 8px 16px;
                    border-radius: 999px;
                    font-size: 12px;
                    font-weight: 600;
                    display: none;
                    z-index: 100;
                }}
            </style>
        </head>
        <body>
            <div class="reels-feed-container" id="reelsFeed">
                {slides_html}
            </div>
            <div id="toast" class="toast-msg">Copied! 📋</div>

            <script>
                // Intersection Observer for Automatic Snap Playback
                const observerOptions = {{
                    root: document.getElementById('reelsFeed'),
                    threshold: 0.6
                }};

                const reelObserver = new IntersectionObserver((entries) => {{
                    entries.forEach(entry => {{
                        const video = entry.target.querySelector('video');
                        const indicator = entry.target.querySelector('.play-indicator');
                        if (entry.isIntersecting) {{
                            if (video) {{
                                video.play().catch(e => console.log('Autoplay deferred:', e));
                                if (indicator) indicator.style.display = 'none';
                            }}
                        }} else {{
                            if (video) {{
                                video.pause();
                            }}
                        }}
                    }});
                }}, observerOptions);

                document.querySelectorAll('.reel-slide').forEach(slide => {{
                    reelObserver.observe(slide);
                }});

                function togglePlay(video) {{
                    const slide = video.closest('.reel-slide');
                    const indicator = slide.querySelector('.play-indicator');
                    if (video.paused) {{
                        video.play();
                        if (indicator) indicator.style.display = 'none';
                    }} else {{
                        video.pause();
                        if (indicator) indicator.style.display = 'flex';
                    }}
                }}

                function togglePlayFromParent(ind) {{
                    const slide = ind.closest('.reel-slide');
                    const video = slide.querySelector('video');
                    if (video) togglePlay(video);
                }}

                function toggleLike(btn) {{
                    const icon = btn.querySelector('.action-btn');
                    if (icon.innerText === '❤️') {{
                        icon.innerText = '🤍';
                    }} else {{
                        icon.innerText = '❤️';
                    }}
                }}

                function toggleSave(btn) {{
                    const icon = btn.querySelector('.action-btn');
                    if (icon.innerText === '🔖') {{
                        icon.innerText = '🏷️';
                    }} else {{
                        icon.innerText = '🔖';
                    }}
                }}

                function copyReelShare(btn) {{
                    const toast = document.getElementById('toast');
                    toast.style.display = 'block';
                    setTimeout(() => {{ toast.style.display = 'none'; }}, 1800);
                }}
            </script>
        </body>
        </html>
        """
        
        st.components.v1.html(reels_feed_html, height=715)

    # -----------------------------------------------------------------
    # TAB 3: EXPLORE & DISCOVERY (DARK THEME)
    # -----------------------------------------------------------------
    elif selected_nav == "🔍 Explore":
        st.markdown("<h2 style='font-size: 24px; font-weight: 800; color: #fff; margin-bottom: 6px;'>Discover & Explore</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color: #94a3b8; font-size: 14px;'>Find trending topics, educational lessons, and verified creators</p>", unsafe_allow_html=True)
        
        c_search, c_filter = st.columns([3, 1])
        with c_search:
            search_query = st.text_input("Search Aura", placeholder="Search topics, tags, or safety datasets (e.g. Science, Space, Coding)...", label_visibility="collapsed")
        with c_filter:
            category_filter = st.selectbox("Category Filter", ["All Content", "Science & Education", "Safety Benchmarks", "Creative Campaigns"], label_visibility="collapsed")
            
        st.markdown("""
            <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 20px;">
                <span class="badge-pill badge-approved" style="cursor: pointer;">🌟 Trending Today</span>
                <span class="badge-pill badge-sponsored" style="cursor: pointer;">🤖 AI Safety Research</span>
                <span class="badge-pill" style="background: rgba(255,255,255,0.06); color: #cbd5e1; cursor: pointer;">🪐 Space Explorations</span>
                <span class="badge-pill" style="background: rgba(255,255,255,0.06); color: #cbd5e1; cursor: pointer;">💻 Python & Web3</span>
                <span class="badge-pill" style="background: rgba(255,255,255,0.06); color: #cbd5e1; cursor: pointer;">🍎 Healthy Living</span>
            </div>
        """, unsafe_allow_html=True)
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, caption, file_path, status FROM Advertisements WHERE status = 'approved' ORDER BY id DESC")
        explore_items = cursor.fetchall()
        conn.close()
        
        cols = st.columns(3)
        for idx, item in enumerate(explore_items):
            iid, ititle, icap, ifile, istatus = item
            if search_query and (search_query.lower() not in ititle.lower() and search_query.lower() not in (icap or "").lower()):
                continue
            with cols[idx % 3]:
                st.markdown(f"""
                    <div class="explore-card" style="padding: 12px;">
                        <div style="font-weight: 700; font-size: 14px; margin-bottom: 6px; color:#fff;">{ititle}</div>
                        <div style="font-size: 12px; color: #94a3b8; margin-bottom: 8px;">{icap or 'Featured creator showcase'}</div>
                    </div>
                """, unsafe_allow_html=True)
                resolved = resolve_media_path(ifile)
                if resolved:
                    if resolved.endswith(".mp4"):
                        st.video(resolved)
                    else:
                        st.image(resolved, use_container_width=True)
                else:
                    st.caption("📷 Verified Media")

    # -----------------------------------------------------------------
    # TAB 4: CREATE STUDIO (DARK THEME)
    # -----------------------------------------------------------------
    elif selected_nav == "➕ Create Post":
        st.markdown("<h2 style='font-size: 24px; font-weight: 800; color: #fff; margin-bottom: 6px;'>Create & Publish Studio</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color: #94a3b8; font-size: 14px;'>Upload creative media with instant multimodal safety analysis (Vision + OCR + Speech)</p>", unsafe_allow_html=True)
        
        col_c_left, col_c_right = st.columns([1.1, 1])
        
        with col_c_left:
            with st.form("create_studio_form", clear_on_submit=False):
                post_title = st.text_input("Post Headline / Title", "Winter Wonder Festival")
                post_caption = st.text_area("Caption & Description", "Join our community gathering for hot cocoa, seasonal crafts, and festive music! #community #winter")
                post_type = st.radio("Media Type", ["Image Post (JPG/PNG)", "Video Reel (MP4)"], horizontal=True)
                uploaded_media = st.file_uploader("Drop Media Creative Here", type=["png", "jpg", "jpeg", "mp4"])
                submit_creative = st.form_submit_button("Submit to SafeAd AI Engine 🚀", type="primary", use_container_width=True)
                
            if submit_creative:
                if not uploaded_media:
                    st.error("Please select an image or video file to publish.")
                else:
                    os.makedirs("website/uploads", exist_ok=True)
                    ext = ".mp4" if "Video" in post_type else ".jpg"
                    f_name = f"user_{current_user}_{int(time.time())}{ext}"
                    save_path = os.path.join("website/uploads", f_name)
                    with open(save_path, "wb") as f:
                        f.write(uploaded_media.getbuffer())
                        
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("SELECT id FROM Users WHERE username = ?", (current_user,))
                    usr_row = cursor.fetchone()
                    uid = usr_row[0] if usr_row else 1
                    
                    cursor.execute("""
                        INSERT INTO Advertisements (title, advertiser_id, caption, file_path, status)
                        VALUES (?, ?, ?, ?, 'under_review')
                    """, (post_title, uid, post_caption, save_path))
                    new_ad_id = cursor.lastrowid
                    conn.commit()
                    conn.close()
                    
                    with st.spinner("Analyzing Multimodal Trust & Safety signals (Visual + Text + Speech)..."):
                        mod_result = run_multimodal_moderation(new_ad_id)
                        time.sleep(0.4)
                        
                    st.session_state["latest_studio_mod"] = mod_result
                    st.success(f"Creative analyzed! Pipeline ID: #{new_ad_id}")
                    
        with col_c_right:
            st.markdown("<h3 style='font-size: 18px; font-weight: 700; color: #fff;'>AI Moderation Breakdown</h3>", unsafe_allow_html=True)
            
            if "latest_studio_mod" in st.session_state:
                res = st.session_state["latest_studio_mod"]
                fused = res["final_score"]
                status = res["status"].upper()
                v_score = res["visual_score"]
                t_score = res["ocr_score"]
                s_score = res["speech_score"]
                
                status_class = "badge-approved" if status == "APPROVED" else ("badge-rejected" if status == "REJECTED" else "badge-review")
                
                st.markdown(f"""
                    <div class="safety-radar-box">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                            <span style="font-weight: 800; font-size: 16px; color:#fff;">Decision: {status}</span>
                            <span class="badge-pill {status_class}">Risk Score: {fused:.1f}%</span>
                        </div>
                        
                        <div class="meter-label"><span>Visual Layer Risk (40%)</span> <span>{v_score:.0f}%</span></div>
                        <div class="meter-bar"><div class="meter-fill" style="width: {v_score}%; background: {'#10b981' if v_score < 40 else '#ef4444'};"></div></div>
                        
                        <div class="meter-label"><span>OCR / NLP Text Risk (30%)</span> <span>{t_score:.0f}%</span></div>
                        <div class="meter-bar"><div class="meter-fill" style="width: {t_score}%; background: {'#10b981' if t_score < 40 else '#ef4444'};"></div></div>
                        
                        <div class="meter-label"><span>Acoustic / Speech Risk (30%)</span> <span>{s_score:.0f}%</span></div>
                        <div class="meter-bar"><div class="meter-fill" style="width: {s_score}%; background: {'#10b981' if s_score < 40 else '#ef4444'};"></div></div>
                        
                        <div style="margin-top: 14px; padding: 12px; border-radius: 8px; background: rgba(15, 23, 42, 0.7); font-size: 13px; border: 1px solid #1e293b; color:#cbd5e1;">
                            <b>Chain-of-Thought Rationale:</b><br>
                            <i>{res.get('explanation', '')}</i>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.info("Submit a post to view real-time multimodal safety scores and policy compliance.")

    # -----------------------------------------------------------------
    # TAB 5: NOTIFICATIONS & ALERTS (DARK THEME)
    # -----------------------------------------------------------------
    elif selected_nav == "🔔 Alerts":
        st.markdown("<h2 style='font-size: 24px; font-weight: 800; color: #fff; margin-bottom: 6px;'>Activity & Safety Alerts</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color: #94a3b8; font-size: 14px;'>Real-time platform events, policy audits, and social interactions</p>", unsafe_allow_html=True)
        
        for n in st.session_state["notifications"]:
            st.markdown(f"""
                <div style="background: #131d33; border: 1px solid #1e293b; border-radius: 14px; padding: 16px; margin-bottom: 12px; display: flex; align-items: flex-start; gap: 14px; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
                    <div style="font-size: 24px;">{n['icon']}</div>
                    <div style="flex: 1;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div style="font-weight: 700; font-size: 14px; color: #fff;">{n['title']}</div>
                            <div style="font-size: 12px; color: #64748b;">{n['time']}</div>
                        </div>
                        <div style="font-size: 13px; color: #94a3b8; margin-top: 4px;">{n['desc']}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    # -----------------------------------------------------------------
    # TAB 6: PROFILE & CREATOR HUB (DARK THEME)
    # -----------------------------------------------------------------
    elif selected_nav == "👤 Profile":
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM Users WHERE username = ?", (current_user,))
        usr_row = cursor.fetchone()
        uid = usr_row[0] if usr_row else 1
        
        cursor.execute("SELECT id, title, caption, file_path, status FROM Advertisements WHERE advertiser_id = ? ORDER BY id DESC", (uid,))
        user_posts = cursor.fetchall()
        conn.close()
        
        st.markdown(f"""
            <div class="profile-banner">
                <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 20px;">
                    <div style="display: flex; align-items: center; gap: 24px;">
                        <div class="profile-avatar-lg">{current_user[0].upper()}</div>
                        <div>
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <h2 style="margin: 0; font-size: 26px; font-weight: 800; color:#fff;">{current_user}</h2>
                                <span class="badge-pill {'badge-approved' if not is_minor else 'badge-review'}">
                                    {age_category} Verified ({age_conf:.0%})
                                </span>
                            </div>
                            <p style="color: #94a3b8; margin-top: 6px; font-size: 14px; margin-bottom: 0;">
                                Verified Aura Member • Trust & Safety Protocol Active
                            </p>
                        </div>
                    </div>
                    <div style="display: flex; gap: 14px;">
                        <div class="profile-stat-box">
                            <div class="profile-stat-val">{len(user_posts)}</div>
                            <div class="profile-stat-lbl">Posts</div>
                        </div>
                        <div class="profile-stat-box">
                            <div class="profile-stat-val">420</div>
                            <div class="profile-stat-lbl">Followers</div>
                        </div>
                        <div class="profile-stat-box">
                            <div class="profile-stat-val">285</div>
                            <div class="profile-stat-lbl">Following</div>
                        </div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        p_tab1, p_tab2, p_tab3 = st.tabs(["📸 Your Posts", "🔖 Saved Content", "🛡️ Safety Passport"])
        
        with p_tab1:
            if not user_posts:
                st.info("You haven't published any posts yet. Head over to 'Create Post' to start.")
            else:
                p_cols = st.columns(3)
                for idx, post in enumerate(user_posts):
                    pid, ptitle, pcap, pfile, pstatus = post
                    with p_cols[idx % 3]:
                        badge_cls = "badge-approved" if pstatus == "approved" else ("badge-rejected" if pstatus == "rejected" else "badge-review")
                        st.markdown(f"""
                            <div class="explore-card" style="padding: 10px; margin-bottom: 16px;">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                                    <span style="font-weight: 700; font-size: 13px; color:#fff;">{ptitle}</span>
                                    <span class="badge-pill {badge_cls}">{pstatus.upper()}</span>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                        resolved = resolve_media_path(pfile)
                        if resolved:
                            if resolved.endswith(".mp4"):
                                st.video(resolved)
                            else:
                                st.image(resolved, use_container_width=True)
                                
        with p_tab2:
            saved_ids = list(st.session_state["saved_posts"])
            if not saved_ids:
                st.info("No saved posts yet.")
            else:
                st.write(f"You have **{len(saved_ids)}** items bookmarked in your personal collection.")
                
        with p_tab3:
            st.markdown(f"""
                <div style="background: #131d33; border: 1px solid #1e293b; border-radius: 16px; padding: 20px;">
                    <h4 style="margin-top: 0; font-weight: 700; color:#fff;">Account Safety Transparency</h4>
                    <p style="font-size: 13px; color: #94a3b8;">Aura Social continuously inspects content delivery through automated biometric verification and multimodal content policy classifiers.</p>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-top: 14px;">
                        <div style="background: rgba(15, 23, 42, 0.7); padding: 14px; border-radius: 10px;">
                            <div style="font-size: 12px; color: #94a3b8;">Age Bracket Classification</div>
                            <div style="font-size: 16px; font-weight: 800; color: #fff;">{age_category}</div>
                        </div>
                        <div style="background: rgba(15, 23, 42, 0.7); padding: 14px; border-radius: 10px;">
                            <div style="font-size: 12px; color: #94a3b8;">Classification Confidence</div>
                            <div style="font-size: 16px; font-weight: 800; color: #fff;">{age_conf:.2%}</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        if st.button("🚪 Sign Out of Session", use_container_width=True):
            st.session_state["logged_in"] = False
            st.session_state["username"] = ""
            st.session_state["age_category"] = "Not a Child"
            st.rerun()

    # -----------------------------------------------------------------
    # TAB 7: SAFETY & TRANSPARENCY AUDIT HUB (DARK THEME)
    # -----------------------------------------------------------------
    elif selected_nav == "🛡️ Safety Hub":
        st.markdown("<h2 style='font-size: 24px; font-weight: 800; color: #fff; margin-bottom: 6px;'>Trust & Safety Intelligence Center</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color: #94a3b8; font-size: 14px;'>Real-time tamper-evident audit logs and active policy catalogs</p>", unsafe_allow_html=True)
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, ad_id, timestamp, model_version, final_decision, log_details 
            FROM AuditLogs 
            ORDER BY id DESC LIMIT 15
        """)
        logs = cursor.fetchall()
        
        cursor.execute("SELECT name, description, age_restriction FROM PolicyRules")
        policies = cursor.fetchall()
        conn.close()
        
        t_hub1, t_hub2 = st.tabs(["📋 System Audit Logs", "📜 Content Policies"])
        
        with t_hub1:
            if logs:
                table_data = [{"Log ID": l[0], "Target Ad ID": l[1], "Timestamp": l[2], "Model Engine": l[3], "Decision": l[4].upper(), "AI Rationale": l[5]} for l in logs]
                st.dataframe(table_data, use_container_width=True)
            else:
                st.info("No audit transactions currently recorded.")
                
        with t_hub2:
            for pol in policies:
                p_name, p_desc, p_age = pol
                st.markdown(f"""
                    <div style="background: #131d33; border: 1px solid #1e293b; border-radius: 12px; padding: 14px; margin-bottom: 10px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-weight: 700; font-size: 15px; color:#fff;">{p_name}</span>
                            <span class="badge-pill badge-review">Min Age: {p_age}+</span>
                        </div>
                        <div style="font-size: 13px; color: #94a3b8; margin-top: 4px;">{p_desc}</div>
                    </div>
                """, unsafe_allow_html=True)
