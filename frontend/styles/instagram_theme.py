"""
SafeAd AI - Instagram Design System & Phone-Responsive Styles
Provides authentic Instagram dark/clean aesthetic, mobile viewport optimizations,
and reusable UI elements (Stories, Reels Action Rail, Verified Badges, Bottom Nav).
"""

import streamlit as st

INSTAGRAM_CSS = """
<style>
/* -------------------------------------------------------------------------
   1. GLOBAL RESET & INSTAGRAM DARK AESTHETIC
   ------------------------------------------------------------------------- */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Grand+Hotel&display=swap');

:root {
    --ig-bg: #000000;
    --ig-surface: #121212;
    --ig-surface-card: #181818;
    --ig-surface-elevated: #242424;
    --ig-border: #262626;
    --ig-border-subtle: #1f1f1f;
    --ig-text: #f5f5f5;
    --ig-text-secondary: #a8a8a8;
    --ig-text-muted: #737373;
    --ig-blue: #0095f6;
    --ig-blue-hover: #1877f2;
    --ig-red: #ff3040;
    --ig-green: #00c950;
    --ig-gradient: linear-gradient(45deg, #f09433 0%, #e6683c 25%, #dc2743 50%, #cc2366 75%, #bc1888 100%);
    --ig-gradient-story: linear-gradient(45deg, #f09433, #dc2743, #bc1888);
}

/* App Background & Base Typography */
html, body, [data-testid="stAppViewContainer"], .main {
    background-color: var(--ig-bg) !important;
    color: var(--ig-text) !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
    -webkit-font-smoothing: antialiased;
}

[data-testid="stHeader"] {
    background: rgba(0, 0, 0, 0.75) !important;
    backdrop-filter: blur(12px) !important;
    border-bottom: 1px solid var(--ig-border);
}

[data-testid="stSidebar"] {
    background-color: #0a0a0a !important;
    border-right: 1px solid var(--ig-border) !important;
}

[data-testid="stSidebar"] * {
    color: var(--ig-text) !important;
}

/* Container Padding & Max Width */
.block-container {
    max-width: 980px !important;
    padding-top: 1rem !important;
    padding-bottom: 5rem !important;
}

/* Headings & Text */
h1, h2, h3, h4, h5, h6, p, span, label {
    color: var(--ig-text) !important;
}

/* Instagram Logo Styling */
.ig-logo {
    font-family: 'Grand Hotel', cursive, -apple-system, sans-serif;
    font-size: 34px;
    font-weight: 500;
    letter-spacing: 0.5px;
    background: var(--ig-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    display: inline-block;
    line-height: 1.2;
}

.ig-logo-badge {
    display: inline-flex;
    align-items: center;
    background: rgba(0, 149, 246, 0.15);
    border: 1px solid rgba(0, 149, 246, 0.4);
    color: var(--ig-blue) !important;
    font-family: -apple-system, BlinkMacSystemFont, sans-serif;
    font-size: 11px;
    font-weight: 700;
    padding: 2px 7px;
    border-radius: 6px;
    vertical-align: middle;
    margin-left: 8px;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    -webkit-text-fill-color: var(--ig-blue) !important;
}

/* -------------------------------------------------------------------------
   2. INSTAGRAM STORIES CAROUSEL
   ------------------------------------------------------------------------- */
.stories-container {
    display: flex;
    gap: 16px;
    overflow-x: auto;
    padding: 12px 6px 16px 6px;
    margin-bottom: 20px;
    border-bottom: 1px solid var(--ig-border);
    scrollbar-width: none; /* Firefox */
}
.stories-container::-webkit-scrollbar {
    display: none; /* Chrome/Safari */
}

.story-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
    cursor: pointer;
    flex-shrink: 0;
    width: 68px;
    transition: transform 0.2s ease;
}
.story-item:hover {
    transform: scale(1.05);
}

.story-ring {
    width: 62px;
    height: 62px;
    border-radius: 50%;
    padding: 2.5px;
    background: var(--ig-gradient-story);
    display: flex;
    align-items: center;
    justify-content: center;
}

.story-ring.seen {
    background: #363636;
}

.story-avatar {
    width: 100%;
    height: 100%;
    border-radius: 50%;
    border: 2px solid #000000;
    object-fit: cover;
    background: #1e1e1e;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
}

.story-name {
    font-size: 11px;
    color: var(--ig-text-secondary);
    max-width: 64px;
    text-align: center;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

/* -------------------------------------------------------------------------
   3. INSTAGRAM REELS STYLING (9:16 VERTICAL CONTAINER & OVERLAYS)
   ------------------------------------------------------------------------- */
.reel-wrapper {
    display: flex;
    justify-content: center;
    width: 100%;
    margin: 0 auto;
}

.reel-card {
    position: relative;
    width: 100%;
    max-width: 420px;
    background: #000000;
    border: 1px solid var(--ig-border);
    border-radius: 18px;
    overflow: hidden;
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.85);
    margin-bottom: 20px;
}

.reel-header-bar {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    padding: 14px 18px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    z-index: 10;
    background: linear-gradient(180deg, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0) 100%);
}

.reel-title {
    font-size: 16px;
    font-weight: 700;
    color: #ffffff;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* Right-side floating action rail */
.reel-actions {
    position: absolute;
    right: 14px;
    bottom: 85px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 16px;
    z-index: 15;
}

.action-btn-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    cursor: pointer;
    background: none;
    border: none;
    outline: none;
}

.action-icon-circle {
    width: 44px;
    height: 44px;
    border-radius: 50%;
    background: rgba(24, 24, 24, 0.65);
    backdrop-filter: blur(8px);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    color: #ffffff;
    transition: transform 0.15s ease, background-color 0.2s;
    border: 1px solid rgba(255, 255, 255, 0.12);
}
.action-icon-circle:hover {
    transform: scale(1.12);
    background: rgba(40, 40, 40, 0.85);
}
.action-icon-circle.liked {
    color: var(--ig-red);
    background: rgba(255, 48, 64, 0.2);
    border-color: rgba(255, 48, 64, 0.4);
}

.action-count {
    font-size: 11px;
    font-weight: 600;
    color: #ffffff;
    text-shadow: 0 1px 4px rgba(0,0,0,0.8);
}

/* Spinning audio disc */
.audio-disc {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    border: 2px solid #ffffff;
    background: linear-gradient(135deg, #222, #555);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    animation: spinDisc 4s linear infinite;
    box-shadow: 0 2px 8px rgba(0,0,0,0.6);
}
@keyframes spinDisc {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

/* Bottom info overlay */
.reel-info-overlay {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 70px;
    padding: 16px 18px 20px 18px;
    background: linear-gradient(0deg, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.5) 60%, rgba(0,0,0,0) 100%);
    z-index: 10;
}

.creator-row {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 8px;
}

.creator-avatar {
    width: 34px;
    height: 34px;
    border-radius: 50%;
    border: 1.5px solid #ffffff;
    object-fit: cover;
    background: #333;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
}

.creator-handle {
    font-size: 14px;
    font-weight: 700;
    color: #ffffff;
    display: flex;
    align-items: center;
    gap: 4px;
}

.verified-blue-badge {
    display: inline-block;
    width: 14px;
    height: 14px;
    color: var(--ig-blue);
    vertical-align: middle;
}

.follow-pill {
    background: transparent;
    border: 1px solid rgba(255, 255, 255, 0.4);
    color: #ffffff;
    font-size: 11px;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 6px;
    cursor: pointer;
    transition: background 0.2s;
}
.follow-pill:hover {
    background: rgba(255, 255, 255, 0.15);
}

.sponsored-pill {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    background: rgba(0, 149, 246, 0.2);
    border: 1px solid rgba(0, 149, 246, 0.5);
    color: #38bdf8;
    font-size: 11px;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 4px;
    margin-bottom: 6px;
}

.reel-caption {
    font-size: 13px;
    color: #e2e8f0;
    line-height: 1.4;
    margin-bottom: 8px;
    text-shadow: 0 1px 3px rgba(0,0,0,0.8);
}

.reel-tags {
    color: #38bdf8;
    font-size: 12px;
}

.reel-audio-bar {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 11px;
    color: #cbd5e1;
    overflow: hidden;
    white-space: nowrap;
}

.cta-banner {
    background: var(--ig-blue);
    color: #ffffff;
    font-size: 13px;
    font-weight: 700;
    padding: 8px 14px;
    border-radius: 8px;
    text-align: center;
    margin-top: 10px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: space-between;
    transition: background 0.2s;
}
.cta-banner:hover {
    background: var(--ig-blue-hover);
}

/* -------------------------------------------------------------------------
   4. INSTAGRAM CARDS & INPUTS
   ------------------------------------------------------------------------- */
.ig-card {
    background: var(--ig-surface);
    border: 1px solid var(--ig-border);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 18px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.5);
}

.ig-card-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 14px;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--ig-border);
}

.ig-card-title {
    font-size: 17px;
    font-weight: 700;
    color: var(--ig-text);
    margin: 0;
}

.ig-card-sub {
    font-size: 12px;
    color: var(--ig-text-secondary);
    margin-top: 2px;
}

/* Streamlit Native Input / Button overrides */
.stTextInput > div > div > input {
    background-color: #1a1a1a !important;
    border: 1px solid var(--ig-border) !important;
    border-radius: 8px !important;
    color: #ffffff !important;
    padding: 10px 14px !important;
    font-size: 14px !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--ig-blue) !important;
    box-shadow: 0 0 0 1px var(--ig-blue) !important;
}

.stButton > button {
    background-color: var(--ig-blue) !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 8px 16px !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background-color: var(--ig-blue-hover) !important;
    transform: translateY(-1px);
}
.stButton > button:active {
    transform: scale(0.98);
}

/* -------------------------------------------------------------------------
   5. PHONE RESPONSIVENESS (MOBILE MEDIA QUERIES)
   ------------------------------------------------------------------------- */
@media (max-width: 768px) {
    .block-container {
        padding-left: 0.25rem !important;
        padding-right: 0.25rem !important;
        padding-top: 0.5rem !important;
        padding-bottom: 4.5rem !important;
        max-width: 100vw !important;
    }

    [data-testid="stSidebar"] {
        display: none !important; /* Hide sidebar on mobile in favor of bottom bar */
    }

    .reel-card {
        max-width: 100vw !important;
        border-radius: 0px !important;
        border-left: none !important;
        border-right: none !important;
    }

    .stories-container {
        gap: 12px;
        padding: 8px 4px 12px 4px;
    }
    
    .story-ring {
        width: 56px;
        height: 56px;
    }

    .story-item {
        width: 60px;
    }

    .ig-card {
        border-radius: 8px;
        padding: 14px;
        margin-left: 4px;
        margin-right: 4px;
    }

    /* Fixed Instagram Mobile Bottom Navigation Bar */
    .ig-mobile-nav {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        height: 52px;
        background: rgba(0, 0, 0, 0.95);
        backdrop-filter: blur(16px);
        border-top: 1px solid var(--ig-border);
        display: flex;
        justify-content: space-around;
        align-items: center;
        z-index: 999999;
    }
    .ig-nav-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        color: var(--ig-text-secondary);
        font-size: 20px;
        text-decoration: none;
        cursor: pointer;
        padding: 6px;
    }
    .ig-nav-item.active {
        color: #ffffff;
    }
}
@media (min-width: 769px) {
    .ig-mobile-nav {
        display: none !important;
    }
}
</style>
"""

def inject_instagram_styles():
    """Injects the core Instagram dark mode and responsive design system."""
    st.markdown(INSTAGRAM_CSS, unsafe_allow_html=True)

def render_instagram_logo(subtitle: str = "SafeAd AI"):
    """Renders the iconic Instagram script logo with SafeAd badge."""
    html = f"""
    <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:14px; padding:0 4px;">
        <div>
            <span class="ig-logo">Instagram</span>
            <span class="ig-logo-badge">{subtitle}</span>
        </div>
        <div style="display:flex; gap:16px; align-items:center; font-size:22px; color:#ffffff;">
            <span style="cursor:pointer;" title="Notifications">❤️</span>
            <span style="cursor:pointer;" title="Direct Messages">💬</span>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_stories_bar():
    """Renders the horizontal Instagram Stories tray with gradient story rings."""
    stories = [
        {"name": "Your Story", "avatar": "➕", "is_user": True},
        {"name": "safead.ai", "avatar": "🛡️", "is_user": False},
        {"name": "tech_pulse", "avatar": "⚡", "is_user": False},
        {"name": "nature_vibes", "avatar": "🌿", "is_user": False},
        {"name": "urban_skate", "avatar": "🛹", "is_user": False},
        {"name": "future_lab", "avatar": "🤖", "is_user": False},
        {"name": "lofi_tunes", "avatar": "☕", "is_user": False},
    ]
    
    html = '<div class="stories-container">'
    for s in stories:
        seen_cls = "" if s.get("is_user") or s["name"] == "safead.ai" else "seen"
        html += f"""
        <div class="story-item">
            <div class="story-ring {seen_cls}">
                <div class="story-avatar">{s['avatar']}</div>
            </div>
            <div class="story-name">{s['name']}</div>
        </div>
        """
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)
