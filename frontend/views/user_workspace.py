import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

try:
    import torch
    torch.backends.mkldnn.enabled = False
    torch.set_num_threads(1)
except Exception:
    pass

import streamlit as st
import time
import sys
import warnings
from pathlib import Path
from PIL import Image, ImageOps
import numpy as np
import cv2

warnings.filterwarnings("ignore")

# Setup sys.path to resolve Sooraj's ai.face_age and models without collision
face_age_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../sooraj_face_age_core/face-age"))
if face_age_dir not in sys.path:
    sys.path.insert(0, face_age_dir)

import importlib.util
spec = importlib.util.spec_from_file_location("sooraj_classifier", os.path.join(face_age_dir, "website", "classifier.py"))
sooraj_classifier = importlib.util.module_from_spec(spec)
sys.modules["sooraj_classifier"] = sooraj_classifier
spec.loader.exec_module(sooraj_classifier)

estimate_age_from_face = sooraj_classifier.estimate_age_from_face
estimate_detailed_age_from_face = sooraj_classifier.estimate_detailed_age_from_face
detect_and_crop_face = sooraj_classifier.detect_and_crop_face
verify_id_card_and_live_face = sooraj_classifier.verify_id_card_and_live_face
process_pdf_id_document = sooraj_classifier.process_pdf_id_document
extract_dob_and_age_from_id = sooraj_classifier.extract_dob_and_age_from_id
extract_arcface_embedding = sooraj_classifier.extract_arcface_embedding
compute_similarity_from_embeddings = sooraj_classifier.compute_similarity_from_embeddings
detect_photo_spoof = sooraj_classifier.detect_photo_spoof
annotate_live_frame = sooraj_classifier.annotate_live_frame
Realtime30FPSVisionEngine = sooraj_classifier.Realtime30FPSVisionEngine

from frontend.services.safead_client import SafeAdClient
from frontend.styles.instagram_theme import render_instagram_logo, render_stories_bar

# =============================================================================
# REELS CATALOG: ORGANIC VIDEOS & SAFEAD SPONSORED ADS
# =============================================================================
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

DEFAULT_REELS = [
    {
        "id": "reel_cyber",
        "type": "organic",
        "creator": "cyber_future",
        "creator_avatar": "🤖",
        "is_verified": True,
        "title": "CYBER CITY 2099",
        "caption": "Flying through neon clouds at 200mph 🌇✨ Who else wants to live in this aesthetic? #cyberpunk #neon #reels #future #synthwave",
        "audio": "ODESZA • A Moment Apart (Cyberpunk Mix) 🎵",
        "likes": 184500,
        "comments_count": 2310,
        "shares_count": 45200,
        "video_path": os.path.join(BASE_DIR, "frontend/assets/reels/reel_cyberpunk.mp4"),
        "comments": [
            {"user": "neon_rider", "text": "The lighting here is just insane 🔥", "time": "2h", "likes": 342},
            {"user": "synth_wave", "text": "Song name please?? 🎧", "time": "4h", "likes": 88},
            {"user": "future_dev", "text": "Rendered in real-time? Looks cinematic!", "time": "6h", "likes": 120}
        ]
    },
    {
        "id": "ad_coding",
        "type": "sponsored",
        "creator": "code_academy_pro",
        "creator_avatar": "💻",
        "is_verified": True,
        "sponsored_label": "Sponsored • SafeAd Verified ✅",
        "safety_policy": "SAFE_FOR_ALL",
        "title": "Master Python & AI in 30 Days",
        "caption": "Unlock high-paying AI skills with interactive bite-sized lessons! 🚀 Certified safe for all audiences by SafeAd AI. #coding #python #learntocode #ai #edtech",
        "cta_text": "Start Free Course ↗",
        "audio": "Lofi Coding Beats • Deep Focus Flow 🎵",
        "likes": 64200,
        "comments_count": 845,
        "shares_count": 12400,
        "video_path": os.path.join(BASE_DIR, "sample_ad_media/coding_lessons.mp4"),
        "comments": [
            {"user": "sophia_tech", "text": "Completed this last month, landed my first freelance gig!", "time": "5h", "likes": 95},
            {"user": "dev_dan", "text": "Is this beginner friendly?", "time": "1d", "likes": 14}
        ]
    },
    {
        "id": "reel_aurora",
        "type": "organic",
        "creator": "aurora_explorers",
        "creator_avatar": "🌌",
        "is_verified": True,
        "title": "NIGHT OF THE AURORA",
        "caption": "Dancing emerald curtains in Tromsø, Norway 🇳🇴 Nature never fails to amaze. Tag someone who needs to see this! 💚 #aurora #norway #travel #nightsky #nature",
        "audio": "Hans Zimmer • Time (Arctic Ambient Mix) 🎵",
        "likes": 321800,
        "comments_count": 4120,
        "shares_count": 89100,
        "video_path": os.path.join(BASE_DIR, "frontend/assets/reels/reel_aurora.mp4"),
        "comments": [
            {"user": "wanderlust_jen", "text": "Bucket list dream destination 😍", "time": "1h", "likes": 512},
            {"user": "alex_lens", "text": "The green color grading is pure magic!", "time": "3h", "likes": 204}
        ]
    },
    {
        "id": "ad_geometry",
        "type": "sponsored",
        "creator": "visual_math_lab",
        "creator_avatar": "📐",
        "is_verified": True,
        "sponsored_label": "Sponsored • SafeAd Verified ✅",
        "safety_policy": "SAFE_FOR_ALL",
        "title": "Interactive 3D Geometry App",
        "caption": "Visualizing complex 3D topological surfaces and mathematical patterns! SafeAd AI certified educational ad. #math #geometry #education #interactive",
        "cta_text": "Try 3D Demo ↗",
        "audio": "Acoustic Math • Classical Study 🎵",
        "likes": 49800,
        "comments_count": 612,
        "shares_count": 9800,
        "video_path": os.path.join(BASE_DIR, "sample_ad_media/geometry_class.mp4"),
        "comments": [
            {"user": "math_prof_dave", "text": "Showing this to my students tomorrow! Excellent visualization.", "time": "3h", "likes": 140}
        ]
    },
    {
        "id": "reel_sunset",
        "type": "organic",
        "creator": "golden_hour_ocean",
        "creator_avatar": "🌊",
        "is_verified": False,
        "title": "GOLDEN HOUR SWELL",
        "caption": "Catching the sunset over calm ocean waters 🌅 Nothing clears the mind like the rhythm of the waves. #sunset #ocean #goldenhour #beachlife #relax",
        "audio": "Ocean Waves & Acoustic Guitar • Sunset Peace 🎵",
        "likes": 152000,
        "comments_count": 1890,
        "shares_count": 34100,
        "video_path": os.path.join(BASE_DIR, "frontend/assets/reels/reel_sunset_ocean.mp4"),
        "comments": [
            {"user": "salt_water_soul", "text": "That reflection on the water is pure art ✨", "time": "2h", "likes": 180}
        ]
    },
    {
        "id": "reel_urban",
        "type": "organic",
        "creator": "tokyo_night_run",
        "creator_avatar": "🏎️",
        "is_verified": True,
        "title": "MIDNIGHT EXPRESSWAY",
        "caption": "Midnight cruise through the neon arteries of Tokyo 🌃 Light streaks and city pulse. Turn the volume up! #tokyo #nightdrive #carsoftiktok #speed #jdm",
        "audio": "Kavinsky • Nightcall (Tokyo Synthwave) 🎵",
        "likes": 278400,
        "comments_count": 3450,
        "shares_count": 67200,
        "video_path": os.path.join(BASE_DIR, "frontend/assets/reels/reel_urban_lights.mp4"),
        "comments": [
            {"user": "gtr_fanatic", "text": "The JDM vibe is completely unmatched 🇯🇵", "time": "4h", "likes": 310}
        ]
    }
]

def format_count(n: int) -> str:
    """Format counts into Instagram style: 142.5K or 1.2M"""
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    elif n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


def user_dashboard():
    # Session state initialization
    if "user_page_view" not in st.session_state:
        st.session_state["user_page_view"] = "feed"  # 'feed' or 'verification'

    if "verified_age_category" not in st.session_state:
        st.session_state["verified_age_category"] = None
        st.session_state["verified_age_norm"] = None
        st.session_state["verification_data"] = None

    if "logged_in_username" not in st.session_state:
        st.session_state["logged_in_username"] = "social_explorer"

    if "current_reel_idx" not in st.session_state:
        st.session_state["current_reel_idx"] = 0

    if "liked_reels" not in st.session_state:
        st.session_state["liked_reels"] = set()

    if "saved_reels" not in st.session_state:
        st.session_state["saved_reels"] = set()

    if "reel_comments_store" not in st.session_state:
        st.session_state["reel_comments_store"] = {r["id"]: list(r["comments"]) for r in DEFAULT_REELS}

    if "show_comments_for" not in st.session_state:
        st.session_state["show_comments_for"] = None

    if "reels_filter" not in st.session_state:
        st.session_state["reels_filter"] = "ALL"  # 'ALL', 'ORGANIC', 'SPONSORED'

    user_norm = st.session_state.get("verified_age_norm", "AGE_18_PLUS")
    user_cat = st.session_state.get("verified_age_category", "18 and above")
    username = st.session_state.get("logged_in_username", "social_explorer")
    is_verified_account = st.session_state.get("verified_age_category") is not None

    # Render Instagram App Header
    render_instagram_logo(subtitle="REELS FEED")

    # Navigation Pills (Reels Feed vs Identity Verification)
    c_nav1, c_nav2 = st.columns([1, 1])
    with c_nav1:
        if st.button("🎥 Explore Reels Feed", key="nav_btn_reels", use_container_width=True, 
                     type="primary" if st.session_state["user_page_view"] == "feed" else "secondary"):
            st.session_state["user_page_view"] = "feed"
            st.rerun()
    with c_nav2:
        badge_text = "🛡️ Verified Account ✓" if is_verified_account else "🛡️ Get Verified (Blue Badge)"
        if st.button(badge_text, key="nav_btn_verify", use_container_width=True,
                     type="primary" if st.session_state["user_page_view"] == "verification" else "secondary"):
            st.session_state["user_page_view"] = "verification"
            st.rerun()

    # =========================================================================
    # VIEW 1: AUTHENTIC INSTAGRAM REELS SECTION
    # =========================================================================
    if st.session_state["user_page_view"] == "feed":
        # 1. Instagram Stories Carousel
        render_stories_bar()

        # 2. Filter tabs: All, Organic Reels, Sponsored Ads
        f_col1, f_col2, f_col3 = st.columns(3)
        with f_col1:
            if st.button("🌟 All Feed", key="flt_all", use_container_width=True,
                         type="primary" if st.session_state["reels_filter"] == "ALL" else "secondary"):
                st.session_state["reels_filter"] = "ALL"
                st.session_state["current_reel_idx"] = 0
                st.rerun()
        with f_col2:
            if st.button("🎥 Organic Reels", key="flt_org", use_container_width=True,
                         type="primary" if st.session_state["reels_filter"] == "ORGANIC" else "secondary"):
                st.session_state["reels_filter"] = "ORGANIC"
                st.session_state["current_reel_idx"] = 0
                st.rerun()
        with f_col3:
            if st.button("🛡️ Sponsored Ads", key="flt_ads", use_container_width=True,
                         type="primary" if st.session_state["reels_filter"] == "SPONSORED" else "secondary"):
                st.session_state["reels_filter"] = "SPONSORED"
                st.session_state["current_reel_idx"] = 0
                st.rerun()

        # Compile Reels List with SafeAd backend ads if available
        active_reels = list(DEFAULT_REELS)
        
        # Filter based on user selection
        if st.session_state["reels_filter"] == "ORGANIC":
            active_reels = [r for r in active_reels if r["type"] == "organic"]
        elif st.session_state["reels_filter"] == "SPONSORED":
            active_reels = [r for r in active_reels if r["type"] == "sponsored"]

        if not active_reels:
            st.info("No reels found for this category.")
            return

        total_reels = len(active_reels)
        idx = st.session_state["current_reel_idx"] % total_reels
        current_reel = active_reels[idx]
        reel_id = current_reel["id"]

        is_liked = reel_id in st.session_state["liked_reels"]
        is_saved = reel_id in st.session_state["saved_reels"]
        like_count = current_reel["likes"] + (1 if is_liked else 0)
        comments_list = st.session_state["reel_comments_store"].get(reel_id, current_reel.get("comments", []))
        comment_count = len(comments_list)

        # ---------------------------------------------------------------------
        # REEL VIEWPORT CONTAINER (9:16 Responsive Card)
        # ---------------------------------------------------------------------
        st.markdown("<div class='reel-wrapper'>", unsafe_allow_html=True)
        
        # Center column for mobile & desktop reel centering
        c_spacer_l, c_reel, c_spacer_r = st.columns([1, 4, 1])
        
        with c_reel:
            # Reel Header Bar
            badge_icon = "✓" if current_reel.get("is_verified") else ""
            st.markdown(f"""
            <div style="background:#121212; border:1px solid #262626; border-radius:16px 16px 0 0; padding:12px 16px; display:flex; justify-content:space-between; align-items:center;">
                <div style="display:flex; align-items:center; gap:10px;">
                    <div style="width:34px; height:34px; border-radius:50%; background:linear-gradient(45deg,#f09433,#dc2743,#bc1888); padding:1.5px; display:flex; align-items:center; justify-content:center;">
                        <div style="width:100%; height:100%; border-radius:50%; background:#181818; display:flex; align-items:center; justify-content:center; font-size:16px;">
                            {current_reel.get('creator_avatar', '👤')}
                        </div>
                    </div>
                    <div>
                        <div style="font-size:14px; font-weight:700; color:#ffffff; display:flex; align-items:center; gap:4px;">
                            @{current_reel['creator']}
                            <span style="color:#0095f6; font-size:12px; font-weight:800;">{badge_icon}</span>
                        </div>
                        <div style="font-size:11px; color:#8e8e8e;">
                            {('🛡️ ' + current_reel.get('sponsored_label', 'Sponsored')) if current_reel['type'] == 'sponsored' else 'Original Audio'}
                        </div>
                    </div>
                </div>
                <div style="font-size:12px; font-weight:700; color:#8e8e8e;">
                    {idx + 1} / {total_reels}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Video player
            video_file = current_reel.get("video_path")
            if video_file and os.path.exists(video_file):
                st.video(video_file, autoplay=True, loop=True)
            else:
                st.warning("Video asset loading...")

            # Reel Info & Caption Overlay
            sponsored_html = ""
            if current_reel["type"] == "sponsored":
                sponsored_html = f"""
                <div style="margin-bottom:8px;">
                    <span style="background:rgba(0,149,246,0.18); border:1px solid rgba(0,149,246,0.4); color:#38bdf8; font-size:11px; font-weight:700; padding:3px 8px; border-radius:6px;">
                        🛡️ SafeAd Verified • Policy: {current_reel.get('safety_policy', 'SAFE_FOR_ALL')}
                    </span>
                </div>
                """

            st.markdown(f"""
            <div style="background:#121212; border:1px solid #262626; border-top:none; padding:14px 16px; border-radius:0 0 16px 16px;">
                {sponsored_html}
                <div style="font-size:14px; font-weight:700; color:#ffffff; margin-bottom:4px;">
                    {current_reel.get('title', '')}
                </div>
                <div style="font-size:13px; color:#e2e8f0; line-height:1.4; margin-bottom:8px;">
                    {current_reel.get('caption', '')}
                </div>
                <div style="display:flex; align-items:center; gap:6px; font-size:11px; color:#8e8e8e; margin-bottom:12px;">
                    <span>🎵</span>
                    <span>{current_reel.get('audio', 'Original Sound')}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # -----------------------------------------------------------------
            # REELS INTERACTIVE ACTION BAR (Likes, Comments, Share, Save)
            # -----------------------------------------------------------------
            act_col1, act_col2, act_col3, act_col4 = st.columns(4)
            with act_col1:
                heart_label = f"❤️ {format_count(like_count)}" if is_liked else f"🤍 {format_count(like_count)}"
                if st.button(heart_label, key=f"btn_like_{reel_id}", use_container_width=True):
                    if is_liked:
                        st.session_state["liked_reels"].remove(reel_id)
                    else:
                        st.session_state["liked_reels"].add(reel_id)
                        st.toast("Liked! ❤️", icon="❤️")
                    st.rerun()

            with act_col2:
                comm_open = (st.session_state["show_comments_for"] == reel_id)
                comm_label = f"💬 {format_count(comment_count)}"
                if st.button(comm_label, key=f"btn_comm_{reel_id}", use_container_width=True,
                             type="primary" if comm_open else "secondary"):
                    st.session_state["show_comments_for"] = None if comm_open else reel_id
                    st.rerun()

            with act_col3:
                if st.button(f"✈️ {format_count(current_reel['shares_count'])}", key=f"btn_share_{reel_id}", use_container_width=True):
                    st.toast("Link copied to clipboard! 📋", icon="✈️")

            with act_col4:
                save_label = "🔖 Saved" if is_saved else "🔖 Save"
                if st.button(save_label, key=f"btn_save_{reel_id}", use_container_width=True):
                    if is_saved:
                        st.session_state["saved_reels"].remove(reel_id)
                    else:
                        st.session_state["saved_reels"].add(reel_id)
                        st.toast("Saved to collection! 🔖", icon="🔖")
                    st.rerun()

            # Optional Call-To-Action button for Sponsored ads
            if current_reel["type"] == "sponsored" and current_reel.get("cta_text"):
                if st.button(f"👉 {current_reel['cta_text']}", key=f"cta_{reel_id}", type="primary", use_container_width=True):
                    st.toast("Redirecting to advertiser landing page...", icon="🚀")

            # -----------------------------------------------------------------
            # INTERACTIVE COMMENTS DRAWER
            # -----------------------------------------------------------------
            if st.session_state["show_comments_for"] == reel_id:
                st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
                st.markdown("""
                <div style="background:#181818; border:1px solid #262626; border-radius:12px; padding:14px; margin-bottom:12px;">
                    <div style="font-size:13px; font-weight:700; color:#ffffff; margin-bottom:10px; border-bottom:1px solid #262626; padding-bottom:6px;">
                        💬 Comments
                    </div>
                """, unsafe_allow_html=True)
                
                for c in comments_list:
                    st.markdown(f"""
                    <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:10px; font-size:12px;">
                        <div>
                            <b style="color:#ffffff;">@{c['user']}</b> &nbsp;
                            <span style="color:#d1d5db;">{c['text']}</span><br>
                            <span style="color:#6b7280; font-size:10px;">{c.get('time', 'Just now')}</span>
                        </div>
                        <div style="color:#6b7280; font-size:11px; cursor:pointer;">
                            ❤️ {c.get('likes', 0)}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                st.markdown("</div>", unsafe_allow_html=True)

                # Add new comment input
                new_comm = st.text_input("Add a comment...", key=f"input_comm_{reel_id}", placeholder="Add a comment as @" + username)
                if st.button("Post Comment", key=f"post_comm_{reel_id}", use_container_width=True):
                    if new_comm.strip():
                        comments_list.append({
                            "user": username,
                            "text": new_comm.strip(),
                            "time": "Just now",
                            "likes": 0
                        })
                        st.session_state["reel_comments_store"][reel_id] = comments_list
                        st.toast("Comment posted! 💬", icon="💬")
                        st.rerun()

            # -----------------------------------------------------------------
            # REELS NAVIGATION (PREV / NEXT)
            # -----------------------------------------------------------------
            st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
            prev_col, next_col = st.columns(2)
            with prev_col:
                if st.button("⬆️ Previous Reel", key="btn_prev_reel", use_container_width=True):
                    st.session_state["current_reel_idx"] = (idx - 1) % total_reels
                    st.session_state["show_comments_for"] = None
                    st.rerun()
            with next_col:
                if st.button("⬇️ Next Reel", key="btn_next_reel", use_container_width=True, type="primary"):
                    st.session_state["current_reel_idx"] = (idx + 1) % total_reels
                    st.session_state["show_comments_for"] = None
                    st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    # =========================================================================
    # VIEW 2: INSTAGRAM BIOMETRIC KYC & BLUE BADGE VERIFICATION
    # =========================================================================
    elif st.session_state["user_page_view"] == "verification":
        st.markdown("""
        <div style="background:linear-gradient(135deg, #181818 0%, #1f1f1f 100%); border:1px solid #262626; border-radius:16px; padding:20px 24px; margin-bottom:20px;">
            <div style="display:flex; align-items:center; gap:12px; margin-bottom:6px;">
                <div style="font-size:32px;">🛡️</div>
                <div>
                    <h2 style="margin:0; font-size:22px; color:#ffffff; font-weight:700;">Instagram Verified Badge Application</h2>
                    <p style="margin:0; font-size:13px; color:#8e8e8e;">Confirm your government ID and live camera biometrics to receive the blue checkmark & age-curated access.</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # User Credentials Box
        st.markdown("""
        <div class="ig-card">
            <div class="ig-card-header">
                <div class="ig-card-title">👤 Account Credentials</div>
            </div>
            <p style="font-size:13px; color:#8e8e8e; margin-bottom:12px;">Enter your username and password below. Upon freezing the live camera and cross-matching with your ID, your account will receive the verified blue checkmark.</p>
        """, unsafe_allow_html=True)

        col_u1, col_u2, col_u3 = st.columns([1.5, 1.5, 1.2])
        with col_u1:
            username_input = st.text_input("Username", value=st.session_state.get("auth_username", username), key="auth_usr_input")
        with col_u2:
            password_input = st.text_input("Password", type="password", value=st.session_state.get("auth_password", ""), key="auth_pwd_input")
        with col_u3:
            st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
            db = st.session_state.get("user_db", {
                "social_explorer": {"password": "demo", "category": "18 and above", "norm": "AGE_18_PLUS"},
                "souravrd": {"password": "loyola", "category": "18 and above", "norm": "AGE_18_PLUS"}
            })
            if username_input in db and password_input and db[username_input].get("password") == password_input:
                if st.button("⚡ Quick Login", use_container_width=True, help="Log in directly with existing password"):
                    st.session_state["logged_in_username"] = username_input
                    st.session_state["verified_age_category"] = db[username_input]["category"]
                    st.session_state["verified_age_norm"] = db[username_input]["norm"]
                    st.session_state["user_page_view"] = "feed"
                    st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("### 🆔 ID Card Verification & Live Face Cross-Matching")
        c_id, c_live = st.columns([1, 1], gap="medium")

        # ---------------------------------------------------------------------
        # 1. UPLOAD OFFICIAL ID CARD
        # ---------------------------------------------------------------------
        with c_id:
            st.markdown("#### 1. Upload Official ID Card")
            st.caption("Supports Passport, Driving License, Student ID, Aadhaar (JPG, PNG, PDF)")
            up_id = st.file_uploader("Upload ID Card Scan or PDF", type=["jpg", "jpeg", "png", "pdf"], key="t1_id_upload")
            
            id_image_np = None
            id_pdf_text = ""
            if up_id is not None:
                try:
                    if up_id.name.lower().endswith(".pdf"):
                        pdf_bytes = up_id.read()
                        id_image_np, id_pdf_text = process_pdf_id_document(pdf_bytes)
                        if id_image_np is not None:
                            st.success(f"📄 PDF Loaded: '{up_id.name}' (First page rendered)")
                        else:
                            st.error(f"Failed to process PDF: {id_pdf_text}")
                    else:
                        up_id.seek(0)
                        pil_img = Image.open(up_id)
                        pil_img = ImageOps.exif_transpose(pil_img)
                        id_image_np = np.array(pil_img.convert("RGB"))
                except Exception as e:
                    st.error(f"Error loading uploaded ID: {e}")
                    
            if id_image_np is not None:
                st.image(id_image_np, caption="Scanned ID Card / PDF Page", width="stretch")
                
                # Immediate OCR analysis upon upload
                cache_key = f"{getattr(up_id, 'name', 'id')}_{id_image_np.shape}_{id_image_np.sum() % 1000000}"
                if st.session_state.get("cached_ocr_key") != cache_key or "cached_ocr_res" not in st.session_state:
                    with st.spinner("🔍 Reading ID Card text & Date of Birth via EasyOCR..."):
                        dob_res = extract_dob_and_age_from_id(id_image_np, pdf_text=id_pdf_text)
                        if len(dob_res) == 4:
                            extracted_dob_str, id_calc_age, id_cat, ocr_log = dob_res
                        else:
                            extracted_dob_str, id_calc_age, id_cat = dob_res
                            ocr_log = ""
                        st.session_state["cached_ocr_key"] = cache_key
                        st.session_state["cached_ocr_res"] = (extracted_dob_str, id_calc_age, id_cat, ocr_log)
                else:
                    extracted_dob_str, id_calc_age, id_cat, ocr_log = st.session_state["cached_ocr_res"]

                # Feedback badge
                if extracted_dob_str and "Estimated" not in extracted_dob_str:
                    st.success(f"✅ **Extracted ID DOB:** **`{extracted_dob_str}`** &nbsp;|&nbsp; Age: **{id_calc_age} yrs** (`{id_cat}`)")
                else:
                    st.warning(f"⚠️ **ID Card DOB:** `{extracted_dob_str or 'Pending OCR'}` &nbsp;|&nbsp; Age: **{id_calc_age or 20} yrs** (`{id_cat or '18 and above'}`)")
                    st.caption("💡 If your ID DOB wasn't recognized cleanly from the scan, please enter your DOB below:")

                # Collapsible OCR raw transcript
                with st.expander("📄 View Raw Extracted ID Text (OCR Log)"):
                    st.text(ocr_log if ocr_log else "No text detected by OCR yet.")

            id_manual_dob = st.text_input("Manual DOB Override (DD/MM/YYYY) if scan is blurry:", placeholder="e.g. 15/08/2004", key="t1_dob")

        # ---------------------------------------------------------------------
        # 2. LIVE FRONT CAMERA / SNAPSHOT (ArcFace & MiniFASNet)
        # ---------------------------------------------------------------------
        with c_live:
            st.markdown("#### 2. Live Front Camera & Liveness Verification")
            st.caption("Real-time ArcFace face tracking + MiniFASNet dual presentation attack detection")
            
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
                if "cached_verif_res" in st.session_state:
                    del st.session_state["cached_verif_res"]
                if "cached_verif_key" in st.session_state:
                    del st.session_state["cached_verif_key"]

            col_c1, col_c2 = st.columns([1, 1])
            with col_c1:
                st.button("📸 Freeze Current Frame", key="freeze_btn", on_click=_on_freeze_click, help="Lock current live frame for analysis & report")
            with col_c2:
                st.button("🔄 Clear Frozen Frame", key="clear_frozen_btn", on_click=_on_clear_click)

            cam_active = st.toggle("🎥 Start Live Camera Feed (ArcFace + Anti-Spoof)", key="t1_cam_toggle", value=False)
            
            live_image_np = st.session_state.get("frozen_live_frame", None)
            
            video_placeholder = st.empty()
            status_placeholder = st.empty()
            
            if cam_active:
                st.caption("🟢 Live Front Camera Video Active — 30 FPS ArcFace Real-Time Verification")
                
                # Precompute ID embedding or reuse engine
                if "vision_engine" not in st.session_state or not getattr(st.session_state["vision_engine"], "running", False):
                    st.session_state["vision_engine"] = Realtime30FPSVisionEngine(id_image_np=id_image_np, target_fps=30.0)
                else:
                    st.session_state["vision_engine"].update_id_image(id_image_np)

                engine = st.session_state["vision_engine"]
                target_interval = 1.0 / 30.0
                last_card_html = None
                
                while getattr(engine, "running", False):
                    t_frame_start = time.time()
                    annotated, raw_rgb, info = engine.get_annotated_frame(target_fps=30.0)
                    
                    if annotated is not None:
                        video_placeholder.image(annotated, caption="Live Front Camera Video (30 FPS | ArcFace Optical Tracking)", width="stretch")
                        
                        is_spoof = info.get("is_spoof", False)
                        match_score = info.get("match_score")
                        is_match = info.get("is_match")
                        
                        card_html = None
                        if is_spoof:
                            score_html = ""
                            if match_score is not None:
                                score_color = "#22c55e" if is_match else "#ef4444"
                                score_tag = "✅ ArcFace Match" if is_match else "❌ ArcFace Mismatch"
                                score_html = f"<div style='margin-top:6px; font-size:12px; color:#fca5a5;'>{score_tag}: {match_score:.1%}</div>"
                            card_html = f"""
                            <div style="background:#450a0a; border:1px solid #ef4444; border-radius:10px; padding:10px; margin-top:6px;">
                                <b style="color:#f87171;">🛑 YOU ARE SHOWING A MOBILE SCREEN</b><br>
                                <span style="color:#fca5a5; font-size:12px;">Photo/Screen Spoof Detected by MiniFASNet!</span>
                                {score_html}
                            </div>
                            """
                        elif match_score is not None:
                            color = "#22c55e" if is_match else "#ef4444"
                            tag = "✅ BIOMETRICS MATCH" if is_match else "❌ BIOMETRIC MISMATCH"
                            card_html = f"""
                            <div style="background:#181818; border:1px solid #262626; border-radius:10px; padding:10px; margin-top:6px; display:flex; justify-content:space-between; align-items:center;">
                                <div>
                                    <span style="font-weight:700; color:{color};">{tag}</span><br>
                                    <span style="font-size:12px; color:#8e8e8e;">ArcFace MS1MV3 Confidence</span>
                                </div>
                                <div style="font-size:22px; font-weight:800; color:{color};">{match_score:.1%}</div>
                            </div>
                            """
                        else:
                            card_html = "<div style='color:#8e8e8e; font-size:12px; padding:6px 0;'>Face detected. Upload an ID Card on the left to cross-match.</div>"

                        if card_html != last_card_html:
                            status_placeholder.markdown(card_html, unsafe_allow_html=True)
                            last_card_html = card_html

                        st.session_state["latest_live_frame"] = raw_rgb

                    dt = time.time() - t_frame_start
                    sleep_time = max(0.005, target_interval - dt)
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
                    <div style="border:2px dashed #333333; border-radius:14px; padding:32px; text-align:center; background:#121212; margin-bottom:12px;">
                        <div style="font-size:36px; margin-bottom:8px;">🎥</div>
                        <div style="font-size:15px; font-weight:600; color:#ffffff;">Live Camera Feed is Off</div>
                        <div style="font-size:12px; color:#8e8e8e;">Toggle <b>'Start Live Camera Feed'</b> above for real-time ArcFace biometric comparison.</div>
                    </div>
                    """, unsafe_allow_html=True)

        # ---------------------------------------------------------------------
        # 3. VERIFICATION & BIOMETRIC VERDICT
        # ---------------------------------------------------------------------
        st.markdown("---")
        st.markdown("### 📊 ID vs Live Face Cross-Matching Verdict")
        if live_image_np is None and "latest_live_frame" in st.session_state:
            live_image_np = st.session_state["latest_live_frame"]

        if id_image_np is not None and live_image_np is not None:
            cache_verif_key = f"{id_image_np.shape}_{id_image_np.sum() % 1000000}_{live_image_np.shape}_{live_image_np.sum() % 1000000}_{id_manual_dob}"
            if st.session_state.get("cached_verif_key") != cache_verif_key or "cached_verif_res" not in st.session_state:
                with st.spinner("⚡ Verifying ID Card Photo vs Live Biometrics & DOB..."):
                    res = verify_id_card_and_live_face(id_image_np, live_image_np, id_manual_dob, id_pdf_text)
                    st.session_state["cached_verif_key"] = cache_verif_key
                    st.session_state["cached_verif_res"] = res
            else:
                res = st.session_state["cached_verif_res"]
            
            c_r1, c_r2, c_r3, c_r4 = st.columns(4)
            with c_r1:
                st.markdown(f"""
                <div class="metric-card" style="background:#181818; border:1px solid #262626; border-radius:12px; padding:12px; text-align:center;">
                    <div class="metric-val" style="font-size:22px; font-weight:700; color:#38bdf8;">{res.get('face_similarity', 0.0):.1%}</div>
                    <div class="metric-lbl" style="font-size:11px; color:#8e8e8e;">Face Match Score</div>
                </div>
                """, unsafe_allow_html=True)
            with c_r2:
                anti_spoof_tag = "🛑 SPOOF" if res.get('is_spoof') else "✅ REAL (LIVE)"
                color = "#ef4444" if res.get('is_spoof') else "#22c55e"
                st.markdown(f"""
                <div class="metric-card" style="background:#181818; border:1px solid #262626; border-radius:12px; padding:12px; text-align:center;">
                    <div class="metric-val" style="font-size:18px; font-weight:700; color:{color};">{anti_spoof_tag}</div>
                    <div class="metric-lbl" style="font-size:11px; color:#8e8e8e;">MiniFASNet Liveness</div>
                </div>
                """, unsafe_allow_html=True)
            with c_r3:
                st.markdown(f"""
                <div class="metric-card" style="background:#181818; border:1px solid #262626; border-radius:12px; padding:12px; text-align:center;">
                    <div class="metric-val" style="font-size:20px; font-weight:700; color:#a855f7;">{res.get('id_age', 'N/A')} yrs</div>
                    <div class="metric-lbl" style="font-size:11px; color:#8e8e8e;">Extracted ID Age</div>
                </div>
                """, unsafe_allow_html=True)
            with c_r4:
                st.markdown(f"""
                <div class="metric-card" style="background:#181818; border:1px solid #262626; border-radius:12px; padding:12px; text-align:center;">
                    <div class="metric-val" style="font-size:18px; font-weight:700; color:#eab308;">{res.get('live_age_category', 'N/A')}</div>
                    <div class="metric-lbl" style="font-size:11px; color:#8e8e8e;">Live ViT Age Scan</div>
                </div>
                """, unsafe_allow_html=True)

            # Overall Status Alert
            if res.get("status") == "VERIFIED_SUCCESS":
                cat = res.get("id_age_category", "18 and above")
                norm = "AGE_18_PLUS"
                if cat == "Less than 14":
                    norm = "AGE_UNDER_14"
                elif cat == "14 to 17":
                    norm = "AGE_14_TO_17"

                st.markdown(f"""
                <div style="background:#052e16; border:1px solid #16a34a; border-radius:12px; padding:18px; margin-top:16px; margin-bottom:18px;">
                    <h3 style="color:#4ade80; margin:0 0 6px 0; display:flex; align-items:center; gap:8px;">
                        🎉 Biometrics Verified: Blue Badge Awarded! <span style="color:#0095f6;">✓</span>
                    </h3>
                    <p style="color:#bbf7d0; margin:0; font-size:13px;">Both the uploaded ID document and live camera face match successfully. Log in below to enter your age-curated Instagram Reels feed.</p>
                </div>
                """, unsafe_allow_html=True)

                col_in1, col_in2 = st.columns(2)
                with col_in1:
                    login_user = st.text_input("Username to Log In", value=username_input or username, key="match_login_usr")
                with col_in2:
                    login_pass = st.text_input("Password to Log In", type="password", value=password_input or "", key="match_login_pwd")

                col_act1, col_act2 = st.columns([1.5, 2])
                with col_act1:
                    if st.button("🚀 Log In to Instagram Reels Feed", type="primary", use_container_width=True):
                        if not login_user or not login_pass:
                            st.error("Please provide both Username and Password to log in.")
                        else:
                            if "user_db" not in st.session_state:
                                st.session_state["user_db"] = {}
                            st.session_state["user_db"][login_user] = {
                                "password": login_pass,
                                "category": cat,
                                "norm": norm
                            }
                            st.session_state["logged_in_username"] = login_user
                            st.session_state["verified_age_category"] = cat
                            st.session_state["verified_age_norm"] = norm
                            st.session_state["verification_data"] = res
                            st.session_state["user_page_view"] = "feed"
                            st.success(f"Verified & logged in as @{login_user}! Redirecting to Reels...")
                            st.rerun()
                with col_act2:
                    st.info(f"Verified Policy Bracket: `{norm}` ({cat}) | ID DOB: **{res.get('id_dob_str')}**")
            elif res.get("is_spoof"):
                st.error("🛑 **Presentation Attack Blocked**: YOU ARE SHOWING A MOBILE SCREEN. MiniFASNet anti-spoofing detector identified digital screen replay artifacts.")
            else:
                st.error(f"❌ **Login Denied**: {res.get('message', 'Facial biometrics do not match.')}")
        else:
            st.info("👈 Please **Upload an ID Card** on the left AND **Freeze the Live Camera** on the right to perform biometric verification.")
