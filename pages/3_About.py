"""
pages/3_About.py — About Cosmic Clock
"""

import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.utils import inject_css

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
    | Planet positions | NASA JPL DE421 via Skyfield | Sub-arcsecond |
    | Moon phase | Ecliptic longitude calculation | ± 1° |
    | Star catalog | Custom hardcoded from Hipparcos | RA/Dec to 0.01° |
    | Sidereal time | Astropy / IERS tables | Sub-second |
    | Cosmic ages | Published cosmological literature | ± uncertainties noted |
    | Cosmic Calendar | Carl Sagan / Wikipedia | Reference-grade |
    """)

with col2:
    st.markdown("## Quick Reference")

    st.markdown("""
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
        1 cosmic year second = <span style="color:#CE93D8;">438 real years</span><br>
        Human lifespan (80yr) = <span style="color:#CE93D8;">0.183 cosmic s</span><br>
        All human history = <span style="color:#CE93D8;">~22 cosmic sec</span><br>
        
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
st.markdown("""
The Cosmic Calendar, popularized by Carl Sagan in his 1980 TV series *Cosmos*, 
compresses the entire history of the universe into a single year. Here's the full scale:

| Cosmic Calendar Date | Real Event | Years Ago |
|---------------------|------------|-----------|
| Jan 1, 00:00:00 | Big Bang | 13.8 billion |
| Jan 22 | First stars and galaxies | 13.5 billion |
| Mar 16 | Milky Way galaxy forms | 10 billion |
| Sep 2 | Solar System forms | 4.6 billion |
| Sep 6 | Oldest rocks on Earth | 4.4 billion |
| Sep 21 | First life (prokaryotes) | 3.8 billion |
| Oct 9 | Eukaryotic cells | 2.7 billion |
| Dec 5 | First multicellular organisms | 0.8 billion |
| Dec 17 | Cambrian explosion (complex animals) | 541 million |
| Dec 19 | First land plants | 470 million |
| Dec 21 | First forests | 370 million |
| Dec 23 | First reptiles | 315 million |
| Dec 24 | Great Permian extinction | 252 million |
| Dec 25 | First dinosaurs | 230 million |
| Dec 25 | First mammals | 225 million |
| Dec 28 | First flowers | 130 million |
| Dec 30, 06:24 | Chicxulub impact / dinosaurs extinct | 66 million |
| Dec 30, 10:00 | Mammals diversify | 65 million |
| Dec 31, 06:05 | First primates | 55 million |
| Dec 31, 22:24 | Homo sapiens emerge | 300,000 |
| Dec 31, 23:44 | First cave paintings | 45,000 |
| Dec 31, 23:59:32 | Agriculture invented | 12,000 |
| Dec 31, 23:59:46 | First cities (Uruk) | 8,000 |
| Dec 31, 23:59:48 | Writing invented | 5,500 |
| Dec 31, 23:59:57.5 | Scientific revolution | 450 |
| Dec 31, 23:59:59.25 | Industrial revolution | 250 |
| Dec 31, 23:59:59.8 | Sputnik launched | 67 |
| Dec 31, 23:59:59.95 | Moon landing | 56 |
| Dec 31, 23:59:59.994 | World Wide Web | 35 |
| **Dec 31, 23:59:59.9999+** | **Right now** | 0 |

*One cosmic second = approximately 438 years of real time.*
""")

st.markdown("---")
st.markdown("""
<div style="text-align:center; font-family: Space Mono; font-size:0.65rem; color:#2a2a4a;">
    Cosmic Clock · Open source · Built with Python, Skyfield, Astropy, Plotly & Streamlit<br>
    "The universe is under no obligation to make sense to you." — Neil deGrasse Tyson
</div>
""", unsafe_allow_html=True)
