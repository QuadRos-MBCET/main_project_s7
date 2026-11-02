import streamlit as st
from frontend.styles.safead_theme import render_svg_icon

def login_page():
    # -------------------------------------------------------------------------
    # 1. QUANTEXA-STYLE HERO BANNER
    # -------------------------------------------------------------------------
    st.markdown("""
    <div class="safead-hero-card">
        <div class="safead-eyebrow">
            <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:#2DE2C0; box-shadow:0 0 8px #2DE2C0;"></span>
            MULTIMODAL DECISION INTELLIGENCE
        </div>
        <div class="safead-title-large">
            Unify Content Safety and Transform Your Decision-Making in <span class="safead-highlight">Ad Moderation</span>
        </div>
        <div class="safead-subtitle" style="max-width: 820px;">
            Protect audiences, automate brand safety, and enforce verifiable age compliance. 
            SafeAd integrates deep vision-language models, learned random forest policy fusion, 
            and real-time 30-FPS biometric KYC verification.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 2. ROLE SELECTION WORKSPACE TILES (FROSTED GLASS CARDS)
    # -------------------------------------------------------------------------
    st.markdown("""
    <div style="margin-bottom: 12px;">
        <span class="safead-eyebrow">SELECT WORKSPACE PORTAL</span>
        <h3 style="margin: 0; font-size: 24px; font-weight: 500; color: #FFFFFF;">Who we help</h3>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3, gap="medium")

    # Card 1: User / Consumer Experience
    with c1:
        st.markdown(f"""
        <div class="safead-card" style="height: 260px; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <div style="width: 44px; height: 44px; border-radius: 12px; background: rgba(45, 226, 192, 0.1); border: 1px solid rgba(45, 226, 192, 0.3); display: flex; align-items: center; justify-content: center; margin-bottom: 16px;">
                    {render_svg_icon("user", size=22, color="#2DE2C0")}
                </div>
                <div class="safead-eyebrow" style="color: #2DE2C0;">AUDIENCE PORTAL</div>
                <div style="font-size: 19px; font-weight: 700; color: #FFFFFF; margin-bottom: 8px;">Social & KYC Feed</div>
                <div style="font-size: 13px; color: #C2BAD8; line-height: 1.5;">
                    Explore curated social feeds with age-aware ad delivery. Verify identity with ArcFace anti-spoof biometric verification.
                </div>
            </div>
            <div style="font-size: 12px; color: #A493C2; font-weight: 600;">@social_explorer</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Access User Portal →", key="btn_user", use_container_width=True, type="secondary"):
            st.session_state["role"] = "USER"
            st.session_state["global_role_selector"] = "User Platform"
            st.rerun()

    # Card 2: Advertiser Studio
    with c2:
        st.markdown(f"""
        <div class="safead-card" style="height: 260px; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <div style="width: 44px; height: 44px; border-radius: 12px; background: rgba(121, 56, 223, 0.14); border: 1px solid rgba(121, 56, 223, 0.35); display: flex; align-items: center; justify-content: center; margin-bottom: 16px;">
                    {render_svg_icon("cpu", size=22, color="#A855F7")}
                </div>
                <div class="safead-eyebrow" style="color: #C084FC;">CREATIVE STUDIO</div>
                <div style="font-size: 19px; font-weight: 700; color: #FFFFFF; margin-bottom: 8px;">Advertiser Studio</div>
                <div style="font-size: 13px; color: #C2BAD8; line-height: 1.5;">
                    Pre-screen ad image and video assets through multimodal safety guards (Violence, NSFW, Child Safety, OCR Text).
                </div>
            </div>
            <div style="font-size: 12px; color: #A493C2; font-weight: 600;">@advertiser_studio</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Launch Advertiser Studio →", key="btn_owner", use_container_width=True, type="primary"):
            st.session_state["role"] = "ADVERTISEMENT_OWNER"
            st.session_state["global_role_selector"] = "Advertiser Studio"
            st.rerun()

    # Card 3: Compliance & Admin Review
    with c3:
        st.markdown(f"""
        <div class="safead-card" style="height: 260px; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <div style="width: 44px; height: 44px; border-radius: 12px; background: rgba(59, 130, 246, 0.12); border: 1px solid rgba(59, 130, 246, 0.3); display: flex; align-items: center; justify-content: center; margin-bottom: 16px;">
                    {render_svg_icon("shield", size=22, color="#60A5FA")}
                </div>
                <div class="safead-eyebrow" style="color: #60A5FA;">GOVERNANCE DESK</div>
                <div style="font-size: 19px; font-weight: 700; color: #FFFFFF; margin-bottom: 8px;">Compliance Admin</div>
                <div style="font-size: 13px; color: #C2BAD8; line-height: 1.5;">
                    Inspect flagged creative campaigns in the Human-in-the-Loop review queue and verify cryptographic audit trails.
                </div>
            </div>
            <div style="font-size: 12px; color: #A493C2; font-weight: 600;">@safead_compliance</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open Governance Desk →", key="btn_admin", use_container_width=True, type="secondary"):
            st.session_state["role"] = "ADMIN"
            st.session_state["global_role_selector"] = "Compliance Admin"
            st.rerun()

    # -------------------------------------------------------------------------
    # 3. QUANTEXA-STYLE FLOATING 'TRUSTED BY & COMPLIANCE' PILL
    # -------------------------------------------------------------------------
    st.markdown("""
    <div style="margin-top: 36px; background: rgba(23, 13, 43, 0.6); backdrop-filter: blur(16px); border: 1px solid rgba(168, 147, 217, 0.16); border-radius: 9999px; padding: 14px 28px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 16px;">
        <div style="font-size: 11px; font-weight: 800; letter-spacing: 0.16em; text-transform: uppercase; color: #A493C2;">
            POLICY STANDARDS
        </div>
        <div style="display: flex; align-items: center; gap: 24px; font-size: 12px; font-weight: 700; color: #E2D9F3; letter-spacing: 0.04em;">
            <span>COPPA CHILD-SAFETY</span>
            <span>•</span>
            <span>EU DIGITAL SERVICES ACT</span>
            <span>•</span>
            <span>FTC TRUTH-IN-ADVERTISING</span>
            <span>•</span>
            <span>ISO/IEC 27001 AI AUDIT</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
