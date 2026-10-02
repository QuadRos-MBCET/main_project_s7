import streamlit as st

def login_page():
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class='card' style='text-align:center;'>
            <h1 style='font-size:48px; margin:0;'>🏢</h1>
            <h3 style='color:#1e3a8a;'>Advertisement Owner</h3>
            <p style='color:#64748b; font-size:14px;'>Submit & analyze ads using SafeAd AI</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Login as Owner", key="btn_owner", use_container_width=True):
            st.session_state["role"] = "ADVERTISEMENT_OWNER"
            st.rerun()
            
    with col2:
        st.markdown("""
        <div class='card' style='text-align:center;'>
            <h1 style='font-size:48px; margin:0;'>👤</h1>
            <h3 style='color:#1e3a8a;'>User</h3>
            <p style='color:#64748b; font-size:14px;'>Verify identity & view age-aware feed</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Login as User", key="btn_user", use_container_width=True):
            st.session_state["role"] = "USER"
            st.rerun()
            
    with col3:
        st.markdown("""
        <div class='card' style='text-align:center;'>
            <h1 style='font-size:48px; margin:0;'>🛡️</h1>
            <h3 style='color:#1e3a8a;'>Admin</h3>
            <p style='color:#64748b; font-size:14px;'>Human review queue & safety audits</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Login as Admin", key="btn_admin", use_container_width=True):
            st.session_state["role"] = "ADMIN"
            st.rerun()
