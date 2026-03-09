"""
Cosmic Clock — app.py
Main Streamlit entry point. Renders the home/landing page.
"""

import streamlit as st
from datetime import datetime, timezone
import sys, os

# Ensure src/ is importable
sys.path.insert(0, os.path.dirname(__file__))

from src.utils import inject_css, COSMIC_CSS, now_utc
from src.timeline import load_events, UNIVERSE_AGE_YEARS, age_to_cosmic_year

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Cosmic Clock",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 20px 0 10px;">
        <div style="font-family: Orbitron; font-size: 1.1rem; font-weight:900;
                    background: linear-gradient(135deg,#4FC3F7,#CE93D8);
                    -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            🌌 COSMIC CLOCK
        </div>
        <div style="font-family: Space Mono; font-size:0.62rem; color:#4a5270; 
                    letter-spacing:0.15em; margin-top:4px;">
            v1.0 · REAL-TIME COSMOS
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="font-family: Space Mono; font-size:0.72rem; color:#8899bb; padding: 0 4px;">
    Navigate the cosmos:<br><br>
    🔭 <b style='color:#4FC3F7'>Sky Clock</b> — Live sky map<br>
    &nbsp;&nbsp;&nbsp;&nbsp;Planet positions, Moon phase,<br>
    &nbsp;&nbsp;&nbsp;&nbsp;stars at your location<br><br>
    🌌 <b style='color:#CE93D8'>Cosmic Timeline</b> — Universe history<br>
    &nbsp;&nbsp;&nbsp;&nbsp;13.8 billion years in perspective<br><br>
    ℹ️ <b style='color:#81C784'>About</b> — Credits & references
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Live clock
    now = now_utc()
    st.markdown(f"""
    <div style="font-family: Space Mono; font-size:0.68rem; color:#4a5270; text-align:center;">
        UTC<br>
        <span style="color:#4FC3F7; font-size:0.9rem;">{now.strftime('%H:%M:%S')}</span><br>
        {now.strftime('%Y · %b %d')}
    </div>
    """, unsafe_allow_html=True)


# ── Main content ──────────────────────────────────────────────────────────────

# Hero section
st.markdown("""
<div style="text-align:center; padding: 3rem 0 1rem;">
    <div style="font-family: Orbitron; font-size: clamp(2rem, 5vw, 3.5rem); font-weight:900;
                background: linear-gradient(135deg, #4FC3F7 0%, #CE93D8 40%, #FFD54F 80%, #81C784 100%);
                -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                background-clip: text; line-height:1.1; margin-bottom:8px;">
        COSMIC CLOCK
    </div>
    <div style="font-family: Space Mono; font-size:0.85rem; color:#6677aa; letter-spacing:0.2em; 
                text-transform:uppercase; margin-bottom:2rem;">
        A Real-Time Astronomical &amp; Cosmological Timepiece
    </div>
</div>
""", unsafe_allow_html=True)


# Cosmic quote
st.markdown("""
> *"The cosmos is within us. We are made of star-stuff. We are a way for the universe to know itself."*
> — Carl Sagan
""")

st.markdown("<br>", unsafe_allow_html=True)

# ── Live stats strip ──────────────────────────────────────────────────────────
now = now_utc()
events = load_events()
cosmic_pos = age_to_cosmic_year(0.0)

# Find the most recent event (closest to present)
recent_event = max(
    [e for e in events if e["age_years"] > 0],
    key=lambda e: -e["age_years"]  # smallest age_years = most recent
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "🌌 Universe Age",
        "13.8 Billion Years",
        "± 20 million years",
    )

with col2:
    st.metric(
        "📅 Cosmic Calendar",
        "Dec 31  23:59:59",
        "You are here",
    )

with col3:
    universe_age_s = 13.8e9 * 365.25 * 24 * 3600
    human_history_s = 10000 * 365.25 * 24 * 3600
    human_pct = human_history_s / universe_age_s * 100
    st.metric(
        "🧠 Human Civilization",
        "~10,000 years",
        f"{human_pct:.7f}% of cosmic time",
    )

with col4:
    seconds_per_cosmic_year = 365.25 * 24 * 3600
    human_life_as_cosmic = (80 / 13.8e9) * seconds_per_cosmic_year
    st.metric(
        "⏱️ Your Lifetime",
        "≈ 80 years",
        f"≈ {human_life_as_cosmic:.4f} cosmic seconds",
    )

st.markdown("<br>", unsafe_allow_html=True)

# ── Feature cards ─────────────────────────────────────────────────────────────
st.markdown("## What is Cosmic Clock?")

col_a, col_b, col_c = st.columns(3)

with col_a:
    st.markdown("""
    <div class="cosmic-card">
        <div style="font-family: Orbitron; color: #4FC3F7; font-size:0.75rem; letter-spacing:0.1em; margin-bottom:10px;">
            🔭 REAL-TIME SKY CLOCK
        </div>
        <div style="font-family: Space Mono; color: #8899bb; font-size:0.78rem; line-height:1.8;">
            A living orrery for your exact location.<br><br>
            • Current planet positions on a sky map<br>
            • Moon phase & illumination<br>
            • Bright stars above your horizon<br>
            • Sidereal time & local solar time<br>
            • Day/twilight/night sky state<br><br>
            <span style="color:#4FC3F7;">Navigate → Sky Clock</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_b:
    st.markdown("""
    <div class="cosmic-card">
        <div style="font-family: Orbitron; color: #CE93D8; font-size:0.75rem; letter-spacing:0.1em; margin-bottom:10px;">
            🌌 COSMIC TIMELINE
        </div>
        <div style="font-family: Space Mono; color: #8899bb; font-size:0.78rem; line-height:1.8;">
            13.8 billion years in human perspective.<br><br>
            • Carl Sagan's Cosmic Calendar<br>
            • 40+ milestone events with descriptions<br>
            • Zoom from Big Bang → your lifetime<br>
            • Multiple time scales to explore<br>
            • Personal overlay: your birth year<br><br>
            <span style="color:#CE93D8;">Navigate → Cosmic Timeline</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_c:
    st.markdown("""
    <div class="cosmic-card">
        <div style="font-family: Orbitron; color: #81C784; font-size:0.75rem; letter-spacing:0.1em; margin-bottom:10px;">
            🌠 PERSPECTIVE ENGINE
        </div>
        <div style="font-family: Space Mono; color: #8899bb; font-size:0.78rem; line-height:1.8;">
            Numbers that transform how you see time.<br><br>
            • 1 human life = 0.18 cosmic seconds<br>
            • All of human history = last 22 min<br>
            • First stars born in February<br>
            • Dinosaurs extinct Dec 30th<br>
            • Agriculture: Dec 31 at 11:59 PM<br><br>
            <span style="color:#81C784;">Feels like yesterday.</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Cosmic Calendar facts ─────────────────────────────────────────────────────
st.markdown("## The Cosmic Calendar at a Glance")

facts = [
    ("💥", "Big Bang",           "Jan 1,  00:00:00",  "13.8 billion years ago"),
    ("⭐", "First Stars",        "Jan 22",             "13.5 billion years ago"),
    ("🌌", "Milky Way Forms",    "Mar 16",             "10.0 billion years ago"),
    ("☀️", "Our Solar System",   "Sep 2",              "4.6 billion years ago"),
    ("🌍", "Earth Forms",        "Sep 6",              "4.54 billion years ago"),
    ("🦠", "First Life",         "Sep 21",             "3.8 billion years ago"),
    ("🦕", "Dinosaurs Rise",     "Dec 25",             "230 million years ago"),
    ("☄️", "Chicxulub Impact",   "Dec 30, 06:24",      "66 million years ago"),
    ("🧠", "Modern Humans",      "Dec 31, 22:24",      "300,000 years ago"),
    ("🌾", "Agriculture",        "Dec 31, 23:59:32",   "12,000 years ago"),
    ("🔭", "Scientific Rev.",    "Dec 31, 23:59:57.5", "450 years ago"),
    ("🚀", "Space Age",          "Dec 31, 23:59:59.8", "67 years ago"),
    ("⏱️", "RIGHT NOW",          "Dec 31, 23:59:59.99", "Present moment"),
]

cols = st.columns(4)
for i, (icon, name, date, real_date) in enumerate(facts):
    with cols[i % 4]:
        st.markdown(f"""
        <div style="background: rgba(13,13,43,0.6); border: 1px solid rgba(79,195,247,0.1);
                    border-radius:8px; padding:10px; margin:4px 0; text-align:center;">
            <div style="font-size:1.4rem; margin-bottom:4px;">{icon}</div>
            <div style="font-family: Orbitron; font-size:0.58rem; color:#4FC3F7; 
                        letter-spacing:0.08em; margin-bottom:4px;">{name}</div>
            <div style="font-family: Space Mono; font-size:0.65rem; color:#e8f0fe;">{date}</div>
            <div style="font-family: Space Mono; font-size:0.58rem; color:#4a5270; margin-top:2px;">{real_date}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Scale of the universe ─────────────────────────────────────────────────────
st.markdown("## The Scale of Deep Time")

st.markdown("""
<div class="cosmic-card">
<div style="font-family: Space Mono; font-size:0.8rem; color:#8899bb; line-height:2.2;">

If the entire history of the universe were compressed into a single calendar year:

<br>

<table style="width:100%; border-collapse:collapse;">
<tr>
<th style="font-family:Orbitron; color:#4FC3F7; font-size:0.65rem; text-align:left; padding:6px; border-bottom:1px solid #1a1a4e;">COSMIC DATE</th>
<th style="font-family:Orbitron; color:#4FC3F7; font-size:0.65rem; text-align:left; padding:6px; border-bottom:1px solid #1a1a4e;">REAL TIME</th>
<th style="font-family:Orbitron; color:#4FC3F7; font-size:0.65rem; text-align:left; padding:6px; border-bottom:1px solid #1a1a4e;">1 COSMIC SECOND =</th>
</tr>
<tr style="color:#e8f0fe;">
<td style="padding:5px 6px; font-size:0.75rem;">1 cosmic year</td>
<td style="padding:5px 6px; font-size:0.75rem;">13.8 billion years</td>
<td style="padding:5px 6px; font-size:0.75rem;">438 years of real time</td>
</tr>
<tr style="color:#8899bb;">
<td style="padding:5px 6px; font-size:0.75rem;">1 cosmic month</td>
<td style="padding:5px 6px; font-size:0.75rem;">1.15 billion years</td>
<td style="padding:5px 6px; font-size:0.75rem;">—</td>
</tr>
<tr style="color:#e8f0fe;">
<td style="padding:5px 6px; font-size:0.75rem;">1 cosmic day</td>
<td style="padding:5px 6px; font-size:0.75rem;">37.8 million years</td>
<td style="padding:5px 6px; font-size:0.75rem;">—</td>
</tr>
<tr style="color:#8899bb;">
<td style="padding:5px 6px; font-size:0.75rem;">1 cosmic hour</td>
<td style="padding:5px 6px; font-size:0.75rem;">1.575 million years</td>
<td style="padding:5px 6px; font-size:0.75rem;">—</td>
</tr>
<tr style="color:#e8f0fe;">
<td style="padding:5px 6px; font-size:0.75rem;">1 cosmic minute</td>
<td style="padding:5px 6px; font-size:0.75rem;">26,250 years</td>
<td style="padding:5px 6px; font-size:0.75rem;">—</td>
</tr>
<tr style="color:#CE93D8; font-weight:bold;">
<td style="padding:5px 6px; font-size:0.75rem;">Your entire lifetime (80 yrs)</td>
<td style="padding:5px 6px; font-size:0.75rem;">80 years</td>
<td style="padding:5px 6px; font-size:0.75rem;"><b>0.183 cosmic seconds</b></td>
</tr>
</table>

</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding:20px 0; font-family: Space Mono; 
            font-size:0.65rem; color:#2a2a4a;">
    Built with ♥ and wonder · Powered by Skyfield & Astropy<br>
    Inspired by Carl Sagan's <i>Cosmos</i> · Data: NASA JPL DE421 Ephemeris<br>
    <span style="color:#1a1a3a;">The universe is under no obligation to make sense to you.</span>
</div>
""", unsafe_allow_html=True)
