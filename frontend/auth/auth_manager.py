import streamlit as st
from frontend.styles.safead_theme import render_svg_icon, render_sparkline, render_html

def login_page():
    # -------------------------------------------------------------------------
    # 1. RITEFLOW HERO BANNER (Centered with Italic Serif Accent & Browser Frame)
    # -------------------------------------------------------------------------
    render_html(f"""
    <div style="text-align: center; padding: 48px 16px 36px 16px; position: relative;">
        <!-- Eyebrow Badge Pill -->
        <div style="margin-bottom: 22px;">
            <div class="rf-eyebrow-pill">
                <span style="display:inline-block; width:7px; height:7px; border-radius:50%; background:#6366F1; box-shadow:0 0 10px #6366F1;"></span>
                AI-POWERED CONTENT SAFETY
            </div>
        </div>

        <!-- Hero Headline with Italic Serif Accent Word (RiteFlow Style) -->
        <h1 class="rf-hero-title">
            Smarter Ad Moderation<br>
            <span class="rf-hero-subtitle-gradient">Starts with</span> <span class="rf-italic-serif">SafeAd</span>
        </h1>

        <!-- Subtitle -->
        <p class="rf-hero-desc">
            Unlock multimodal AI to pre-screen ad creatives, enforce age compliance, and automate
            policy safety — in real-time. Designed for modern media networks and advertisers.
        </p>

        <!-- Glossy Hero Pill CTA (RiteFlow "Start for Free" Style) -->
        <div style="display: flex; justify-content: center; gap: 16px; margin-bottom: 44px; flex-wrap: wrap;">
            <a href="#workspaces" class="rf-btn-white">
                <span>Start for Free</span>
                {render_svg_icon("arrow_right", size=14, color="#080B14")}
            </a>
            <div class="rf-btn-secondary">
                {render_svg_icon("shield", size=15, color="#A5B4FC")}
                <span style="margin-left:8px;">Multimodal Decision Engine</span>
            </div>
        </div>

        <!-- Signature Browser Frame Dashboard Showcase (RiteFlow Ambient Halo) -->
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
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 22px; flex-wrap:wrap; gap:12px;">
                        <div style="display:flex; align-items:center; gap:12px;">
                            <div style="width:36px; height:36px; border-radius:10px; background:rgba(79,70,229,0.2); border:1px solid rgba(99,102,241,0.4); display:flex; align-items:center; justify-content:center; box-shadow:0 0 12px rgba(79,70,229,0.4);">
                                {render_svg_icon("cpu", size=18, color="#818CF8")}
                            </div>
                            <div>
                                <div style="font-size:16px; font-weight:700; color:#FFFFFF; font-family:'Outfit',sans-serif;">Dashboard</div>
                                <div style="font-size:12px; color:#94A3B8;">Today, Decision Intelligence Active • Learned RF & Qwen3-VL</div>
                            </div>
                        </div>
                        <div style="display:flex; align-items:center; gap:8px;">
                            <span class="rf-badge-safe">
                                {render_svg_icon("check", size=11, color="#10B981")}
                                SYSTEM ONLINE
                            </span>
                            <span style="font-size:12px; color:#94A3B8;">v2.4 Production</span>
                        </div>
                    </div>

                    <!-- 3 Compact Stat Panels inside Browser Showcase -->
                    <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap:16px; margin-bottom:10px;">
                        <!-- Panel 1: Monthly Sales / Creatives -->
                        <div class="rf-stat-card">
                            <div class="rf-stat-label">Monthly Creatives</div>
                            <div style="display:flex; justify-content:space-between; align-items:baseline; margin: 8px 0 12px 0;">
                                <div>
                                    <div style="font-size:11px; color:#64748B;">Total Screened</div>
                                    <div class="rf-stat-value">25.4k</div>
                                </div>
                                <div style="text-align:right;">
                                    <div style="font-size:11px; color:#64748B;">Protected Brand Value</div>
                                    <div style="font-size:18px; font-weight:700; color:#FFFFFF; font-family:'Outfit',sans-serif;">$6.35M</div>
                                </div>
                            </div>
                            <div style="font-size:11px; color:#64748B; margin-bottom:4px;">Total throughput: 1.3M events</div>
                            <div style="height:4px; width:100%; background:rgba(255,255,255,0.06); border-radius:9999px; overflow:hidden;">
                                <div style="height:100%; width:68%; background:linear-gradient(90deg, #4F46E5 0%, #818CF8 100%); border-radius:9999px;"></div>
                            </div>
                        </div>

                        <!-- Panel 2: Revenue Summary Table -->
                        <div class="rf-stat-card">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                                <div class="rf-stat-label" style="margin-bottom:0;">Revenue / Safety Summary</div>
                                <span style="font-size:11px; color:#64748B;">Last 30 Days</span>
                            </div>
                            <div>
                                <div class="rf-table-row">
                                    <span style="color:#94A3B8;">Safe For All Ads</span>
                                    <span style="color:#FFFFFF; font-weight:600;">$12,900</span>
                                </div>
                                <div class="rf-table-row">
                                    <span style="color:#94A3B8;">Age-Gated (18+ / 14+)</span>
                                    <span style="color:#C7D2FE; font-weight:600;">$9,950</span>
                                </div>
                                <div class="rf-table-row">
                                    <span style="color:#94A3B8;">Enterprise Compliance</span>
                                    <span style="color:#C7D2FE; font-weight:600;">$3,700</span>
                                </div>
                                <div class="rf-table-row" style="border-bottom:none;">
                                    <span style="color:#94A3B8;">Violations Blocked</span>
                                    <span style="color:#EF4444; font-weight:600;">$3,700</span>
                                </div>
                            </div>
                        </div>

                        <!-- Panel 3: Real-Time Queue + Sparkline -->
                        <div class="rf-stat-card">
                            <div class="rf-stat-label">Real-time</div>
                            <div class="rf-stat-value" style="font-size:36px; margin: 4px 0 8px 0;">49</div>
                            <div style="font-size:12px; color:#94A3B8; margin-bottom:12px;">Active audits processing now</div>
                            {render_sparkline([12, 16, 14, 22, 18, 25, 20, 28, 24, 35, 42, 49], width=210, height=44, color="#6366F1")}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """)

    # -------------------------------------------------------------------------
    # 2. TRUSTED BY / INDUSTRY STANDARDS MARQUEE
    # -------------------------------------------------------------------------
    render_html("""
    <div style="text-align: center; margin: 36px auto 52px auto; max-width: 980px;">
        <div style="font-size: 11px; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: #64748B; margin-bottom: 18px;">
            TRUSTED BY INNOVATIVE TEAMS & COMPLIANCE NETWORKS
        </div>
        <div style="background: rgba(13, 18, 32, 0.6); backdrop-filter: blur(12px); border: 1px solid rgba(99, 102, 241, 0.18); border-radius: 9999px; padding: 14px 28px; display: flex; align-items: center; justify-content: space-around; flex-wrap: wrap; gap: 20px;">
            <div style="display:flex; align-items:center; gap:8px; font-size:12px; font-weight:700; color:#C7D2FE; letter-spacing:0.04em;">
                <span style="color:#6366F1;">●</span> COPPA CHILD SAFETY
            </div>
            <div style="display:flex; align-items:center; gap:8px; font-size:12px; font-weight:700; color:#C7D2FE; letter-spacing:0.04em;">
                <span style="color:#6366F1;">●</span> EU DIGITAL SERVICES ACT
            </div>
            <div style="display:flex; align-items:center; gap:8px; font-size:12px; font-weight:700; color:#C7D2FE; letter-spacing:0.04em;">
                <span style="color:#6366F1;">●</span> FTC TRUTH-IN-ADVERTISING
            </div>
            <div style="display:flex; align-items:center; gap:8px; font-size:12px; font-weight:700; color:#C7D2FE; letter-spacing:0.04em;">
                <span style="color:#6366F1;">●</span> ISO/IEC 27001 AI AUDIT
            </div>
        </div>
    </div>
    """)

    # -------------------------------------------------------------------------
    # 3. ROLE SELECTION WORKSPACE TILES (RiteFlow Glass Cards with Checklist)
    # -------------------------------------------------------------------------
    render_html("""
    <div id="workspaces" style="margin-bottom: 24px; text-align: left;">
        <div class="rf-eyebrow-pill" style="margin-bottom: 10px;">WORKSPACE DIRECTORY</div>
        <h2 style="margin: 0; font-size: 26px; font-weight: 700; color: #FFFFFF; font-family: 'Outfit', sans-serif;">
            Who we help
        </h2>
        <p style="margin: 6px 0 0 0; font-size: 14px; color: #94A3B8;">
            Select your dedicated portal to access audience feeds, creator moderation, or governance desks.
        </p>
    </div>
    """)

    c1, c2, c3 = st.columns(3, gap="medium")

    # Card 1: User / Consumer Experience
    with c1:
        render_html(f"""
        <div class="rf-card" style="height: 350px; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <div style="width: 44px; height: 44px; border-radius: 12px; background: rgba(79, 70, 229, 0.16); border: 1px solid rgba(99, 102, 241, 0.35); display: flex; align-items: center; justify-content: center; margin-bottom: 16px;">
                    {render_svg_icon("user", size=22, color="#818CF8")}
                </div>
                <div style="font-size: 11px; font-weight: 800; letter-spacing: 0.12em; color: #818CF8; text-transform: uppercase; margin-bottom: 6px;">AUDIENCE PLATFORM</div>
                <div style="font-size: 20px; font-weight: 700; color: #FFFFFF; margin-bottom: 10px; font-family:'Outfit',sans-serif;">User Platform</div>
                <div style="font-size: 13px; color: #94A3B8; line-height: 1.5; margin-bottom: 16px;">
                    Explore curated social feeds with age-aware ad delivery. Verify identity with ArcFace anti-spoof biometric verification.
                </div>
                <div style="display:flex; flex-direction:column; gap:8px;">
                    <div style="display:flex; align-items:center; gap:8px; font-size:12px; color:#C7D2FE;">
                        <span class="rf-circle-check">{render_svg_icon("check", size=10, color="#FFFFFF")}</span>
                        <span>Age-gated social feed & short reels</span>
                    </div>
                    <div style="display:flex; align-items:center; gap:8px; font-size:12px; color:#C7D2FE;">
                        <span class="rf-circle-check">{render_svg_icon("check", size=10, color="#FFFFFF")}</span>
                        <span>30-FPS ArcFace anti-spoof KYC</span>
                    </div>
                    <div style="display:flex; align-items:center; gap:8px; font-size:12px; color:#C7D2FE;">
                        <span class="rf-circle-check">{render_svg_icon("check", size=10, color="#FFFFFF")}</span>
                        <span>Zero-exposure child protection shields</span>
                    </div>
                </div>
            </div>
            <div style="font-size: 11px; color: #64748B; font-weight: 600; margin-top:14px;">@social_explorer</div>
        </div>
        """)
        if st.button("Enter User Platform →", key="btn_user", use_container_width=True, type="secondary"):
            st.session_state["role"] = "USER"
            st.rerun()

    # Card 2: Advertiser Studio
    with c2:
        render_html(f"""
        <div class="rf-card" style="height: 350px; display: flex; flex-direction: column; justify-content: space-between; border-color: rgba(99, 102, 241, 0.45); box-shadow: 0 0 30px rgba(79, 70, 229, 0.18);">
            <div>
                <div style="width: 44px; height: 44px; border-radius: 12px; background: rgba(79, 70, 229, 0.25); border: 1px solid rgba(99, 102, 241, 0.5); display: flex; align-items: center; justify-content: center; margin-bottom: 16px;">
                    {render_svg_icon("cpu", size=22, color="#A5B4FC")}
                </div>
                <div style="font-size: 11px; font-weight: 800; letter-spacing: 0.12em; color: #A5B4FC; text-transform: uppercase; margin-bottom: 6px;">CREATIVE STUDIO</div>
                <div style="font-size: 20px; font-weight: 700; color: #FFFFFF; margin-bottom: 10px; font-family:'Outfit',sans-serif;">Advertiser Studio</div>
                <div style="font-size: 13px; color: #94A3B8; line-height: 1.5; margin-bottom: 16px;">
                    Pre-screen ad image and video assets through multimodal safety guards (Violence, NSFW, Child Safety, OCR Text).
                </div>
                <div style="display:flex; flex-direction:column; gap:8px;">
                    <div style="display:flex; align-items:center; gap:8px; font-size:12px; color:#C7D2FE;">
                        <span class="rf-circle-check">{render_svg_icon("check", size=10, color="#FFFFFF")}</span>
                        <span>Multi-modal pre-flight asset audit</span>
                    </div>
                    <div style="display:flex; align-items:center; gap:8px; font-size:12px; color:#C7D2FE;">
                        <span class="rf-circle-check">{render_svg_icon("check", size=10, color="#FFFFFF")}</span>
                        <span>Hierarchical Strategy D AI fusion</span>
                    </div>
                    <div style="display:flex; align-items:center; gap:8px; font-size:12px; color:#C7D2FE;">
                        <span class="rf-circle-check">{render_svg_icon("check", size=10, color="#FFFFFF")}</span>
                        <span>Instant compliance scorecard & verdict</span>
                    </div>
                </div>
            </div>
            <div style="font-size: 11px; color: #64748B; font-weight: 600; margin-top:14px;">@advertiser_studio</div>
        </div>
        """)
        if st.button("Launch Advertiser Studio →", key="btn_owner", use_container_width=True, type="primary"):
            st.session_state["role"] = "ADVERTISEMENT_OWNER"
            st.rerun()

    # Card 3: Compliance & Admin Review
    with c3:
        render_html(f"""
        <div class="rf-card" style="height: 350px; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <div style="width: 44px; height: 44px; border-radius: 12px; background: rgba(79, 70, 229, 0.16); border: 1px solid rgba(99, 102, 241, 0.35); display: flex; align-items: center; justify-content: center; margin-bottom: 16px;">
                    {render_svg_icon("shield", size=22, color="#818CF8")}
                </div>
                <div style="font-size: 11px; font-weight: 800; letter-spacing: 0.12em; color: #818CF8; text-transform: uppercase; margin-bottom: 6px;">GOVERNANCE DESK</div>
                <div style="font-size: 20px; font-weight: 700; color: #FFFFFF; margin-bottom: 10px; font-family:'Outfit',sans-serif;">Compliance Admin</div>
                <div style="font-size: 13px; color: #94A3B8; line-height: 1.5; margin-bottom: 16px;">
                    Inspect flagged creative campaigns in the Human-in-the-Loop review queue and verify cryptographic audit trails.
                </div>
                <div style="display:flex; flex-direction:column; gap:8px;">
                    <div style="display:flex; align-items:center; gap:8px; font-size:12px; color:#C7D2FE;">
                        <span class="rf-circle-check">{render_svg_icon("check", size=10, color="#FFFFFF")}</span>
                        <span>Human-in-the-loop review queue</span>
                    </div>
                    <div style="display:flex; align-items:center; gap:8px; font-size:12px; color:#C7D2FE;">
                        <span class="rf-circle-check">{render_svg_icon("check", size=10, color="#FFFFFF")}</span>
                        <span>Multi-stage policy arbitration logs</span>
                    </div>
                    <div style="display:flex; align-items:center; gap:8px; font-size:12px; color:#C7D2FE;">
                        <span class="rf-circle-check">{render_svg_icon("check", size=10, color="#FFFFFF")}</span>
                        <span>One-click adjudication & feed dispatch</span>
                    </div>
                </div>
            </div>
            <div style="font-size: 11px; color: #64748B; font-weight: 600; margin-top:14px;">@safead_compliance</div>
        </div>
        """)
        if st.button("Open Compliance Desk →", key="btn_admin", use_container_width=True, type="secondary"):
            st.session_state["role"] = "ADMIN"
            st.rerun()
