"""
pages/1_Sky_Clock.py — Real-Time Astronomical Sky Clock
Interactive sky map showing the current sky at your location.
"""

import streamlit as st
import sys
import os
from datetime import datetime, timezone, timedelta
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.utils import (
    inject_css, PRESET_CITIES, DEFAULT_LAT, DEFAULT_LON, DEFAULT_CITY,
    format_ra, format_dec, now_utc, glow_metric, cosmic_header
)
from src.astronomy import (
    get_planet_positions, get_sun_position, get_moon_data,
    get_sidereal_time, get_solar_time, get_sky_state, get_current_zodiac,
    get_bright_stars_altaz,
)
from src.visuals import build_sky_map, build_planet_visibility_chart, build_moon_phase_diagram

st.set_page_config(
    page_title="Sky Clock · Cosmic Clock",
    page_icon="🔭",
    layout="wide",
)
inject_css()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="font-family: Orbitron; font-size:0.7rem; color:#4FC3F7; 
            letter-spacing:0.2em; text-transform:uppercase; margin-bottom:4px;">
    Real-Time Astronomical
</div>
""", unsafe_allow_html=True)
st.title("🔭 Sky Clock")
st.markdown("""
<p style="color:#6677aa; font-family: Space Mono; font-size:0.8rem; margin-top:-8px;">
    A live view of the sky from your location — planets, moon, stars and more
</p>
""", unsafe_allow_html=True)

st.markdown("---")

# ── Sidebar controls ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="font-family: Orbitron; font-size:0.7rem; color:#4FC3F7; 
                letter-spacing:0.1em; margin-bottom:12px; padding-top:8px;">
        📍 OBSERVER LOCATION
    </div>
    """, unsafe_allow_html=True)

    city_choice = st.selectbox("City Preset", list(PRESET_CITIES.keys()),
                                index=0, key="city_select")

    preset_lat, preset_lon = PRESET_CITIES[city_choice]

    if preset_lat is None:
        lat = st.number_input("Latitude (°N)", value=DEFAULT_LAT, min_value=-90.0, max_value=90.0, step=0.01)
        lon = st.number_input("Longitude (°E)", value=DEFAULT_LON, min_value=-180.0, max_value=180.0, step=0.01)
    else:
        lat = preset_lat
        lon = preset_lon
        st.markdown(f"<div style='font-family:Space Mono; font-size:0.68rem; color:#4a5270;'>"
                    f"📍 {lat:.4f}°N, {lon:.4f}°E</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="font-family: Orbitron; font-size:0.7rem; color:#CE93D8; 
                letter-spacing:0.1em; margin-bottom:12px;">
        ⏰ TIME SETTINGS
    </div>
    """, unsafe_allow_html=True)

    use_now = st.checkbox("Use current time (live)", value=True)

    if not use_now:
        date_override = st.date_input("Date", value=now_utc().date())
        time_override = st.time_input("Time (UTC)", value=now_utc().time())
        obs_dt = datetime.combine(date_override, time_override).replace(tzinfo=timezone.utc)
    else:
        obs_dt = now_utc()

    st.markdown("---")
    st.markdown("""
    <div style="font-family: Orbitron; font-size:0.7rem; color:#81C784; 
                letter-spacing:0.1em; margin-bottom:12px;">
        🔎 DISPLAY LAYERS
    </div>
    """, unsafe_allow_html=True)

    show_planets = st.checkbox("Show Planets", value=True)
    show_stars = st.checkbox("Show Bright Stars", value=True)
    show_labels = st.checkbox("Show Labels", value=True)

    st.markdown("---")
    if st.button("🔄 Refresh Sky"):
        st.rerun()


# ── Load all data ─────────────────────────────────────────────────────────────

with st.spinner("Calculating celestial positions…"):
    planets   = get_planet_positions(lat, lon, obs_dt)
    sun       = get_sun_position(lat, lon, obs_dt)
    moon      = get_moon_data(lat, lon, obs_dt)
    stars     = get_bright_stars_altaz(lat, lon, obs_dt)
    sky_state = get_sky_state(sun["alt"])
    lst       = get_sidereal_time(lon, obs_dt)
    solar_t   = get_solar_time(lon, obs_dt)
    zodiac    = get_current_zodiac(obs_dt)


# ── Info strip ────────────────────────────────────────────────────────────────
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("🌅 Sky Condition", sky_state["name"])

with col2:
    lst_h = int(lst)
    lst_m = int((lst - lst_h) * 60)
    lst_s = int(((lst - lst_h) * 60 - lst_m) * 60)
    st.metric("⭐ Sidereal Time", f"{lst_h:02d}h {lst_m:02d}m {lst_s:02d}s")

with col3:
    st.metric("☀️ Solar Time", solar_t.strftime("%H:%M:%S"))

with col4:
    st.metric("🌙 Moon Phase", moon["phase_name"].split(" ", 1)[-1],
              f"{moon['illumination']:.0f}% lit")

with col5:
    st.metric("♈ Sun in", f"{zodiac['symbol']} {zodiac['name']}")


st.markdown("<br>", unsafe_allow_html=True)

# ── Main layout: Sky Map + Info ───────────────────────────────────────────────
map_col, info_col = st.columns([3, 1])

with map_col:
    st.markdown("""
    <div style="font-family: Orbitron; font-size:0.7rem; color:#4FC3F7; 
                letter-spacing:0.15em; margin-bottom:8px;">
        ALL-SKY MAP — STEREOGRAPHIC PROJECTION
    </div>
    """, unsafe_allow_html=True)

    sky_fig = build_sky_map(
        planets=planets,
        stars=stars,
        sun=sun,
        moon=moon,
        sky_state=sky_state,
        lat=lat,
        show_planets=show_planets,
        show_stars=show_stars,
        show_labels=show_labels,
    )
    st.plotly_chart(sky_fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown("""
    <div style="font-family: Space Mono; font-size:0.65rem; color:#2a2a5a; text-align:center;">
        Center = Zenith (directly overhead) · Edge = Horizon · N/E/S/W = Cardinal directions<br>
        Altitude rings at 0°, 30°, 60° · Azimuth spokes every 45°
    </div>
    """, unsafe_allow_html=True)

with info_col:
    # Moon phase diagram
    st.markdown("""
    <div style="font-family: Orbitron; font-size:0.65rem; color:#CE93D8; 
                letter-spacing:0.1em; margin-bottom:6px;">
        🌙 MOON
    </div>
    """, unsafe_allow_html=True)

    moon_fig = build_moon_phase_diagram(moon["phase"], moon["illumination"])
    st.plotly_chart(moon_fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown(f"""
    <div style="font-family: Space Mono; font-size:0.68rem; color:#8899bb; 
                text-align:center; margin-top:-10px;">
        {moon['phase_name']}<br>
        {moon['illumination']:.0f}% illuminated<br>
        Alt: {moon['alt']:.1f}° · Az: {moon['az']:.1f}°<br>
        {'🔼 Above horizon' if moon['above_horizon'] else '🔽 Below horizon'}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Sun position info
    st.markdown("""
    <div style="font-family: Orbitron; font-size:0.65rem; color:#FFD54F; 
                letter-spacing:0.1em; margin-bottom:6px;">
        ☀️ SUN
    </div>
    """, unsafe_allow_html=True)
    st.markdown(f"""
    <div style="font-family: Space Mono; font-size:0.68rem; color:#8899bb;">
        Alt: {sun['alt']:.2f}°<br>
        Az:  {sun['az']:.2f}°<br>
        RA:  {format_ra(sun['ra'])}<br>
        Dec: {format_dec(sun['dec'])}<br>
        {'☀️ Above horizon' if sun['above_horizon'] else '🌙 Below horizon'}
    </div>
    """, unsafe_allow_html=True)


st.markdown("---")

# ── Planet details table ──────────────────────────────────────────────────────
st.markdown("### 🪐 Planet Positions")

vis_col, detail_col = st.columns([1, 2])

with vis_col:
    st.markdown("""
    <div style="font-family: Orbitron; font-size:0.65rem; color:#4FC3F7; 
                letter-spacing:0.1em; margin-bottom:8px;">
        ALTITUDE OVERVIEW
    </div>
    """, unsafe_allow_html=True)
    planet_fig = build_planet_visibility_chart(planets)
    st.plotly_chart(planet_fig, use_container_width=True, config={"displayModeBar": False})

with detail_col:
    st.markdown("""
    <div style="font-family: Orbitron; font-size:0.65rem; color:#4FC3F7; 
                letter-spacing:0.1em; margin-bottom:8px;">
        DETAILED COORDINATES
    </div>
    """, unsafe_allow_html=True)

    # Build planet table
    table_rows = []
    for p in planets:
        visibility = "✅ Visible" if p["visible"] else "❌ Below horizon"
        table_rows.append({
            "Planet": f"{p['symbol']} {p['name']}",
            "Altitude": f"{p['alt']:.1f}°",
            "Azimuth": f"{p['az']:.1f}°",
            "RA": format_ra(p["ra"]),
            "Dec": format_dec(p["dec"]),
            "Distance": f"{p['distance_au']:.3f} AU",
            "Status": visibility,
        })

    import pandas as pd
    df = pd.DataFrame(table_rows)
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Planet": st.column_config.TextColumn(width="small"),
            "Status": st.column_config.TextColumn(width="small"),
        }
    )


st.markdown("---")

# ── Bright Stars ──────────────────────────────────────────────────────────────
with st.expander("⭐ Bright Stars Above Horizon"):
    visible_stars = [s for s in stars if s.get("above_horizon", False)]

    if visible_stars:
        st.markdown(f"""
        <div style="font-family: Space Mono; font-size:0.72rem; color:#8899bb; margin-bottom:12px;">
            {len(visible_stars)} bright stars currently above your horizon
        </div>
        """, unsafe_allow_html=True)

        star_rows = [{
            "Star": s["name"],
            "Constellation": s["constellation"],
            "Magnitude": f"{s['mag']:.2f}",
            "Altitude": f"{s['alt']:.1f}°",
            "Azimuth": f"{s['az']:.1f}°",
            "RA": format_ra(s["ra"]),
            "Dec": format_dec(s["dec"]),
        } for s in sorted(visible_stars, key=lambda x: x["mag"])]

        star_df = pd.DataFrame(star_rows)
        st.dataframe(star_df, use_container_width=True, hide_index=True)
    else:
        st.info("No bright named stars are currently above your horizon.")


# ── Educational info ──────────────────────────────────────────────────────────
with st.expander("ℹ️ About Astronomical Coordinates"):
    st.markdown("""
    **How to read the sky map:**

    - **Altitude (Alt)**: Angular height above the horizon. 0° = horizon, 90° = zenith (directly overhead).
      Anything below 0° is below your horizon and not visible.

    - **Azimuth (Az)**: Direction measured clockwise from North. N=0°, E=90°, S=180°, W=270°.

    - **Right Ascension (RA)**: The celestial equivalent of longitude, measured eastward in hours (0h–24h).

    - **Declination (Dec)**: The celestial equivalent of latitude, measured in degrees (+90° = north celestial pole,
      −90° = south celestial pole).

    - **Sidereal Time (LST)**: A measure of Earth's rotation relative to distant stars. The RA on the meridian
      equals your current LST.

    **Twilight types:**
    - **Civil twilight**: Sun 0° to −6° — bright enough to read outdoors
    - **Nautical twilight**: Sun −6° to −12° — horizon visible for navigation
    - **Astronomical twilight**: Sun −12° to −18° — faint stars becoming visible
    - **Night**: Sun below −18° — full dark sky

    *Positions calculated using NASA JPL DE421 ephemeris via the Skyfield library.*
    """)
