import streamlit as st

def login_page():
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    
    # Instagram-styled login container
    c_left, c_center, c_right = st.columns([1, 2, 1])
    
    with c_center:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 24px;">
            <div style="font-family:'Grand Hotel', cursive, -apple-system, sans-serif; font-size:46px; background:linear-gradient(45deg,#f09433,#e6683c,#dc2743,#cc2366,#bc1888); -webkit-background-clip:text; -webkit-text-fill-color:transparent; line-height:1.2;">
                Instagram
            </div>
            <div style="display:inline-block; background:rgba(0,149,246,0.15); border:1px solid rgba(0,149,246,0.4); color:#0095f6; font-size:11px; font-weight:800; padding:3px 10px; border-radius:6px; letter-spacing:1px; margin-top:4px;">
                SAFEAD AI PLATFORM
            </div>
            <p style="color:#a8a8a8; font-size:13px; margin-top:10px;">Select an account profile to log in to the platform</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 1. User Profile Account Card
        st.markdown("""
        <div class="ig-card" style="display:flex; align-items:center; justify-content:space-between; padding:16px 20px; margin-bottom:14px; border-color:#262626;">
            <div style="display:flex; align-items:center; gap:14px;">
                <div style="width:48px; height:48px; border-radius:50%; background:linear-gradient(45deg,#f09433,#dc2743,#bc1888); padding:2px; display:flex; align-items:center; justify-content:center;">
                    <div style="width:100%; height:100%; border-radius:50%; background:#121212; display:flex; align-items:center; justify-content:center; font-size:22px; border:2px solid #000;">
                        📱
                    </div>
                </div>
                <div>
                    <div style="font-size:15px; font-weight:700; color:#ffffff; display:flex; align-items:center; gap:4px;">
                        @social_explorer
                        <span style="color:#0095f6; font-size:13px;" title="Verified Profile">✓</span>
                    </div>
                    <div style="font-size:12px; color:#8e8e8e;">User • Reels Feed & Biometric KYC</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Log In as @social_explorer (User)", key="btn_user", use_container_width=True):
            st.session_state["role"] = "USER"
            st.rerun()

        # 2. Ad Owner Profile Account Card
        st.markdown("""
        <div class="ig-card" style="display:flex; align-items:center; justify-content:space-between; padding:16px 20px; margin-bottom:14px; border-color:#262626; margin-top:16px;">
            <div style="display:flex; align-items:center; gap:14px;">
                <div style="width:48px; height:48px; border-radius:50%; background:#333; padding:2px; display:flex; align-items:center; justify-content:center;">
                    <div style="width:100%; height:100%; border-radius:50%; background:#121212; display:flex; align-items:center; justify-content:center; font-size:22px; border:2px solid #000;">
                        🏢
                    </div>
                </div>
                <div>
                    <div style="font-size:15px; font-weight:700; color:#ffffff;">
                        @advertiser_studio
                    </div>
                    <div style="font-size:12px; color:#8e8e8e;">Creator • Multimodal Ad Moderation</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Log In as @advertiser_studio (Owner)", key="btn_owner", use_container_width=True):
            st.session_state["role"] = "ADVERTISEMENT_OWNER"
            st.rerun()

        # 3. Admin Safety Auditor Account Card
        st.markdown("""
        <div class="ig-card" style="display:flex; align-items:center; justify-content:space-between; padding:16px 20px; margin-bottom:14px; border-color:#262626; margin-top:16px;">
            <div style="display:flex; align-items:center; gap:14px;">
                <div style="width:48px; height:48px; border-radius:50%; background:#333; padding:2px; display:flex; align-items:center; justify-content:center;">
                    <div style="width:100%; height:100%; border-radius:50%; background:#121212; display:flex; align-items:center; justify-content:center; font-size:22px; border:2px solid #000;">
                        🛡️
                    </div>
                </div>
                <div>
                    <div style="font-size:15px; font-weight:700; color:#ffffff;">
                        @safead_compliance
                    </div>
                    <div style="font-size:12px; color:#8e8e8e;">Admin • HITL Queue & Safety Audits</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Log In as @safead_compliance (Admin)", key="btn_admin", use_container_width=True):
            st.session_state["role"] = "ADMIN"
            st.rerun()

        # Footer
        st.markdown("""
        <div style="text-align:center; margin-top:30px; font-size:11px; color:#737373;">
            from <b style="color:#a8a8a8;">Meta / SafeAd AI</b><br>
            © 2026 SafeAd Instagram Platform • Phone-Responsive Biometric KYC
        </div>
        """, unsafe_allow_html=True)
