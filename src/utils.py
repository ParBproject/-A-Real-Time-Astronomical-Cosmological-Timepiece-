"""
utils.py — Shared utility functions for Cosmic Clock.
"""

import streamlit as st
from datetime import datetime, timezone
from typing import Optional
import math


# ── CSS injection ─────────────────────────────────────────────────────────────

COSMIC_CSS = """
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Space+Mono:ital,wght@0,400;0,700;1,400&family=Crimson+Pro:ital,wght@0,300;0,400;1,300&display=swap');

/* ── Root variables ── */
:root {
    --cosmic-black:  #03030f;
    --cosmic-deep:   #07071a;
    --cosmic-panel:  #0d0d2b;
    --cosmic-border: #1a1a4e;
    --cosmic-glow:   #4FC3F7;
    --cosmic-gold:   #FFD54F;
    --cosmic-violet: #CE93D8;
    --cosmic-green:  #81C784;
    --text-primary:  #e8f0fe;
    --text-dim:      #8899bb;
}

/* ── App-wide background ── */
.stApp {
    background: radial-gradient(ellipse at 20% 50%, #0a0a2e 0%, #03030f 50%, #000008 100%) !important;
    color: var(--text-primary);
}

/* Star field background */
.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background-image:
        radial-gradient(1px 1px at 10% 15%, rgba(255,255,255,0.6) 0%, transparent 100%),
        radial-gradient(1px 1px at 25% 40%, rgba(255,255,255,0.4) 0%, transparent 100%),
        radial-gradient(1px 1px at 50% 20%, rgba(200,220,255,0.5) 0%, transparent 100%),
        radial-gradient(1px 1px at 75% 60%, rgba(255,255,255,0.3) 0%, transparent 100%),
        radial-gradient(1px 1px at 90% 35%, rgba(255,255,255,0.6) 0%, transparent 100%),
        radial-gradient(2px 2px at 35% 75%, rgba(200,220,255,0.4) 0%, transparent 100%),
        radial-gradient(1px 1px at 65% 85%, rgba(255,255,255,0.5) 0%, transparent 100%);
    pointer-events: none;
    z-index: -1;
}

/* ── Sidebar ── */
.css-1d391kg, [data-testid="stSidebar"] {
    background: linear-gradient(180deg, #050518 0%, #0a0a25 100%) !important;
    border-right: 1px solid var(--cosmic-border) !important;
}

/* ── Headings ── */
h1, h2, h3 {
    font-family: 'Orbitron', sans-serif !important;
    letter-spacing: 0.08em;
}

h1 {
    background: linear-gradient(135deg, #4FC3F7 0%, #CE93D8 50%, #FFD54F 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 900;
    text-shadow: none;
}

h2 { color: var(--cosmic-glow) !important; font-size: 1.2rem !important; }
h3 { color: var(--cosmic-violet) !important; font-size: 1rem !important; }

/* ── Body text ── */
p, .stMarkdown, label {
    font-family: 'Space Mono', monospace !important;
    font-size: 0.82rem !important;
    color: var(--text-dim) !important;
    line-height: 1.7 !important;
}

/* ── Metric boxes ── */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, rgba(13,13,43,0.9) 0%, rgba(7,7,26,0.9) 100%);
    border: 1px solid var(--cosmic-border);
    border-radius: 12px;
    padding: 12px 16px !important;
    backdrop-filter: blur(10px);
    box-shadow: 0 0 20px rgba(79,195,247,0.05), inset 0 1px 0 rgba(79,195,247,0.1);
}

[data-testid="stMetricLabel"] {
    font-family: 'Orbitron', sans-serif !important;
    font-size: 0.65rem !important;
    color: var(--cosmic-glow) !important;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

[data-testid="stMetricValue"] {
    font-family: 'Space Mono', monospace !important;
    font-size: 1.2rem !important;
    color: var(--text-primary) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--cosmic-border) !important;
    gap: 0;
}

.stTabs [data-baseweb="tab"] {
    font-family: 'Orbitron', sans-serif !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.08em;
    color: var(--text-dim) !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    padding: 8px 20px !important;
}

.stTabs [aria-selected="true"] {
    color: var(--cosmic-glow) !important;
    border-bottom: 2px solid var(--cosmic-glow) !important;
    background: transparent !important;
}

/* ── Buttons ── */
.stButton > button {
    font-family: 'Orbitron', sans-serif !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.12em;
    background: linear-gradient(135deg, rgba(79,195,247,0.1) 0%, rgba(206,147,216,0.1) 100%) !important;
    border: 1px solid rgba(79,195,247,0.4) !important;
    color: var(--cosmic-glow) !important;
    border-radius: 6px !important;
    transition: all 0.3s ease !important;
}

.stButton > button:hover {
    background: linear-gradient(135deg, rgba(79,195,247,0.25) 0%, rgba(206,147,216,0.25) 100%) !important;
    border-color: var(--cosmic-glow) !important;
    box-shadow: 0 0 15px rgba(79,195,247,0.3) !important;
    transform: translateY(-1px) !important;
}

/* ── Sliders ── */
.stSlider > div > div > div > div {
    background: var(--cosmic-glow) !important;
}

/* ── Select boxes ── */
.stSelectbox > div > div {
    background: var(--cosmic-panel) !important;
    border: 1px solid var(--cosmic-border) !important;
    color: var(--text-primary) !important;
    font-family: 'Space Mono', monospace !important;
}

/* ── Expanders ── */
.streamlit-expanderHeader {
    font-family: 'Orbitron', sans-serif !important;
    font-size: 0.75rem !important;
    color: var(--cosmic-violet) !important;
    letter-spacing: 0.08em;
    background: var(--cosmic-panel) !important;
    border: 1px solid var(--cosmic-border) !important;
}

/* ── Info/callout boxes ── */
.stInfo {
    background: rgba(79,195,247,0.08) !important;
    border-left: 3px solid var(--cosmic-glow) !important;
    border-radius: 0 8px 8px 0 !important;
}

/* ── Plotly chart containers ── */
.element-container:has(.js-plotly-plot) {
    border: 1px solid var(--cosmic-border);
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 0 30px rgba(79,195,247,0.04);
}

/* ── Divider ── */
hr {
    border: none !important;
    border-top: 1px solid var(--cosmic-border) !important;
    margin: 1.5rem 0 !important;
}

/* ── Number inputs ── */
.stNumberInput > div > div > input {
    background: var(--cosmic-panel) !important;
    border: 1px solid var(--cosmic-border) !important;
    color: var(--text-primary) !important;
    font-family: 'Space Mono', monospace !important;
}

/* ── Glow text utility ── */
.glow-text {
    text-shadow: 0 0 20px rgba(79,195,247,0.8), 0 0 40px rgba(79,195,247,0.4);
}

/* ── Cosmic card ── */
.cosmic-card {
    background: linear-gradient(135deg, rgba(13,13,43,0.95) 0%, rgba(7,7,26,0.95) 100%);
    border: 1px solid rgba(79,195,247,0.2);
    border-radius: 16px;
    padding: 20px 24px;
    margin: 8px 0;
    backdrop-filter: blur(10px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.5), inset 0 1px 0 rgba(79,195,247,0.1);
}

/* ── Quote / callout ── */
blockquote {
    border-left: 3px solid var(--cosmic-violet) !important;
    background: rgba(206,147,216,0.05) !important;
    padding: 12px 20px !important;
    font-family: 'Crimson Pro', serif !important;
    font-style: italic !important;
    font-size: 1rem !important;
    color: rgba(206,147,216,0.9) !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--cosmic-black); }
::-webkit-scrollbar-thumb { background: var(--cosmic-border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--cosmic-glow); }

/* ── Hide Streamlit branding ── */
#MainMenu, footer, header { visibility: hidden; }

/* ── Sidebar nav ── */
[data-testid="stSidebarNav"] a {
    font-family: 'Orbitron', sans-serif !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.06em !important;
    color: var(--text-dim) !important;
}

[data-testid="stSidebarNav"] a:hover,
[data-testid="stSidebarNav"] a[aria-current="page"] {
    color: var(--cosmic-glow) !important;
}

</style>
"""


def inject_css():
    """Inject global cosmic CSS into the Streamlit app."""
    st.markdown(COSMIC_CSS, unsafe_allow_html=True)


def cosmic_header(title: str, subtitle: str = ""):
    """Render a styled cosmic header."""
    st.markdown(f"# {title}")
    if subtitle:
        st.markdown(f"<p style='color:#8899bb; font-family: Space Mono; font-size:0.85rem; margin-top:-8px;'>{subtitle}</p>",
                    unsafe_allow_html=True)


def cosmic_card(content: str):
    """Render content in a styled cosmic card."""
    st.markdown(
        f'<div class="cosmic-card">{content}</div>',
        unsafe_allow_html=True
    )


def glow_metric(label: str, value: str, delta: str = ""):
    """Display a glowing metric."""
    delta_html = f"<div style='font-size:0.72rem; color: #81C784; margin-top:2px;'>{delta}</div>" if delta else ""
    st.markdown(f"""
    <div class="cosmic-card" style="text-align:center; padding: 12px;">
        <div style="font-family: Orbitron; font-size:0.6rem; color:#4FC3F7; letter-spacing:0.12em; text-transform:uppercase; margin-bottom:6px;">{label}</div>
        <div style="font-family: Space Mono; font-size:1.1rem; color:#e8f0fe;">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def format_ra(ra_hours: float) -> str:
    """Format RA in hours/minutes/seconds."""
    h = int(ra_hours)
    m = int((ra_hours - h) * 60)
    s = int(((ra_hours - h) * 60 - m) * 60)
    return f"{h:02d}h {m:02d}m {s:02d}s"


def format_dec(dec_deg: float) -> str:
    """Format Dec in degrees/arcmin/arcsec."""
    sign = "+" if dec_deg >= 0 else "-"
    dec_deg = abs(dec_deg)
    d = int(dec_deg)
    m = int((dec_deg - d) * 60)
    s = int(((dec_deg - d) * 60 - m) * 60)
    return f"{sign}{d:02d}° {m:02d}' {s:02d}\""


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def divider():
    st.markdown('<hr>', unsafe_allow_html=True)


# ── Default location ──────────────────────────────────────────────────────────

DEFAULT_LAT = 48.8566
DEFAULT_LON = 2.3522
DEFAULT_CITY = "Paris, France"

PRESET_CITIES = {
    "Paris, France":           (48.8566,  2.3522),
    "New York, USA":           (40.7128, -74.0060),
    "London, UK":              (51.5074,  -0.1278),
    "Tokyo, Japan":            (35.6762, 139.6503),
    "Sydney, Australia":       (-33.8688, 151.2093),
    "Mexico City, Mexico":     (19.4326,  -99.1332),
    "São Paulo, Brazil":       (-23.5505, -46.6333),
    "Cairo, Egypt":            (30.0444,  31.2357),
    "Mumbai, India":           (19.0760,  72.8777),
    "Moscow, Russia":          (55.7558,  37.6173),
    "Cape Town, South Africa": (-33.9249,  18.4241),
    "Reykjavik, Iceland":      (64.1355, -21.8954),
    "Mauna Kea, Hawaii":       (19.8207, -155.4681),
    "Atacama Desert, Chile":   (-23.0,   -67.7),
    "Custom…":                 (None, None),
}
