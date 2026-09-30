"""
pages/3_About.py — About Cosmic Clock
"""

import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.utils import inject_css
from src.timeline import (
    load_events, age_to_cosmic_year, years_ago_to_human_readable,
    UNIVERSE_AGE_YEARS, SECONDS_PER_YEAR, HUMAN_LIFESPAN_YEARS,
)

st.set_page_config(
    page_title="About · Cosmic Clock",
    page_icon="ℹ️",
    layout="wide",
)
inject_css()

st.markdown("""
<div style="font-family: Orbitron; font-size:0.7rem; color:#81C784; 
            letter-spacing:0.2em; text-transform:uppercase; margin-bottom:4px;">
    About This Project
</div>
""", unsafe_allow_html=True)
st.title("ℹ️ About Cosmic Clock")

st.markdown("---")

col1, col2 = st.columns([3, 2])

with col1:
    st.markdown("## What is Cosmic Clock?")
    st.markdown("""
    **Cosmic Clock** is an interactive astronomical and cosmological timepiece — a real-time 
    window into both the immediate sky above you and the vast sweep of cosmic history.

    It operates on two scales simultaneously:

    - **The immediate**: Where are the planets right now? What phase is the Moon in? 
      Which stars are above your horizon at this moment?

    - **The cosmic**: Where are *we* in the 13.8-billion-year story of the universe? 
      How does a human lifetime compare to the age of the stars?

    The goal is to inspire a sense of **cosmic perspective** — the kind that comes from 
    truly *feeling* how vast time and space are, and how improbable and precious our moment in them is.
    """)

    st.markdown("## Design Philosophy")
    st.markdown("""
    ### Why Skyfield over pure Astropy for planet positions?

    Both libraries are excellent, but Skyfield was chosen as the primary engine for several reasons:

    1. **Accuracy**: Skyfield uses the NASA JPL DE421 ephemeris, giving sub-arcsecond accuracy 
       for planet positions — more than sufficient for any visual display.

    2. **Simplicity**: Skyfield's API for computing alt/az coordinates for a specific observer 
       location is cleaner and more direct than Astropy's equivalent.

    3. **Self-contained**: After downloading the DE421 file once (~17 MB), all calculations 
       run completely offline — no internet required.

    4. **Moon phases**: Skyfield's moon phase calculation using ecliptic longitude differences 
       is straightforward and accurate.

    Astropy is still used for: sidereal time calculation, coordinate formatting utilities, 
    and as a fallback when Skyfield is unavailable.

    ### Why Streamlit?

    Streamlit was chosen because:
    - It allows rapid development of interactive data apps in pure Python
    - No JavaScript required for widgets, sliders, or real-time updates  
    - Native Plotly integration for interactive charts
    - Multi-page support with sidebar navigation
    - Easy deployment to Streamlit Cloud for sharing

    ### Visual design choices

    The app uses a **deep space aesthetic** with:
    - **Orbitron** for headings: a geometric, futuristic font that evokes space mission control
    - **Space Mono** for data and body text: monospaced precision for coordinates and numbers
    - **Crimson Pro** for quotes: a classical serif for the philosophical, humanist content
    - A deep blue-black color palette with carefully chosen accent colors:
      - Ice blue (#4FC3F7) for primary UI
      - Soft violet (#CE93D8) for timeline elements
      - Sage green (#81C784) for life-related content
      - Warm gold (#FFD54F) for solar/stellar elements
    """)

    st.markdown("## Data Sources & Accuracy")
    st.markdown("""
    | Data | Source | Accuracy |
    |------|--------|----------|
    | Planet, Sun, Moon positions | NASA JPL DE421 via Skyfield | Ephemeris-grade; the map shows 0.1° |
    | Moon phase | Difference of ecliptic longitudes | Matches new, quarter, and full moons |
    | Star catalog | Bright stars, Hipparcos round numbers | About 0.01 h in RA and 0.01° in Dec |
    | Sidereal time | Astropy apparent sidereal time | Sub-second when Astropy is installed |
    | Equation of time | DE421 hour angle of the Sun | Seconds; a day-of-year formula is the offline fallback |
    | Cosmic Calendar | 13.8 billion years on a 365-day civil year | Same function as the timeline |
    """)

with col2:
    st.markdown("## Quick Reference")

    st.markdown(f"""
    <div class="cosmic-card">
        <div style="font-family: Orbitron; font-size:0.65rem; color:#4FC3F7; 
                    letter-spacing:0.1em; margin-bottom:12px;">COSMIC FACTS</div>
        <div style="font-family: Space Mono; font-size:0.7rem; color:#8899bb; line-height:2.2;">
        
        Age of universe: <span style="color:#e8f0fe;">13.8 billion years</span><br>
        Age of Sun: <span style="color:#e8f0fe;">4.6 billion years</span><br>
        Age of Earth: <span style="color:#e8f0fe;">4.54 billion years</span><br>
        Age of life on Earth: <span style="color:#e8f0fe;">~3.8 billion years</span><br>
        Age of Homo sapiens: <span style="color:#e8f0fe;">~300,000 years</span><br>
        Age of agriculture: <span style="color:#e8f0fe;">~12,000 years</span><br>
        <br>
        1 cosmic second = <span style="color:#CE93D8;">{UNIVERSE_AGE_YEARS / SECONDS_PER_YEAR:.0f} real years</span><br>
        Human lifespan (80yr) = <span style="color:#CE93D8;">{HUMAN_LIFESPAN_YEARS / UNIVERSE_AGE_YEARS * SECONDS_PER_YEAR:.3f} cosmic s</span><br>
        10,000 years of history = <span style="color:#CE93D8;">{10000 / UNIVERSE_AGE_YEARS * SECONDS_PER_YEAR:.1f} cosmic sec</span><br>
        
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("## Credits & References")
    st.markdown("""
    <div class="cosmic-card">
        <div style="font-family: Orbitron; font-size:0.65rem; color:#81C784; 
                    letter-spacing:0.1em; margin-bottom:12px;">LIBRARIES & DATA</div>
        <div style="font-family: Space Mono; font-size:0.68rem; color:#8899bb; line-height:2.0;">
        
        🔭 <a href="https://rhodesmill.org/skyfield/" style="color:#4FC3F7;">Skyfield</a> 
            by Brandon Rhodes<br>
        🌌 <a href="https://www.astropy.org/" style="color:#4FC3F7;">Astropy</a> 
            — Astropy Collaboration<br>
        📊 <a href="https://plotly.com/" style="color:#4FC3F7;">Plotly</a> 
            — Interactive charts<br>
        🚀 <a href="https://streamlit.io/" style="color:#4FC3F7;">Streamlit</a> 
            — Web framework<br>
        🛸 <a href="https://ssd.jpl.nasa.gov/" style="color:#4FC3F7;">NASA JPL</a> 
            — DE421 Ephemeris<br>
        ⭐ <a href="https://www.cosmos.esa.int/web/hipparcos" style="color:#4FC3F7;">ESA Hipparcos</a> 
            — Star catalog<br>
        
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <div class="cosmic-card">
        <div style="font-family: Orbitron; font-size:0.65rem; color:#CE93D8; 
                    letter-spacing:0.1em; margin-bottom:12px;">INSPIRATIONS</div>
        <div style="font-family: Space Mono; font-size:0.68rem; color:#8899bb; line-height:2.0;">
        
        📚 Carl Sagan — <i>Cosmos</i> (1980)<br>
        📚 Carl Sagan — <i>Pale Blue Dot</i> (1994)<br>
        📚 Neil deGrasse Tyson — <i>Astrophysics for People in a Hurry</i><br>
        📚 The Cosmic Calendar — Wikipedia<br>
        🔭 Stellarium — Open-source planetarium<br>
        🌌 NASA Astronomy Picture of the Day<br>
        
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

st.markdown("## The Cosmic Calendar — Full Reference")
st.markdown(
    """
The Cosmic Calendar, popularized by Carl Sagan, compresses the history of the
universe into one civil year. The rows below are computed from the timeline
events with the same function the rest of the app uses: 13.8 billion years
mapped onto 365 days, with real month lengths and no 29 February. The present
is the last millisecond of 31 December.
"""
)
_events = load_events()
_rows = [
    "| Cosmic Calendar | Event | Years ago |",
    "| --- | --- | --- |",
]
for _ev in _events:
    _cal = age_to_cosmic_year(_ev["age_years"])
    _rows.append(
        f"| {_cal['display']} | {_ev['name']} | {years_ago_to_human_readable(_ev['age_years'])} |"
    )
st.markdown("\n".join(_rows))
st.markdown(
    f"*One cosmic second = {UNIVERSE_AGE_YEARS / SECONDS_PER_YEAR:.1f} years of real time.*"
)

st.markdown("---")
st.markdown("""
<div style="text-align:center; font-family: Space Mono; font-size:0.65rem; color:#2a2a4a;">
    Cosmic Clock · Open source · Built with Python, Skyfield, Astropy, Plotly & Streamlit<br>
    "The universe is under no obligation to make sense to you." — Neil deGrasse Tyson
</div>
""", unsafe_allow_html=True)
