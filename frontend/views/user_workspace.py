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
from frontend.styles.safead_theme import render_safead_brand, render_stories_bar, render_svg_icon, render_html
import sqlite3


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

# =============================================================================
# CURATED FEED POSTS (AUTHENTIC USER PICTURES)
# =============================================================================
CURATED_POSTS = [
    {
        "id": "post_1",
        "creator": "comic_vault",
        "creator_avatar": "📚",
        "is_verified": True,
        "location": "Akihabara, Tokyo",
        "image_path": os.path.join(BASE_DIR, "frontend/assets/posts/download1.jpg"),
        "likes": 42100,
        "caption": "Classic golden era cover artwork. The ink craftsmanship here is legendary ✨ #comics #art #vintage #collection",
        "time": "2 hours ago"
    },
    {
        "id": "post_2",
        "creator": "wildlife_chronicles",
        "creator_avatar": "🌲",
        "is_verified": True,
        "location": "Pacific Northwest",
        "image_path": os.path.join(BASE_DIR, "frontend/assets/posts/download2.jpg"),
        "likes": 88400,
        "caption": "Mysteries of the ancient forest floor 🍄 Nature's hidden architecture. #nature #outdoors #macro",
        "time": "4 hours ago"
    },
    {
        "id": "post_3",
        "creator": "geology_explorer",
        "creator_avatar": "🌋",
        "is_verified": True,
        "location": "Reykjavik, Iceland",
        "image_path": os.path.join(BASE_DIR, "frontend/assets/posts/download3.jpg"),
        "likes": 129000,
        "caption": "Raw earth energy erupting in the heart of the volcanic rift. Mesmerizing power! 🌋 #volcano #geology #earth",
        "time": "5 hours ago"
    },
    {
        "id": "post_4",
        "creator": "hoops_nation",
        "creator_avatar": "🏀",
        "is_verified": True,
        "location": "Rucker Park, NYC",
        "image_path": os.path.join(BASE_DIR, "frontend/assets/posts/download4.jpg"),
        "likes": 95200,
        "caption": "Nothing beats summer streetball under the city lights. Pure basketball energy 🏀🔥 #basketball #streetball #nyc",
        "time": "7 hours ago"
    },
    {
        "id": "post_5",
        "creator": "quantum_labs",
        "creator_avatar": "🔬",
        "is_verified": True,
        "location": "CERN, Geneva",
        "image_path": os.path.join(BASE_DIR, "frontend/assets/posts/download5.jpg"),
        "likes": 64300,
        "caption": "Late night in the cleanroom prepping new quantum sensor wafers. The future is being built today ⚡ #science #research #physics",
        "time": "9 hours ago"
    },
    {
        "id": "post_6",
        "creator": "artisan_spirits",
        "creator_avatar": "🍸",
        "is_verified": False,
        "location": "Milan, Italy",
        "image_path": os.path.join(BASE_DIR, "frontend/assets/posts/download6.jpg"),
        "likes": 38700,
        "caption": "Handcrafted botanical infusions & crystal glass craft. Aesthetic evening vibes 🍸✨ #mixology #cocktails #design",
        "time": "11 hours ago"
    },
    {
        "id": "post_7",
        "creator": "terra_incognita",
        "creator_avatar": "🗻",
        "is_verified": True,
        "location": "Mount Fuji, Japan",
        "image_path": os.path.join(BASE_DIR, "frontend/assets/posts/download7.jpg"),
        "likes": 172000,
        "caption": "Sunrise over the caldera rim above the sea of clouds. Moments that leave you speechless 🗻🌅 #travel #japan #fuji",
        "time": "14 hours ago"
    },
    {
        "id": "post_8",
        "creator": "gridiron_highlights",
        "creator_avatar": "🏈",
        "is_verified": True,
        "location": "Dallas, Texas",
        "image_path": os.path.join(BASE_DIR, "frontend/assets/posts/download8.jpg"),
        "likes": 143500,
        "caption": "Game day helmet prep. Lights on, crowd roaring, ready to battle under Friday night lights 🏈🔥 #football #nfl #gameday",
        "time": "18 hours ago"
    },
    {
        "id": "post_9",
        "creator": "stadium_culture",
        "creator_avatar": "🏟️",
        "is_verified": True,
        "location": "Camp Nou, Barcelona",
        "image_path": os.path.join(BASE_DIR, "frontend/assets/posts/download9.jpg"),
        "likes": 210000,
        "caption": "Iconic matchday kit colors under the floodlights. The stadium roar is electric! ⚽🔵🔴 #football #soccer #matchday",
        "time": "1 day ago"
    }
]

# =============================================================================
# REELS CATALOG: ORGANIC SHORT VIDEOS (NO DEFAULT ADS)
# =============================================================================
DEFAULT_REELS = [
    {
        "id": "reel_ronaldo",
        "type": "organic",
        "creator": "fifa_worldcup_hub",
        "creator_avatar": "⚽",
        "is_verified": True,
        "title": "CR7 WORLD CUP HISTORY",
        "caption": "Cristiano Ronaldo breaks the record and scores at his 6th World Cup tournament! 🐐⚽ #FIFAWorldCup #CR7 #legend #football",
        "audio": "World Cup Official Stadium Anthem 🎵",
        "likes": 482000,
        "comments_count": 8900,
        "shares_count": 124000,
        "video_path": os.path.join(BASE_DIR, "frontend/assets/reels/reel_ronaldo_world_cup.mp4"),
        "comments": [
            {"user": "madridista7", "text": "The greatest to ever touch a football! SIUUU 🔥", "time": "1h", "likes": 1420},
            {"user": "football_talk", "text": "6 tournaments in a row is unreal longevity 👏", "time": "2h", "likes": 560}
        ]
    },
    {
        "id": "reel_mbappe",
        "type": "organic",
        "creator": "france_football_tv",
        "creator_avatar": "🇫🇷",
        "is_verified": True,
        "title": "MBAPPE LIGHTNING STRIKE",
        "caption": "Kylian Mbappé opens the scoring with blistering speed! Pure world-class finishing ⚡⚽ #Mbappe #France #WorldCup #football",
        "audio": "French National Team Stadium Mix 🎵",
        "likes": 345000,
        "comments_count": 5210,
        "shares_count": 78000,
        "video_path": os.path.join(BASE_DIR, "frontend/assets/reels/reel_mbappe_france_goal.mp4"),
        "comments": [
            {"user": "speed_demon", "text": "Nobody in world football can catch him in a sprint!", "time": "3h", "likes": 780}
        ]
    },
    {
        "id": "reel_neymar",
        "type": "organic",
        "creator": "joga_bonito_daily",
        "creator_avatar": "🇧🇷",
        "is_verified": True,
        "title": "NEYMAR SIGNATURE MOVES",
        "caption": "Pure Brazilian flair & impossible footwork! That flick was sensational 🕺⚽ #Neymar #JogaBonito #skills #brazil",
        "audio": "Samba Rio Beats • Brazilian Rhythm 🎵",
        "likes": 412000,
        "comments_count": 7320,
        "shares_count": 95000,
        "video_path": os.path.join(BASE_DIR, "frontend/assets/reels/reel_neymar_skills.mp4"),
        "comments": [
            {"user": "samba_king", "text": "The flair and joy he plays with is art ✨", "time": "2h", "likes": 920}
        ]
    },
    {
        "id": "reel_space",
        "type": "organic",
        "creator": "cosmos_unfolded",
        "creator_avatar": "🌌",
        "is_verified": True,
        "title": "HOW BIG IS SPACE REALLY?",
        "caption": "Zooming out from Earth to the edge of the observable universe... Mind-bending scale! 🪐🔭 #space #astronomy #science #cosmos",
        "audio": "Interstellar Theme • Cosmic Ambient 🎵",
        "likes": 298000,
        "comments_count": 4890,
        "shares_count": 82000,
        "video_path": os.path.join(BASE_DIR, "frontend/assets/reels/reel_how_big_is_space.mp4"),
        "comments": [
            {"user": "stargazer", "text": "Existential dread in the best way possible 🤯", "time": "4h", "likes": 1150}
        ]
    },
    {
        "id": "reel_study_hacks",
        "type": "organic",
        "creator": "student_productivity",
        "creator_avatar": "📚",
        "is_verified": True,
        "title": "3 STUDY HACKS FOR STUDENTS",
        "caption": "Supercharge your research speed with these game-changing search operators! 💡🚀 Save for your next exam #study #tips #productivity #studentlife",
        "audio": "Chill Lo-Fi Study Session 🎵",
        "likes": 189000,
        "comments_count": 2100,
        "shares_count": 64000,
        "video_path": os.path.join(BASE_DIR, "frontend/assets/reels/reel_google_study_hacks.mp4"),
        "comments": [
            {"user": "college_grind", "text": "Tip #2 saved my essay research tonight!", "time": "5h", "likes": 340}
        ]
    },
    {
        "id": "reel_checo",
        "type": "organic",
        "creator": "f1_paddock_pulse",
        "creator_avatar": "🏎️",
        "is_verified": True,
        "title": "CHECO PEREZ BLIND RANKING",
        "caption": "Sergio 'Checo' Perez blind ranks his greatest career moments in Formula 1! 🇲🇽🏆 #F1 #Checo #Formula1 #motorsport",
        "audio": "Formula 1 V10 Soundwaves 🎵",
        "likes": 224000,
        "comments_count": 3150,
        "shares_count": 41000,
        "video_path": os.path.join(BASE_DIR, "frontend/assets/reels/reel_checo_perez_f1.mp4"),
        "comments": [
            {"user": "redbull_fan", "text": "The Baku 2021 defense was legendary!", "time": "6h", "likes": 480}
        ]
    },
    {
        "id": "reel_avengers",
        "type": "organic",
        "creator": "marvel_cinematics",
        "creator_avatar": "🛡️",
        "is_verified": True,
        "title": "AVENGERS ASSEMBLE!",
        "caption": "That one moment in cinema history that gave everybody goosebumps ⚡🎬 #Marvel #Avengers #CaptainAmerica #MCU",
        "audio": "Alan Silvestri • The Avengers Theme 🎵",
        "likes": 560000,
        "comments_count": 11200,
        "shares_count": 180000,
        "video_path": os.path.join(BASE_DIR, "frontend/assets/reels/reel_avengers_assemble.mp4"),
        "comments": [
            {"user": "cap_shield", "text": "Nothing will ever top the theater reaction to this!", "time": "1h", "likes": 2100}
        ]
    },
    {
        "id": "reel_cricket",
        "type": "organic",
        "creator": "cricket_fever_247",
        "creator_avatar": "🏏",
        "is_verified": True,
        "title": "IND VS NZ T20I THRILLER",
        "caption": "Sensational death bowling & clutch boundary hits in the 5th T20I! 🏏🇮🇳🇳🇿 #Cricket #INDvsNZ #T20I #TeamIndia",
        "audio": "Stadium Cricket Roar • Beat Drop 🎵",
        "likes": 389000,
        "comments_count": 6400,
        "shares_count": 92000,
        "video_path": os.path.join(BASE_DIR, "frontend/assets/reels/reel_india_vs_nz_cricket.mp4"),
        "comments": [
            {"user": "virat_fanclub", "text": "What a game! T20 cricket at its finest 🔥", "time": "3h", "likes": 890}
        ]
    },
    {
        "id": "reel_notes_pdf",
        "type": "organic",
        "creator": "workflow_optimizer",
        "creator_avatar": "📝",
        "is_verified": True,
        "title": "MESSY NOTES TO CLEAN PDF",
        "caption": "Turn scribbled paper notes into search-indexed digital PDFs in under 10 seconds 📲📄 #lifehack #productivity #tech #apps",
        "audio": "Minimal Tech Beats 🎵",
        "likes": 165000,
        "comments_count": 1820,
        "shares_count": 53000,
        "video_path": os.path.join(BASE_DIR, "frontend/assets/reels/reel_google_notes_pdf.mp4"),
        "comments": [
            {"user": "student_life", "text": "Need this for my calculus lectures right now!", "time": "4h", "likes": 290}
        ]
    },
    {
        "id": "reel_viral",
        "type": "organic",
        "creator": "reflex_athletes",
        "creator_avatar": "⚡",
        "is_verified": True,
        "title": "UNREAL ATHLETIC REFLEXES",
        "caption": "Human reaction speed at the absolute limit ⚡🔥 Who can react this fast? #athletics #reflex #sports #viral",
        "audio": "Bass Boosted High Energy 🎵",
        "likes": 275000,
        "comments_count": 3890,
        "shares_count": 61000,
        "video_path": os.path.join(BASE_DIR, "frontend/assets/reels/reel_viral_sports.mp4"),
        "comments": [
            {"user": "gym_junkie", "text": "The hand-eye coordination is mind-blowing!", "time": "2h", "likes": 410}
        ]
    },
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
    elif user_cat == "18 and above":
        return classification in ["SAFE_FOR_ALL", "APPROVED", "SAFE_14_PLUS", "SAFE_18_PLUS"]
    else:
        # Fail-closed default for unauthenticated, uncertain or unverified profiles
        return classification in ["SAFE_FOR_ALL", "APPROVED"]



# =============================================================================
# DATASET HUB CONTENT LOADER (Age-Gated Reels & Photos)
# =============================================================================
@st.cache_data(show_spinner=False)
def load_dataset_hub_content():
    """
    Loads approved, authentic images and reels from safead-dataset-hub manifest.
    Enforces Phase 7B Task 4 Gates:
    1. Configurable dataset path via SAFEAD_DATASET_HUB_PATH or standard paths.
    2. Only verified, authorized, and APPROVED samples included.
    3. UNSAFE_FOR_ALL samples strictly barred.
    4. Synthetic review cards (800x520) strictly barred.
    5. Missing media fails safely.
    """
    hub_candidates = [
        os.getenv("SAFEAD_DATASET_HUB_PATH", ""),
        os.getenv("DATASET_HUB_ROOT", ""),
        r"C:\Users\hello\Videos\sourav\datasets\safead-dataset-hub",
        os.path.abspath(os.path.join(BASE_DIR, "..", "safead-dataset-hub")),
        os.path.abspath(os.path.join(BASE_DIR, ".."))
    ]
    
    hub_root = None
    manifest_path = None
    for cand in hub_candidates:
        if cand and os.path.exists(cand):
            p = os.path.join(cand, "app_content", "content_manifest.json")
            if os.path.exists(p):
                hub_root = cand
                manifest_path = p
                break
                
    if not manifest_path or not hub_root:
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
        age_cat = str(item.get("age_category", "")).upper()
        mod_status = str(item.get("moderation_status", "")).upper()
        res = str(item.get("resolution", "")).lower()

        # Gate 1: Prohibited content is strictly excluded
        if age_cat in ["UNSAFE_FOR_ALL", "REJECT", "PROHIBITED"]:
            continue

        # Gate 2: Unreviewed or unapproved content is strictly excluded
        if mod_status != "APPROVED":
            continue

        # Gate 3: Synthetic review card templates (800x520) strictly barred
        if res == "800x520" or item.get("is_synthetic") is True:
            continue

        # Gate 4: Permissible categories only
        if age_cat not in ["SAFE_FOR_ALL", "SAFE_14_PLUS", "SAFE_18_PLUS"]:
            continue

        # Gate 5: Safe media path resolution
        media_rel = item.get("media_path", "")
        full_path = os.path.abspath(os.path.join(hub_root, media_rel))
        if not os.path.exists(full_path):
            continue  # Fail-safe: omit missing media
            
        entry = {
            "id": item["content_id"],
            "type": "sponsored",
            "creator": item.get("source_name", "SafeAd Archive"),
            "creator_avatar": "📺" if item["content_type"] == "reel" else "📸",
            "is_verified": True,
            "sponsored_label": f"SafeAd AI • Verified {age_cat}",
            "safety_policy": age_cat,
            "title": item.get("title", ""),
            "caption": item.get("caption", ""),
            "cta_text": "Watch Reel ↗" if item["content_type"] == "reel" else "View Creative ↗",
            "audio": "Commercial Soundtrack • SafeAd Vault 🎵",
            "likes": 12000 + (abs(hash(item["content_id"])) % 45000),
            "comments_count": 80 + (abs(hash(item["content_id"])) % 350),
            "shares_count": 1400 + (abs(hash(item["content_id"])) % 5000),
            "media_path": full_path,
            "video_path": full_path,
            "content_type": item["content_type"],
            "comments": [
                {"user": "safead_compliance", "text": f"✅ Verified safe for {age_cat} demographic.", "time": "2h", "likes": 42}
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
        st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
        
        c_l, c_center, c_r = st.columns([1, 1.8, 1])
        with c_center:
            st.markdown("""
            <div style="text-align: center; margin-bottom: 24px;">
                <div class="rf-eyebrow-pill" style="margin-bottom: 12px;">
                    <span style="display:inline-block; width:7px; height:7px; border-radius:50%; background:#6C5CE7; box-shadow:0 0 8px #6C5CE7;"></span>
                    IDENTITY & ACCESS MANAGEMENT
                </div>
                <h1 style="margin: 0; font-size: 32px; font-weight: 700; color: #FFFFFF; font-family: 'Outfit', sans-serif;">
                    Safe<span class="rf-italic-serif">Ad</span> User Portal
                </h1>
                <p style="color:#A493C2; font-size:14px; margin-top:6px;">Sign in to access your age-verified social media feed</p>
            </div>
            """, unsafe_allow_html=True)

            # Login Card containing ONLY username, password, login button, and register link
            st.markdown("""
            <div class="rf-card" style="padding:28px 30px; margin-bottom:16px;">
                <div style="font-size:18px; font-weight:700; color:#ffffff; margin-bottom:18px; text-align:center; font-family:'Outfit',sans-serif;">
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
                <div style="background:rgba(11,15,28,0.7); border:1px dashed rgba(108,92,231,0.35); border-radius:10px; padding:12px 14px; margin-top:18px; font-size:12px; color:#A493C2; text-align:center;">
                    💡 <b>Developer Test Account:</b> Username: <code style="color:#6C5CE7; font-weight:700;">sourav</code> &nbsp;|&nbsp; Password: <code style="color:#6C5CE7; font-weight:700;">sourav</code>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Registration redirection box
            st.markdown("""
            <div class="rf-card" style="padding:16px 20px; text-align:center; margin-bottom:20px;">
                <span style="color:#A493C2; font-size:13px;">Don't have an account? </span>
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

        render_safead_brand(subtitle="IDENTITY ONBOARDING & KYC")

        # 3-STEP KYC STEPPER (RiteFlow Dark SaaS Style)
        st.markdown("""
        <div style="display:flex; align-items:center; justify-content:center; gap:16px; margin: 18px 0 28px 0; flex-wrap:wrap;">
            <div style="display:flex; align-items:center; gap:8px;">
                <div style="width:28px; height:28px; border-radius:50%; background:#6C5CE7; color:#FFFFFF; font-size:12px; font-weight:800; display:flex; align-items:center; justify-content:center; box-shadow:0 0 10px rgba(108,92,231,0.5);">1</div>
                <span style="font-size:13px; font-weight:700; color:#FFFFFF;">Account Credentials</span>
            </div>
            <div style="width:36px; height:1px; background:rgba(108,92,231,0.4);"></div>
            <div style="display:flex; align-items:center; gap:8px;">
                <div style="width:28px; height:28px; border-radius:50%; background:rgba(108,92,231,0.2); border:1px solid #6C5CE7; color:#E2D9F3; font-size:12px; font-weight:800; display:flex; align-items:center; justify-content:center;">2</div>
                <span style="font-size:13px; font-weight:600; color:#E2D9F3;">Official ID Scan & OCR</span>
            </div>
            <div style="width:36px; height:1px; background:rgba(108,92,231,0.4);"></div>
            <div style="display:flex; align-items:center; gap:8px;">
                <div style="width:28px; height:28px; border-radius:50%; background:rgba(108,92,231,0.2); border:1px solid #6C5CE7; color:#E2D9F3; font-size:12px; font-weight:800; display:flex; align-items:center; justify-content:center;">3</div>
                <span style="font-size:13px; font-weight:600; color:#E2D9F3;">Live Biometrics (ArcFace)</span>
            </div>
        </div>
        
        <div class="rf-card" style="padding:22px 26px; margin-bottom:20px;">
            <div style="margin-bottom:14px;">
                <div class="rf-eyebrow-pill" style="margin-bottom:8px;">STEP 1 OF 3 • PROFILE SETUP</div>
                <div style="font-size:18px; color:#FFFFFF; font-weight:700; font-family:'Outfit',sans-serif;">Account Credentials</div>
                <p style="margin:4px 0 0 0; font-size:13px; color:#A493C2;">Create your user credentials. Complete steps 2 & 3 below to verify identity.</p>
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
                <div class="rf-stat-card" style="text-align:center; padding:14px;">
                    <div class="rf-stat-value" style="font-size:22px; color:#6C5CE7;">{verif_res.get('face_similarity', 0.0):.1%}</div>
                    <div class="rf-stat-label">Face Match Score</div>
                </div>
                """, unsafe_allow_html=True)
            with c_r2:
                anti_spoof_tag = "🛑 SPOOF" if verif_res.get('is_spoof') else "✅ REAL (LIVE)"
                color = "#EF4444" if verif_res.get('is_spoof') else "#22C55E"
                st.markdown(f"""
                <div class="rf-stat-card" style="text-align:center; padding:14px;">
                    <div class="rf-stat-value" style="font-size:18px; color:{color};">{anti_spoof_tag}</div>
                    <div class="rf-stat-label">Liveness Check</div>
                </div>
                """, unsafe_allow_html=True)
            with c_r3:
                st.markdown(f"""
                <div class="rf-stat-card" style="text-align:center; padding:14px;">
                    <div class="rf-stat-value" style="font-size:20px; color:#A855F7;">{verif_res.get('id_age', 'N/A')} yrs</div>
                    <div class="rf-stat-label">Extracted ID Age</div>
                </div>
                """, unsafe_allow_html=True)
            with c_r4:
                st.markdown(f"""
                <div class="rf-stat-card" style="text-align:center; padding:14px;">
                    <div class="rf-stat-value" style="font-size:18px; color:#F59E0B;">{verif_res.get('live_age_category', 'N/A')}</div>
                    <div class="rf-stat-label">Live ViT Age Scan</div>
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
    username = st.session_state.get("logged_in_username", "guest_minor")
    user_cat = st.session_state.get("verified_age_category", "Less than 14")
    user_norm = st.session_state.get("verified_age_norm", "UNDER_14")

    # App Header with User Greeting and Verified Badge
    render_safead_brand(subtitle="AGE-VERIFIED SOCIAL FEED")

    # User Profile Info & Navigation Sub-Bar (RiteFlow Style)
    render_html(f"""
    <div class="rf-card" style="padding:12px 18px; margin-bottom:16px; display:flex; justify-content:space-between; align-items:center;">
        <div style="display:flex; align-items:center; gap:12px;">
            <div style="width:38px; height:38px; border-radius:50%; background:linear-gradient(135deg,#6C5CE7,#8B5CF6); padding:2px; display:flex; align-items:center; justify-content:center; box-shadow:0 0 12px rgba(108,92,231,0.35);">
                <div style="width:100%; height:100%; border-radius:50%; background:#0B0F1C; display:flex; align-items:center; justify-content:center; font-size:16px;">
                    👤
                </div>
            </div>
            <div>
                <div style="font-size:15px; font-weight:700; color:#ffffff; display:flex; align-items:center; gap:6px; font-family:'Outfit',sans-serif;">
                    @{username}
                    <span style="color:#22C55E; font-size:14px; font-weight:800;" title="Verified Account">✓</span>
                    <span class="rf-badge-safe" style="font-size:10px; padding:2px 8px; margin-left:6px;">
                        {user_norm} ({user_cat})
                    </span>
                </div>
                <div style="font-size:11px; color:#A493C2;">Verified Identity • Age-Gated Social Feed Active</div>
            </div>
        </div>
    </div>
    """)

    # Top Tabs: Instagram Home Page vs Reels Tab
    c_tab1, c_tab2, c_tab3 = st.columns([1, 1, 0.8])
    with c_tab1:
        if st.button("📰 Curated Content Feed", key="tab_home_btn", use_container_width=True,
                     type="primary" if st.session_state["user_subtab"] == "feed" else "secondary"):
            st.session_state["user_subtab"] = "feed"
            st.rerun()
    with c_tab2:
        if st.button("🎥 Short-Form Reels", key="tab_reels_btn", use_container_width=True,
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
            <div style="background:rgba(17,23,38,0.75); border:1px solid rgba(108,92,231,0.22); border-radius:14px; margin-bottom:20px;">
                <div style="padding:12px 16px; display:flex; justify-content:space-between; align-items:center;">
                    <div style="display:flex; align-items:center; gap:10px;">
                        <div style="width:32px; height:32px; border-radius:50%; background:linear-gradient(135deg,#6C5CE7,#8B5CF6); padding:1.5px; display:flex; align-items:center; justify-content:center;">
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
            <div style="background:rgba(17,23,38,0.75); border:1px solid rgba(108,92,231,0.22); border-top:none; border-radius:0 0 14px 14px; padding:12px 16px; margin-top:-20px; margin-bottom:24px;">
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

            # Render Authentic Curated User Posts (from uploaded photos)
            for p_idx, post in enumerate(CURATED_POSTS):
                render_html(f"""
                <div style="background:rgba(17,23,38,0.75); border:1px solid rgba(108,92,231,0.22); border-radius:14px 14px 0 0; margin-bottom:0;">
                    <div style="padding:12px 16px; display:flex; justify-content:space-between; align-items:center;">
                        <div style="display:flex; align-items:center; gap:10px;">
                            <div style="width:34px; height:34px; border-radius:50%; background:linear-gradient(135deg,#6C5CE7,#8B5CF6); padding:2px; display:flex; align-items:center; justify-content:center;">
                                <div style="width:100%; height:100%; border-radius:50%; background:#181818; display:flex; align-items:center; justify-content:center; font-size:15px;">
                                    {post.get('creator_avatar', '📸')}
                                </div>
                            </div>
                            <div>
                                <div style="font-size:13px; font-weight:700; color:#ffffff;">@{post['creator']} <span style="color:#0095f6;">✓</span></div>
                                <div style="font-size:11px; color:#A493C2;">{post.get('location', 'Global')}</div>
                            </div>
                        </div>
                        <div style="color:#8e8e8e; font-size:14px; letter-spacing:2px;">•••</div>
                    </div>
                </div>
                """)
                if os.path.exists(post["image_path"]):
                    st.image(post["image_path"], use_container_width=True)
                render_html(f"""
                <div style="background:rgba(17,23,38,0.75); border:1px solid rgba(108,92,231,0.22); border-top:none; border-radius:0 0 14px 14px; padding:12px 16px; margin-top:-6px; margin-bottom:24px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <div style="display:flex; gap:14px; font-size:20px;">
                            <span>❤️</span> <span>💬</span> <span>✈️</span>
                        </div>
                        <span style="font-size:11px; color:#A493C2;">{post.get('time', 'Recently')}</span>
                    </div>
                    <div style="font-size:13px; font-weight:700; color:#ffffff; margin-bottom:4px;">{format_count(post.get('likes', 14000))} likes</div>
                    <div style="font-size:13px; color:#e2e8f0; margin-bottom:4px;">
                        <b>@{post['creator']}</b> {post.get('caption', '')}
                    </div>
                    <div style="font-size:11px; color:#8e8e8e;">SafeAd AI Safety Verified • Age-Appropriate</div>
                </div>
                """)

            # Post 2: Age-Appropriate Brand Owner Sponsored Ad
            # If Brand Owner has ads in global_ads, display the top approved ad
            owner_ads = [r for r in curated_reels if r["type"] == "sponsored"]
            if owner_ads:
                top_ad = owner_ads[0]
                pol = top_ad.get("safety_policy", "SAFE_FOR_ALL")
                render_html(f"""
                <div style="background:rgba(17,23,38,0.75); border:1px solid rgba(108,92,231,0.22); border-radius:14px; margin-bottom:20px;">
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
                """)

                ad_vid = top_ad.get("video_path")
                if ad_vid and os.path.exists(ad_vid):
                    st.video(ad_vid, autoplay=False, loop=True)

                st.markdown(f"""
                <div style="background:rgba(17,23,38,0.75); border:1px solid rgba(108,92,231,0.22); border-top:none; border-radius:0 0 14px 14px; padding:12px 16px; margin-top:-20px; margin-bottom:24px;">
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
            <div style="background:rgba(17,23,38,0.75); border:1px solid rgba(108,92,231,0.22); border-radius:14px; margin-bottom:20px;">
                <div style="padding:12px 16px; display:flex; justify-content:space-between; align-items:center;">
                    <div style="display:flex; align-items:center; gap:10px;">
                        <div style="width:32px; height:32px; border-radius:50%; background:linear-gradient(135deg,#6C5CE7,#8B5CF6); padding:1.5px; display:flex; align-items:center; justify-content:center;">
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
            <div style="background:rgba(17,23,38,0.75); border:1px solid rgba(108,92,231,0.22); border-top:none; border-radius:0 0 14px 14px; padding:12px 16px; margin-top:-20px; margin-bottom:24px;">
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
            if st.session_state["reels_filter"] == "SPONSORED":
                render_html("""
                <div class="rf-card" style="text-align:center; padding:48px 24px; margin:24px auto; max-width:480px;">
                    <div style="width:48px; height:48px; border-radius:50%; background:rgba(79,70,229,0.18); border:1px solid rgba(99,102,241,0.3); display:inline-flex; align-items:center; justify-content:center; margin-bottom:14px;">
                        🛡️
                    </div>
                    <div style="font-size:17px; font-weight:700; color:#FFFFFF; margin-bottom:8px; font-family:'Outfit',sans-serif;">No Brand Owner Ads Active</div>
                    <div style="font-size:13px; color:#94A3B8; line-height:1.5;">
                        All current placeholder ads have been removed. When advertisers upload and approve campaigns in the Advertiser Studio, verified creatives will appear here.
                    </div>
                </div>
                """)
            else:
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
            <div style="background:rgba(17,23,38,0.75); border:1px solid rgba(108,92,231,0.22); border-radius:16px 16px 0 0; padding:12px 16px; display:flex; justify-content:space-between; align-items:center;">
                <div style="display:flex; align-items:center; gap:10px;">
                    <div style="width:34px; height:34px; border-radius:50%; background:linear-gradient(135deg,#6C5CE7,#8B5CF6); padding:1.5px; display:flex; align-items:center; justify-content:center;">
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
            <div style="background:rgba(17,23,38,0.75); border:1px solid rgba(108,92,231,0.22); border-top:none; padding:14px 16px; border-radius:0 0 16px 16px;">
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
                render_html("<div style='height:12px;'></div>")
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
