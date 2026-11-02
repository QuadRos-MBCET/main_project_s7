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
    page_title="SafeAd AI • Decision Intelligence Platform",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inject RiteFlow Dark SaaS Design System
inject_safead_styles()

# -----------------------------------------------------------------------------
# 1. SESSION STATE INITIALIZATION & ROLE MAPPINGS
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
    else:
        st.session_state["role"] = None

# Synchronize segmented control state with current role BEFORE widget is instantiated
expected_role_label = REV_ROLE_MAP.get(st.session_state.get("role"), None)
if "global_role_selector" in st.session_state and st.session_state["global_role_selector"] != expected_role_label:
    st.session_state["global_role_selector"] = expected_role_label

# -----------------------------------------------------------------------------
# 2. PERSISTENT RITEFLOW TOP BAR WITH ROLE SWITCHER
# -----------------------------------------------------------------------------
col_logo, col_nav, col_action = st.columns([1.5, 2.5, 1.2], vertical_alignment="center")

with col_logo:
    st.markdown("""
    <div style="display:flex; align-items:center; gap:10px; padding:2px 0;">
        <div style="width:30px; height:30px; border-radius:9px; background:linear-gradient(135deg, #4F46E5 0%, #818CF8 100%); display:flex; align-items:center; justify-content:center; box-shadow:0 0 16px rgba(79,70,229,0.55);">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2.5" stroke-linecap="round"><path d="M2 12h4l3-9 4 18 3-9h6"/></svg>
        </div>
        <span style="font-family:'Outfit', sans-serif; font-size:20px; font-weight:800; letter-spacing:-0.03em; color:#FFFFFF;">
            Safe<span style="color:#C7D2FE;">Ad</span>
        </span>
    </div>
    """, unsafe_allow_html=True)

with col_nav:
    role_options = ["User Platform", "Advertiser Studio", "Compliance Admin"]
    selected_role_label = st.segmented_control(
        label="Role Switcher Navigation",
        options=role_options,
        default=expected_role_label,
        key="global_role_selector",
        label_visibility="collapsed",
        on_change=on_role_selector_change
    )

with col_action:
    role = st.session_state["role"]
    if role == "USER":
        uname = st.session_state.get("logged_in_username", "Guest") if st.session_state.get("user_auth_state") == "AUTHENTICATED" else "Visitor"
        btn_text = f"● @{uname}"
        help_msg = "Active in User Platform. Click to return to Portal Selection."
    elif role == "ADVERTISEMENT_OWNER":
        btn_text = "● @advertiser"
        help_msg = "Active in Advertiser Studio. Click to return to Portal Selection."
    elif role == "ADMIN":
        btn_text = "● @compliance"
        help_msg = "Active in Compliance Admin. Click to return to Portal Selection."
    else:
        btn_text = "● Select Portal"
        help_msg = "Click to open Advertiser Decision Studio."

    if st.button(btn_text, key="top_portal_pill_btn", help=help_msg, use_container_width=True):
        if role:
            st.session_state["role"] = None
        else:
            st.session_state["role"] = "ADVERTISEMENT_OWNER"
        st.rerun()

st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. SIDEBAR NAVIGATION
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style="padding:10px 0 16px 0; border-bottom:1px solid rgba(255,255,255,0.08); margin-bottom:16px;">
        <div style="font-family:'Outfit', sans-serif; font-size:22px; font-weight:800; color:#FFFFFF;">
            Safe<span style="color:#A29BFE;">Ad</span> AI
        </div>
        <div style="font-size:10px; font-weight:700; color:#A2AECB; letter-spacing:0.08em; text-transform:uppercase; margin-top:2px;">
            Decision Intelligence Suite
        </div>
    </div>
    """, unsafe_allow_html=True)

    if role:
        role_label = role.replace('_', ' ').title()
        st.markdown(f"""
        <div style="background:#151D30; border:1px solid rgba(108,92,231,0.2); border-radius:12px; padding:12px 14px; margin-bottom:18px;">
            <div style="font-size:11px; text-transform:uppercase; letter-spacing:0.08em; color:#A2AECB; font-weight:700;">Active Portal</div>
            <div style="font-size:14px; font-weight:700; color:#FFFFFF; margin-top:3px;">{role_label}</div>
        </div>
        """, unsafe_allow_html=True)

        if role == "USER":
            st.caption("Navigation")
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
                if st.button("📝 Register / KYC", key="sb_signup_nav", use_container_width=True, type="primary" if auth_state == "SIGNUP" else "secondary"):
                    st.session_state["user_auth_state"] = "SIGNUP"
                    st.rerun()

        st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
        if st.button("🚪 Switch Account / Logout", key="sb_logout", use_container_width=True):
            if "vision_engine" in st.session_state:
                try:
                    st.session_state["vision_engine"].stop()
                except Exception:
                    pass
                del st.session_state["vision_engine"]
            st.session_state["user_auth_state"] = "LOGIN"
            st.session_state["logged_in_username"] = None
            st.session_state["role"] = None
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
