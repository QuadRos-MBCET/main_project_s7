import streamlit as st
import os
import sys

# Ensure frontend is in path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from frontend.auth.auth_manager import login_page
from frontend.views.owner_workspace import owner_dashboard
from frontend.views.user_workspace import user_dashboard
from frontend.views.admin_workspace import admin_dashboard

st.set_page_config(
    page_title="SafeAd AI - Unified Platform",
    page_icon="🛡️",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
.main-title { font-size: 36px; color: #1e3a8a; font-weight: 700; text-align: center; }
.sub-title { font-size: 16px; color: #64748b; text-align: center; margin-bottom: 30px; }
.card { background: rgba(255, 255, 255, 0.7); border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 16px; border: 1px solid rgba(255,255,255,0.3); backdrop-filter: blur(10px); }
</style>
""", unsafe_allow_html=True)

if "role" not in st.session_state:
    st.session_state["role"] = None

if st.session_state["role"] is None:
    st.markdown("<div class='main-title'>SAFEAD AI</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>Multimodal Advertisement Safety & Age-Aware Content Platform</div>", unsafe_allow_html=True)
    login_page()
else:
    role = st.session_state["role"]
    st.sidebar.title(f"{role.replace('_', ' ').title()} Portal")
    if st.sidebar.button("Logout"):
        st.session_state["role"] = None
        st.rerun()
        
    if role == "ADVERTISEMENT_OWNER":
        owner_dashboard()
    elif role == "USER":
        user_dashboard()
    elif role == "ADMIN":
        admin_dashboard()
