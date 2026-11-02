"""
SafeAd AI - RiteFlow Dark SaaS Design System
Authentic SaaS aesthetic matching the RiteFlow template:
- Deep navy-black canvas (#0B0F1C) with violet radial glow halos (#6C5CE7)
- Geometric sans (Outfit & DM Sans) paired with elegant italic serif accent (Playfair Display)
- Outlined eyebrow pills, white glossy pill CTA, and solid indigo action buttons
- Signature Browser Frame component (macOS window dots + URL pill + back-glow halo)
- Compact stat cards with progress bars, clean table rows, and real-time sparklines
- Filled indigo circle-check icons and zero-flash persistent role switching
"""

import streamlit as st

RITEFLOW_CSS = """
<style>
/* -------------------------------------------------------------------------
   1. TYPOGRAPHY & COLOR TOKENS (Google Fonts)
   ------------------------------------------------------------------------- */
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:ital,wght@1,400;1,600;1,700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    /* Background & Atmospheric Halos */
    --rf-bg: #0B0F1C;
    --rf-surface: #111726;
    --rf-surface-card: #151D30;
    --rf-surface-elevated: #1B243B;
    --rf-surface-glass: rgba(21, 29, 48, 0.72);
    --rf-surface-glass-border: rgba(108, 92, 231, 0.22);

    /* Electric Indigo Accent System */
    --rf-indigo: #6C5CE7;
    --rf-indigo-hover: #5B4DE0;
    --rf-indigo-dark: #372A8F;
    --rf-indigo-glow: rgba(108, 92, 231, 0.38);
    --rf-indigo-soft: rgba(108, 92, 231, 0.14);

    /* Text & Readability (WCAG AA Compliant) */
    --rf-text: #FFFFFF;
    --rf-text-secondary: #B2B9D2;
    --rf-text-muted: #6C7A9C;
    --rf-text-subtle: #4D5875;

    /* Semantic Accents */
    --rf-green-delta: #10B981;
    --rf-green-bg: rgba(16, 185, 129, 0.14);
    --rf-amber-warning: #F59E0B;
    --rf-amber-bg: rgba(245, 158, 11, 0.14);
    --rf-red-danger: #EF4444;
    --rf-red-bg: rgba(239, 68, 68, 0.16);
    --rf-blue-info: #3B82F6;
    --rf-blue-bg: rgba(59, 130, 246, 0.14);

    /* Borders & Glows */
    --rf-border: rgba(255, 255, 255, 0.08);
    --rf-border-hover: rgba(108, 92, 231, 0.45);
    --rf-border-subtle: rgba(108, 92, 231, 0.2);
}

/* -------------------------------------------------------------------------
   2. GLOBAL CANVAS & SUBTLE GRID BACKGROUND
   ------------------------------------------------------------------------- */
html, body, [data-testid="stAppViewContainer"], .main {
    background-color: var(--rf-bg) !important;
    background-image: 
        radial-gradient(circle at 50% 16%, rgba(108, 92, 231, 0.25) 0%, transparent 60%),
        radial-gradient(circle at 85% 70%, rgba(91, 77, 224, 0.12) 0%, transparent 45%),
        radial-gradient(circle at 15% 85%, rgba(55, 42, 143, 0.16) 0%, transparent 45%),
        radial-gradient(rgba(108, 92, 231, 0.1) 1px, transparent 1px) !important;
    background-size: 100% 100%, 100% 100%, 100% 100%, 30px 30px !important;
    background-attachment: fixed !important;
    color: var(--rf-text) !important;
    font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    -webkit-font-smoothing: antialiased;
}

/* Generous top-padding to completely eliminate header clipping */
.block-container {
    max-width: 1240px !important;
    padding-top: 4.5rem !important;
    padding-bottom: 5rem !important;
    min-height: 85vh !important;
    animation: rfFadeReveal 0.35s cubic-bezier(0.16, 1, 0.3, 1) !important;
}

@keyframes rfFadeReveal {
    from {
        opacity: 0;
        transform: translateY(6px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* -------------------------------------------------------------------------
   3. STREAMLIT INTERNALS & ANTI-FLICKER OVERRIDES (COMMENTED)
   ------------------------------------------------------------------------- */

/* [data-stale="true"]: Keep 96% opacity during script reruns to eliminate grey flashing */
div[data-stale="true"] {
    opacity: 0.96 !important;
    filter: none !important;
    transition: opacity 0.15s ease-in-out !important;
}

/* [data-testid="stStatusWidget"]: Hide default running spinner to avoid reflow spikes */
[data-testid="stStatusWidget"] {
    display: none !important;
}

/* [data-testid="stDecoration"]: Hide top rainbow decoration line */
[data-testid="stDecoration"] {
    display: none !important;
}

/* [data-testid="stHeader"]: Clean dark top header with subtle bottom border */
[data-testid="stHeader"] {
    background: rgba(11, 15, 28, 0.88) !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    border-bottom: 1px solid var(--rf-border) !important;
}

/* [data-testid="stSidebar"]: Dark navy drawer */
[data-testid="stSidebar"] {
    background-color: #0d1222 !important;
    border-right: 1px solid var(--rf-border) !important;
}

[data-testid="stSidebar"] * {
    color: var(--rf-text) !important;
}

/* Accessible focus ring */
button:focus-visible, input:focus-visible, select:focus-visible, textarea:focus-visible {
    outline: 2px solid var(--rf-indigo) !important;
    outline-offset: 2px !important;
}

/* -------------------------------------------------------------------------
   4. RITEFLOW TYPOGRAPHY
   ------------------------------------------------------------------------- */
h1, h2, h3, h4, .rf-heading {
    font-family: 'Outfit', sans-serif !important;
    color: #FFFFFF !important;
    letter-spacing: -0.02em;
}

.rf-hero-title {
    font-family: 'Outfit', sans-serif !important;
    font-size: 54px;
    font-weight: 700;
    line-height: 1.15;
    letter-spacing: -0.03em;
    color: #FFFFFF;
    text-align: center;
    margin: 14px 0 16px 0;
}

.rf-hero-subtitle-gradient {
    background: linear-gradient(180deg, #FFFFFF 30%, #B2B9D2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    display: inline-block;
}

.rf-italic-serif {
    font-family: 'Playfair Display', 'Instrument Serif', Georgia, serif !important;
    font-style: italic !important;
    font-weight: 400 !important;
    color: #C3B8FF !important;
    letter-spacing: normal;
    padding: 0 4px;
}

.rf-hero-desc {
    font-size: 16px;
    line-height: 1.6;
    color: var(--rf-text-secondary);
    text-align: center;
    max-width: 680px;
    margin: 0 auto 24px auto;
}

.rf-eyebrow-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(108, 92, 231, 0.12);
    border: 1px solid rgba(108, 92, 231, 0.38);
    color: #C3B8FF;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 5px 16px;
    border-radius: 9999px;
    margin-bottom: 12px;
}

/* -------------------------------------------------------------------------
   5. RITEFLOW BROWSER FRAME COMPONENT
   ------------------------------------------------------------------------- */
.rf-browser-frame {
    background: #111728;
    border: 1px solid rgba(108, 92, 231, 0.28);
    border-radius: 20px;
    overflow: hidden;
    box-shadow: 0 0 70px -15px var(--rf-indigo-glow), 0 25px 50px -12px rgba(0, 0, 0, 0.7);
    margin: 24px 0;
    position: relative;
}

.rf-browser-header {
    background: #0d1222;
    border-bottom: 1px solid var(--rf-border);
    padding: 12px 18px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.rf-window-dots {
    display: flex;
    gap: 7px;
}

.rf-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
}
.rf-dot-red { background: #FF5F56; }
.rf-dot-yellow { background: #FFBD2E; }
.rf-dot-green { background: #27C93F; }

.rf-url-pill {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 9999px;
    padding: 3px 20px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: var(--rf-text-muted);
}

.rf-browser-body {
    padding: 24px;
    background: linear-gradient(180deg, #111728 0%, #0e1322 100%);
}

/* -------------------------------------------------------------------------
   6. RITEFLOW COMPACT STAT CARDS & TABLE ROWS
   ------------------------------------------------------------------------- */
.rf-stat-card {
    background: #151D30;
    border: 1px solid var(--rf-border);
    border-radius: 14px;
    padding: 18px 20px;
    margin-bottom: 14px;
    position: relative;
    overflow: hidden;
}

.rf-stat-label {
    font-size: 12px;
    font-weight: 600;
    color: var(--rf-text-muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 6px;
}

.rf-stat-number {
    font-family: 'Outfit', sans-serif;
    font-size: 28px;
    font-weight: 700;
    color: #FFFFFF;
    line-height: 1.2;
}

.rf-progress-bar {
    height: 4px;
    background: rgba(255, 255, 255, 0.08);
    border-radius: 9999px;
    margin-top: 10px;
    overflow: hidden;
}

.rf-progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #6C5CE7 0%, #A29BFE 100%);
    border-radius: 9999px;
}

.rf-table-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    font-size: 13px;
}
.rf-table-row:last-child {
    border-bottom: none;
}

.rf-circle-check {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: var(--rf-indigo);
    color: #FFFFFF;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    font-weight: 700;
    flex-shrink: 0;
}

/* -------------------------------------------------------------------------
   7. BUTTONS (WHITE GLOSSY HERO CTA, INDIGO PILL, GLASS OUTLINE)
   ------------------------------------------------------------------------- */
.rf-btn-white {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(180deg, #FFFFFF 0%, #E2E8F0 100%) !important;
    color: #0B0F1C !important;
    font-family: 'DM Sans', sans-serif;
    font-size: 14px !important;
    font-weight: 700 !important;
    padding: 11px 28px !important;
    border-radius: 9999px !important;
    border: none !important;
    cursor: pointer;
    box-shadow: 0 4px 20px rgba(255, 255, 255, 0.25);
    transition: all 0.2s ease;
    text-decoration: none !important;
}
.rf-btn-white:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 24px rgba(255, 255, 255, 0.35);
}

.rf-btn-indigo {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: var(--rf-indigo) !important;
    color: #FFFFFF !important;
    font-family: 'DM Sans', sans-serif;
    font-size: 14px !important;
    font-weight: 600 !important;
    padding: 10px 24px !important;
    border-radius: 9999px !important;
    border: none !important;
    cursor: pointer;
    box-shadow: 0 4px 16px var(--rf-indigo-glow);
    transition: all 0.2s ease;
    text-decoration: none !important;
}
.rf-btn-indigo:hover {
    background: var(--rf-indigo-hover) !important;
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(108, 92, 231, 0.5);
}

/* Streamlit Button Native Overrides */
div.stButton > button[kind="primary"] {
    background: var(--rf-indigo) !important;
    color: #FFFFFF !important;
    border: none !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    border-radius: 9999px !important;
    padding: 10px 24px !important;
    box-shadow: 0 4px 16px var(--rf-indigo-glow) !important;
    transition: all 0.2s ease !important;
}
div.stButton > button[kind="primary"]:hover {
    background: var(--rf-indigo-hover) !important;
    transform: translateY(-1px) !important;
}

div.stButton > button[kind="secondary"] {
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid var(--rf-border) !important;
    color: var(--rf-text) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    border-radius: 9999px !important;
    transition: all 0.2s ease !important;
}
div.stButton > button[kind="secondary"]:hover {
    border-color: var(--rf-indigo) !important;
    color: var(--rf-indigo) !important;
    background: rgba(108, 92, 231, 0.08) !important;
}

/* -------------------------------------------------------------------------
   8. DUAL-ENCODED VERDICT & STATUS BADGES (ICON + TEXT + TINT)
   ------------------------------------------------------------------------- */
.badge-safe, .badge-approve {
    background-color: var(--rf-green-bg);
    border: 1px solid var(--rf-green-delta);
    color: var(--rf-green-delta);
    padding: 10px 18px;
    border-radius: 10px;
    font-size: 15px;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 14px;
}

.badge-warning, .badge-18 {
    background-color: var(--rf-amber-bg);
    border: 1px solid var(--rf-amber-warning);
    color: var(--rf-amber-warning);
    padding: 10px 18px;
    border-radius: 10px;
    font-size: 15px;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 14px;
}

.badge-14 {
    background-color: var(--rf-blue-bg);
    border: 1px solid var(--rf-blue-info);
    color: var(--rf-blue-info);
    padding: 10px 18px;
    border-radius: 10px;
    font-size: 15px;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 14px;
}

.badge-hitl {
    background-color: var(--rf-indigo-soft);
    border: 1px solid var(--rf-indigo);
    color: #A29BFE;
    padding: 10px 18px;
    border-radius: 10px;
    font-size: 15px;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 14px;
}

.badge-danger, .badge-reject {
    background-color: var(--rf-red-bg);
    border: 1px solid var(--rf-red-danger);
    color: var(--rf-red-danger);
    padding: 10px 18px;
    border-radius: 10px;
    font-size: 15px;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 14px;
}

/* -------------------------------------------------------------------------
   9. STEPPER & RESPONSIVE BREAKPOINTS
   ------------------------------------------------------------------------- */
.rf-stepper {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: var(--rf-surface-card);
    border: 1px solid var(--rf-border);
    border-radius: 14px;
    padding: 14px 20px;
    margin-bottom: 22px;
}

.rf-step {
    display: flex;
    align-items: center;
    gap: 10px;
    color: var(--rf-text-muted);
    font-size: 13px;
    font-weight: 600;
}
.rf-step.active { color: #A29BFE; }
.rf-step.completed { color: #FFFFFF; }

.rf-step-num {
    width: 26px;
    height: 26px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.08);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: 700;
}
.rf-step.active .rf-step-num {
    background: var(--rf-indigo);
    color: #FFFFFF;
    box-shadow: 0 0 10px var(--rf-indigo);
}
.rf-step.completed .rf-step-num {
    background: #372A8F;
    color: #FFFFFF;
}

.rf-step-divider {
    flex: 1;
    height: 1px;
    background: var(--rf-border);
    margin: 0 16px;
}

@media (max-width: 768px) {
    .block-container {
        padding-top: 3.5rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    .rf-hero-title {
        font-size: 34px !important;
    }
    .rf-stepper {
        flex-direction: column;
        align-items: flex-start;
        gap: 10px;
    }
    .rf-step-divider {
        display: none;
    }
}

@media (prefers-reduced-motion: reduce) {
    *, ::before, ::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
        scroll-behavior: auto !important;
    }
}
</style>
"""

def inject_safead_styles():
    """Injects the RiteFlow dark SaaS design system."""
    st.markdown(RITEFLOW_CSS, unsafe_allow_html=True)

# Aliases for backwards compatibility
inject_instagram_styles = inject_safead_styles

def render_safead_brand(subtitle: str = "DECISION ENGINE"):
    """Renders the RiteFlow-styled brand mark with gradient wave icon."""
    html = f"""
    <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:18px; padding:0 2px;">
        <div style="display:flex; align-items:center; gap:12px;">
            <div style="width:28px; height:28px; border-radius:8px; background:linear-gradient(135deg, #6C5CE7 0%, #A29BFE 100%); display:flex; align-items:center; justify-content:center; box-shadow:0 0 14px rgba(108,92,231,0.5);">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2.5" stroke-linecap="round"><path d="M2 12h4l3-9 4 18 3-9h6"/></svg>
            </div>
            <div style="font-family:'Outfit', sans-serif; font-size:22px; font-weight:800; letter-spacing:-0.03em; color:#FFFFFF;">
                Safe<span style="color:#A29BFE;">Ad</span>
            </div>
            <div style="background:rgba(108, 92, 231, 0.15); border:1px solid rgba(108, 92, 231, 0.4); color:#C3B8FF; font-size:9px; font-weight:800; padding:2px 8px; border-radius:9999px; letter-spacing:0.1em; text-transform:uppercase;">
                {subtitle}
            </div>
        </div>
        <div style="display:flex; align-items:center; gap:8px; font-size:12px; color:#A2AECB;">
            <span style="width:7px; height:7px; border-radius:50%; background:#10B981; display:inline-block; box-shadow:0 0 8px #10B981;"></span>
            <span>Online</span>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

render_instagram_logo = render_safead_brand

def render_stories_bar():
    return

def render_svg_icon(name: str, size: int = 20, color: str = "currentColor") -> str:
    """Returns minimalist SVG line icons."""
    icons = {
        "shield": f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>''',
        "eye": f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>''',
        "user": f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>''',
        "cpu": f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2" ry="2"/><rect x="9" y="9" width="6" height="6"/><line x1="9" y1="1" x2="9" y2="4"/><line x1="15" y1="1" x2="15" y2="4"/><line x1="9" y1="20" x2="9" y2="23"/><line x1="15" y1="20" x2="15" y2="23"/><line x1="20" y1="9" x2="23" y2="9"/><line x1="20" y1="14" x2="23" y2="14"/><line x1="1" y1="9" x2="4" y2="9"/><line x1="1" y1="14" x2="4" y2="14"/></svg>''',
        "check": f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>''',
        "alert": f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>'''
    }
    return icons.get(name, "")

def render_risk_gauge(score: float, label: str = "Risk Index"):
    """Renders circular SVG risk score gauge with indigo/emerald arcs."""
    score = max(0.0, min(100.0, float(score or 0.0)))
    radius = 36
    circumference = 2 * 3.14159 * radius
    stroke_dashoffset = circumference - (score / 100.0) * circumference
    
    if score < 35.0:
        stroke_color = "#10B981"
        badge_text = "LOW RISK"
    elif score < 70.0:
        stroke_color = "#F59E0B"
        badge_text = "MODERATE RISK"
    else:
        stroke_color = "#EF4444"
        badge_text = "HIGH RISK"

    svg = f"""
    <div style="display:flex; align-items:center; gap:20px; background:#151D30; border:1px solid var(--rf-border); border-radius:14px; padding:16px 20px;">
        <div style="position:relative; width:88px; height:88px; display:flex; align-items:center; justify-content:center;">
            <svg width="88" height="88" viewBox="0 0 100 100" style="transform: rotate(-90deg);">
                <circle cx="50" cy="50" r="{radius}" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="8"/>
                <circle cx="50" cy="50" r="{radius}" fill="none" stroke="{stroke_color}" stroke-width="8"
                        stroke-dasharray="{circumference}" stroke-dashoffset="{stroke_dashoffset}"
                        stroke-linecap="round" style="transition: stroke-dashoffset 0.8s ease;"/>
            </svg>
            <div style="position:absolute; text-align:center;">
                <div style="font-family:'Outfit',sans-serif; font-size:22px; font-weight:800; color:#FFFFFF; line-height:1;">{score:.0f}</div>
                <div style="font-size:9px; font-weight:700; color:#6C7A9C;">/ 100</div>
            </div>
        </div>
        <div>
            <div style="font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; color:#A2AECB; margin-bottom:4px;">{label}</div>
            <div style="font-size:16px; font-weight:700; color:{stroke_color}; margin-bottom:4px;">{badge_text}</div>
            <div style="font-size:12px; color:#B2B9D2;">Multimodal policy score evaluated across visual, audio, and text guardrails.</div>
        </div>
    </div>
    """
    st.markdown(svg, unsafe_allow_html=True)
