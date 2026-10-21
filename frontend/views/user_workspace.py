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
if "sooraj_classifier" in sys.modules:
    sooraj_classifier = sys.modules["sooraj_classifier"]
else:
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
import sqlite3

def render_html(html_str: str):
    """Safely renders HTML without Markdown interpreting indented lines as code blocks."""
    cleaned = "\n".join(line.strip() for line in html_str.splitlines() if line.strip())
    st.markdown(cleaned, unsafe_allow_html=True)

# Persistent User Database for Account Registrations
USER_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../safead_users.db"))

def init_user_storage():
    """Initializes persistent SQLite storage for registered users."""
    try:
        conn = sqlite3.connect(USER_DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS registered_users (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                age_category TEXT NOT NULL,
                norm_group TEXT NOT NULL,
                is_verified INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("""
            INSERT OR IGNORE INTO registered_users (username, password, age_category, norm_group, is_verified)
            VALUES ('sourav', 'sourav', '18 and above', 'AGE_18_PLUS', 1)
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error initializing user storage: {e}")

def load_all_users() -> dict:
    init_user_storage()
    users = {
        "sourav": {
            "password": "sourav",
            "category": "18 and above",
            "norm": "AGE_18_PLUS",
            "is_verified": True
        }
    }
    try:
        conn = sqlite3.connect(USER_DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT username, password, age_category, norm_group, is_verified FROM registered_users")
        rows = cur.fetchall()
        conn.close()
        for r in rows:
            users[r[0]] = {
                "password": r[1],
                "category": r[2],
                "norm": r[3],
                "is_verified": bool(r[4])
            }
    except Exception as e:
        print(f"Error loading users: {e}")
    return users

def save_new_user(username: str, password: str, category: str, norm: str):
    init_user_storage()
    try:
        conn = sqlite3.connect(USER_DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            INSERT OR REPLACE INTO registered_users (username, password, age_category, norm_group, is_verified)
            VALUES (?, ?, ?, ?, 1)
        """, (username, password, category, norm))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error saving user: {e}")


# =============================================================================
# REELS CATALOG: ORGANIC VIDEOS & BRAND OWNER ADS
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


def is_ad_allowed_for_age(classification: str, user_cat: str) -> bool:
    """
    Strict age-gating verification:
    - Less than 14: ONLY SAFE_FOR_ALL / APPROVED
    - 14 to 17: SAFE_FOR_ALL / APPROVED + SAFE_14_PLUS
    - 18 and above: SAFE_FOR_ALL / APPROVED + SAFE_14_PLUS + SAFE_18_PLUS
    - UNSAFE_FOR_ALL / REJECT: NEVER ALLOWED
    """
    if not classification or classification in ["UNSAFE_FOR_ALL", "REJECT", "REQUIRES_HUMAN_REVIEW"]:
        return False
    
    classification = str(classification).upper()
    if user_cat == "Less than 14":
        return classification in ["SAFE_FOR_ALL", "APPROVED"]
    elif user_cat == "14 to 17":
        return classification in ["SAFE_FOR_ALL", "APPROVED", "SAFE_14_PLUS"]
    else:  # 18 and above
        return classification in ["SAFE_FOR_ALL", "APPROVED", "SAFE_14_PLUS", "SAFE_18_PLUS"]



# =============================================================================
# DATASET HUB CONTENT LOADER (Age-Gated Reels & Photos)
# =============================================================================
@st.cache_data(show_spinner=False)
def load_dataset_hub_content():
    """Loads approved, authentic images and reels from safead-dataset-hub manifest."""
    hub_root = os.path.abspath(os.path.join(BASE_DIR, ".."))
    manifest_path = os.path.join(hub_root, "app_content", "content_manifest.json")
    
    if not os.path.exists(manifest_path):
        return {"images": [], "reels": []}
    
    try:
        import json
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading content manifest: {e}")
        return {"images": [], "reels": []}
        
    images = []
    reels = []
    
    for item in data.get("content_items", []):
        media_rel = item.get("media_path", "")
        full_path = os.path.abspath(os.path.join(hub_root, media_rel))
        
        if not os.path.exists(full_path):
            continue
            
        entry = {
            "id": item["content_id"],
            "type": "sponsored",
            "creator": item.get("source_name", "SafeAd Archive"),
            "creator_avatar": "📺" if item["content_type"] == "reel" else "📸",
            "is_verified": True,
            "sponsored_label": f"SafeAd AI • Verified {item['age_category']}",
            "safety_policy": item["age_category"],
            "title": item.get("title", ""),
            "caption": item.get("caption", ""),
            "cta_text": "Watch Reel ↗" if item["content_type"] == "reel" else "View Creative ↗",
            "audio": "Vintage Commercial Soundtrack • SafeAd Vault 🎵",
            "likes": 12000 + (abs(hash(item["content_id"])) % 45000),
            "comments_count": 80 + (abs(hash(item["content_id"])) % 350),
            "shares_count": 1400 + (abs(hash(item["content_id"])) % 5000),
            "media_path": full_path,
            "video_path": full_path,
            "content_type": item["content_type"],
            "comments": [
                {"user": "safead_compliance", "text": f"✅ Verified safe for {item['age_category']} demographic.", "time": "2h", "likes": 42}
            ]
        }
        
        if item["content_type"] == "reel":
            reels.append(entry)
        else:
            images.append(entry)
            
    return {"images": images, "reels": reels}

def build_curated_reels(user_cat: str, user_norm: str) -> list:
    """
    Builds the reels catalog dynamically:
    1. Base organic reels (all ages)
    2. Default sponsored ads that match age
    3. Brand Owner ads uploaded and approved in the Advertisement Validity tab
    """
    curated = []
    
    # 1. Process default organic reels (all ages)
    for r in DEFAULT_REELS:
        if r["type"] == "organic":
            curated.append(r)
        elif r["type"] == "sponsored":
            pol = r.get("safety_policy", "SAFE_FOR_ALL")
            if is_ad_allowed_for_age(pol, user_cat):
                curated.append(r)

    # 2. Load and inject authentic reels from safead-dataset-hub matching user's age category
    hub_data = load_dataset_hub_content()
    for reel in hub_data["reels"]:
        pol = reel.get("safety_policy", "SAFE_FOR_ALL")
        if is_ad_allowed_for_age(pol, user_cat):
            curated.append(reel)

    # 2. Add Brand Owner Ads uploaded in Brand Owner portal (global_ads)
    global_ads = st.session_state.get("global_ads", [])
    seen_paths = set()
    
    for ad in global_ads:
        pol = ad.get("classification", "SAFE_FOR_ALL")
        fpath = ad.get("file_path", "")
        if not fpath or fpath in seen_paths:
            continue
        seen_paths.add(fpath)
        
        if is_ad_allowed_for_age(pol, user_cat):
            # Check if file exists and is a video
            ext = os.path.splitext(fpath)[1].lower()
            if os.path.exists(fpath) and ext in [".mp4", ".avi", ".mov", ".webm", ".mkv"]:
                curated.append({
                    "id": f"brand_ad_{ad.get('ad_id', hash(fpath))}",
                    "type": "sponsored",
                    "creator": "brand_partner",
                    "creator_avatar": "🏢",
                    "is_verified": True,
                    "sponsored_label": f"Sponsored • Brand Owner Ad ({pol})",
                    "safety_policy": pol,
                    "title": ad.get("title", "Sponsored Advertisement"),
                    "caption": ad.get("caption", "SafeAd AI verified creative approved for your age group."),
                    "cta_text": "Learn More ↗",
                    "audio": "Brand Commercial Audio • Verified SafeAd 🎵",
                    "likes": 15800,
                    "comments_count": 92,
                    "shares_count": 3100,
                    "video_path": fpath,
                    "comments": [
                        {"user": "safead_ai", "text": f"✅ Content verified safe for {user_cat} audience.", "time": "Just now", "likes": 42}
                    ]
                })

    # 3. If Brand Owner analyzed an ad that is still in moderation_report (active in session)
    if "moderation_report" in st.session_state and st.session_state["moderation_report"]:
        rep = st.session_state["moderation_report"]
        pol = rep.get("classification", "")
        fpath = st.session_state.get("last_temp_path", "")
        if fpath and fpath not in seen_paths and os.path.exists(fpath):
            ext = os.path.splitext(fpath)[1].lower()
            if ext in [".mp4", ".avi", ".mov", ".webm", ".mkv"] and is_ad_allowed_for_age(pol, user_cat):
                seen_paths.add(fpath)
                curated.append({
                    "id": f"active_owner_ad_{int(time.time())}",
                    "type": "sponsored",
                    "creator": "brand_partner",
                    "creator_avatar": "🏢",
                    "is_verified": True,
                    "sponsored_label": f"Sponsored • Brand Owner Ad ({pol})",
                    "safety_policy": pol,
                    "title": rep.get("title", st.session_state.get("last_ad_title", "Sponsored Advertisement")),
                    "caption": rep.get("caption", st.session_state.get("last_ad_caption", "Verified by SafeAd AI")),
                    "cta_text": "Shop Now ↗",
                    "audio": "Promotional Soundtrack 🎵",
                    "likes": 9800,
                    "comments_count": 45,
                    "shares_count": 1200,
                    "video_path": fpath,
                    "comments": [
                        {"user": "ad_compliance", "text": f"Approved for {pol} audience tier.", "time": "Just now", "likes": 18}
                    ]
                })

    # 4. Include benchmark ads from sample_ad_media if user is 18+
    casino_path = os.path.join(BASE_DIR, "sample_ad_media/casino_ad.mp4")
    if user_cat == "18 and above" and os.path.exists(casino_path) and casino_path not in seen_paths:
        curated.append({
            "id": "ad_casino_18",
            "type": "sponsored",
            "creator": "vegas_grand_casino",
            "creator_avatar": "🎰",
            "is_verified": True,
            "sponsored_label": "Sponsored • 18+ Age Restricted Ad",
            "safety_policy": "SAFE_18_PLUS",
            "title": "Grand Casino Slots & Poker Club",
            "caption": "Experience luxury casino thrills! 18+ Only. Certified Age-Restricted by SafeAd AI. Please gamble responsibly.",
            "cta_text": "Play Responsibly (18+) ↗",
            "audio": "Casino Nightlife • High Roller Beats 🎵",
            "likes": 21300,
            "comments_count": 420,
            "shares_count": 5600,
            "video_path": casino_path,
            "comments": [
                {"user": "safead_bot", "text": "Age-gated strictly to verified 18+ accounts.", "time": "2h", "likes": 88}
            ]
        })

    return curated


# =============================================================================
# MAIN USER DASHBOARD CONTROLLER
# =============================================================================
def user_dashboard():
    # 1. Global User Database with Persistent Storage
    db_users = load_all_users()
    if "user_db" not in st.session_state:
        st.session_state["user_db"] = {}
    st.session_state["user_db"].update(db_users)

    # 2. User Authentication State: 'LOGIN', 'SIGNUP', or 'AUTHENTICATED'
    if "user_auth_state" not in st.session_state:
        st.session_state["user_auth_state"] = "LOGIN"

    if "user_subtab" not in st.session_state:
        st.session_state["user_subtab"] = "feed"

    if "current_reel_idx" not in st.session_state:
        st.session_state["current_reel_idx"] = 0

    if "liked_reels" not in st.session_state:
        st.session_state["liked_reels"] = set()

    if "saved_reels" not in st.session_state:
        st.session_state["saved_reels"] = set()

    if "reel_comments_store" not in st.session_state:
        st.session_state["reel_comments_store"] = {r["id"]: list(r.get("comments", [])) for r in DEFAULT_REELS}

    if "show_comments_for" not in st.session_state:
        st.session_state["show_comments_for"] = None

    if "reels_filter" not in st.session_state:
        st.session_state["reels_filter"] = "ALL"

    # =========================================================================
    # OPTION 1: LOGIN PAGE
    # =========================================================================
    if st.session_state["user_auth_state"] == "LOGIN":
        st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
        
        c_l, c_center, c_r = st.columns([1, 1.8, 1])
        with c_center:
            st.markdown("""
            <div style="text-align: center; margin-bottom: 24px;">
                <div style="font-family:'Grand Hotel', cursive, -apple-system, sans-serif; font-size:52px; background:linear-gradient(45deg,#f09433,#e6683c,#dc2743,#cc2366,#bc1888); -webkit-background-clip:text; -webkit-text-fill-color:transparent; line-height:1.2;">
                    Instagram
                </div>
                <div style="display:inline-block; background:rgba(0,149,246,0.15); border:1px solid rgba(0,149,246,0.4); color:#0095f6; font-size:11px; font-weight:800; padding:3px 12px; border-radius:6px; letter-spacing:1px; margin-top:6px;">
                    SAFEAD AI USER PORTAL
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Login Card containing ONLY username, password, login button, and register link
            st.markdown("""
            <div style="background:#121212; border:1px solid #262626; border-radius:14px; padding:24px 28px; margin-bottom:16px;">
                <div style="font-size:16px; font-weight:700; color:#ffffff; margin-bottom:16px; text-align:center;">
                    Log In to Your Account
                </div>
            """, unsafe_allow_html=True)

            login_user = st.text_input("Username", key="login_usr_input", placeholder="Enter username")
            login_pass = st.text_input("Password", type="password", key="login_pwd_input", placeholder="Enter password")

            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

            if st.button("Log In", key="btn_login_submit", type="primary", use_container_width=True):
                st.session_state["user_db"].update(load_all_users())
                db = st.session_state.get("user_db", {})
                if login_user in db and db[login_user].get("password") == login_pass:
                    user_data = db[login_user]
                    st.session_state["logged_in_username"] = login_user
                    st.session_state["verified_age_category"] = user_data.get("category", "18 and above")
                    st.session_state["verified_age_norm"] = user_data.get("norm", "AGE_18_PLUS")
                    st.session_state["user_auth_state"] = "AUTHENTICATED"
                    st.session_state["user_subtab"] = "feed"
                    st.success(f"✅ Welcome back @{login_user}! Logging in...")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password. Please verify credentials.")

            # Developer testing account note
            st.markdown("""
                <div style="background:#181818; border:1px dashed #3f3f46; border-radius:8px; padding:10px 14px; margin-top:16px; font-size:12px; color:#a1a1aa; text-align:center;">
                    💡 <b>Developer Testing Account:</b> Username: <code style="color:#38bdf8;">sourav</code> &nbsp;|&nbsp; Password: <code style="color:#38bdf8;">sourav</code>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Registration redirection box
            st.markdown("""
            <div style="background:#121212; border:1px solid #262626; border-radius:14px; padding:16px 20px; text-align:center; margin-bottom:20px;">
                <span style="color:#a8a8a8; font-size:13px;">Don't have an account? </span>
            </div>
            """, unsafe_allow_html=True)

            if st.button("New User? Register Now", key="btn_goto_register", use_container_width=True):
                st.session_state["user_auth_state"] = "SIGNUP"
                st.rerun()

        return

    # =========================================================================
    # OPTION 2: SIGN UP PAGE (BIOMETRIC KYC & ID VERIFICATION)
    # =========================================================================
    elif st.session_state["user_auth_state"] == "SIGNUP":
        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

        render_instagram_logo(subtitle="CREATE ACCOUNT & VERIFY KYC")

        # Top Card with Only Username and Password (+ Confirm Password) Textboxes & Sign In Button
        st.markdown("""
        <div style="background:linear-gradient(135deg, #181818 0%, #1a1a1a 100%); border:1px solid #262626; border-radius:14px; padding:20px 24px; margin-bottom:20px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
                <div>
                    <h3 style="margin:0; font-size:18px; color:#ffffff; font-weight:700;">👤 Account Registration</h3>
                    <p style="margin:0; font-size:12px; color:#8e8e8e;">Create your login credentials. Complete the ID & live biometric verification below to activate your account.</p>
                </div>
            </div>
        """, unsafe_allow_html=True)

        col_reg1, col_reg2, col_reg3 = st.columns([1.5, 1.5, 1.5])
        with col_reg1:
            new_username = st.text_input("New Username", key="reg_username_input", placeholder="Choose username")
        with col_reg2:
            new_password = st.text_input("Password", type="password", key="reg_password_input", placeholder="Create password")
        with col_reg3:
            confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm_password", placeholder="Confirm password")

        st.markdown("</div>", unsafe_allow_html=True)

        # ---------------------------------------------------------------------
        # FACE DETECTION & ID CARD UPLOAD FEATURES
        # ---------------------------------------------------------------------
        st.markdown("### 🆔 Biometric Verification: ID Document & Live Camera")
        c_id, c_live = st.columns([1, 1], gap="medium")

        # 1. Upload Official ID Card
        with c_id:
            st.markdown("#### 1. Upload Official ID Card")
            st.caption("Supports Passport, Driving License, Student ID, Aadhaar (JPG, PNG, PDF)")
            up_id = st.file_uploader("Upload ID Card Scan or PDF", type=["jpg", "jpeg", "png", "pdf"], key="reg_id_upload")
            
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
                            st.error(f"Failed to render PDF: {id_pdf_text}")
                    else:
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

                with st.expander("📄 View Raw Extracted ID Text (OCR Log)"):
                    st.text(ocr_log if ocr_log else "No text detected by OCR yet.")

            id_manual_dob = st.text_input("Manual DOB Override (DD/MM/YYYY) if scan is blurry:", placeholder="e.g. 15/08/2004", key="reg_manual_dob")

        # 2. Live Front Camera Video Stream & Freeze Frame
        with c_live:
            st.markdown("#### 2. Live Front Camera & Liveness Verification")
            st.caption("Real-time ArcFace face tracking + Anti-Spoof Liveness Detection")
            
            def _on_freeze_click():
                if "latest_live_frame" in st.session_state and st.session_state["latest_live_frame"] is not None:
                    st.session_state["frozen_live_frame"] = st.session_state["latest_live_frame"]
                    st.session_state["frozen_annotated_frame"] = st.session_state.get("latest_annotated_frame", st.session_state["latest_live_frame"])
                    st.session_state["reg_cam_toggle"] = False
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
                st.button("📸 Freeze Current Frame", key="reg_freeze_btn", on_click=_on_freeze_click, help="Lock current live frame for analysis & report")
            with col_c2:
                st.button("🔄 Clear Frozen Frame", key="reg_clear_frozen_btn", on_click=_on_clear_click)

            cam_active = st.toggle("🎥 Start Live Camera Feed (ArcFace + Anti-Spoof)", key="reg_cam_toggle", value=False)
            
            live_image_np = st.session_state.get("frozen_live_frame", None)
            
            video_placeholder = st.empty()
            status_placeholder = st.empty()
            
            if cam_active:
                st.caption("🟢 Live Front Camera Video Active — 30 FPS ArcFace Real-Time Verification")
                
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
                        video_placeholder.image(annotated, caption="Live Front Camera Video (30 FPS | ArcFace)", width="stretch")
                        
                        is_spoof = info.get("is_spoof", False)
                        match_score = info.get("match_score")
                        is_match = info.get("is_match")
                        
                        card_html = None
                        if is_spoof:
                            score_html = ""
                            if match_score is not None:
                                score_tag = "✅ ArcFace Match" if is_match else "❌ ArcFace Mismatch"
                                score_html = f"<div style='margin-top:6px; font-size:12px; color:#fca5a5;'>{score_tag}: {match_score:.1%}</div>"
                            spoof_detail = info.get("spoof_reason", "Screen/Photo Presentation Attack")
                            card_html = f"""
                            <div style="background:#450a0a; border:1px solid #ef4444; border-radius:10px; padding:10px; margin-top:6px;">
                                <b style="color:#f87171;">🛑 YOU ARE A SCREEN</b><br>
                                <span style="color:#fca5a5; font-size:12px;">Photo/Screen Spoof Detected! ({spoof_detail})</span>
                                {score_html.strip() if score_html else ""}
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
                        st.session_state["latest_annotated_frame"] = annotated

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

                disp_frame = st.session_state.get("frozen_annotated_frame", live_image_np)
                if disp_frame is not None:
                    video_placeholder.image(disp_frame, caption="Frozen Live Camera Snapshot (Biometrics Captured)", width="stretch")
                else:
                    video_placeholder.markdown("""
                    <div style="border:2px dashed #333333; border-radius:14px; padding:32px; text-align:center; background:#121212; margin-bottom:12px;">
                        <div style="font-size:36px; margin-bottom:8px;">🎥</div>
                        <div style="font-size:15px; font-weight:600; color:#ffffff;">Live Camera Feed is Off</div>
                        <div style="font-size:12px; color:#8e8e8e;">Toggle <b>'Start Live Camera Feed'</b> above and freeze a frame to verify identity.</div>
                    </div>
                    """, unsafe_allow_html=True)

        # ---------------------------------------------------------------------
        # 3. VERIFICATION & BIOMETRIC VERDICT
        # ---------------------------------------------------------------------
        st.markdown("---")
        st.markdown("### 📊 Verification & Biometric Cross-Match Verdict")
        if live_image_np is None and "latest_live_frame" in st.session_state:
            live_image_np = st.session_state["latest_live_frame"]

        verif_ready = (id_image_np is not None and live_image_np is not None)
        verif_res = None

        if verif_ready:
            cache_verif_key = f"{id_image_np.shape}_{id_image_np.sum() % 1000000}_{live_image_np.shape}_{live_image_np.sum() % 1000000}_{id_manual_dob}"
            if st.session_state.get("cached_verif_key") != cache_verif_key or "cached_verif_res" not in st.session_state:
                with st.spinner("⚡ Verifying ID Card Photo vs Live Biometrics & DOB..."):
                    verif_res = verify_id_card_and_live_face(id_image_np, live_image_np, id_manual_dob, id_pdf_text)
                    st.session_state["cached_verif_key"] = cache_verif_key
                    st.session_state["cached_verif_res"] = verif_res
            else:
                verif_res = st.session_state["cached_verif_res"]

            c_r1, c_r2, c_r3, c_r4 = st.columns(4)
            with c_r1:
                st.markdown(f"""
                <div class="metric-card" style="background:#181818; border:1px solid #262626; border-radius:12px; padding:12px; text-align:center;">
                    <div class="metric-val" style="font-size:22px; font-weight:700; color:#38bdf8;">{verif_res.get('face_similarity', 0.0):.1%}</div>
                    <div class="metric-lbl" style="font-size:11px; color:#8e8e8e;">Face Match Score</div>
                </div>
                """, unsafe_allow_html=True)
            with c_r2:
                anti_spoof_tag = "🛑 SPOOF" if verif_res.get('is_spoof') else "✅ REAL (LIVE)"
                color = "#ef4444" if verif_res.get('is_spoof') else "#22c55e"
                st.markdown(f"""
                <div class="metric-card" style="background:#181818; border:1px solid #262626; border-radius:12px; padding:12px; text-align:center;">
                    <div class="metric-val" style="font-size:18px; font-weight:700; color:{color};">{anti_spoof_tag}</div>
                    <div class="metric-lbl" style="font-size:11px; color:#8e8e8e;">Liveness Check</div>
                </div>
                """, unsafe_allow_html=True)
            with c_r3:
                st.markdown(f"""
                <div class="metric-card" style="background:#181818; border:1px solid #262626; border-radius:12px; padding:12px; text-align:center;">
                    <div class="metric-val" style="font-size:20px; font-weight:700; color:#a855f7;">{verif_res.get('id_age', 'N/A')} yrs</div>
                    <div class="metric-lbl" style="font-size:11px; color:#8e8e8e;">Extracted ID Age</div>
                </div>
                """, unsafe_allow_html=True)
            with c_r4:
                st.markdown(f"""
                <div class="metric-card" style="background:#181818; border:1px solid #262626; border-radius:12px; padding:12px; text-align:center;">
                    <div class="metric-val" style="font-size:18px; font-weight:700; color:#eab308;">{verif_res.get('live_age_category', 'N/A')}</div>
                    <div class="metric-lbl" style="font-size:11px; color:#8e8e8e;">Live ViT Age Scan</div>
                </div>
                """, unsafe_allow_html=True)

            # Overall Status Alert
            if verif_res.get("status") == "VERIFIED_SUCCESS":
                st.markdown(f"""
                <div style="background:#052e16; border:1px solid #16a34a; border-radius:12px; padding:16px; margin-top:16px; margin-bottom:18px;">
                    <h3 style="color:#4ade80; margin:0 0 6px 0; font-size:16px;">
                        🎉 Biometrics Verified: Blue Badge Awarded! <span style="color:#0095f6;">✓</span>
                    </h3>
                    <p style="color:#bbf7d0; margin:0; font-size:12px;">ID and live camera facial scan cross-matched with {verif_res.get('face_similarity', 0.0):.1%} similarity. Click Complete Registration below to create your account.</p>
                </div>
                """, unsafe_allow_html=True)
            elif verif_res.get("is_spoof"):
                st.markdown(f"""
                <div style="background:#450a0a; border:1px solid #ef4444; border-radius:12px; padding:16px; margin-top:16px; margin-bottom:18px;">
                    <h3 style="color:#f87171; margin:0 0 6px 0; font-size:16px;">
                        🛑 Presentation Attack Blocked: YOU ARE A SCREEN
                    </h3>
                    <p style="color:#fca5a5; margin:0; font-size:12px;">Photo/Screen Spoof Detected! ({verif_res.get('spoof_reason')}). Please present a real live person.</p>
                </div>
                """, unsafe_allow_html=True)
            elif not verif_res.get("face_match"):
                st.markdown(f"""
                <div style="background:#450a0a; border:1px solid #ef4444; border-radius:12px; padding:16px; margin-top:16px; margin-bottom:18px;">
                    <h3 style="color:#f87171; margin:0 0 6px 0; font-size:16px;">
                        ❌ Biometric Mismatch: ID Card & Live User Do Not Match!
                    </h3>
                    <p style="color:#fca5a5; margin:0; font-size:12px;">ArcFace MS1MV3 biometric similarity confidence is <b>{verif_res.get('face_similarity', 0.0):.1%}</b> (Threshold: &ge; 65.0%). Verification rejected.</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("👈 Please **Upload an ID Card** on the left AND **Freeze the Live Camera** on the right to perform biometric verification.")

        # Complete Registration Action Button
        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
        if st.button("🚀 Complete Registration & Sign In", key="btn_do_signup", type="primary", use_container_width=True):
            if not new_username or not new_password:
                st.error("Please provide both a Username and Password.")
            elif new_password != confirm_password:
                st.error("Passwords do not match! Please check confirm password.")
            elif new_username in st.session_state.get("user_db", {}):
                st.error(f"Username '@{new_username}' is already taken. Please pick another username.")
            elif not verif_ready or not verif_res or verif_res.get("status") != "VERIFIED_SUCCESS":
                st.error("Identity Verification Required! You must successfully complete the ID card & live face cross-match before creating an account.")
            else:
                cat = verif_res.get("id_age_category", "18 and above")
                norm = "AGE_18_PLUS"
                if cat == "Less than 14":
                    norm = "AGE_UNDER_14"
                elif cat == "14 to 17":
                    norm = "AGE_14_TO_17"

                # Save new user to persistent database
                save_new_user(new_username, new_password, cat, norm)

                if "user_db" not in st.session_state:
                    st.session_state["user_db"] = {}

                st.session_state["user_db"][new_username] = {
                    "password": new_password,
                    "category": cat,
                    "norm": norm,
                    "is_verified": True,
                    "verification_data": verif_res
                }
                st.session_state["logged_in_username"] = new_username
                st.session_state["verified_age_category"] = cat
                st.session_state["verified_age_norm"] = norm
                st.session_state["user_auth_state"] = "AUTHENTICATED"
                st.session_state["user_subtab"] = "feed"
                st.success(f"🎉 Account created & verified for @{new_username}! Redirecting to Instagram...")
                st.rerun()

        # Sign-In Navigation moved to bottom of registration page
        render_html("""
        <div style="text-align:center; padding:18px 0 8px 0; border-top:1px solid #262626; margin-top:24px;">
            <span style="color:#a8a8a8; font-size:13px;">Already have an account? </span>
        </div>
        """)
        if st.button("🔑 Already Have an Account? Return to Sign In", key="btn_back_to_signin_bottom", use_container_width=True):
            if "vision_engine" in st.session_state:
                try:
                    st.session_state["vision_engine"].stop()
                except Exception:
                    pass
                del st.session_state["vision_engine"]
            st.session_state["user_auth_state"] = "LOGIN"
            st.rerun()

        return

    # =========================================================================
    # OPTION 3: AUTHENTICATED INSTAGRAM HOMEPAGE & REELS INTERFACE
    # =========================================================================
    username = st.session_state.get("logged_in_username", "sourav")
    user_cat = st.session_state.get("verified_age_category", "18 and above")
    user_norm = st.session_state.get("verified_age_norm", "AGE_18_PLUS")

    # App Header with User Greeting and Verified Badge
    render_instagram_logo(subtitle="AURA SOCIAL")

    # User Profile Info & Navigation Sub-Bar
    st.markdown(f"""
    <div style="background:#121212; border:1px solid #262626; border-radius:12px; padding:10px 16px; margin-bottom:14px; display:flex; justify-content:space-between; align-items:center;">
        <div style="display:flex; align-items:center; gap:10px;">
            <div style="width:34px; height:34px; border-radius:50%; background:linear-gradient(45deg,#f09433,#dc2743,#bc1888); padding:1.5px; display:flex; align-items:center; justify-content:center;">
                <div style="width:100%; height:100%; border-radius:50%; background:#181818; display:flex; align-items:center; justify-content:center; font-size:15px;">
                    👤
                </div>
            </div>
            <div>
                <div style="font-size:14px; font-weight:700; color:#ffffff; display:flex; align-items:center; gap:4px;">
                    @{username}
                    <span style="color:#0095f6; font-size:13px; font-weight:800;" title="Verified Account">✓</span>
                    <span style="background:rgba(0,149,246,0.15); border:1px solid rgba(0,149,246,0.3); color:#38bdf8; font-size:10px; font-weight:700; padding:1px 6px; border-radius:4px; margin-left:6px;">
                        {user_norm} ({user_cat})
                    </span>
                </div>
                <div style="font-size:11px; color:#8e8e8e;">Verified Identity • Age-Gated Social Feed Active</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Top Tabs: Instagram Home Page vs Reels Tab
    c_tab1, c_tab2, c_tab3 = st.columns([1, 1, 0.8])
    with c_tab1:
        if st.button("🏠 Instagram Home", key="tab_home_btn", use_container_width=True,
                     type="primary" if st.session_state["user_subtab"] == "feed" else "secondary"):
            st.session_state["user_subtab"] = "feed"
            st.rerun()
    with c_tab2:
        if st.button("🎥 Reels Tab", key="tab_reels_btn", use_container_width=True,
                     type="primary" if st.session_state["user_subtab"] == "reels" else "secondary"):
            st.session_state["user_subtab"] = "reels"
            st.rerun()
    with c_tab3:
        if st.button("🚪 Log Out", key="user_logout_btn", use_container_width=True):
            if "vision_engine" in st.session_state:
                try:
                    st.session_state["vision_engine"].stop()
                except Exception:
                    pass
                del st.session_state["vision_engine"]
            st.session_state["user_auth_state"] = "LOGIN"
            st.session_state["logged_in_username"] = None
            st.rerun()

    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

    # Compile the active age-appropriate reels list
    curated_reels = build_curated_reels(user_cat, user_norm)

    # -------------------------------------------------------------------------
    # TAB 1: USUAL INSTAGRAM HOMEPAGE INTERFACE
    # -------------------------------------------------------------------------
    if st.session_state["user_subtab"] == "feed":
        # 1. Instagram Stories Carousel
        render_stories_bar()

        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

        # Feed Posts Layout (Organic Posts + Verified Brand Owner Ads)
        c_spacer_l, c_feed, c_spacer_r = st.columns([1, 2.5, 1])

        with c_feed:
            # Post 1: Organic Community Post
            st.markdown("""
            <div style="background:#121212; border:1px solid #262626; border-radius:14px; margin-bottom:20px;">
                <div style="padding:12px 16px; display:flex; justify-content:space-between; align-items:center;">
                    <div style="display:flex; align-items:center; gap:10px;">
                        <div style="width:32px; height:32px; border-radius:50%; background:linear-gradient(45deg,#f09433,#dc2743,#bc1888); padding:1.5px; display:flex; align-items:center; justify-content:center;">
                            <div style="width:100%; height:100%; border-radius:50%; background:#181818; display:flex; align-items:center; justify-content:center; font-size:14px;">
                                🌌
                            </div>
                        </div>
                        <div>
                            <div style="font-size:13px; font-weight:700; color:#ffffff;">@aurora_explorers <span style="color:#0095f6;">✓</span></div>
                            <div style="font-size:11px; color:#8e8e8e;">Tromsø, Norway</div>
                        </div>
                    </div>
                    <div style="color:#8e8e8e; font-size:14px;">•••</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            aurora_path = os.path.join(BASE_DIR, "frontend/assets/reels/reel_aurora.mp4")
            if os.path.exists(aurora_path):
                st.video(aurora_path, autoplay=False, loop=True)

            st.markdown(f"""
            <div style="background:#121212; border:1px solid #262626; border-top:none; border-radius:0 0 14px 14px; padding:12px 16px; margin-top:-20px; margin-bottom:24px;">
                <div style="display:flex; gap:14px; font-size:20px; margin-bottom:8px;">
                    <span>❤️</span> <span>💬</span> <span>✈️</span>
                </div>
                <div style="font-size:13px; font-weight:700; color:#ffffff; margin-bottom:4px;">321,800 likes</div>
                <div style="font-size:13px; color:#e2e8f0; margin-bottom:4px;">
                    <b>@aurora_explorers</b> Dancing emerald curtains in Tromsø 🇳🇴 Nature never fails to amaze. Tag someone who needs to see this! 💚
                </div>
                <div style="font-size:11px; color:#8e8e8e;">View all 4,120 comments • 2 hours ago</div>
            </div>
            """, unsafe_allow_html=True)

            # Dataset Hub Age-Filtered Approved Photos Feed
            hub_photos = load_dataset_hub_content()["images"]
            age_appropriate_photos = [img for img in hub_photos if is_ad_allowed_for_age(img["safety_policy"], user_cat)]
            
            for p_idx, photo in enumerate(age_appropriate_photos[:12]):
                pol = photo.get("safety_policy", "SAFE_FOR_ALL")
                render_html(f"""
                <div style="background:#121212; border:1px solid #262626; border-radius:14px; margin-bottom:20px;">
                    <div style="padding:12px 16px; display:flex; justify-content:space-between; align-items:center;">
                        <div style="display:flex; align-items:center; gap:10px;">
                            <div style="width:32px; height:32px; border-radius:50%; background:linear-gradient(45deg,#0095f6,#38bdf8); padding:1.5px; display:flex; align-items:center; justify-content:center;">
                                <div style="width:100%; height:100%; border-radius:50%; background:#181818; display:flex; align-items:center; justify-content:center; font-size:14px;">
                                    📸
                                </div>
                            </div>
                            <div>
                                <div style="font-size:13px; font-weight:700; color:#ffffff;">@{photo['id']} <span style="color:#0095f6;">✓</span></div>
                                <div style="font-size:11px; color:#38bdf8;">🛡️ SafeAd Verified • Policy: {pol} (Approved for {user_cat})</div>
                            </div>
                        </div>
                        <div style="font-size:11px; background:rgba(0,149,246,0.15); border:1px solid rgba(0,149,246,0.3); color:#38bdf8; padding:2px 8px; border-radius:4px;">
                            {pol}
                        </div>
                    </div>
                </div>
                """)
                if os.path.exists(photo["media_path"]):
                    st.image(photo["media_path"], use_container_width=True)
                render_html(f"""
                <div style="background:#121212; border:1px solid #262626; border-top:none; border-radius:0 0 14px 14px; padding:12px 16px; margin-top:-20px; margin-bottom:24px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <div style="display:flex; gap:14px; font-size:20px;">
                            <span>❤️</span> <span>💬</span> <span>✈️</span>
                        </div>
                        <span style="font-size:12px; font-weight:700; color:#38bdf8;">{photo.get('cta_text', 'View Product ↗')}</span>
                    </div>
                    <div style="font-size:13px; font-weight:700; color:#ffffff; margin-bottom:4px;">{format_count(photo.get('likes', 14000))} likes</div>
                    <div style="font-size:13px; color:#e2e8f0; margin-bottom:4px;">
                        <b>@{photo['id']}</b> {photo.get('title', '')} — {photo.get('caption', '')}
                    </div>
                    <div style="font-size:11px; color:#8e8e8e;">SafeAd AI Verified Creative • Source: {photo.get('creator')}</div>
                </div>
                """)

            # Post 2: Age-Appropriate Brand Owner Sponsored Ad
            # If Brand Owner has ads in global_ads, display the top approved ad
            owner_ads = [r for r in curated_reels if r["type"] == "sponsored"]
            if owner_ads:
                top_ad = owner_ads[0]
                pol = top_ad.get("safety_policy", "SAFE_FOR_ALL")
                st.markdown(f"""
                <div style="background:#121212; border:1px solid #262626; border-radius:14px; margin-bottom:20px;">
                    <div style="padding:12px 16px; display:flex; justify-content:space-between; align-items:center;">
                        <div style="display:flex; align-items:center; gap:10px;">
                            <div style="width:32px; height:32px; border-radius:50%; background:linear-gradient(45deg,#0095f6,#38bdf8); padding:1.5px; display:flex; align-items:center; justify-content:center;">
                                <div style="width:100%; height:100%; border-radius:50%; background:#181818; display:flex; align-items:center; justify-content:center; font-size:14px;">
                                    {top_ad.get('creator_avatar', '🏢')}
                                </div>
                            </div>
                            <div>
                                <div style="font-size:13px; font-weight:700; color:#ffffff;">@{top_ad['creator']} <span style="color:#0095f6;">✓</span></div>
                                <div style="font-size:11px; color:#38bdf8;">🛡️ Sponsored • Verified for {user_cat} ({pol})</div>
                            </div>
                        </div>
                        <div style="font-size:11px; background:rgba(0,149,246,0.15); border:1px solid rgba(0,149,246,0.3); color:#38bdf8; padding:2px 8px; border-radius:4px;">
                            {pol}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                ad_vid = top_ad.get("video_path")
                if ad_vid and os.path.exists(ad_vid):
                    st.video(ad_vid, autoplay=False, loop=True)

                st.markdown(f"""
                <div style="background:#121212; border:1px solid #262626; border-top:none; border-radius:0 0 14px 14px; padding:12px 16px; margin-top:-20px; margin-bottom:24px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <div style="display:flex; gap:14px; font-size:20px;">
                            <span>❤️</span> <span>💬</span> <span>✈️</span>
                        </div>
                        <span style="font-size:12px; font-weight:700; color:#38bdf8;">{top_ad.get('cta_text', 'Learn More ↗')}</span>
                    </div>
                    <div style="font-size:13px; font-weight:700; color:#ffffff; margin-bottom:4px;">{format_count(top_ad.get('likes', 10000))} likes</div>
                    <div style="font-size:13px; color:#e2e8f0; margin-bottom:4px;">
                        <b>@{top_ad['creator']}</b> {top_ad.get('caption', '')}
                    </div>
                    <div style="font-size:11px; color:#8e8e8e;">SafeAd AI Verified Sponsored Content • Validated for your demographic</div>
                </div>
                """, unsafe_allow_html=True)

            # Post 3: Second Organic Post
            st.markdown("""
            <div style="background:#121212; border:1px solid #262626; border-radius:14px; margin-bottom:20px;">
                <div style="padding:12px 16px; display:flex; justify-content:space-between; align-items:center;">
                    <div style="display:flex; align-items:center; gap:10px;">
                        <div style="width:32px; height:32px; border-radius:50%; background:linear-gradient(45deg,#f09433,#dc2743,#bc1888); padding:1.5px; display:flex; align-items:center; justify-content:center;">
                            <div style="width:100%; height:100%; border-radius:50%; background:#181818; display:flex; align-items:center; justify-content:center; font-size:14px;">
                                🏎️
                            </div>
                        </div>
                        <div>
                            <div style="font-size:13px; font-weight:700; color:#ffffff;">@tokyo_night_run <span style="color:#0095f6;">✓</span></div>
                            <div style="font-size:11px; color:#8e8e8e;">Shuto Expressway, Tokyo</div>
                        </div>
                    </div>
                    <div style="color:#8e8e8e; font-size:14px;">•••</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            urban_path = os.path.join(BASE_DIR, "frontend/assets/reels/reel_urban_lights.mp4")
            if os.path.exists(urban_path):
                st.video(urban_path, autoplay=False, loop=True)

            st.markdown(f"""
            <div style="background:#121212; border:1px solid #262626; border-top:none; border-radius:0 0 14px 14px; padding:12px 16px; margin-top:-20px; margin-bottom:24px;">
                <div style="display:flex; gap:14px; font-size:20px; margin-bottom:8px;">
                    <span>❤️</span> <span>💬</span> <span>✈️</span>
                </div>
                <div style="font-size:13px; font-weight:700; color:#ffffff; margin-bottom:4px;">278,400 likes</div>
                <div style="font-size:13px; color:#e2e8f0; margin-bottom:4px;">
                    <b>@tokyo_night_run</b> Midnight cruise through the neon arteries of Tokyo 🌃 Light streaks and city pulse. Turn the volume up!
                </div>
                <div style="font-size:11px; color:#8e8e8e;">View all 3,450 comments • 5 hours ago</div>
            </div>
            """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # TAB 2: REELS TAB (AGE-APPROPRIATE REELS & BRAND OWNER ADS)
    # -------------------------------------------------------------------------
    elif st.session_state["user_subtab"] == "reels":
        # 1. Category Filter Pills
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
            if st.button("🛡️ Brand Owner Ads", key="flt_ads", use_container_width=True,
                         type="primary" if st.session_state["reels_filter"] == "SPONSORED" else "secondary"):
                st.session_state["reels_filter"] = "SPONSORED"
                st.session_state["current_reel_idx"] = 0
                st.rerun()

        # Filter reels based on user selection
        active_reels = list(curated_reels)
        if st.session_state["reels_filter"] == "ORGANIC":
            active_reels = [r for r in active_reels if r["type"] == "organic"]
        elif st.session_state["reels_filter"] == "SPONSORED":
            active_reels = [r for r in active_reels if r["type"] == "sponsored"]

        if not active_reels:
            st.info(f"No reels available in this category for age group '{user_cat}'.")
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
        # REEL VIEWPORT CONTAINER
        # ---------------------------------------------------------------------
        c_spacer_l, c_reel, c_spacer_r = st.columns([1, 3.8, 1])

        with c_reel:
            # Header Bar
            badge_icon = "✓" if current_reel.get("is_verified") else ""
            render_html(f"""
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
            """)

            # Video Player
            video_file = current_reel.get("video_path")
            if video_file and os.path.exists(video_file):
                st.video(video_file, autoplay=True, loop=True)
            else:
                st.warning("Video asset loading...")

            # Reel Info & Caption Overlay
            sponsored_html = ""
            if current_reel["type"] == "sponsored":
                pol = current_reel.get('safety_policy', 'SAFE_FOR_ALL')
                sponsored_html = f"""
                <div style="margin-bottom:8px;">
                    <span style="background:rgba(0,149,246,0.18); border:1px solid rgba(0,149,246,0.4); color:#38bdf8; font-size:11px; font-weight:700; padding:3px 8px; border-radius:6px;">
                        🛡️ SafeAd Verified • Policy: {pol} (Approved for @{username})
                    </span>
                </div>
                """

            render_html(f"""
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
            """)

            # -----------------------------------------------------------------
            # REELS INTERACTIVE ACTION BAR
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
                    st.toast(f"Redirecting to brand landing page ({current_reel.get('title')})...", icon="🚀")

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
                        <div style="color:#6b7280; font-size:11px;">
                            ❤️ {c.get('likes', 0)}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                st.markdown("</div>", unsafe_allow_html=True)

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
