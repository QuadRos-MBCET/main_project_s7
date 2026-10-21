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
    from frontend.styles.instagram_theme import inject_instagram_styles, render_instagram_logo
    from frontend.auth.auth_manager import login_page
    from frontend.views.owner_workspace import owner_dashboard
    from frontend.views.user_workspace import user_dashboard
    from frontend.views.admin_workspace import admin_dashboard
except ImportError:
    from styles.instagram_theme import inject_instagram_styles, render_instagram_logo
    from auth.auth_manager import login_page
    from views.owner_workspace import owner_dashboard
    from views.user_workspace import user_dashboard
    from views.admin_workspace import admin_dashboard

st.set_page_config(
    page_title="Instagram • SafeAd AI",
    page_icon="📸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inject Instagram Dark & Phone-Responsive Design System
inject_instagram_styles()

if "role" not in st.session_state:
    st.session_state["role"] = None

if st.session_state["role"] is None:
    login_page()
else:
    role = st.session_state["role"]
    
    with st.sidebar:
        st.markdown("""
        <div style="padding:10px 0 16px 0; border-bottom:1px solid #262626; margin-bottom:14px;">
            <div style="font-family:'Grand Hotel', cursive, -apple-system, sans-serif; font-size:32px; background:linear-gradient(45deg,#f09433,#e6683c,#dc2743,#cc2366,#bc1888); -webkit-background-clip:text; -webkit-text-fill-color:transparent; line-height:1;">
                Instagram
            </div>
            <div style="font-size:11px; font-weight:700; color:#0095f6; letter-spacing:0.8px; margin-top:2px;">
                SAFEAD AI PLATFORM
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Display Current Active Profile
        role_label = role.replace('_', ' ').title()
        role_icon = "📱" if role == "USER" else ("🏢" if role == "ADVERTISEMENT_OWNER" else "🛡️")
        if role == "USER":
            if st.session_state.get("user_auth_state") == "AUTHENTICATED":
                user_name = st.session_state.get("logged_in_username", "sourav")
            else:
                user_name = "guest_user"
        else:
            user_name = role.lower()
        
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:10px; background:#181818; border:1px solid #262626; border-radius:10px; padding:10px 12px; margin-bottom:16px;">
            <div style="width:36px; height:36px; border-radius:50%; background:linear-gradient(45deg,#f09433,#dc2743,#bc1888); padding:1.5px; display:flex; align-items:center; justify-content:center;">
                <div style="width:100%; height:100%; border-radius:50%; background:#121212; display:flex; align-items:center; justify-content:center; font-size:16px;">
                    {role_icon}
                </div>
            </div>
            <div>
                <div style="font-size:13px; font-weight:700; color:#ffffff;">@{user_name}</div>
                <div style="font-size:11px; color:#8e8e8e;">{role_label}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.caption("Navigation")
        if role == "USER":
            if st.session_state.get("user_auth_state") == "AUTHENTICATED":
                subtab = st.session_state.get("user_subtab", "feed")
                if st.button("🏠 Instagram Home", key="sb_home", use_container_width=True, type="primary" if subtab == "feed" else "secondary"):
                    st.session_state["user_subtab"] = "feed"
                    st.rerun()
                if st.button("🎥 Explore Reels Feed", key="sb_reels", use_container_width=True, type="primary" if subtab == "reels" else "secondary"):
                    st.session_state["user_subtab"] = "reels"
                    st.rerun()
            else:
                auth_state = st.session_state.get("user_auth_state", "LOGIN")
                if st.button("🔑 Log In", key="sb_login_nav", use_container_width=True, type="primary" if auth_state == "LOGIN" else "secondary"):
                    st.session_state["user_auth_state"] = "LOGIN"
                    st.rerun()
                if st.button("📝 Register / Sign Up", key="sb_signup_nav", use_container_width=True, type="primary" if auth_state == "SIGNUP" else "secondary"):
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
            
    # Route to dashboards
    if role == "ADVERTISEMENT_OWNER":
        owner_dashboard()
    elif role == "USER":
        user_dashboard()
    elif role == "ADMIN":
        admin_dashboard()
