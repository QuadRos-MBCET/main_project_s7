import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

try:
    import torch
    if hasattr(torch.backends, "mkldnn"):
        torch.backends.mkldnn.enabled = False
    torch.set_num_threads(1)
except Exception:
    pass

import warnings
warnings.filterwarnings("ignore")

import streamlit as st
import sys
from pathlib import Path

# Ensure project root and subpackages are in sys.path regardless of execution CWD
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

FRONTEND_DIR = os.path.abspath(os.path.dirname(__file__))
if FRONTEND_DIR not in sys.path:
    sys.path.insert(0, FRONTEND_DIR)

try:
    from frontend.styles.safead_theme import inject_safead_styles, render_safead_brand, render_svg_icon
    from frontend.auth.auth_manager import login_page
    from frontend.views.owner_workspace import owner_dashboard
    from frontend.views.user_workspace import user_dashboard
    from frontend.views.admin_workspace import admin_dashboard
except ImportError:
    from styles.safead_theme import inject_safead_styles, render_safead_brand, render_svg_icon
    from auth.auth_manager import login_page
    from views.owner_workspace import owner_dashboard
    from views.user_workspace import user_dashboard
    from views.admin_workspace import admin_dashboard

st.set_page_config(
    page_title="SafeAd AI • Multimodal Decision Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inject Quantexa-Inspired Enterprise Design System
inject_safead_styles()

# -----------------------------------------------------------------------------
# 1. SESSION STATE INITIALIZATION
# -----------------------------------------------------------------------------
if "role" not in st.session_state:
    st.session_state["role"] = None

ROLE_MAP = {
    "User Platform": "USER",
    "Advertiser Studio": "ADVERTISEMENT_OWNER",
    "Compliance Admin": "ADMIN"
}
REV_ROLE_MAP = {v: k for k, v in ROLE_MAP.items()}

def on_role_selector_change():
    """Single-rerun callback for the persistent top bar role switcher."""
    selected_label = st.session_state.get("global_role_selector")
    if selected_label in ROLE_MAP:
        st.session_state["role"] = ROLE_MAP[selected_label]

# Sync selector key with current role state
current_role_label = REV_ROLE_MAP.get(st.session_state["role"], None)

# -----------------------------------------------------------------------------
# 2. PERSISTENT ENTERPRISE TOP BAR WITH ROLE SWITCHER
# -----------------------------------------------------------------------------
col_brand, col_nav, col_profile = st.columns([1.6, 2.4, 1.2], vertical_alignment="center")

with col_brand:
    st.markdown("""
    <div style="display:flex; align-items:center; gap:10px; padding:4px 0;">
        <span style="font-family:'Manrope', sans-serif; font-size:22px; font-weight:800; letter-spacing:-0.03em; color:#FFFFFF;">
            Safe<span style="color:#2DE2C0;">Ad</span>
        </span>
        <span style="background:rgba(45, 226, 192, 0.12); border:1px solid rgba(45, 226, 192, 0.35); color:#2DE2C0; font-size:9px; font-weight:800; padding:2px 7px; border-radius:5px; letter-spacing:0.12em; text-transform:uppercase;">
            ENTERPRISE
        </span>
    </div>
    """, unsafe_allow_html=True)

with col_nav:
    # Segmented control for instant switching across all three platform roles
    role_options = ["User Platform", "Advertiser Studio", "Compliance Admin"]
    default_idx = role_options.index(current_role_label) if current_role_label in role_options else None
    
    selected_role_label = st.segmented_control(
        label="Platform Role Switcher",
        options=role_options,
        default=current_role_label,
        key="global_role_selector",
        label_visibility="collapsed",
        on_change=on_role_selector_change
    )

with col_profile:
    role = st.session_state["role"]
    if role == "USER":
        uname = st.session_state.get("logged_in_username", "guest_user") if st.session_state.get("user_auth_state") == "AUTHENTICATED" else "Visitor"
        badge_color = "#2DE2C0"
        badge_text = f"@{uname}"
    elif role == "ADVERTISEMENT_OWNER":
        badge_color = "#A855F7"
        badge_text = "@advertiser_studio"
    elif role == "ADMIN":
        badge_color = "#3B82F6"
        badge_text = "@trust_safety_officer"
    else:
        badge_color = "#8E83AA"
        badge_text = "Select Role"

    st.markdown(f"""
    <div style="display:flex; justify-content:flex-end; align-items:center; gap:8px;">
        <div style="display:inline-flex; align-items:center; gap:6px; background:rgba(28, 17, 51, 0.7); border:1px solid rgba(168, 147, 217, 0.2); padding:5px 12px; border-radius:9999px;">
            <span style="width:6px; height:6px; border-radius:50%; background:{badge_color}; box-shadow:0 0 6px {badge_color};"></span>
            <span style="font-size:12px; font-weight:600; color:#FFFFFF;">{badge_text}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. SIDEBAR CONTROLS & NAVIGATION
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style="padding:10px 0 16px 0; border-bottom:1px solid rgba(168,147,217,0.18); margin-bottom:16px;">
        <div style="font-family:'Manrope', sans-serif; font-size:22px; font-weight:800; color:#FFFFFF;">
            Safe<span style="color:#2DE2C0;">Ad</span> AI
        </div>
        <div style="font-size:10px; font-weight:700; color:#A493C2; letter-spacing:0.12em; text-transform:uppercase; margin-top:2px;">
            Decision Intelligence Suite
        </div>
    </div>
    """, unsafe_allow_html=True)

    if role:
        role_label = role.replace('_', ' ').title()
        st.markdown(f"""
        <div style="background:rgba(28,17,51,0.65); border:1px solid rgba(168,147,217,0.18); border-radius:12px; padding:12px 14px; margin-bottom:18px;">
            <div style="font-size:11px; text-transform:uppercase; letter-spacing:0.1em; color:#A493C2; font-weight:700;">Active Workspace</div>
            <div style="font-size:14px; font-weight:700; color:#FFFFFF; margin-top:3px;">{role_label}</div>
        </div>
        """, unsafe_allow_html=True)

        if role == "USER":
            st.caption("User Navigation")
            if st.session_state.get("user_auth_state") == "AUTHENTICATED":
                subtab = st.session_state.get("user_subtab", "feed")
                if st.button("📰 Curated Social Feed", key="sb_home", use_container_width=True, type="primary" if subtab == "feed" else "secondary"):
                    st.session_state["user_subtab"] = "feed"
                    st.rerun()
                if st.button("🎥 Short Video Reels", key="sb_reels", use_container_width=True, type="primary" if subtab == "reels" else "secondary"):
                    st.session_state["user_subtab"] = "reels"
                    st.rerun()
            else:
                auth_state = st.session_state.get("user_auth_state", "LOGIN")
                if st.button("🔑 Log In", key="sb_login_nav", use_container_width=True, type="primary" if auth_state == "LOGIN" else "secondary"):
                    st.session_state["user_auth_state"] = "LOGIN"
                    st.rerun()
                if st.button("📝 Register / KYC Onboarding", key="sb_signup_nav", use_container_width=True, type="primary" if auth_state == "SIGNUP" else "secondary"):
                    st.session_state["user_auth_state"] = "SIGNUP"
                    st.rerun()

        st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
        if st.button("🚪 Reset Role / Sign Out", key="sb_logout", use_container_width=True):
            if "vision_engine" in st.session_state:
                try:
                    st.session_state["vision_engine"].stop()
                except Exception:
                    pass
                del st.session_state["vision_engine"]
            st.session_state["user_auth_state"] = "LOGIN"
            st.session_state["logged_in_username"] = None
            st.session_state["role"] = None
            st.session_state["global_role_selector"] = None
            st.rerun()

# -----------------------------------------------------------------------------
# 4. VIEW ROUTING
# -----------------------------------------------------------------------------
if st.session_state["role"] is None:
    login_page()
elif st.session_state["role"] == "ADVERTISEMENT_OWNER":
    owner_dashboard()
elif st.session_state["role"] == "USER":
    user_dashboard()
elif st.session_state["role"] == "ADMIN":
    admin_dashboard()
