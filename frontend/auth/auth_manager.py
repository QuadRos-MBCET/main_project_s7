import streamlit as st
from frontend.styles.safead_theme import render_svg_icon, render_sparkline

def login_page():
    # -------------------------------------------------------------------------
    # 1. RITEFLOW HERO BANNER (Centered with Italic Serif Accent & Browser Frame)
    # -------------------------------------------------------------------------
    st.markdown(f"""
    <div style="text-align: center; padding: 48px 16px 36px 16px; position: relative;">
        <!-- Eyebrow Badge Pill -->
        <div class="rf-eyebrow-pill" style="margin-bottom: 22px;">
            <span style="display:inline-block; width:7px; height:7px; border-radius:50%; background:#6C5CE7; box-shadow:0 0 10px #6C5CE7;"></span>
            AI-POWERED CONTENT SAFETY
        </div>

        <!-- Hero Headline with Italic Serif Accent Word -->
        <h1 class="rf-hero-title">
            Smarter Ad Moderation<br>
            <span class="gradient-text">Starts with</span> <span class="rf-italic-serif">SafeAd</span>
        </h1>

        <!-- Subtitle -->
        <p class="rf-hero-subtitle">
            Unlock multimodal AI to pre-screen ad creatives, enforce age compliance, and automate
            policy safety — in real-time. Designed for modern media networks and advertisers.
        </p>

        <!-- Glossy Hero Pill CTA -->
        <div style="display: flex; justify-content: center; gap: 14px; margin-bottom: 40px; flex-wrap: wrap;">
            <a href="#workspaces" class="rf-btn-white" style="text-decoration:none; display:inline-flex; align-items:center; gap:8px;">
                <span>Explore Workspaces</span>
                {render_svg_icon("arrow_right", size=14, color="#0B0F1C")}
            </a>
            <div class="rf-btn-secondary" style="display:inline-flex; align-items:center; gap:8px;">
                {render_svg_icon("shield", size=14, color="#A493C2")}
                <span>Multimodal Vision & Audio</span>
            </div>
        </div>

        <!-- Signature Browser Frame Dashboard Showcase -->
        <div style="max-width: 980px; margin: 0 auto; text-align: left;">
            <div class="rf-browser-frame">
                <div class="rf-browser-header">
                    <div class="rf-browser-dots">
                        <span class="rf-dot red"></span>
                        <span class="rf-dot yellow"></span>
                        <span class="rf-dot green"></span>
                    </div>
                    <div class="rf-browser-url">safead.ai/decision-engine</div>
                    <div style="width: 52px;"></div>
                </div>
                <div class="rf-browser-body">
                    <!-- Showcase Header inside Browser -->
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 20px; flex-wrap:wrap; gap:12px;">
                        <div style="display:flex; align-items:center; gap:12px;">
                            <div style="width:36px; height:36px; border-radius:10px; background:rgba(108,92,231,0.18); border:1px solid rgba(108,92,231,0.35); display:flex; align-items:center; justify-content:center;">
                                {render_svg_icon("cpu", size=18, color="#6C5CE7")}
                            </div>
                            <div>
                                <div style="font-size:16px; font-weight:700; color:#FFFFFF; font-family:'Outfit',sans-serif;">SafeAd Multimodal Decision Engine</div>
                                <div style="font-size:12px; color:#A493C2;">Real-Time Two-Stage Arbitration • Learned Random Forest & Qwen3-VL</div>
                            </div>
                        </div>
                        <div style="display:flex; align-items:center; gap:8px;">
                            <span class="rf-badge-safe">
                                {render_svg_icon("check", size=11, color="#22C55E")}
                                SYSTEM ONLINE
                            </span>
                            <span style="font-size:12px; color:#A493C2;">v2.4 Production</span>
                        </div>
                    </div>

                    <!-- 3 Compact Stat Panels inside Browser Showcase -->
                    <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap:16px; margin-bottom:20px;">
                        <!-- Panel 1: Monthly Creatives -->
                        <div class="rf-stat-card">
                            <div class="rf-stat-label">Creatives Screened</div>
                            <div class="rf-stat-value">25.4k</div>
                            <div style="display:flex; align-items:center; gap:8px; font-size:12px; color:#A493C2;">
                                <span class="rf-stat-delta">+18.2%</span>
                                <span>vs last month</span>
                            </div>
                        </div>

                        <!-- Panel 2: Revenue / Protection Summary Table -->
                        <div class="rf-stat-card">
                            <div class="rf-stat-label">Policy Enforcement Summary</div>
                            <div style="margin-top:8px;">
                                <div class="rf-table-row">
                                    <span style="color:#A493C2;">Safe For All (Universal)</span>
                                    <span style="color:#FFFFFF; font-weight:600;">84.2%</span>
                                </div>
                                <div class="rf-table-row">
                                    <span style="color:#A493C2;">Age Restricted (14+ / 18+)</span>
                                    <span style="color:#E2D9F3; font-weight:600;">11.6%</span>
                                </div>
                                <div class="rf-table-row" style="border-bottom:none;">
                                    <span style="color:#A493C2;">Rejected Violations</span>
                                    <span style="color:#EF4444; font-weight:600;">4.2%</span>
                                </div>
                            </div>
                        </div>

                        <!-- Panel 3: Real-Time Queue + Sparkline -->
                        <div class="rf-stat-card">
                            <div class="rf-stat-label">Real-Time Threat Index</div>
                            <div class="rf-stat-value">0.08</div>
                            <div style="font-size:12px; color:#A493C2; margin-bottom:8px;">Zero critical leaks across 24h</div>
                            {render_sparkline([4, 6, 5, 8, 3, 4, 2, 5, 3, 2, 1, 2], width=200, height=36, color="#6C5CE7")}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 2. TRUSTED BY / INDUSTRY STANDARDS MARQUEE
    # -------------------------------------------------------------------------
    st.markdown("""
    <div style="text-align: center; margin: 28px auto 48px auto; max-width: 980px;">
        <div style="font-size: 11px; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: #6E7287; margin-bottom: 16px;">
            TRUSTED BY INNOVATIVE MEDIA NETWORKS & COMPLIANCE TEAMS
        </div>
        <div style="background: rgba(17, 23, 38, 0.6); backdrop-filter: blur(12px); border: 1px solid rgba(108, 92, 231, 0.15); border-radius: 9999px; padding: 12px 28px; display: flex; align-items: center; justify-content: space-around; flex-wrap: wrap; gap: 20px;">
            <div style="display:flex; align-items:center; gap:8px; font-size:12px; font-weight:700; color:#E2D9F3; letter-spacing:0.04em;">
                <span style="color:#6C5CE7;">●</span> COPPA CHILD SAFETY
            </div>
            <div style="display:flex; align-items:center; gap:8px; font-size:12px; font-weight:700; color:#E2D9F3; letter-spacing:0.04em;">
                <span style="color:#6C5CE7;">●</span> EU DIGITAL SERVICES ACT
            </div>
            <div style="display:flex; align-items:center; gap:8px; font-size:12px; font-weight:700; color:#E2D9F3; letter-spacing:0.04em;">
                <span style="color:#6C5CE7;">●</span> FTC TRUTH-IN-ADVERTISING
            </div>
            <div style="display:flex; align-items:center; gap:8px; font-size:12px; font-weight:700; color:#E2D9F3; letter-spacing:0.04em;">
                <span style="color:#6C5CE7;">●</span> ISO/IEC 27001 AI AUDIT
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 3. ROLE SELECTION WORKSPACE TILES (RiteFlow Glass Cards with Checklist)
    # -------------------------------------------------------------------------
    st.markdown("""
    <div id="workspaces" style="margin-bottom: 24px; text-align: left;">
        <div class="rf-eyebrow-pill" style="margin-bottom: 10px;">WORKSPACE DIRECTORY</div>
        <h2 style="margin: 0; font-size: 26px; font-weight: 700; color: #FFFFFF; font-family: 'Outfit', sans-serif;">
            Who we help
        </h2>
        <p style="margin: 6px 0 0 0; font-size: 14px; color: #A493C2;">
            Select your dedicated portal to access audience feeds, creator moderation, or governance desks.
        </p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3, gap="medium")

    # Card 1: User / Consumer Experience
    with c1:
        st.markdown(f"""
        <div class="rf-card" style="height: 340px; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <div style="width: 44px; height: 44px; border-radius: 12px; background: rgba(108, 92, 231, 0.14); border: 1px solid rgba(108, 92, 231, 0.32); display: flex; align-items: center; justify-content: center; margin-bottom: 16px;">
                    {render_svg_icon("user", size=22, color="#6C5CE7")}
                </div>
                <div style="font-size: 11px; font-weight: 800; letter-spacing: 0.12em; color: #A493C2; text-transform: uppercase; margin-bottom: 6px;">AUDIENCE PLATFORM</div>
                <div style="font-size: 20px; font-weight: 700; color: #FFFFFF; margin-bottom: 10px; font-family:'Outfit',sans-serif;">User Platform</div>
                <div style="font-size: 13px; color: #A493C2; line-height: 1.5; margin-bottom: 16px;">
                    Explore curated social feeds with age-aware ad delivery. Verify identity with ArcFace anti-spoof biometric verification.
                </div>
                <div style="display:flex; flex-direction:column; gap:8px;">
                    <div style="display:flex; align-items:center; gap:8px; font-size:12px; color:#E2D9F3;">
                        <span class="rf-circle-check">{render_svg_icon("check", size=10, color="#FFFFFF")}</span>
                        <span>Age-gated social feed & short reels</span>
                    </div>
                    <div style="display:flex; align-items:center; gap:8px; font-size:12px; color:#E2D9F3;">
                        <span class="rf-circle-check">{render_svg_icon("check", size=10, color="#FFFFFF")}</span>
                        <span>30-FPS ArcFace anti-spoof KYC</span>
                    </div>
                    <div style="display:flex; align-items:center; gap:8px; font-size:12px; color:#E2D9F3;">
                        <span class="rf-circle-check">{render_svg_icon("check", size=10, color="#FFFFFF")}</span>
                        <span>Zero-exposure child protection shields</span>
                    </div>
                </div>
            </div>
            <div style="font-size: 11px; color: #6E7287; font-weight: 600; margin-top:14px;">@social_explorer</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Enter User Platform →", key="btn_user", use_container_width=True, type="secondary"):
            st.session_state["role"] = "USER"
            st.rerun()

    # Card 2: Advertiser Studio
    with c2:
        st.markdown(f"""
        <div class="rf-card" style="height: 340px; display: flex; flex-direction: column; justify-content: space-between; border-color: rgba(108, 92, 231, 0.4); box-shadow: 0 0 24px rgba(108, 92, 231, 0.12);">
            <div>
                <div style="width: 44px; height: 44px; border-radius: 12px; background: rgba(108, 92, 231, 0.22); border: 1px solid rgba(108, 92, 231, 0.45); display: flex; align-items: center; justify-content: center; margin-bottom: 16px;">
                    {render_svg_icon("cpu", size=22, color="#6C5CE7")}
                </div>
                <div style="font-size: 11px; font-weight: 800; letter-spacing: 0.12em; color: #6C5CE7; text-transform: uppercase; margin-bottom: 6px;">CREATIVE STUDIO</div>
                <div style="font-size: 20px; font-weight: 700; color: #FFFFFF; margin-bottom: 10px; font-family:'Outfit',sans-serif;">Advertiser Studio</div>
                <div style="font-size: 13px; color: #A493C2; line-height: 1.5; margin-bottom: 16px;">
                    Pre-screen ad image and video assets through multimodal safety guards (Violence, NSFW, Child Safety, OCR Text).
                </div>
                <div style="display:flex; flex-direction:column; gap:8px;">
                    <div style="display:flex; align-items:center; gap:8px; font-size:12px; color:#E2D9F3;">
                        <span class="rf-circle-check">{render_svg_icon("check", size=10, color="#FFFFFF")}</span>
                        <span>Multi-modal pre-flight asset audit</span>
                    </div>
                    <div style="display:flex; align-items:center; gap:8px; font-size:12px; color:#E2D9F3;">
                        <span class="rf-circle-check">{render_svg_icon("check", size=10, color="#FFFFFF")}</span>
                        <span>Hierarchical Strategy D AI fusion</span>
                    </div>
                    <div style="display:flex; align-items:center; gap:8px; font-size:12px; color:#E2D9F3;">
                        <span class="rf-circle-check">{render_svg_icon("check", size=10, color="#FFFFFF")}</span>
                        <span>Instant compliance scorecard & verdict</span>
                    </div>
                </div>
            </div>
            <div style="font-size: 11px; color: #6E7287; font-weight: 600; margin-top:14px;">@advertiser_studio</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Launch Advertiser Studio →", key="btn_owner", use_container_width=True, type="primary"):
            st.session_state["role"] = "ADVERTISEMENT_OWNER"
            st.rerun()

    # Card 3: Compliance & Admin Review
    with c3:
        st.markdown(f"""
        <div class="rf-card" style="height: 340px; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <div style="width: 44px; height: 44px; border-radius: 12px; background: rgba(108, 92, 231, 0.14); border: 1px solid rgba(108, 92, 231, 0.32); display: flex; align-items: center; justify-content: center; margin-bottom: 16px;">
                    {render_svg_icon("shield", size=22, color="#6C5CE7")}
                </div>
                <div style="font-size: 11px; font-weight: 800; letter-spacing: 0.12em; color: #A493C2; text-transform: uppercase; margin-bottom: 6px;">GOVERNANCE DESK</div>
                <div style="font-size: 20px; font-weight: 700; color: #FFFFFF; margin-bottom: 10px; font-family:'Outfit',sans-serif;">Compliance Admin</div>
                <div style="font-size: 13px; color: #A493C2; line-height: 1.5; margin-bottom: 16px;">
                    Inspect flagged creative campaigns in the Human-in-the-Loop review queue and verify cryptographic audit trails.
                </div>
                <div style="display:flex; flex-direction:column; gap:8px;">
                    <div style="display:flex; align-items:center; gap:8px; font-size:12px; color:#E2D9F3;">
                        <span class="rf-circle-check">{render_svg_icon("check", size=10, color="#FFFFFF")}</span>
                        <span>Human-in-the-loop review queue</span>
                    </div>
                    <div style="display:flex; align-items:center; gap:8px; font-size:12px; color:#E2D9F3;">
                        <span class="rf-circle-check">{render_svg_icon("check", size=10, color="#FFFFFF")}</span>
                        <span>Multi-stage policy arbitration logs</span>
                    </div>
                    <div style="display:flex; align-items:center; gap:8px; font-size:12px; color:#E2D9F3;">
                        <span class="rf-circle-check">{render_svg_icon("check", size=10, color="#FFFFFF")}</span>
                        <span>One-click adjudication & feed dispatch</span>
                    </div>
                </div>
            </div>
            <div style="font-size: 11px; color: #6E7287; font-weight: 600; margin-top:14px;">@safead_compliance</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open Compliance Desk →", key="btn_admin", use_container_width=True, type="secondary"):
            st.session_state["role"] = "ADMIN"
            st.rerun()
