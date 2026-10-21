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
import base64
from pathlib import Path
from PIL import Image, ImageOps
import numpy as np
import cv2

warnings.filterwarnings("ignore")

# =============================================================================
# FACE DETECTION & AGE ESTIMATION ENGINE (from feature/face-age-estimation)
# =============================================================================
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
from frontend.styles.instagram_theme import (
    render_instagram_logo,
    render_stories_bar,
    inject_instagram_web_light_theme
)

# Base project paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
ASSETS_DIR = os.path.join(BASE_DIR, "frontend/assets")

def get_base64_image(image_path: str) -> str:
    """Helper to convert local images to base64 for high-fidelity inline HTML rendering."""
    full_path = image_path if os.path.isabs(image_path) else os.path.join(BASE_DIR, image_path)
    if os.path.exists(full_path):
        ext = os.path.splitext(full_path)[1].lower().replace(".", "")
        mime = f"image/{'jpeg' if ext in ['jpg', 'jpeg'] else 'png'}"
        try:
            with open(full_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("utf-8")
                return f"data:{mime};base64,{b64}"
        except Exception:
            return ""
    return ""


# =============================================================================
# REELS CATALOG: INCLUDES @__shra1__ (IMAGE 2 REPLICA) & BRAND OWNER ADS
# =============================================================================
DEFAULT_REELS = [
    {
        "id": "reel_shra1",
        "type": "organic",
        "creator": "__shra1__",
        "creator_avatar": os.path.join(ASSETS_DIR, "avatar_shra1.png"),
        "is_verified": False,
        "location": "Kerala",
        "title": "Ep:40:Friends after Rejection??",
        "caption": "Ep:40:Friends after Rejection?? 💔✨ #malayalam #reels #friendship #kerala #relatable",
        "audio": "Original audio • __shra1__ 🎵",
        "likes": 68,
        "comments_count": 68,
        "shares_count": 104,
        "video_path": os.path.join(ASSETS_DIR, "reels/reel_shra1.mp4"),
        "fallback_image": os.path.join(ASSETS_DIR, "reel_shra1_full.png"),
        "comments": [
            {"user": "amal_v", "text": "True friendship never dies bro 🙌", "time": "2h", "likes": 14},
            {"user": "kavya_n", "text": "Waiting for Ep 41! ❤️", "time": "4h", "likes": 8},
            {"user": "arun_k", "text": "Relatable content 💯", "time": "5h", "likes": 5}
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
        "location": "Tromsø, Norway",
        "title": "NIGHT OF THE AURORA",
        "caption": "Dancing emerald curtains in Tromsø, Norway 🇳🇴 Nature never fails to amaze. Tag someone who needs to see this! 💚 #aurora #norway #travel #nightsky #nature",
        "audio": "Hans Zimmer • Time (Arctic Ambient Mix) 🎵",
        "likes": 321800,
        "comments_count": 4120,
        "shares_count": 89100,
        "video_path": os.path.join(ASSETS_DIR, "reels/reel_aurora.mp4"),
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
        "id": "reel_cyber",
        "type": "organic",
        "creator": "cyber_future",
        "creator_avatar": "🤖",
        "is_verified": True,
        "location": "Neo Tokyo",
        "title": "CYBER CITY 2099",
        "caption": "Flying through neon clouds at 200mph 🌇✨ Who else wants to live in this aesthetic? #cyberpunk #neon #reels #future #synthwave",
        "audio": "ODESZA • A Moment Apart (Cyberpunk Mix) 🎵",
        "likes": 184500,
        "comments_count": 2310,
        "shares_count": 45200,
        "video_path": os.path.join(ASSETS_DIR, "reels/reel_cyberpunk.mp4"),
        "comments": [
            {"user": "neon_rider", "text": "The lighting here is just insane 🔥", "time": "2h", "likes": 342}
        ]
    },
    {
        "id": "reel_sunset",
        "type": "organic",
        "creator": "golden_hour_ocean",
        "creator_avatar": "🌊",
        "is_verified": False,
        "location": "Maui, Hawaii",
        "title": "GOLDEN HOUR SWELL",
        "caption": "Catching the sunset over calm ocean waters 🌅 Nothing clears the mind like the rhythm of the waves. #sunset #ocean #goldenhour #beachlife #relax",
        "audio": "Ocean Waves & Acoustic Guitar • Sunset Peace 🎵",
        "likes": 152000,
        "comments_count": 1890,
        "shares_count": 34100,
        "video_path": os.path.join(ASSETS_DIR, "reels/reel_sunset_ocean.mp4"),
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
        "location": "Shuto Expressway, Tokyo",
        "title": "MIDNIGHT EXPRESSWAY",
        "caption": "Midnight cruise through the neon arteries of Tokyo 🌃 Light streaks and city pulse. Turn the volume up! #tokyo #nightdrive #carsoftiktok #speed #jdm",
        "audio": "Kavinsky • Nightcall (Tokyo Synthwave) 🎵",
        "likes": 278400,
        "comments_count": 3450,
        "shares_count": 67200,
        "video_path": os.path.join(ASSETS_DIR, "reels/reel_urban_lights.mp4"),
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


def build_curated_reels(user_cat: str, user_norm: str) -> list:
    """
    Builds the reels catalog dynamically:
    1. Base organic reels (starts with @__shra1__ as in Image 2)
    2. Brand Owner ads uploaded and approved in the Advertisement Validity tab
    3. Benchmark sponsored ads matching age
    """
    curated = []
    
    # 1. Start with the organic shra1 reel
    for r in DEFAULT_REELS:
        if r["id"] == "reel_shra1":
            curated.append(r)
            break

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

    # 4. Include default sponsored ads that match user's age
    for r in DEFAULT_REELS:
        if r["type"] == "sponsored":
            pol = r.get("safety_policy", "SAFE_FOR_ALL")
            if is_ad_allowed_for_age(pol, user_cat):
                curated.append(r)

    # 5. Include 18+ benchmark ad (casino) if user is 18+
    casino_path = os.path.join(BASE_DIR, "sample_ad_media/casino_ad.mp4")
    if user_cat == "18 and above" and os.path.exists(casino_path) and casino_path not in seen_paths:
        curated.append({
            "id": "ad_casino_18",
            "type": "sponsored",
            "creator": "vegas_grand_casino",
            "creator_avatar": "🎰",
            "is_verified": True,
            "sponsored_label": "Sponsored • 18+ Restricted Ad",
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

    # 6. Add remaining organic reels
    for r in DEFAULT_REELS:
        if r["type"] == "organic" and r["id"] != "reel_shra1":
            curated.append(r)

    return curated


# =============================================================================
# MAIN USER DASHBOARD CONTROLLER
# =============================================================================
def user_dashboard():
    # 1. Global User Database with Default Developer Testing Account (sourav/sourav)
    if "user_db" not in st.session_state:
        st.session_state["user_db"] = {
            "sourav": {
                "password": "sourav",
                "category": "18 and above",
                "norm": "AGE_18_PLUS",
                "is_verified": True,
                "display_name": "soorajjosegeorge",
                "full_name": "Sooraj Jose George"
            }
        }

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
        st.markdown("<div style='height: 35px;'></div>", unsafe_allow_html=True)
        
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
            <div style="background:#ffffff; border:1px solid #dbdbdb; border-radius:12px; padding:28px 32px; margin-bottom:16px; box-shadow:0 4px 18px rgba(0,0,0,0.04);">
                <div style="font-size:16px; font-weight:700; color:#262626; margin-bottom:16px; text-align:center;">
                    Log In to Your Account
                </div>
            """, unsafe_allow_html=True)

            login_user = st.text_input("Username", key="login_usr_input", placeholder="Enter username")
            login_pass = st.text_input("Password", type="password", key="login_pwd_input", placeholder="Enter password")

            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

            if st.button("Log In", key="btn_login_submit", type="primary", use_container_width=True):
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
                <div style="background:#f8fafc; border:1px dashed #cbd5e1; border-radius:8px; padding:10px 14px; margin-top:16px; font-size:12px; color:#64748b; text-align:center;">
                    💡 <b>Developer Testing Account:</b> Username: <code style="color:#0284c7; font-weight:700;">sourav</code> &nbsp;|&nbsp; Password: <code style="color:#0284c7; font-weight:700;">sourav</code>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Registration redirection box
            st.markdown("""
            <div style="background:#ffffff; border:1px solid #dbdbdb; border-radius:12px; padding:16px 20px; text-align:center; margin-bottom:20px; box-shadow:0 2px 10px rgba(0,0,0,0.03);">
                <span style="color:#737373; font-size:13px;">Don't have an account? </span>
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
        <div style="background:#ffffff; border:1px solid #dbdbdb; border-radius:12px; padding:20px 24px; margin-bottom:20px; box-shadow:0 2px 12px rgba(0,0,0,0.04);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
                <div>
                    <h3 style="margin:0; font-size:18px; color:#262626; font-weight:700;">👤 Account Registration</h3>
                    <p style="margin:0; font-size:12px; color:#737373;">Enter your new login credentials below. Complete ID & live biometric verification to activate your account.</p>
                </div>
            </div>
        """, unsafe_allow_html=True)

        col_reg1, col_reg2, col_reg3, col_reg4 = st.columns([1.5, 1.5, 1.5, 1.2])
        with col_reg1:
            new_username = st.text_input("New Username", key="reg_username_input", placeholder="Choose username")
        with col_reg2:
            new_password = st.text_input("Password", type="password", key="reg_password_input", placeholder="Create password")
        with col_reg3:
            confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm_password", placeholder="Confirm password")
        with col_reg4:
            st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
            if st.button("Sign IN", key="btn_back_to_signin", use_container_width=True, help="Already have an account? Return to Sign In"):
                if "vision_engine" in st.session_state:
                    try:
                        st.session_state["vision_engine"].stop()
                    except Exception:
                        pass
                    del st.session_state["vision_engine"]
                st.session_state["user_auth_state"] = "LOGIN"
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

        # ---------------------------------------------------------------------
        # FACE DETECTION & ID CARD UPLOAD FEATURES (ORIGINAL FROM SOORAJ'S BRANCH)
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
                            <div style="background:#fee2e2; border:1px solid #ef4444; border-radius:10px; padding:10px; margin-top:6px;">
                                <b style="color:#b91c1c;">🛑 YOU ARE A SCREEN</b><br>
                                <span style="color:#dc2626; font-size:12px;">Photo/Screen Spoof Detected! ({spoof_detail})</span>
                                {score_html.strip() if score_html else ""}
                            </div>
                            """
                        elif match_score is not None:
                            color = "#16a34a" if is_match else "#dc2626"
                            tag = "✅ BIOMETRICS MATCH" if is_match else "❌ BIOMETRIC MISMATCH"
                            card_html = f"""
                            <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:10px; margin-top:6px; display:flex; justify-content:space-between; align-items:center;">
                                <div>
                                    <span style="font-weight:700; color:{color};">{tag}</span><br>
                                    <span style="font-size:12px; color:#64748b;">ArcFace MS1MV3 Confidence</span>
                                </div>
                                <div style="font-size:22px; font-weight:800; color:{color};">{match_score:.1%}</div>
                            </div>
                            """
                        else:
                            card_html = "<div style='color:#64748b; font-size:12px; padding:6px 0;'>Face detected. Upload an ID Card on the left to cross-match.</div>"

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
                    <div style="border:2px dashed #cbd5e1; border-radius:12px; padding:32px; text-align:center; background:#f8fafc; margin-bottom:12px;">
                        <div style="font-size:36px; margin-bottom:8px;">🎥</div>
                        <div style="font-size:15px; font-weight:600; color:#334155;">Live Camera Feed is Off</div>
                        <div style="font-size:12px; color:#64748b;">Toggle <b>'Start Live Camera Feed'</b> above and freeze a frame to verify identity.</div>
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
                <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:10px; padding:12px; text-align:center; box-shadow:0 1px 4px rgba(0,0,0,0.03);">
                    <div style="font-size:22px; font-weight:700; color:#0284c7;">{verif_res.get('face_similarity', 0.0):.1%}</div>
                    <div style="font-size:11px; color:#64748b;">Face Match Score</div>
                </div>
                """, unsafe_allow_html=True)
            with c_r2:
                anti_spoof_tag = "🛑 SPOOF" if verif_res.get('is_spoof') else "✅ REAL (LIVE)"
                color = "#dc2626" if verif_res.get('is_spoof') else "#16a34a"
                st.markdown(f"""
                <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:10px; padding:12px; text-align:center; box-shadow:0 1px 4px rgba(0,0,0,0.03);">
                    <div style="font-size:18px; font-weight:700; color:{color};">{anti_spoof_tag}</div>
                    <div style="font-size:11px; color:#64748b;">Liveness Check</div>
                </div>
                """, unsafe_allow_html=True)
            with c_r3:
                st.markdown(f"""
                <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:10px; padding:12px; text-align:center; box-shadow:0 1px 4px rgba(0,0,0,0.03);">
                    <div style="font-size:20px; font-weight:700; color:#7c3aed;">{verif_res.get('id_age', 'N/A')} yrs</div>
                    <div style="font-size:11px; color:#64748b;">Extracted ID Age</div>
                </div>
                """, unsafe_allow_html=True)
            with c_r4:
                st.markdown(f"""
                <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:10px; padding:12px; text-align:center; box-shadow:0 1px 4px rgba(0,0,0,0.03);">
                    <div style="font-size:18px; font-weight:700; color:#d97706;">{verif_res.get('live_age_category', 'N/A')}</div>
                    <div style="font-size:11px; color:#64748b;">Live ViT Age Scan</div>
                </div>
                """, unsafe_allow_html=True)

            # Overall Status Alert
            if verif_res.get("status") == "VERIFIED_SUCCESS":
                st.markdown(f"""
                <div style="background:#f0fdf4; border:1px solid #22c55e; border-radius:12px; padding:16px; margin-top:16px; margin-bottom:18px;">
                    <h3 style="color:#15803d; margin:0 0 6px 0; font-size:16px;">
                        🎉 Biometrics Verified: Blue Badge Awarded! <span style="color:#0095f6;">✓</span>
                    </h3>
                    <p style="color:#166534; margin:0; font-size:12px;">ID and live camera facial scan cross-matched with {verif_res.get('face_similarity', 0.0):.1%} similarity. Click Complete Registration below to create your account.</p>
                </div>
                """, unsafe_allow_html=True)
            elif verif_res.get("is_spoof"):
                st.markdown(f"""
                <div style="background:#fef2f2; border:1px solid #ef4444; border-radius:12px; padding:16px; margin-top:16px; margin-bottom:18px;">
                    <h3 style="color:#b91c1c; margin:0 0 6px 0; font-size:16px;">
                        🛑 Presentation Attack Blocked: YOU ARE A SCREEN
                    </h3>
                    <p style="color:#991b1b; margin:0; font-size:12px;">Photo/Screen Spoof Detected! ({verif_res.get('spoof_reason')}). Please present a real live person.</p>
                </div>
                """, unsafe_allow_html=True)
            elif not verif_res.get("face_match"):
                st.markdown(f"""
                <div style="background:#fef2f2; border:1px solid #ef4444; border-radius:12px; padding:16px; margin-top:16px; margin-bottom:18px;">
                    <h3 style="color:#b91c1c; margin:0 0 6px 0; font-size:16px;">
                        ❌ Biometric Mismatch: ID Card & Live User Do Not Match!
                    </h3>
                    <p style="color:#991b1b; margin:0; font-size:12px;">ArcFace MS1MV3 biometric similarity confidence is <b>{verif_res.get('face_similarity', 0.0):.1%}</b> (Threshold: &ge; 65.0%). Verification rejected.</p>
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

                if "user_db" not in st.session_state:
                    st.session_state["user_db"] = {}

                st.session_state["user_db"][new_username] = {
                    "password": new_password,
                    "category": cat,
                    "norm": norm,
                    "is_verified": True,
                    "display_name": new_username,
                    "full_name": new_username.title(),
                    "verification_data": verif_res
                }
                st.session_state["logged_in_username"] = new_username
                st.session_state["verified_age_category"] = cat
                st.session_state["verified_age_norm"] = norm
                st.session_state["user_auth_state"] = "AUTHENTICATED"
                st.session_state["user_subtab"] = "feed"
                st.success(f"🎉 Account created & verified for @{new_username}! Redirecting to Instagram...")
                st.rerun()

        return

    # =========================================================================
    # OPTION 3: AUTHENTICATED INSTAGRAM INTERFACE (EXACT REPLICA OF IMAGES 1 & 2)
    # =========================================================================
    # Inject authentic desktop Instagram white theme
    inject_instagram_web_light_theme()

    username = st.session_state.get("logged_in_username", "sourav")
    user_db_entry = st.session_state.get("user_db", {}).get(username, {})
    display_user = user_db_entry.get("display_name", username)
    user_cat = st.session_state.get("verified_age_category", "18 and above")
    user_norm = st.session_state.get("verified_age_norm", "AGE_18_PLUS")

    # Load base64 assets for instant zero-lag rendering
    b64_merling = get_base64_image(os.path.join(ASSETS_DIR, "avatar_merling.png"))
    b64_shra1 = get_base64_image(os.path.join(ASSETS_DIR, "avatar_shra1.png"))
    b64_sooraj = get_base64_image(os.path.join(ASSETS_DIR, "avatar_sooraj.png"))
    b64_flower = get_base64_image(os.path.join(ASSETS_DIR, "post_flower.png"))
    b64_ganesh = get_base64_image(os.path.join(ASSETS_DIR, "avatar_ganesh_rajesh.png"))
    b64_modtech = get_base64_image(os.path.join(ASSETS_DIR, "avatar_modtechsolar.png"))
    b64_shreya = get_base64_image(os.path.join(ASSETS_DIR, "avatar_shreya_ann_jacob.png"))
    b64_moly = get_base64_image(os.path.join(ASSETS_DIR, "avatar_molystuitions.png"))
    b64_k = get_base64_image(os.path.join(ASSETS_DIR, "avatar_k.png"))
    b64_msg_pill = get_base64_image(os.path.join(ASSETS_DIR, "messages_pill.png"))

    curated_reels = build_curated_reels(user_cat, user_norm)

    # 3-COLUMN DESKTOP INSTAGRAM LAYOUT: Left Nav | Center Main Feed / Reel | Right Sidebar
    col_nav, col_main, col_side = st.columns([1.1, 2.7, 1.4], gap="large")

    # -------------------------------------------------------------------------
    # COLUMN 1: LEFT NAVIGATION RAIL (INSTAGRAM DESKTOP NAVBAR)
    # -------------------------------------------------------------------------
    with col_nav:
        st.markdown("""
        <div style="padding:12px 8px 18px 8px;">
            <div style="font-family:'Grand Hotel', cursive, -apple-system, sans-serif; font-size:38px; color:#262626; line-height:1; margin-bottom:20px; cursor:pointer;">
                Instagram
            </div>
        </div>
        """, unsafe_allow_html=True)

        is_feed = (st.session_state["user_subtab"] == "feed")
        is_reels = (st.session_state["user_subtab"] == "reels")

        # Home Nav Button
        if st.button("🏠  Home", key="nav_btn_home", use_container_width=True, type="primary" if is_feed else "secondary"):
            st.session_state["user_subtab"] = "feed"
            st.rerun()

        # Search Nav Button
        if st.button("🔍  Search", key="nav_btn_search", use_container_width=True):
            st.session_state["show_search_box"] = not st.session_state.get("show_search_box", False)
            st.rerun()

        # Explore Nav Button
        st.button("🧭  Explore", key="nav_btn_explore", use_container_width=True)

        # Reels Nav Button (Matching Image 2)
        if st.button("🎬  Reels", key="nav_btn_reels", use_container_width=True, type="primary" if is_reels else "secondary"):
            st.session_state["user_subtab"] = "reels"
            st.rerun()

        # Messages Nav Button with Badge "1"
        st.markdown("""
        <div style="position:relative; margin-bottom:4px;">
            <div style="display:flex; align-items:center; justify-content:space-between; padding:9px 14px; border-radius:8px; color:#262626; font-size:14px; font-weight:500; cursor:pointer;" onmouseover="this.style.background='#f2f2f2'" onmouseout="this.style.background='transparent'">
                <div style="display:flex; align-items:center; gap:12px;">
                    <span style="font-size:17px;">💬</span> <span>Messages</span>
                </div>
                <span style="background:#ff3040; color:#fff; font-size:10px; font-weight:800; border-radius:10px; padding:1px 6px;">1</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Notifications Nav with Red Pill Badge "💬 12 ❤️ 5 👤 2"
        st.markdown("""
        <div style="position:relative; margin-bottom:4px;">
            <div style="display:flex; align-items:center; justify-content:space-between; padding:9px 14px; border-radius:8px; color:#262626; font-size:14px; font-weight:500; cursor:pointer;" onmouseover="this.style.background='#f2f2f2'" onmouseout="this.style.background='transparent'">
                <div style="display:flex; align-items:center; gap:12px;">
                    <span style="font-size:17px;">❤️</span> <span>Notifications</span>
                </div>
                <span style="background:#ff3040; color:#fff; font-size:9px; font-weight:700; border-radius:10px; padding:2px 6px; letter-spacing:0.2px;">💬 12 &nbsp;❤️ 5 &nbsp;👤 2</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.button("➕  Create", key="nav_btn_create", use_container_width=True)

        # Profile Nav Link
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:12px; padding:9px 14px; border-radius:8px; color:#262626; font-size:14px; font-weight:600; cursor:pointer; margin-bottom:24px;" onmouseover="this.style.background='#f2f2f2'" onmouseout="this.style.background='transparent'">
            <img src="{b64_sooraj}" style="width:24px; height:24px; border-radius:50%; object-fit:cover; border:1px solid #dbdbdb;">
            <span>Profile</span>
            <span style="color:#0095f6; font-size:12px; margin-left:auto;">✓</span>
        </div>
        """, unsafe_allow_html=True)

        # Bottom items: Threads & Logout
        st.markdown("<div style='height:80px;'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div style="display:flex; align-items:center; gap:12px; padding:8px 14px; border-radius:8px; color:#262626; font-size:14px; cursor:pointer;" onmouseover="this.style.background='#f2f2f2'" onmouseout="this.style.background='transparent'">
            <span style="font-size:16px;">🧵</span> <span>Threads</span>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚪  Log Out", key="nav_btn_logout", use_container_width=True):
            if "vision_engine" in st.session_state:
                try:
                    st.session_state["vision_engine"].stop()
                except Exception:
                    pass
                del st.session_state["vision_engine"]
            st.session_state["user_auth_state"] = "LOGIN"
            st.session_state["logged_in_username"] = None
            st.rerun()

        # Age-Gated Safety Info Card
        st.markdown(f"""
        <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:10px 12px; margin-top:20px;">
            <div style="font-size:10px; font-weight:800; color:#0284c7; letter-spacing:0.5px;">SAFEAD VERIFIED</div>
            <div style="font-size:12px; font-weight:700; color:#334155; margin-top:2px;">@{username}</div>
            <div style="font-size:10px; color:#64748b;">Tier: <b>{user_norm}</b> ({user_cat})</div>
        </div>
        """, unsafe_allow_html=True)


    # -------------------------------------------------------------------------
    # COLUMN 2: MAIN CONTENT AREA (HOMEPAGE FEED OR REELS VIEW)
    # -------------------------------------------------------------------------
    with col_main:
        # Search Box Popup (if triggered)
        if st.session_state.get("show_search_box"):
            search_query = st.text_input("Search Instagram...", placeholder="Search accounts, tags, audio...", key="main_search_input")
            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

        # =====================================================================
        # TAB 1: USUAL INSTAGRAM HOMEPAGE INTERFACE (EXACT REPLICA OF IMAGE 1)
        # =====================================================================
        if st.session_state["user_subtab"] == "feed":
            # 1. Instagram Stories Tray (Matching Image 1: _alw1n_, freeda_irut..., ig_abhines..., geethama..., v_anantha..., d.mxhi)
            st.markdown(f"""
            <div style="background:#ffffff; border:1px solid #dbdbdb; border-radius:10px; padding:14px 16px; margin-bottom:20px; display:flex; align-items:center; justify-content:space-between; overflow-x:auto;">
                <div style="display:flex; gap:18px; align-items:center;">
                    <!-- Story 1: _alw1n_ -->
                    <div style="display:flex; flex-direction:column; align-items:center; gap:5px; cursor:pointer; width:64px;">
                        <div style="width:58px; height:58px; border-radius:50%; background:linear-gradient(45deg,#f09433,#dc2743,#bc1888); padding:2px; display:flex; align-items:center; justify-content:center;">
                            <div style="width:100%; height:100%; border-radius:50%; background:#f3f4f6; border:2px solid #fff; display:flex; align-items:center; justify-content:center; font-size:20px;">
                                🧢
                            </div>
                        </div>
                        <span style="font-size:11px; color:#262626; max-width:62px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">_alw1n_</span>
                    </div>
                    <!-- Story 2: freeda_irut... -->
                    <div style="display:flex; flex-direction:column; align-items:center; gap:5px; cursor:pointer; width:64px;">
                        <div style="width:58px; height:58px; border-radius:50%; background:linear-gradient(45deg,#f09433,#dc2743,#bc1888); padding:2px; display:flex; align-items:center; justify-content:center;">
                            <div style="width:100%; height:100%; border-radius:50%; background:#f3f4f6; border:2px solid #fff; display:flex; align-items:center; justify-content:center; font-size:20px;">
                                🌸
                            </div>
                        </div>
                        <span style="font-size:11px; color:#262626; max-width:62px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">freeda_irut...</span>
                    </div>
                    <!-- Story 3: ig_abhines... -->
                    <div style="display:flex; flex-direction:column; align-items:center; gap:5px; cursor:pointer; width:64px;">
                        <div style="width:58px; height:58px; border-radius:50%; background:linear-gradient(45deg,#f09433,#dc2743,#bc1888); padding:2px; display:flex; align-items:center; justify-content:center;">
                            <div style="width:100%; height:100%; border-radius:50%; background:#f3f4f6; border:2px solid #fff; display:flex; align-items:center; justify-content:center; font-size:20px;">
                                📸
                            </div>
                        </div>
                        <span style="font-size:11px; color:#262626; max-width:62px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">ig_abhines...</span>
                    </div>
                    <!-- Story 4: geethama... -->
                    <div style="display:flex; flex-direction:column; align-items:center; gap:5px; cursor:pointer; width:64px;">
                        <div style="width:58px; height:58px; border-radius:50%; background:linear-gradient(45deg,#f09433,#dc2743,#bc1888); padding:2px; display:flex; align-items:center; justify-content:center;">
                            <div style="width:100%; height:100%; border-radius:50%; background:#f3f4f6; border:2px solid #fff; display:flex; align-items:center; justify-content:center; font-size:20px;">
                                🪔
                            </div>
                        </div>
                        <span style="font-size:11px; color:#262626; max-width:62px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">geethama...</span>
                    </div>
                    <!-- Story 5: v_anantha... -->
                    <div style="display:flex; flex-direction:column; align-items:center; gap:5px; cursor:pointer; width:64px;">
                        <div style="width:58px; height:58px; border-radius:50%; background:linear-gradient(45deg,#f09433,#dc2743,#bc1888); padding:2px; display:flex; align-items:center; justify-content:center;">
                            <div style="width:100%; height:100%; border-radius:50%; background:#f3f4f6; border:2px solid #fff; display:flex; align-items:center; justify-content:center; font-size:20px;">
                                🏄‍♂️
                            </div>
                        </div>
                        <span style="font-size:11px; color:#262626; max-width:62px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">v_anantha...</span>
                    </div>
                    <!-- Story 6: d.mxhi -->
                    <div style="display:flex; flex-direction:column; align-items:center; gap:5px; cursor:pointer; width:64px;">
                        <div style="width:58px; height:58px; border-radius:50%; background:linear-gradient(45deg,#f09433,#dc2743,#bc1888); padding:2px; display:flex; align-items:center; justify-content:center;">
                            <div style="width:100%; height:100%; border-radius:50%; background:#f3f4f6; border:2px solid #fff; display:flex; align-items:center; justify-content:center; font-size:20px;">
                                🌿
                            </div>
                        </div>
                        <span style="font-size:11px; color:#262626; max-width:62px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">d.mxhi</span>
                    </div>
                </div>
                <!-- Right arrow navigation chevron -->
                <div style="width:28px; height:28px; border-radius:50%; background:#fff; border:1px solid #dbdbdb; box-shadow:0 1px 4px rgba(0,0,0,0.1); display:flex; align-items:center; justify-content:center; cursor:pointer; color:#737373; font-weight:700;">
                    ›
                </div>
            </div>
            """, unsafe_allow_html=True)

            # -----------------------------------------------------------------
            # POST 1: EXACT REPLICA OF @_merling FLOWER POST (FROM IMAGE 1)
            # -----------------------------------------------------------------
            st.markdown(f"""
            <div style="background:#ffffff; border:1px solid #dbdbdb; border-radius:8px; margin-bottom:24px; overflow:hidden;">
                <!-- Post Header -->
                <div style="padding:10px 14px; display:flex; justify-content:space-between; align-items:center;">
                    <div style="display:flex; align-items:center; gap:10px;">
                        <img src="{b64_merling}" style="width:32px; height:32px; border-radius:50%; object-fit:cover; border:1px solid #dbdbdb;">
                        <div>
                            <div style="display:flex; align-items:center; gap:6px;">
                                <span style="font-size:13px; font-weight:700; color:#262626;">_merling</span>
                                <span style="font-size:12px; color:#737373;">• 1d •</span>
                                <span style="font-size:12px; font-weight:700; color:#0095f6; cursor:pointer;">Follow</span>
                            </div>
                            <div style="font-size:11px; color:#737373;">Taj Green Cove Resort and Spa Kovalam</div>
                        </div>
                    </div>
                    <div style="color:#737373; font-size:16px; font-weight:700; cursor:pointer; padding:4px 8px;">•••</div>
                </div>
                
                <!-- Main Post Image: Yellow Flower Held in Hand -->
                <div style="width:100%; text-align:center; background:#f8fafc; border-top:1px solid #f2f2f2; border-bottom:1px solid #f2f2f2;">
                    <img src="{b64_flower}" style="width:100%; max-height:480px; object-fit:contain; display:block; margin:0 auto;">
                </div>

                <!-- Carousel Indicator Dots -->
                <div style="display:flex; justify-content:center; align-items:center; gap:4px; padding-top:8px;">
                    <span style="width:6px; height:6px; border-radius:50%; background:#0095f6; display:inline-block;"></span>
                    <span style="width:5px; height:5px; border-radius:50%; background:#dbdbdb; display:inline-block;"></span>
                    <span style="width:5px; height:5px; border-radius:50%; background:#dbdbdb; display:inline-block;"></span>
                </div>

                <!-- Action Bar -->
                <div style="padding:8px 14px 4px 14px; display:flex; justify-content:space-between; align-items:center;">
                    <div style="display:flex; gap:16px; font-size:22px; color:#262626;">
                        <span style="cursor:pointer;" title="Like">❤️</span>
                        <span style="cursor:pointer;" title="Comment">💬</span>
                        <span style="cursor:pointer;" title="Share">✈️</span>
                    </div>
                    <span style="font-size:22px; color:#262626; cursor:pointer;" title="Save">🔖</span>
                </div>

                <!-- Likes Count -->
                <div style="padding:2px 14px; font-size:13px; font-weight:700; color:#262626;">
                    107 likes
                </div>

                <!-- Caption -->
                <div style="padding:2px 14px 4px 14px; font-size:13px; color:#262626;">
                    <b>_merling</b> 💛
                </div>

                <!-- Comments Count & Timestamp -->
                <div style="padding:2px 14px; font-size:12px; color:#737373; cursor:pointer;">
                    View all 6 comments
                </div>
                <div style="padding:2px 14px 10px 14px; font-size:10px; color:#8e8e8e; text-transform:uppercase; letter-spacing:0.5px;">
                    1 DAY AGO
                </div>

                <!-- Add a Comment Bar -->
                <div style="border-top:1px solid #efefef; padding:10px 14px; display:flex; justify-content:space-between; align-items:center; background:#ffffff;">
                    <span style="color:#8e8e8e; font-size:13px;">Add a comment...</span>
                    <div style="display:flex; gap:10px; align-items:center;">
                        <span style="color:#0095f6; font-size:13px; font-weight:700; cursor:pointer;">Post</span>
                        <span style="cursor:pointer; font-size:15px;">😊</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # -----------------------------------------------------------------
            # POST 2: AGE-APPROPRIATE BRAND OWNER AD (FROM ADVERTISEMENT VALIDITY TAB)
            # -----------------------------------------------------------------
            owner_ads = [r for r in curated_reels if r["type"] == "sponsored"]
            if owner_ads:
                top_ad = owner_ads[0]
                pol = top_ad.get("safety_policy", "SAFE_FOR_ALL")
                st.markdown(f"""
                <div style="background:#ffffff; border:1px solid #dbdbdb; border-radius:8px; margin-bottom:24px; overflow:hidden;">
                    <!-- Ad Header -->
                    <div style="padding:10px 14px; display:flex; justify-content:space-between; align-items:center;">
                        <div style="display:flex; align-items:center; gap:10px;">
                            <div style="width:32px; height:32px; border-radius:50%; background:linear-gradient(45deg,#0095f6,#38bdf8); padding:1.5px; display:flex; align-items:center; justify-content:center;">
                                <div style="width:100%; height:100%; border-radius:50%; background:#fff; display:flex; align-items:center; justify-content:center; font-size:15px;">
                                    {top_ad.get('creator_avatar', '🏢')}
                                </div>
                            </div>
                            <div>
                                <div style="display:flex; align-items:center; gap:6px;">
                                    <span style="font-size:13px; font-weight:700; color:#262626;">@{top_ad['creator']}</span>
                                    <span style="color:#0095f6; font-size:12px;">✓</span>
                                </div>
                                <div style="font-size:11px; color:#0284c7; font-weight:600;">
                                    🛡️ Sponsored • Verified for {user_cat} ({pol})
                                </div>
                            </div>
                        </div>
                        <span style="background:#e0f2fe; color:#0369a1; font-size:10px; font-weight:700; padding:2px 8px; border-radius:4px;">
                            {pol}
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                ad_vid = top_ad.get("video_path")
                if ad_vid and os.path.exists(ad_vid):
                    st.video(ad_vid, autoplay=False, loop=True)

                st.markdown(f"""
                <div style="background:#ffffff; border:1px solid #dbdbdb; border-top:none; border-radius:0 0 8px 8px; margin-top:-20px; padding:12px 14px 14px 14px; margin-bottom:24px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                        <div style="display:flex; gap:16px; font-size:22px; color:#262626;">
                            <span>❤️</span> <span>💬</span> <span>✈️</span>
                        </div>
                        <span style="background:#0095f6; color:#ffffff; font-size:12px; font-weight:700; padding:4px 12px; border-radius:6px; cursor:pointer;">
                            {top_ad.get('cta_text', 'Learn More ↗')}
                        </span>
                    </div>
                    <div style="font-size:13px; font-weight:700; color:#262626; margin-bottom:4px;">
                        {format_count(top_ad.get('likes', 12400))} likes
                    </div>
                    <div style="font-size:13px; color:#262626; margin-bottom:4px;">
                        <b>@{top_ad['creator']}</b> {top_ad.get('caption', '')}
                    </div>
                    <div style="font-size:11px; color:#64748b; margin-top:4px;">
                        SafeAd AI Certified • Content meets compliance standards for age bracket <b>{user_cat}</b>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # -----------------------------------------------------------------
            # POST 3: ORGANIC COMMUNITY POST (AURORA EXPLORERS)
            # -----------------------------------------------------------------
            aurora_path = os.path.join(ASSETS_DIR, "reels/reel_aurora.mp4")
            st.markdown(f"""
            <div style="background:#ffffff; border:1px solid #dbdbdb; border-radius:8px; margin-bottom:24px; overflow:hidden;">
                <div style="padding:10px 14px; display:flex; justify-content:space-between; align-items:center;">
                    <div style="display:flex; align-items:center; gap:10px;">
                        <div style="width:32px; height:32px; border-radius:50%; background:linear-gradient(45deg,#f09433,#dc2743,#bc1888); padding:1.5px; display:flex; align-items:center; justify-content:center;">
                            <div style="width:100%; height:100%; border-radius:50%; background:#fff; display:flex; align-items:center; justify-content:center; font-size:14px;">
                                🌌
                            </div>
                        </div>
                        <div>
                            <div style="font-size:13px; font-weight:700; color:#262626;">@aurora_explorers <span style="color:#0095f6;">✓</span></div>
                            <div style="font-size:11px; color:#737373;">Tromsø, Norway</div>
                        </div>
                    </div>
                    <div style="color:#737373; font-size:16px;">•••</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if os.path.exists(aurora_path):
                st.video(aurora_path, autoplay=False, loop=True)

            st.markdown(f"""
            <div style="background:#ffffff; border:1px solid #dbdbdb; border-top:none; border-radius:0 0 8px 8px; margin-top:-20px; padding:12px 14px 14px 14px; margin-bottom:24px;">
                <div style="display:flex; gap:16px; font-size:22px; color:#262626; margin-bottom:6px;">
                    <span>❤️</span> <span>💬</span> <span>✈️</span>
                </div>
                <div style="font-size:13px; font-weight:700; color:#262626; margin-bottom:4px;">321,800 likes</div>
                <div style="font-size:13px; color:#262626; margin-bottom:4px;">
                    <b>@aurora_explorers</b> Dancing emerald curtains in Tromsø 🇳🇴 Nature never fails to amaze! Tag a travel buddy 💚
                </div>
                <div style="font-size:11px; color:#737373;">View all 4,120 comments • 2 hours ago</div>
            </div>
            """, unsafe_allow_html=True)


        # =====================================================================
        # TAB 2: REELS USER PAGE (EXACT REPLICA OF IMAGE 2)
        # =====================================================================
        elif st.session_state["user_subtab"] == "reels":
            # Filter pills for Reels
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

            active_reels = list(curated_reels)
            if st.session_state["reels_filter"] == "ORGANIC":
                active_reels = [r for r in active_reels if r["type"] == "organic"]
            elif st.session_state["reels_filter"] == "SPONSORED":
                active_reels = [r for r in active_reels if r["type"] == "sponsored"]

            if not active_reels:
                st.info(f"No reels available in this category for age category '{user_cat}'.")
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

            # 2 Columns for Reels: 9:16 Video Player Container on left + Vertical Action Rail on right
            r_col_vid, r_col_rail = st.columns([4, 1.2], gap="small")

            with r_col_vid:
                # Top Sound & Status Bar
                st.markdown(f"""
                <div style="background:#ffffff; border:1px solid #dbdbdb; border-radius:12px 12px 0 0; padding:10px 14px; display:flex; justify-content:space-between; align-items:center;">
                    <div style="display:flex; align-items:center; gap:8px;">
                        <span style="font-size:16px;">🔊</span>
                        <span style="font-size:12px; font-weight:700; color:#262626;">Instagram Reels</span>
                    </div>
                    <div style="font-size:11px; font-weight:700; color:#737373;">{idx + 1} / {total_reels}</div>
                </div>
                """, unsafe_allow_html=True)

                # Vertical Video Viewport (9:16)
                vid_file = current_reel.get("video_path")
                if vid_file and os.path.exists(vid_file):
                    st.video(vid_file, autoplay=True, loop=True)
                elif current_reel.get("fallback_image") and os.path.exists(current_reel.get("fallback_image")):
                    st.image(current_reel["fallback_image"], width="stretch")
                else:
                    st.warning("Video asset loading...")

                # Reel Overlay Details (Matching Image 2: @__shra1__, Kerala, Ep:40:Friends after Rejection??)
                sponsored_badge_html = ""
                if current_reel["type"] == "sponsored":
                    pol = current_reel.get('safety_policy', 'SAFE_FOR_ALL')
                    sponsored_badge_html = f"""
                    <div style="margin-bottom:6px;">
                        <span style="background:#e0f2fe; border:1px solid #0284c7; color:#0369a1; font-size:11px; font-weight:700; padding:2px 8px; border-radius:4px;">
                            🛡️ Sponsored • Verified for {user_cat} ({pol})
                        </span>
                    </div>
                    """

                avatar_src = b64_shra1 if current_reel.get("creator") == "__shra1__" else ""
                avatar_tag = f'<img src="{avatar_src}" style="width:34px; height:34px; border-radius:50%; object-fit:cover; border:1.5px solid #fff;">' if avatar_src else f'<div style="width:34px; height:34px; border-radius:50%; background:#1e293b; color:#fff; display:flex; align-items:center; justify-content:center; font-size:16px;">{current_reel.get("creator_avatar", "👤")}</div>'

                st.markdown(f"""
                <div style="background:#ffffff; border:1px solid #dbdbdb; border-top:none; border-radius:0 0 12px 12px; padding:12px 16px; margin-top:-20px; margin-bottom:20px;">
                    {sponsored_badge_html}
                    <!-- Creator Row -->
                    <div style="display:flex; align-items:center; gap:10px; margin-bottom:6px;">
                        {avatar_tag}
                        <div style="display:flex; align-items:center; gap:6px;">
                            <span style="font-size:14px; font-weight:700; color:#262626;">@{current_reel['creator']}</span>
                            <span style="border:1px solid #dbdbdb; border-radius:6px; padding:2px 8px; font-size:11px; font-weight:700; color:#262626; cursor:pointer;">Follow</span>
                        </div>
                    </div>
                    <!-- Location -->
                    <div style="font-size:11px; color:#737373; margin-bottom:4px;">
                        📍 {current_reel.get('location', 'Kerala')}
                    </div>
                    <!-- Caption -->
                    <div style="font-size:13px; font-weight:600; color:#262626; margin-bottom:6px;">
                        {current_reel.get('title', '')}
                    </div>
                    <div style="font-size:12px; color:#475569; margin-bottom:8px; line-height:1.4;">
                        {current_reel.get('caption', '')}
                    </div>
                    <!-- Audio Track -->
                    <div style="display:flex; align-items:center; gap:6px; font-size:11px; color:#737373;">
                        <span>🎵</span> <span>{current_reel.get('audio', 'Original sound')}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if current_reel["type"] == "sponsored" and current_reel.get("cta_text"):
                    if st.button(f"👉 {current_reel['cta_text']}", key=f"cta_reel_{reel_id}", type="primary", use_container_width=True):
                        st.toast(f"Opening sponsor landing page ({current_reel.get('title')})...", icon="🚀")

            # Right Vertical Action Rail (Matching Image 2: ❤️ 68, 💬 68, 🔄 104, ✈️, 🔖, ..., disc)
            with r_col_rail:
                st.markdown("<div style='height:40px;'></div>", unsafe_allow_html=True)
                
                # Up Navigation Arrow
                if st.button("🔼", key="btn_reel_up", use_container_width=True, help="Previous Reel"):
                    st.session_state["current_reel_idx"] = (idx - 1) % total_reels
                    st.session_state["show_comments_for"] = None
                    st.rerun()

                st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

                # Like Action (Heart)
                heart_label = f"❤️\n{format_count(like_count)}" if is_liked else f"🤍\n{format_count(like_count)}"
                if st.button(heart_label, key=f"btn_like_{reel_id}", use_container_width=True):
                    if is_liked:
                        st.session_state["liked_reels"].remove(reel_id)
                    else:
                        st.session_state["liked_reels"].add(reel_id)
                        st.toast("Liked! ❤️", icon="❤️")
                    st.rerun()

                st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

                # Comment Action (Speech Bubble)
                comm_open = (st.session_state["show_comments_for"] == reel_id)
                comm_label = f"💬\n{format_count(comment_count)}"
                if st.button(comm_label, key=f"btn_comm_{reel_id}", use_container_width=True, type="primary" if comm_open else "secondary"):
                    st.session_state["show_comments_for"] = None if comm_open else reel_id
                    st.rerun()

                st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

                # Repost / Loops Action
                reposts_cnt = current_reel.get("reposts_count", 104)
                if st.button(f"🔄\n{format_count(reposts_cnt)}", key=f"btn_repost_{reel_id}", use_container_width=True):
                    st.toast("Re-shared to your feed!", icon="🔄")

                st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

                # Share Action
                if st.button("✈️", key=f"btn_share_{reel_id}", use_container_width=True, help="Share reel"):
                    st.toast("Link copied to clipboard! 📋", icon="✈️")

                st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

                # Save Bookmark Action
                save_icon = "🔖\nSaved" if is_saved else "🔖"
                if st.button(save_icon, key=f"btn_save_{reel_id}", use_container_width=True, help="Save to collection"):
                    if is_saved:
                        st.session_state["saved_reels"].remove(reel_id)
                    else:
                        st.session_state["saved_reels"].add(reel_id)
                        st.toast("Saved to your collection! 🔖", icon="🔖")
                    st.rerun()

                st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

                # More Options Action
                st.button("•••", key=f"btn_more_{reel_id}", use_container_width=True)

                st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

                # Down Navigation Arrow (Next Reel)
                if st.button("🔽", key="btn_reel_down", use_container_width=True, type="primary", help="Next Reel"):
                    st.session_state["current_reel_idx"] = (idx + 1) % total_reels
                    st.session_state["show_comments_for"] = None
                    st.rerun()

            # Interactive Comments Drawer (if opened)
            if st.session_state["show_comments_for"] == reel_id:
                st.markdown("""
                <div style="background:#ffffff; border:1px solid #dbdbdb; border-radius:10px; padding:14px; margin-top:10px; margin-bottom:12px;">
                    <div style="font-size:13px; font-weight:700; color:#262626; border-bottom:1px solid #efefef; padding-bottom:6px; margin-bottom:10px;">
                        💬 Comments
                    </div>
                """, unsafe_allow_html=True)

                for c in comments_list:
                    st.markdown(f"""
                    <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:8px; font-size:12px;">
                        <div>
                            <b style="color:#262626;">@{c['user']}</b> &nbsp;
                            <span style="color:#475569;">{c['text']}</span><br>
                            <span style="color:#94a3b8; font-size:10px;">{c.get('time', 'Just now')}</span>
                        </div>
                        <div style="color:#94a3b8; font-size:11px;">❤️ {c.get('likes', 0)}</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)

                new_comm = st.text_input("Add a comment...", key=f"inp_comm_{reel_id}", placeholder="Comment as @" + username)
                if st.button("Post", key=f"post_btn_{reel_id}"):
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


    # -------------------------------------------------------------------------
    # COLUMN 3: RIGHT SIDEBAR (PROFILE, SUGGESTIONS & FOOTER FROM IMAGE 1)
    # -------------------------------------------------------------------------
    with col_side:
        # User Profile Header Row (Matching Image 1: soorajjosegeorge / Sooraj Jose George + Switch)
        st.markdown(f"""
        <div style="display:flex; align-items:center; justify-content:space-between; padding:10px 0 16px 0; margin-bottom:12px;">
            <div style="display:flex; align-items:center; gap:12px;">
                <img src="{b64_sooraj}" style="width:44px; height:44px; border-radius:50%; object-fit:cover; border:1px solid #dbdbdb;">
                <div>
                    <div style="font-size:13px; font-weight:700; color:#262626; line-height:1.2;">
                        {display_user}
                        <span style="color:#0095f6; font-size:11px;">✓</span>
                    </div>
                    <div style="font-size:12px; color:#737373;">Sooraj Jose George</div>
                </div>
            </div>
            <div style="font-size:12px; font-weight:700; color:#0095f6; cursor:pointer;" title="Switch Account">
                Switch
            </div>
        </div>
        """, unsafe_allow_html=True)

        # "Suggested for you" Section (Matching Image 1: Ganesh Rajesh, Modtech Solar, Shreya Ann Jacob, Molystuitions, K)
        st.markdown("""
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
            <span style="font-size:13px; font-weight:700; color:#737373;">Suggested for you</span>
            <span style="font-size:12px; font-weight:700; color:#262626; cursor:pointer;">See All</span>
        </div>
        """, unsafe_allow_html=True)

        # Suggestion 1: ganesh_rajesh
        st.markdown(f"""
        <div style="display:flex; align-items:center; justify-content:space-between; padding:6px 0;">
            <div style="display:flex; align-items:center; gap:10px;">
                <img src="{b64_ganesh}" style="width:32px; height:32px; border-radius:50%; object-fit:cover; border:1px solid #dbdbdb;">
                <div>
                    <div style="font-size:12px; font-weight:700; color:#262626;">ganesh_rajesh</div>
                    <div style="font-size:11px; color:#737373;">Suggested for you</div>
                </div>
            </div>
            <span style="font-size:12px; font-weight:700; color:#0095f6; cursor:pointer;">Follow</span>
        </div>
        """, unsafe_allow_html=True)

        # Suggestion 2: modtechsolar
        st.markdown(f"""
        <div style="display:flex; align-items:center; justify-content:space-between; padding:6px 0;">
            <div style="display:flex; align-items:center; gap:10px;">
                <img src="{b64_modtech}" style="width:32px; height:32px; border-radius:50%; object-fit:cover; border:1px solid #dbdbdb;">
                <div>
                    <div style="font-size:12px; font-weight:700; color:#262626;">modtechsolar</div>
                    <div style="font-size:11px; color:#737373;">Suggested for you</div>
                </div>
            </div>
            <span style="font-size:12px; font-weight:700; color:#0095f6; cursor:pointer;">Follow</span>
        </div>
        """, unsafe_allow_html=True)

        # Suggestion 3: shreya_ann_jacob
        st.markdown(f"""
        <div style="display:flex; align-items:center; justify-content:space-between; padding:6px 0;">
            <div style="display:flex; align-items:center; gap:10px;">
                <img src="{b64_shreya}" style="width:32px; height:32px; border-radius:50%; object-fit:cover; border:1px solid #dbdbdb;">
                <div>
                    <div style="font-size:12px; font-weight:700; color:#262626;">shreya_ann_jacob</div>
                    <div style="font-size:11px; color:#737373;">Suggested for you</div>
                </div>
            </div>
            <span style="font-size:12px; font-weight:700; color:#0095f6; cursor:pointer;">Follow</span>
        </div>
        """, unsafe_allow_html=True)

        # Suggestion 4: molystuitions
        st.markdown(f"""
        <div style="display:flex; align-items:center; justify-content:space-between; padding:6px 0;">
            <div style="display:flex; align-items:center; gap:10px;">
                <img src="{b64_moly}" style="width:32px; height:32px; border-radius:50%; object-fit:cover; border:1px solid #dbdbdb;">
                <div>
                    <div style="font-size:12px; font-weight:700; color:#262626;">molystuitions</div>
                    <div style="font-size:11px; color:#737373;">Suggested for you</div>
                </div>
            </div>
            <span style="font-size:12px; font-weight:700; color:#0095f6; cursor:pointer;">Follow</span>
        </div>
        """, unsafe_allow_html=True)

        # Suggestion 5: k
        st.markdown(f"""
        <div style="display:flex; align-items:center; justify-content:space-between; padding:6px 0; margin-bottom:20px;">
            <div style="display:flex; align-items:center; gap:10px;">
                <img src="{b64_k}" style="width:32px; height:32px; border-radius:50%; object-fit:cover; border:1px solid #dbdbdb;">
                <div>
                    <div style="font-size:12px; font-weight:700; color:#262626;">k</div>
                    <div style="font-size:11px; color:#737373;">Follows you</div>
                </div>
            </div>
            <span style="font-size:12px; font-weight:700; color:#0095f6; cursor:pointer;">Follow</span>
        </div>
        """, unsafe_allow_html=True)

        # Instagram Desktop Web Footer Links (Matching Image 1)
        st.markdown("""
        <div style="font-size:11px; color:#c7c7c7; line-height:1.6; margin-bottom:12px;">
            <a href="#" style="color:#c7c7c7; text-decoration:none;">About</a> • 
            <a href="#" style="color:#c7c7c7; text-decoration:none;">Help</a> • 
            <a href="#" style="color:#c7c7c7; text-decoration:none;">Press</a> • 
            <a href="#" style="color:#c7c7c7; text-decoration:none;">API</a> • 
            <a href="#" style="color:#c7c7c7; text-decoration:none;">Jobs</a> • 
            <a href="#" style="color:#c7c7c7; text-decoration:none;">Privacy</a> • 
            <a href="#" style="color:#c7c7c7; text-decoration:none;">Terms</a> • 
            <a href="#" style="color:#c7c7c7; text-decoration:none;">Locations</a> • 
            <a href="#" style="color:#c7c7c7; text-decoration:none;">Language</a> • 
            <a href="#" style="color:#c7c7c7; text-decoration:none;">Meta Verified</a>
        </div>
        <div style="font-size:11px; color:#c7c7c7; text-transform:uppercase; margin-bottom:20px;">
            © 2026 INSTAGRAM FROM META
        </div>
        """, unsafe_allow_html=True)

        # Bottom-Right Floating Messages Pill (Matching Image 1)
        if b64_msg_pill:
            st.markdown(f"""
            <div style="position:fixed; bottom:16px; right:20px; z-index:9999; cursor:pointer;">
                <img src="{b64_msg_pill}" style="max-height:48px; border-radius:24px; box-shadow:0 4px 16px rgba(0,0,0,0.18);">
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="position:fixed; bottom:16px; right:20px; z-index:9999; background:#ffffff; border:1px solid #dbdbdb; border-radius:24px; padding:8px 16px; box-shadow:0 4px 16px rgba(0,0,0,0.15); display:flex; align-items:center; gap:8px; cursor:pointer;">
                <span style="font-size:16px;">💬</span>
                <span style="font-size:13px; font-weight:700; color:#262626;">Messages</span>
                <span style="background:#ff3040; color:#fff; font-size:10px; font-weight:800; border-radius:10px; padding:1px 6px;">1</span>
            </div>
            """, unsafe_allow_html=True)
