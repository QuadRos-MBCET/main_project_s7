"""
SafeAd AI - RiteFlow Dark SaaS Design System
Authentic SaaS aesthetic exactly matching the RiteFlow template:
- Deep navy-black canvas (#080B14) with luminous royal-indigo/violet radial glow halos (#4F46E5 / #6366F1)
- Geometric sans (Outfit & DM Sans) paired with elegant italic serif accent (Playfair Display)
- Outlined eyebrow pills, glossy white pill CTA, and solid electric-indigo action buttons
- Signature Browser Frame component (macOS window dots + URL pill + intense atmospheric back-glow)
- Segmented control navigation styled as centered pill links with active indigo gradient glow
- Compact stat cards (#0D1220) with progress bars, clean table rows, and real-time sparklines
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
    /* Background & Atmospheric Halos - Exact RiteFlow Midnight & Indigo */
    --rf-bg: #080B14;
    --rf-surface: #0D1220;
    --rf-surface-card: #101626;
    --rf-surface-elevated: #151D32;
    --rf-surface-glass: rgba(13, 18, 32, 0.85);
    --rf-surface-glass-border: rgba(99, 102, 241, 0.25);

    /* Electric Indigo Accent System (Exact RiteFlow Vibrancy) */
    --rf-indigo: #4F46E5;
    --rf-indigo-bright: #6366F1;
    --rf-indigo-hover: #4338CA;
    --rf-indigo-dark: #312E81;
    --rf-indigo-glow: rgba(79, 70, 229, 0.45);
    --rf-indigo-soft: rgba(79, 70, 229, 0.14);
    --rf-lavender: #C7D2FE;
    --rf-periwinkle: #A5B4FC;

    /* Text & Readability (WCAG AA Compliant) */
    --rf-text: #FFFFFF;
    --rf-text-secondary: #94A3B8;
    --rf-text-muted: #64748B;
    --rf-text-subtle: #475569;

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
    --rf-border-hover: rgba(99, 102, 241, 0.45);
    --rf-border-subtle: rgba(99, 102, 241, 0.22);
}

/* -------------------------------------------------------------------------
   2. GLOBAL CANVAS & EXACT RITEFLOW INDIGO/VIOLET RADIAL GLOW
   ------------------------------------------------------------------------- */
html, body, [data-testid="stAppViewContainer"], .main {
    background-color: var(--rf-bg) !important;
    background-image: 
        radial-gradient(ellipse 85% 55% at 50% 10%, rgba(79, 70, 229, 0.38) 0%, rgba(99, 102, 241, 0.16) 42%, transparent 75%),
        radial-gradient(circle at 50% 48%, rgba(67, 56, 202, 0.16) 0%, transparent 60%),
        radial-gradient(rgba(129, 140, 248, 0.08) 1px, transparent 1px) !important;
    background-size: 100% 100%, 100% 100%, 28px 28px !important;
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
   3. STREAMLIT INTERNALS & ANTI-FLICKER OVERRIDES
   ------------------------------------------------------------------------- */
div[data-stale="true"] {
    opacity: 0.96 !important;
    filter: none !important;
    transition: opacity 0.15s ease-in-out !important;
}

[data-testid="stStatusWidget"] {
    display: none !important;
}

[data-testid="stDecoration"] {
    display: none !important;
}

[data-testid="stHeader"] {
    background: rgba(8, 11, 20, 0.88) !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    border-bottom: 1px solid var(--rf-border) !important;
}

[data-testid="stSidebar"] {
    background-color: #0b0f1c !important;
    border-right: 1px solid var(--rf-border) !important;
}

[data-testid="stSidebar"] * {
    color: var(--rf-text) !important;
}

/* Accessible focus ring */
button:focus-visible, input:focus-visible, select:focus-visible, textarea:focus-visible {
    outline: 2px solid var(--rf-indigo-bright) !important;
    outline-offset: 2px !important;
}

/* -------------------------------------------------------------------------
   4. STREAMLIT SEGMENTED CONTROL (RITEFLOW CENTER PILL NAVIGATION)
   ------------------------------------------------------------------------- */
div[data-testid="stSegmentedControl"] {
    background: rgba(13, 18, 32, 0.85) !important;
    border: 1px solid rgba(99, 102, 241, 0.25) !important;
    border-radius: 9999px !important;
    padding: 3px !important;
    display: inline-flex !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4), 0 0 20px rgba(79, 70, 229, 0.12) !important;
}

div[data-testid="stSegmentedControl"] button {
    border-radius: 9999px !important;
    border: none !important;
    color: #94A3B8 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    padding: 6px 18px !important;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
    background: transparent !important;
}

div[data-testid="stSegmentedControl"] button:hover {
    color: #FFFFFF !important;
    background: rgba(255, 255, 255, 0.05) !important;
}

div[data-testid="stSegmentedControl"] button[aria-checked="true"],
div[data-testid="stSegmentedControl"] button[data-selected="true"],
div[data-testid="stSegmentedControl"] button[aria-pressed="true"] {
    background: linear-gradient(135deg, #4F46E5 0%, #6366F1 100%) !important;
    color: #FFFFFF !important;
    font-weight: 700 !important;
    box-shadow: 0 0 16px rgba(79, 70, 229, 0.55), 0 2px 6px rgba(0, 0, 0, 0.3) !important;
}

/* -------------------------------------------------------------------------
   5. RITEFLOW TYPOGRAPHY
   ------------------------------------------------------------------------- */
h1, h2, h3, h4, .rf-heading {
    font-family: 'Outfit', sans-serif !important;
    color: #FFFFFF !important;
    letter-spacing: -0.02em;
}

.rf-hero-title {
    font-family: 'Outfit', sans-serif !important;
    font-size: 58px;
    font-weight: 700;
    line-height: 1.15;
    letter-spacing: -0.035em;
    color: #FFFFFF;
    text-align: center;
    margin: 16px 0 20px 0;
}

.rf-hero-subtitle-gradient {
    background: linear-gradient(180deg, #FFFFFF 40%, #C7D2FE 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    display: inline-block;
}

.rf-italic-serif {
    font-family: 'Playfair Display', 'Instrument Serif', Georgia, serif !important;
    font-style: italic !important;
    font-weight: 400 !important;
    background: linear-gradient(135deg, #C7D2FE 0%, #A5B4FC 45%, #E0E7FF 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: 0 0 30px rgba(165, 180, 252, 0.4);
    letter-spacing: normal;
    padding: 0 4px;
}

.rf-hero-desc, .rf-hero-subtitle {
    font-size: 16px;
    line-height: 1.6;
    color: var(--rf-text-secondary);
    text-align: center;
    max-width: 680px;
    margin: 0 auto 28px auto;
}

.rf-eyebrow-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(79, 70, 229, 0.14);
    border: 1px solid rgba(129, 140, 248, 0.38);
    color: #C7D2FE;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 5px 18px;
    border-radius: 9999px;
    box-shadow: 0 0 16px rgba(79, 70, 229, 0.2);
}

/* -------------------------------------------------------------------------
   6. RITEFLOW BROWSER FRAME COMPONENT (SIGNATURE VIOLET HALO)
   ------------------------------------------------------------------------- */
.rf-browser-frame {
    background: #080B14;
    border: 1px solid rgba(99, 102, 241, 0.3);
    border-radius: 20px;
    overflow: hidden;
    box-shadow: 
        0 0 70px rgba(79, 70, 229, 0.32),
        0 0 130px rgba(99, 102, 241, 0.16),
        0 30px 60px rgba(0, 0, 0, 0.85);
    margin: 28px 0;
    position: relative;
}

.rf-browser-header {
    background: #0B0F1C;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    padding: 12px 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.rf-browser-dots, .rf-window-dots {
    display: flex;
    gap: 7px;
}

.rf-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    display: inline-block;
}
.rf-dot.red, .rf-dot-red { background: #FF5F56; }
.rf-dot.yellow, .rf-dot-yellow { background: #FFBD2E; }
.rf-dot.green, .rf-dot-green { background: #27C93F; }

.rf-browser-url, .rf-url-pill {
    background: rgba(13, 18, 32, 0.85);
    border: 1px solid rgba(99, 102, 241, 0.2);
    border-radius: 9999px;
    padding: 4px 22px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: #94A3B8;
}

.rf-browser-body {
    padding: 26px;
    background: #080B14;
}

/* -------------------------------------------------------------------------
   7. RITEFLOW STAT CARDS, REVENUE SUMMARY TABLES & CHECKLISTS
   ------------------------------------------------------------------------- */
.rf-stat-card {
    background: #0D1220;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 18px 20px;
    margin-bottom: 14px;
    position: relative;
    overflow: hidden;
    transition: all 0.25s ease;
}
.rf-stat-card:hover {
    border-color: rgba(99, 102, 241, 0.35);
    box-shadow: 0 4px 24px rgba(79, 70, 229, 0.15);
}

.rf-card {
    background: #0D1220;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 24px 26px;
    transition: all 0.25s ease;
}
.rf-card:hover {
    border-color: rgba(99, 102, 241, 0.4);
    box-shadow: 0 0 30px rgba(79, 70, 229, 0.16);
}

.rf-stat-label {
    font-size: 11px;
    font-weight: 700;
    color: var(--rf-text-muted);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 6px;
}

.rf-stat-number, .rf-stat-value {
    font-family: 'Outfit', sans-serif;
    font-size: 28px;
    font-weight: 700;
    color: #FFFFFF;
    line-height: 1.2;
}

.rf-stat-delta {
    display: inline-flex;
    align-items: center;
    gap: 3px;
    font-size: 11px;
    font-weight: 700;
    color: var(--rf-green-delta);
    background: var(--rf-green-bg);
    border-radius: 9999px;
    padding: 2px 8px;
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
    box-shadow: 0 0 8px rgba(79, 70, 229, 0.5);
}

/* -------------------------------------------------------------------------
   8. BUTTONS (WHITE GLOSSY HERO CTA, INDIGO PILL, GLASS OUTLINE)
   ------------------------------------------------------------------------- */
.rf-btn-white {
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    background: #FFFFFF !important;
    color: #080B14 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    font-weight: 700 !important;
    padding: 10px 26px !important;
    border-radius: 9999px !important;
    border: none !important;
    cursor: pointer !important;
    box-shadow: 0 0 24px rgba(255, 255, 255, 0.3), 0 4px 14px rgba(0, 0, 0, 0.4) !important;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
    text-decoration: none !important;
}
.rf-btn-white:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 0 32px rgba(255, 255, 255, 0.5), 0 6px 18px rgba(0, 0, 0, 0.5) !important;
    color: #080B14 !important;
}

.rf-btn-indigo {
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    background: linear-gradient(135deg, #4F46E5 0%, #6366F1 100%) !important;
    color: #FFFFFF !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    font-weight: 700 !important;
    padding: 10px 24px !important;
    border-radius: 9999px !important;
    border: none !important;
    cursor: pointer !important;
    box-shadow: 0 0 20px rgba(79, 70, 229, 0.45) !important;
    transition: all 0.2s ease !important;
    text-decoration: none !important;
}
.rf-btn-indigo:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 0 26px rgba(79, 70, 229, 0.65) !important;
}

.rf-btn-secondary {
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    background: rgba(13, 18, 32, 0.8) !important;
    border: 1px solid rgba(99, 102, 241, 0.3) !important;
    color: #C7D2FE !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    padding: 10px 22px !important;
    border-radius: 9999px !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
}
.rf-btn-secondary:hover {
    border-color: #6366F1 !important;
    color: #FFFFFF !important;
    box-shadow: 0 0 16px rgba(79, 70, 229, 0.25) !important;
}

/* Streamlit Button Native Overrides */
div.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #4F46E5 0%, #6366F1 100%) !important;
    color: #FFFFFF !important;
    border: none !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 700 !important;
    border-radius: 9999px !important;
    padding: 10px 24px !important;
    box-shadow: 0 4px 18px rgba(79, 70, 229, 0.45) !important;
    transition: all 0.2s ease !important;
}
div.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 24px rgba(79, 70, 229, 0.65) !important;
}

div.stButton > button[kind="secondary"] {
    background: rgba(13, 18, 32, 0.7) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    color: var(--rf-text) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    border-radius: 9999px !important;
    transition: all 0.2s ease !important;
}
div.stButton > button[kind="secondary"]:hover {
    border-color: rgba(99, 102, 241, 0.45) !important;
    color: #C7D2FE !important;
    background: rgba(79, 70, 229, 0.12) !important;
}

/* -------------------------------------------------------------------------
   9. DUAL-ENCODED VERDICT & STATUS BADGES (ICON + TEXT + TINT)
   ------------------------------------------------------------------------- */
.rf-badge-safe, .badge-safe, .badge-approve {
    background-color: var(--rf-green-bg);
    border: 1px solid var(--rf-green-delta);
    color: var(--rf-green-delta);
    padding: 8px 16px;
    border-radius: 9999px;
    font-size: 13px;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    gap: 7px;
}

.rf-badge-danger, .badge-danger, .badge-reject {
    background-color: var(--rf-red-bg);
    border: 1px solid var(--rf-red-danger);
    color: var(--rf-red-danger);
    padding: 8px 16px;
    border-radius: 9999px;
    font-size: 13px;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    gap: 7px;
}

.rf-badge-warning, .badge-warning, .badge-18 {
    background-color: var(--rf-amber-bg);
    border: 1px solid var(--rf-amber-warning);
    color: var(--rf-amber-warning);
    padding: 8px 16px;
    border-radius: 9999px;
    font-size: 13px;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    gap: 7px;
}

.rf-badge-hitl, .badge-hitl {
    background-color: var(--rf-indigo-soft);
    border: 1px solid var(--rf-indigo);
    color: #C7D2FE;
    padding: 8px 16px;
    border-radius: 9999px;
    font-size: 13px;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    gap: 7px;
}

.badge-14 {
    background-color: var(--rf-blue-bg);
    border: 1px solid var(--rf-blue-info);
    color: var(--rf-blue-info);
    padding: 8px 16px;
    border-radius: 9999px;
    font-size: 13px;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    gap: 7px;
}

/* -------------------------------------------------------------------------
   10. RESPONSIVE BREAKPOINTS
   ------------------------------------------------------------------------- */
@media (max-width: 768px) {
    .block-container {
        padding-top: 3.5rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    .rf-hero-title {
        font-size: 34px !important;
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

def render_html(html_str: str, *args, **kwargs):
    """Safely renders HTML without Markdown interpreting indented lines as code blocks."""
    cleaned = "\n".join(line.strip() for line in str(html_str).splitlines() if line.strip())
    st.markdown(cleaned, unsafe_allow_html=True)

# Aliases for backwards compatibility
inject_instagram_styles = inject_safead_styles

def render_safead_brand(subtitle: str = "DECISION ENGINE"):
    """Renders the RiteFlow-styled brand mark with gradient wave icon."""
    html = f"""
    <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:18px; padding:0 2px;">
        <div style="display:flex; align-items:center; gap:12px;">
            <div style="width:28px; height:28px; border-radius:8px; background:linear-gradient(135deg, #4F46E5 0%, #818CF8 100%); display:flex; align-items:center; justify-content:center; box-shadow:0 0 14px rgba(79,70,229,0.5);">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2.5" stroke-linecap="round"><path d="M2 12h4l3-9 4 18 3-9h6"/></svg>
            </div>
            <div style="font-family:'Outfit', sans-serif; font-size:22px; font-weight:800; letter-spacing:-0.03em; color:#FFFFFF;">
                Safe<span style="color:#A5B4FC;">Ad</span>
            </div>
            <div style="background:rgba(79, 70, 229, 0.15); border:1px solid rgba(129, 140, 248, 0.4); color:#C7D2FE; font-size:9px; font-weight:800; padding:2px 9px; border-radius:9999px; letter-spacing:0.1em; text-transform:uppercase;">
                {subtitle}
            </div>
        </div>
        <div style="display:flex; align-items:center; gap:8px; font-size:12px; color:#94A3B8;">
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
        "arrow_right": f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>''',
        "alert": f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>'''
    }
    return icons.get(name, "")

def render_sparkline(data: list, width: int = 180, height: int = 36, color: str = "#6366F1") -> str:
    """Renders a smooth SVG sparkline with gradient fill area."""
    if not data or len(data) < 2:
        return ""
    min_v = min(data)
    max_v = max(data)
    rng = max(1e-5, max_v - min_v)
    
    step_x = width / (len(data) - 1)
    pts = []
    for i, v in enumerate(data):
        x = i * step_x
        y = height - ((v - min_v) / rng) * (height - 8) - 4
        pts.append((x, y))
        
    line_d = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    area_d = f"{line_d} L {width:.1f},{height:.1f} L 0,{height:.1f} Z"
    
    return f'''
    <svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" style="overflow: visible;">
        <defs>
            <linearGradient id="sparkGrad_{id(data)}" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="{color}" stop-opacity="0.38"/>
                <stop offset="100%" stop-color="{color}" stop-opacity="0.0"/>
            </linearGradient>
        </defs>
        <path d="{area_d}" fill="url(#sparkGrad_{id(data)})"/>
        <path d="{line_d}" fill="none" stroke="{color}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
        <circle cx="{pts[-1][0]:.1f}" cy="{pts[-1][1]:.1f}" r="3.5" fill="{color}" filter="drop-shadow(0 0 6px {color})"/>
    </svg>
    '''

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
    <div style="display:flex; align-items:center; gap:20px; background:#0D1220; border:1px solid var(--rf-border); border-radius:14px; padding:16px 20px;">
        <div style="position:relative; width:88px; height:88px; display:flex; align-items:center; justify-content:center;">
            <svg width="88" height="88" viewBox="0 0 100 100" style="transform: rotate(-90deg);">
                <circle cx="50" cy="50" r="{radius}" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="8"/>
                <circle cx="50" cy="50" r="{radius}" fill="none" stroke="{stroke_color}" stroke-width="8"
                        stroke-dasharray="{circumference}" stroke-dashoffset="{stroke_dashoffset}"
                        stroke-linecap="round" style="transition: stroke-dashoffset 0.8s ease;"/>
            </svg>
            <div style="position:absolute; text-align:center;">
                <div style="font-family:'Outfit',sans-serif; font-size:22px; font-weight:800; color:#FFFFFF; line-height:1;">{score:.0f}</div>
                <div style="font-size:9px; font-weight:700; color:#64748B;">/ 100</div>
            </div>
        </div>
        <div>
            <div style="font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; color:#94A3B8; margin-bottom:4px;">{label}</div>
            <div style="font-size:16px; font-weight:700; color:{stroke_color}; margin-bottom:4px;">{badge_text}</div>
            <div style="font-size:12px; color:#94A3B8;">Multimodal policy score evaluated across visual, audio, and text guardrails.</div>
        </div>
    </div>
    """
    st.markdown(svg, unsafe_allow_html=True)
