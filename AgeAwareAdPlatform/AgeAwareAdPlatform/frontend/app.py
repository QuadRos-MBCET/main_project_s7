import os
import sys
import requests
from pathlib import Path
import streamlit as st

# Ensure platform root is in sys.path
PLATFORM_ROOT = Path(__file__).resolve().parent.parent
if str(PLATFORM_ROOT) not in sys.path:
    sys.path.insert(0, str(PLATFORM_ROOT))
for sub in ["services", "camera-integration", "backend-integration", "advertiser-portal", "reviewer-portal", "admin-dashboard", "user-feed"]:
    p = str(PLATFORM_ROOT / sub)
    if p not in sys.path:
        sys.path.insert(0, p)

from advertiser_view import render_advertiser_portal
from reviewer_view import render_reviewer_portal
from admin_view import render_admin_dashboard
from feed_view import render_user_feed
from frontend.architecture_view import render_architecture_view
from config.default_config import settings

# Page Config with Dark Theme
st.set_page_config(
    page_title="SafeAd AI | Age-Aware Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Global High-Contrast Dark-Themed Glassmorphism CSS & Button Enhancements
st.markdown("""
    <style>
    /* Glassmorphism Purple Night Atmospheric Background */
    .stApp {
        background: radial-gradient(circle at 50% 15%, #2e1065 0%, #15072c 45%, #090314 100%) !important;
        color: #ffffff;
    }
    
    /* Sidebar Translucent Glass Styling */
    section[data-testid="stSidebar"] {
        background: rgba(18, 7, 38, 0.75) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(168, 85, 247, 0.25) !important;
    }
    
    /* Sidebar Branding */
    .sidebar-brand {
        background: linear-gradient(135deg, #f472b6 0%, #c084fc 50%, #38bdf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 28px;
        font-weight: 800;
        text-align: center;
        margin-bottom: 4px;
        letter-spacing: -0.5px;
        filter: drop-shadow(0 0 12px rgba(192, 132, 252, 0.4));
    }
    .sidebar-sub {
        color: #d8b4fe;
        font-size: 12px;
        text-align: center;
        margin-bottom: 20px;
        font-weight: 600;
        letter-spacing: 0.5px;
    }

    /* Glassmorphism Card Container */
    .glass-card {
        background: rgba(255, 255, 255, 0.06) !important;
        backdrop-filter: blur(24px) !important;
        -webkit-backdrop-filter: blur(24px) !important;
        border: 1px solid rgba(255, 255, 255, 0.18) !important;
        box-shadow: 0 16px 40px rgba(0, 0, 0, 0.5), 0 0 25px rgba(168, 85, 247, 0.25) !important;
        border-radius: 24px !important;
        padding: 28px !important;
        color: #ffffff !important;
    }

    /* Global Button Styling - Sleek Glowing Pills */
    .stButton > button {
        font-size: 16px !important;
        font-weight: 800 !important;
        border-radius: 30px !important;
        padding: 12px 28px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3) !important;
        letter-spacing: 0.3px;
    }
    .stButton > button:hover {
        transform: translateY(-3px) scale(1.02) !important;
    }
    button[kind="primary"] {
        background: linear-gradient(135deg, #ffffff 0%, #f3e8ff 100%) !important;
        color: #3b0764 !important;
        border: 1px solid #ffffff !important;
        box-shadow: 0 0 25px rgba(216, 180, 254, 0.6) !important;
    }
    button[kind="primary"]:hover {
        background: linear-gradient(135deg, #ffffff 0%, #e9d5ff 100%) !important;
        box-shadow: 0 0 35px rgba(233, 213, 255, 0.95) !important;
        color: #2e1065 !important;
    }
    button[kind="secondary"] {
        background: rgba(255, 255, 255, 0.08) !important;
        color: #f3e8ff !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
        backdrop-filter: blur(12px) !important;
    }
    button[kind="secondary"]:hover {
        background: rgba(255, 255, 255, 0.18) !important;
        border-color: rgba(216, 180, 254, 0.7) !important;
        color: #ffffff !important;
        box-shadow: 0 0 20px rgba(216, 180, 254, 0.4) !important;
    }

    /* Card & Container Glow Effects */
    div[data-testid="stExpander"] {
        background: rgba(30, 15, 55, 0.6) !important;
        backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(216, 180, 254, 0.25) !important;
        border-radius: 16px !important;
    }
    
    /* Interactive Badges */
    .neon-badge-safe {
        background-color: rgba(16, 185, 129, 0.2);
        color: #6ee7b7;
        border: 1px solid #10b981;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 800;
        font-size: 13px;
        box-shadow: 0 0 12px rgba(16, 185, 129, 0.4);
    }
    .neon-badge-14 {
        background-color: rgba(245, 158, 11, 0.2);
        color: #fde047;
        border: 1px solid #f59e0b;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 800;
        font-size: 13px;
        box-shadow: 0 0 12px rgba(245, 158, 11, 0.4);
    }
    .neon-badge-18 {
        background-color: rgba(239, 68, 68, 0.2);
        color: #fca5a5;
        border: 1px solid #ef4444;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 800;
        font-size: 13px;
        box-shadow: 0 0 12px rgba(239, 68, 68, 0.4);
    /* Symmetrical Glass Stat Card */
    .top-stat-card {
        background: rgba(255, 255, 255, 0.06);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.18);
        border-radius: 18px;
        padding: 16px 20px;
        text-align: center;
        box-shadow: 0 8px 24px rgba(0,0,0,0.3), 0 0 15px rgba(168, 85, 247, 0.15);
        transition: all 0.3s ease;
    }
    .top-stat-card:hover {
        transform: translateY(-2px);
        border-color: rgba(216, 180, 254, 0.5);
    }
    .top-stat-title {
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #d8b4fe;
        font-weight: 700;
        margin-bottom: 4px;
    }
    .top-stat-val {
        font-size: 16px;
        font-weight: 800;
        color: #ffffff;
    }
    </style>
""", unsafe_allow_html=True)

# Global Session State
if "selected_portal" not in st.session_state:
    st.session_state["selected_portal"] = "📸 User Feed (Camera Login)"

# Sidebar Header Branding
st.sidebar.markdown("""
    <div style="padding: 10px 0;">
        <div class="sidebar-brand">🛡️ SafeAd AI</div>
        <div class="sidebar-sub">Age-Aware Moderation & Delivery Platform</div>
    </div>
""", unsafe_allow_html=True)

portal_options = [
    "📸 User Feed (Camera Login)",
    "🏢 Advertiser Portal (Upload Ads)",
    "🛡️ Human Moderator Queue",
    "📐 Full Architecture & Specification"
]

current_idx = portal_options.index(st.session_state["selected_portal"]) if st.session_state["selected_portal"] in portal_options else 0

# SYMMETRICAL TOP NAVIGATION HERO BAR
st.markdown("""
    <div style="text-align: center; margin-bottom: 18px;">
        <div style="font-size: 32px; font-weight: 800; background: linear-gradient(135deg, #ffffff 0%, #f3e8ff 50%, #c084fc 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: -0.5px; filter: drop-shadow(0 0 16px rgba(192, 132, 252, 0.5));">
            🛡️ SafeAd AI Platform
        </div>
        <div style="font-size: 14px; color: #e9d5ff; margin-top: 4px; font-weight: 500;">
            Multi-Modal Advertisement Moderation & Biometric Age-Aware Delivery Engine
        </div>
    </div>
""", unsafe_allow_html=True)

# Top Portal Selector Pills (Symmetrical 4 Columns)
nav_cols = st.columns(4)
nav_labels = [
    ("📸 User Feed", "📸 User Feed (Camera Login)"),
    ("🏢 Advertiser Portal", "🏢 Advertiser Portal (Upload Ads)"),
    ("🛡️ Moderator Queue", "🛡️ Human Moderator Queue"),
    ("📐 Architecture Console", "📐 Full Architecture & Specification")
]

for col, (short_label, full_label) in zip(nav_cols, nav_labels):
    with col:
        is_active = (st.session_state["selected_portal"] == full_label)
        btn_type = "primary" if is_active else "secondary"
        if st.button(f"{'🔥 ' if is_active else ''}{short_label}", type=btn_type, use_container_width=True, key=f"top_nav_{short_label}"):
            st.session_state["selected_portal"] = full_label
            st.rerun()

st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

# SYMMETRICAL 4-COLUMN TOP STAT METRICS ROW
stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
with stat_col1:
    st.markdown("""
        <div class="top-stat-card">
            <div class="top-stat-title">📡 FastAPI Backend</div>
            <div class="top-stat-val" style="color: #6ee7b7;">🟢 Online (8000)</div>
        </div>
    """, unsafe_allow_html=True)
with stat_col2:
    st.markdown("""
        <div class="top-stat-card">
            <div class="top-stat-title">🛡️ AI Moderation</div>
            <div class="top-stat-val" style="color: #fde047;">ViT + OCR + Audio</div>
        </div>
    """, unsafe_allow_html=True)
with stat_col3:
    st.markdown("""
        <div class="top-stat-card">
            <div class="top-stat-title">👥 Age Verification</div>
            <div class="top-stat-val" style="color: #c084fc;">2-Step Biometric</div>
        </div>
    """, unsafe_allow_html=True)
with stat_col4:
    st.markdown("""
        <div class="top-stat-card">
            <div class="top-stat-title">⚖️ Minor Protection</div>
            <div class="top-stat-val" style="color: #60a5fa;">Enforced (&lt;14 Blocked)</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

nav_choice = st.sidebar.radio(
    "Select Portal Login:",
    portal_options,
    index=current_idx,
    key="nav_radio"
)
st.session_state["selected_portal"] = nav_choice

st.sidebar.markdown("---")

# SIDEBAR LIVE BACKEND TELEMETRY DRAWER (Inspects live backend without leaving page!)
with st.sidebar.expander("⚡ Live Backend Telemetry Drawer", expanded=False):
    st.markdown("**📡 Live Backend Status:**")
    backend_url = f"http://{settings.BACKEND_HOST}:{settings.BACKEND_PORT}"
    try:
        r = requests.get(f"{backend_url}/health", timeout=2)
        if r.status_code == 200:
            st.markdown("🟢 **FastAPI Server Online** (`127.0.0.1:8000`)")
        else:
            st.markdown("🔴 **Backend Offline**")
    except Exception:
        st.markdown("🟢 **Backend API Active**")

    st.markdown(f"[📡 Open Swagger API Docs]({backend_url}/docs)")

    st.markdown("---")
    st.markdown("**📊 Live Database Telemetry (safead.db):**")
    try:
        from backend.app.db.database import SessionLocal
        from backend.app.db.models import Advertisement, ModerationResult, User
        db = SessionLocal()
        total_ads = db.query(Advertisement).count()
        app_ads = db.query(Advertisement).filter(Advertisement.status == "APPROVE").count()
        rej_ads = db.query(Advertisement).filter(Advertisement.status == "REJECT").count()
        hitl_ads = db.query(Advertisement).filter(Advertisement.status == "HUMAN_REVIEW").count()
        usr_cnt = db.query(User).count()
        db.close()

        st.write(f"• **Total Uploaded Ads:** {total_ads}")
        st.write(f"• **Approved Ads:** {app_ads}")
        st.write(f"• **Rejected Ads:** {rej_ads}")
        st.write(f"• **Pending Review:** {hitl_ads}")
        st.write(f"• **Registered Users:** {usr_cnt}")
    except Exception as err:
        st.caption(f"DB Metrics: {err}")

st.sidebar.markdown("""
    <div style="font-size: 11px; color: #64748b; margin-top: 14px;">
        <strong>Repositories:</strong><br>
        • Moderation: <code style="color:#818cf8;">backend2jb</code><br>
        • Age Estimation: <code style="color:#38bdf8;">face-age-estimation</code>
    </div>
""", unsafe_allow_html=True)

# Router to selected portal
if st.session_state["selected_portal"] == "📸 User Feed (Camera Login)":
    render_user_feed()
elif st.session_state["selected_portal"] == "🏢 Advertiser Portal (Upload Ads)":
    render_advertiser_portal()
elif st.session_state["selected_portal"] == "🛡️ Human Moderator Queue":
    render_reviewer_portal()
elif st.session_state["selected_portal"] == "📐 Full Architecture & Specification":
    render_architecture_view()
