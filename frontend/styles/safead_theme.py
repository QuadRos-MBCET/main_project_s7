"""
SafeAd AI - Quantexa-Inspired Enterprise Design System
Modern, high-trust Decision Intelligence aesthetic:
- Deep indigo/near-black purple canvas (#0D0819, #230F3E)
- Mint/Teal key accents (#2DE2C0) for maximum decision clarity
- Frosted glass cards, translucent borders, and soft glows
- Grotesk typography (Manrope & Inter Tight) with letter-spaced eyebrows
- Smooth role-switching and Streamlit internal flicker elimination
"""

import streamlit as st

SAFEAD_CSS = """
<style>
/* -------------------------------------------------------------------------
   1. TYPOGRAPHY & COLOR TOKENS (Google Fonts)
   ------------------------------------------------------------------------- */
@import url('https://fonts.googleapis.com/css2?family=Inter+Tight:wght@300;400;500;600;700&family=Manrope:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    /* Canvas & Surfaces */
    --safead-bg: #0D0819;
    --safead-hero: #230F3E;
    --safead-surface: #170D2B;
    --safead-surface-card: rgba(28, 17, 51, 0.68);
    --safead-surface-card-hover: rgba(38, 23, 69, 0.82);
    --safead-surface-elevated: rgba(43, 26, 77, 0.88);
    
    /* Translucent Borders & Subtle Glows */
    --safead-border: rgba(168, 147, 217, 0.16);
    --safead-border-bright: rgba(168, 147, 217, 0.32);
    --safead-border-glow: rgba(45, 226, 192, 0.45);
    --safead-glass-specular: rgba(255, 255, 255, 0.08);

    /* Text & Readability (WCAG AA Compliant) */
    --safead-text: #F8F6FC;
    --safead-text-secondary: #C2BAD8;
    --safead-text-muted: #8E83AA;
    --safead-eyebrow: #A493C2;

    /* Brand Accents */
    --safead-mint: #2DE2C0;
    --safead-mint-hover: #24C8A9;
    --safead-mint-glow: rgba(45, 226, 192, 0.22);
    --safead-purple-primary: #7938DF;
    --safead-purple-deep: #3B1A6B;
    --safead-purple-glow: rgba(121, 56, 223, 0.25);
    --safead-topbar-gradient: linear-gradient(90deg, #3B1A6B 0%, #210D40 50%, #125B5A 100%);

    /* Decision & Policy Status System (Dual-Encoded) */
    --safead-safe: #10B981;
    --safead-safe-bg: rgba(16, 185, 129, 0.14);
    --safead-warning: #F59E0B;
    --safead-warning-bg: rgba(245, 158, 11, 0.14);
    --safead-hitl: #8B5CF6;
    --safead-hitl-bg: rgba(139, 92, 246, 0.16);
    --safead-danger: #F43F5E;
    --safead-danger-bg: rgba(244, 63, 94, 0.16);
}

/* -------------------------------------------------------------------------
   2. GLOBAL RESET & BASE TYPOGRAPHY
   ------------------------------------------------------------------------- */
html, body, [data-testid="stAppViewContainer"], .main {
    background-color: var(--safead-bg) !important;
    background-image: 
        radial-gradient(circle at 15% 15%, rgba(59, 26, 107, 0.35) 0%, transparent 45%),
        radial-gradient(circle at 85% 30%, rgba(18, 91, 90, 0.22) 0%, transparent 40%),
        radial-gradient(circle at 50% 85%, rgba(35, 15, 62, 0.3) 0%, transparent 50%) !important;
    background-attachment: fixed !important;
    color: var(--safead-text) !important;
    font-family: 'Manrope', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    -webkit-font-smoothing: antialiased;
}

/* Fix header clipping: give .block-container generous padding below fixed top header */
.block-container {
    max-width: 1240px !important;
    padding-top: 4.5rem !important;
    padding-bottom: 5rem !important;
    min-height: 85vh !important;
    animation: safeadFadeReveal 0.35s cubic-bezier(0.16, 1, 0.3, 1) !important;
}

@keyframes safeadFadeReveal {
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
   3. STREAMLIT INTERNALS & ANTI-FLICKER OVERRIDES (COMMENTED AS REQUIRED)
   ------------------------------------------------------------------------- */

/* [data-stale="true"]: Streamlit default dims out unmounted or rerunning widgets to 33% opacity.
   We override this to 95% opacity so role switches cross-fade smoothly without screen flashing grey. */
div[data-stale="true"] {
    opacity: 0.95 !important;
    filter: none !important;
    transition: opacity 0.15s ease-in-out !important;
}

/* [data-testid="stStatusWidget"]: Streamlit top-right running animation/icon.
   Hidden to prevent jarring layout reflows during fast state switches. */
[data-testid="stStatusWidget"] {
    display: none !important;
}

/* [data-testid="stDecoration"]: Streamlit top rainbow gradient line.
   Hidden to maintain a clean, high-trust enterprise header bar. */
[data-testid="stDecoration"] {
    display: none !important;
}

/* [data-testid="stHeader"]: Streamlit top navigation bar.
   Given subtle translucent background with blur and 1px border. */
[data-testid="stHeader"] {
    background: rgba(13, 8, 25, 0.85) !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    border-bottom: 1px solid var(--safead-border) !important;
}

/* [data-testid="stSidebar"]: Streamlit left drawer. */
[data-testid="stSidebar"] {
    background-color: #0b0716 !important;
    border-right: 1px solid var(--safead-border) !important;
}

[data-testid="stSidebar"] * {
    color: var(--safead-text) !important;
}

/* Accessible focus outline */
button:focus-visible, input:focus-visible, select:focus-visible, textarea:focus-visible {
    outline: 2px solid var(--safead-mint) !important;
    outline-offset: 2px !important;
}

/* -------------------------------------------------------------------------
   4. QUANTEXA ENTERPRISE CARDS & SURFACES
   ------------------------------------------------------------------------- */
.safead-card {
    background: var(--safead-surface-card);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid var(--safead-border);
    border-radius: 18px;
    padding: 24px;
    margin-bottom: 18px;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    position: relative;
    overflow: hidden;
}

.safead-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent 0%, var(--safead-glass-specular) 50%, transparent 100%);
}

.safead-card:hover {
    border-color: var(--safead-border-bright);
    background: var(--safead-surface-card-hover);
    transform: translateY(-2px);
    box-shadow: 0 12px 36px 0 rgba(0, 0, 0, 0.45);
}

.safead-hero-card {
    background: linear-gradient(135deg, rgba(35, 15, 62, 0.85) 0%, rgba(18, 9, 36, 0.95) 100%);
    border: 1px solid rgba(168, 147, 217, 0.22);
    border-radius: 20px;
    padding: 32px 36px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}

.safead-hero-card::after {
    content: '';
    position: absolute;
    bottom: -60px;
    right: -60px;
    width: 220px;
    height: 220px;
    background: radial-gradient(circle, var(--safead-mint-glow) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
}

/* Eyebrow Label */
.safead-eyebrow {
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.16em;
    color: var(--safead-eyebrow);
    margin-bottom: 8px;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}

/* Grotesk Headlines */
.safead-title {
    font-size: 32px;
    font-weight: 400;
    letter-spacing: -0.02em;
    line-height: 1.25;
    color: #FFFFFF;
    margin-top: 0;
    margin-bottom: 12px;
}

.safead-title-large {
    font-size: 44px;
    font-weight: 300;
    letter-spacing: -0.03em;
    line-height: 1.18;
    color: #FFFFFF;
}

.safead-highlight {
    color: var(--safead-mint) !important;
    font-weight: 600;
}

.safead-subtitle {
    font-size: 15px;
    font-weight: 400;
    line-height: 1.6;
    color: var(--safead-text-secondary);
    margin-bottom: 20px;
}

/* -------------------------------------------------------------------------
   5. BUTTON & LINK STYLES
   ------------------------------------------------------------------------- */
/* Primary White Pill Button (Like Quantexa 'See our Platform') */
.safead-btn-primary {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: #FFFFFF !important;
    color: #0D0819 !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    padding: 10px 24px !important;
    border-radius: 9999px !important;
    text-decoration: none !important;
    border: none !important;
    cursor: pointer;
    box-shadow: 0 4px 14px rgba(255, 255, 255, 0.15);
    transition: all 0.2s ease;
}

.safead-btn-primary:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(255, 255, 255, 0.25);
    opacity: 0.95;
}

/* Teal Action Pill Button */
.safead-btn-mint {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #2DE2C0 0%, #1BAE93 100%) !important;
    color: #06231D !important;
    font-size: 14px !important;
    font-weight: 700 !important;
    padding: 10px 24px !important;
    border-radius: 9999px !important;
    border: none !important;
    cursor: pointer;
    box-shadow: 0 4px 16px rgba(45, 226, 192, 0.28);
    transition: all 0.2s ease;
}

.safead-btn-mint:hover {
    background: linear-gradient(135deg, #37ECC9 0%, #20C2A4 100%) !important;
    transform: translateY(-1px);
    box-shadow: 0 6px 22px rgba(45, 226, 192, 0.4);
}

/* Secondary Glass Outline Pill */
.safead-btn-glass {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: rgba(255, 255, 255, 0.05) !important;
    color: var(--safead-text) !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    padding: 9px 22px !important;
    border-radius: 9999px !important;
    border: 1px solid rgba(255, 255, 255, 0.18) !important;
    cursor: pointer;
    transition: all 0.2s ease;
}

.safead-btn-glass:hover {
    border-color: var(--safead-mint) !important;
    color: var(--safead-mint) !important;
    background: rgba(45, 226, 192, 0.08) !important;
}

/* Tertiary Link ('LEARN MORE ->' style) */
.safead-link-more {
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    color: #9D62F3;
    display: inline-flex;
    align-items: center;
    gap: 4px;
    text-decoration: none;
    transition: all 0.2s ease;
    cursor: pointer;
}

.safead-link-more:hover {
    color: var(--safead-mint);
    transform: translateX(2px);
}

/* Streamlit Native Primary / Secondary Button Overrides */
div.stButton > button[kind="primary"] {
    background: #FFFFFF !important;
    color: #0D0819 !important;
    border: none !important;
    font-weight: 600 !important;
    border-radius: 9999px !important;
    padding: 10px 24px !important;
    transition: all 0.2s ease !important;
}
div.stButton > button[kind="primary"]:hover {
    box-shadow: 0 4px 20px rgba(255, 255, 255, 0.25) !important;
    transform: translateY(-1px) !important;
}

div.stButton > button[kind="secondary"] {
    background: rgba(28, 17, 51, 0.6) !important;
    border: 1px solid var(--safead-border) !important;
    color: var(--safead-text) !important;
    font-weight: 500 !important;
    border-radius: 9999px !important;
    transition: all 0.2s ease !important;
}
div.stButton > button[kind="secondary"]:hover {
    border-color: var(--safead-mint) !important;
    color: var(--safead-mint) !important;
}

/* Native Streamlit Tabs Styling */
div[data-baseweb="tab-list"] {
    background-color: rgba(23, 13, 43, 0.5) !important;
    border-bottom: 1px solid var(--safead-border) !important;
    gap: 8px !important;
    padding: 4px 6px !important;
    border-radius: 12px !important;
}

button[data-baseweb="tab"] {
    color: var(--safead-text-secondary) !important;
    font-weight: 500 !important;
    border-radius: 8px !important;
    padding: 8px 18px !important;
    border: none !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    background-color: var(--safead-surface-elevated) !important;
    color: #FFFFFF !important;
    font-weight: 700 !important;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3) !important;
}

/* Native Streamlit Text Inputs */
div[data-baseweb="input"] {
    background-color: rgba(18, 10, 34, 0.75) !important;
    border: 1px solid var(--safead-border) !important;
    border-radius: 10px !important;
    color: var(--safead-text) !important;
}

div[data-baseweb="input"]:focus-within {
    border-color: var(--safead-mint) !important;
    box-shadow: 0 0 0 1px var(--safead-mint) !important;
}

/* -------------------------------------------------------------------------
   6. DUAL-ENCODED VERDICT & STATUS BADGES (ICON + TEXT + TINT)
   ------------------------------------------------------------------------- */
.badge-safe {
    background-color: var(--safead-safe-bg);
    border: 1px solid var(--safead-safe);
    color: var(--safead-safe);
    padding: 10px 18px;
    border-radius: 10px;
    font-size: 16px;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 14px;
}

.badge-warning {
    background-color: var(--safead-warning-bg);
    border: 1px solid var(--safead-warning);
    color: var(--safead-warning);
    padding: 10px 18px;
    border-radius: 10px;
    font-size: 16px;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 14px;
}

.badge-hitl {
    background-color: var(--safead-hitl-bg);
    border: 1px solid var(--safead-hitl);
    color: var(--safead-hitl);
    padding: 10px 18px;
    border-radius: 10px;
    font-size: 16px;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 14px;
}

.badge-danger, .badge-reject {
    background-color: var(--safead-danger-bg);
    border: 1px solid var(--safead-danger);
    color: var(--safead-danger);
    padding: 10px 18px;
    border-radius: 10px;
    font-size: 16px;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 14px;
}

/* Backward compatibility classes for existing workspace views */
.badge-18 {
    background-color: var(--safead-warning-bg);
    border: 1px solid var(--safead-warning);
    color: var(--safead-warning);
    padding: 10px 18px;
    border-radius: 10px;
    font-size: 16px;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 14px;
}

.badge-14 {
    background-color: rgba(59, 130, 246, 0.16);
    border: 1px solid #3B82F6;
    color: #60A5FA;
    padding: 10px 18px;
    border-radius: 10px;
    font-size: 16px;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 14px;
}

.badge-approve {
    background-color: var(--safead-safe-bg);
    border: 1px solid var(--safead-safe);
    color: var(--safead-safe);
    padding: 10px 18px;
    border-radius: 10px;
    font-size: 16px;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 14px;
}

/* -------------------------------------------------------------------------
   7. STEPPER & KYC INDICATORS
   ------------------------------------------------------------------------- */
.safead-stepper {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: var(--safead-surface-card);
    border: 1px solid var(--safead-border);
    border-radius: 14px;
    padding: 14px 20px;
    margin-bottom: 22px;
}

.safead-step {
    display: flex;
    align-items: center;
    gap: 10px;
    color: var(--safead-text-muted);
    font-size: 13px;
    font-weight: 600;
}

.safead-step.active {
    color: var(--safead-mint);
}

.safead-step.completed {
    color: #FFFFFF;
}

.safead-step-number {
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

.safead-step.active .safead-step-number {
    background: var(--safead-mint);
    color: #072620;
}

.safead-step.completed .safead-step-number {
    background: var(--safead-purple-primary);
    color: #FFFFFF;
}

.safead-step-divider {
    flex: 1;
    height: 1px;
    background: var(--safead-border);
    margin: 0 16px;
}

/* -------------------------------------------------------------------------
   8. RESPONSIVE BREAKPOINTS & ACCESSIBILITY
   ------------------------------------------------------------------------- */
@media (max-width: 768px) {
    .block-container {
        padding-top: 3.5rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    .safead-title-large {
        font-size: 28px !important;
    }
    .safead-title {
        font-size: 22px !important;
    }
    .safead-stepper {
        flex-direction: column;
        align-items: flex-start;
        gap: 12px;
    }
    .safead-step-divider {
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
    """Injects the core Quantexa-inspired enterprise design system."""
    st.markdown(SAFEAD_CSS, unsafe_allow_html=True)

# Aliases for backwards compatibility with any existing imports
inject_instagram_styles = inject_safead_styles

def render_safead_brand(subtitle: str = "TRUST & SAFETY INTELLIGENCE"):
    """Renders the clean enterprise SafeAd wordmark with status badge."""
    html = f"""
    <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:18px; padding:0 2px;">
        <div style="display:flex; align-items:center; gap:12px;">
            <div style="font-family:'Manrope', sans-serif; font-size:24px; font-weight:800; letter-spacing:-0.03em; color:#FFFFFF;">
                Safe<span style="color:#2DE2C0;">Ad</span>
            </div>
            <div style="background:rgba(45, 226, 192, 0.12); border:1px solid rgba(45, 226, 192, 0.35); color:#2DE2C0; font-size:10px; font-weight:800; padding:2px 8px; border-radius:5px; letter-spacing:0.12em; text-transform:uppercase;">
                {subtitle}
            </div>
        </div>
        <div style="display:flex; align-items:center; gap:14px; font-size:12px; color:#A493C2;">
            <span style="display:inline-flex; align-items:center; gap:5px;">
                <span style="width:7px; height:7px; border-radius:50%; background:#2DE2C0; display:inline-block; box-shadow:0 0 8px #2DE2C0;"></span>
                Systems Operational
            </span>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

render_instagram_logo = render_safead_brand

def render_stories_bar():
    """Clean enterprise no-op replacing legacy Instagram story tray."""
    return

def render_svg_icon(name: str, size: int = 20, color: str = "currentColor") -> str:
    """Returns SVG line icons matching Quantexa minimalist icon style."""
    icons = {
        "shield": f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>''',
        "eye": f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>''',
        "user": f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>''',
        "briefcase": f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>''',
        "check": f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>''',
        "alert": f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>''',
        "x": f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>''',
        "upload": f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>''',
        "camera": f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg>''',
        "cpu": f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2" ry="2"/><rect x="9" y="9" width="6" height="6"/><line x1="9" y1="1" x2="9" y2="4"/><line x1="15" y1="1" x2="15" y2="4"/><line x1="9" y1="20" x2="9" y2="23"/><line x1="15" y1="20" x2="15" y2="23"/><line x1="20" y1="9" x2="23" y2="9"/><line x1="20" y1="14" x2="23" y2="14"/><line x1="1" y1="9" x2="4" y2="9"/><line x1="1" y1="14" x2="4" y2="14"/></svg>'''
    }
    return icons.get(name, "")

def render_risk_gauge(score: float, label: str = "Risk Score"):
    """Renders a sleek Quantexa circular SVG risk score gauge (0-100%)."""
    score = max(0.0, min(100.0, float(score or 0.0)))
    radius = 36
    circumference = 2 * 3.14159 * radius
    stroke_dashoffset = circumference - (score / 100.0) * circumference
    
    if score < 35.0:
        stroke_color = "#10B981"  # Mint/Green
        badge_text = "LOW RISK"
    elif score < 70.0:
        stroke_color = "#F59E0B"  # Amber
        badge_text = "MODERATE RISK"
    else:
        stroke_color = "#F43F5E"  # Rose
        badge_text = "HIGH RISK"

    svg = f"""
    <div style="display:flex; align-items:center; gap:20px; background:rgba(23,13,43,0.5); border:1px solid var(--safead-border); border-radius:14px; padding:16px 20px;">
        <div style="position:relative; width:90px; height:90px; display:flex; align-items:center; justify-content:center;">
            <svg width="90" height="90" viewBox="0 0 100 100" style="transform: rotate(-90deg);">
                <circle cx="50" cy="50" r="{radius}" fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="8"/>
                <circle cx="50" cy="50" r="{radius}" fill="none" stroke="{stroke_color}" stroke-width="8"
                        stroke-dasharray="{circumference}" stroke-dashoffset="{stroke_dashoffset}"
                        stroke-linecap="round" style="transition: stroke-dashoffset 0.8s ease;"/>
            </svg>
            <div style="position:absolute; text-align:center;">
                <div style="font-size:20px; font-weight:800; color:#FFFFFF; line-height:1;">{score:.0f}</div>
                <div style="font-size:9px; font-weight:700; color:#8E83AA;">/ 100</div>
            </div>
        </div>
        <div>
            <div style="font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:0.12em; color:#A493C2; margin-bottom:4px;">{label}</div>
            <div style="font-size:16px; font-weight:700; color:{stroke_color}; margin-bottom:4px;">{badge_text}</div>
            <div style="font-size:12px; color:#C2BAD8;">Evaluated across multimodal visual, audio, and text guardrails.</div>
        </div>
    </div>
    """
    st.markdown(svg, unsafe_allow_html=True)
