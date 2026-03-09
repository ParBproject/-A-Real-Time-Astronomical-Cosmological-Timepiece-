"""
pages/2_Cosmic_Timeline.py — The Cosmic Calendar & Universe Timeline Explorer
"""

import streamlit as st
import sys
import os
from datetime import datetime, timezone
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.utils import inject_css, now_utc
from src.timeline import (
    load_events, UNIVERSE_AGE_YEARS, SCALES,
    age_to_cosmic_year, age_to_scale, years_ago_to_human_readable,
    format_cosmic_fraction, compute_personal_stats,
    CATEGORY_COLORS, CATEGORY_LABELS,
)
from src.visuals import build_cosmic_timeline, build_cosmic_calendar_wheel

st.set_page_config(
    page_title="Cosmic Timeline · Cosmic Clock",
    page_icon="🌌",
    layout="wide",
)
inject_css()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="font-family: Orbitron; font-size:0.7rem; color:#CE93D8; 
            letter-spacing:0.2em; text-transform:uppercase; margin-bottom:4px;">
    13.8 Billion Years of
</div>
""", unsafe_allow_html=True)
st.title("🌌 Cosmic Timeline")
st.markdown("""
<p style="color:#6677aa; font-family: Space Mono; font-size:0.8rem; margin-top:-8px;">
    The entire history of the universe — compressed, explored, and made personal
</p>
""", unsafe_allow_html=True)

st.markdown("---")

# ── Load events ───────────────────────────────────────────────────────────────
events = load_events()

# ── Sidebar controls ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="font-family: Orbitron; font-size:0.7rem; color:#CE93D8; 
                letter-spacing:0.1em; margin-bottom:12px; padding-top:8px;">
        ⏳ TIMELINE SETTINGS
    </div>
    """, unsafe_allow_html=True)

    scale_name = st.selectbox(
        "Compress universe into:",
        list(SCALES.keys()),
        index=0,
        help="Choose the time unit used to represent the full 13.8B year history",
    )

    st.markdown("---")
    st.markdown("""
    <div style="font-family: Orbitron; font-size:0.7rem; color:#FFD54F; 
                letter-spacing:0.1em; margin-bottom:12px;">
        🔍 ZOOM WINDOW
    </div>
    """, unsafe_allow_html=True)

    zoom_mode = st.select_slider(
        "View range",
        options=["Full Universe", "Last 1 Billion Yrs", "Last 500 Myr", "Last 100 Myr",
                 "Last 10 Myr", "Human History", "Last 10,000 Yrs"],
        value="Full Universe",
    )

    zoom_ranges = {
        "Full Universe":       [0.0, 1.02],
        "Last 1 Billion Yrs":  [1 - 1e9 / UNIVERSE_AGE_YEARS - 0.01, 1.02],
        "Last 500 Myr":        [1 - 5e8 / UNIVERSE_AGE_YEARS - 0.005, 1.02],
        "Last 100 Myr":        [1 - 1e8 / UNIVERSE_AGE_YEARS - 0.001, 1.02],
        "Last 10 Myr":         [1 - 1e7 / UNIVERSE_AGE_YEARS - 0.0002, 1.02],
        "Human History":       [1 - 3e6 / UNIVERSE_AGE_YEARS - 0.00003, 1.02],
        "Last 10,000 Yrs":     [1 - 1e4 / UNIVERSE_AGE_YEARS - 0.000002, 1.02],
    }
    zoom_range = zoom_ranges.get(zoom_mode, [0.0, 1.02])

    st.markdown("---")
    st.markdown("""
    <div style="font-family: Orbitron; font-size:0.7rem; color:#81C784; 
                letter-spacing:0.1em; margin-bottom:12px;">
        🎯 FILTER CATEGORIES
    </div>
    """, unsafe_allow_html=True)

    all_cats = list(CATEGORY_LABELS.keys())
    selected_cats = []
    for cat, label in CATEGORY_LABELS.items():
        if st.checkbox(label, value=True, key=f"cat_{cat}"):
            selected_cats.append(cat)

    st.markdown("---")
    st.markdown("""
    <div style="font-family: Orbitron; font-size:0.7rem; color:#CE93D8; 
                letter-spacing:0.1em; margin-bottom:12px;">
        🎂 PERSONAL OVERLAY
    </div>
    """, unsafe_allow_html=True)

    use_personal = st.checkbox("Show my birth year", value=False)
    birth_year = None
    if use_personal:
        birth_year = st.number_input("Birth Year", value=1990, min_value=1900, max_value=2024, step=1)


# ── Main content tabs ─────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📅 Cosmic Calendar",
    "📏 Timeline Explorer",
    "🔬 Zoom: Human Era",
    "🧬 Personal Scale",
])


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1: COSMIC CALENDAR
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("### The Universe as a Single Year")
    st.markdown("""
    <div style="font-family: Space Mono; font-size:0.78rem; color:#8899bb; 
                margin-bottom:20px; max-width:680px;">
        If all of cosmic history — 13.8 billion years — were compressed into a single calendar year,
        the Big Bang would be at midnight on January 1st, and <i>this very moment</i> would be the 
        last fraction of a second before midnight on December 31st.
    </div>
    """, unsafe_allow_html=True)

    cal_col, wheel_col = st.columns([1, 1])

    with wheel_col:
        st.markdown("""
        <div style="font-family: Orbitron; font-size:0.65rem; color:#CE93D8; 
                    letter-spacing:0.1em; margin-bottom:8px; text-align:center;">
            COSMIC CALENDAR WHEEL
        </div>
        """, unsafe_allow_html=True)
        wheel_fig = build_cosmic_calendar_wheel(
            [e for e in events if e.get("category") in selected_cats]
        )
        st.plotly_chart(wheel_fig, use_container_width=True, config={"displayModeBar": False})

    with cal_col:
        st.markdown("""
        <div style="font-family: Orbitron; font-size:0.65rem; color:#CE93D8; 
                    letter-spacing:0.1em; margin-bottom:12px;">
            KEY DATES ON THE COSMIC CALENDAR
        </div>
        """, unsafe_allow_html=True)

        # Show events on the calendar
        for ev in events:
            if ev.get("category") not in selected_cats:
                continue
            cal = age_to_cosmic_year(ev["age_years"])
            cat = ev.get("category", "cosmological")
            color = CATEGORY_COLORS.get(cat, "#aaaaaa")

            st.markdown(f"""
            <div style="display:flex; align-items:flex-start; margin-bottom:8px;
                        background: rgba(13,13,43,0.4); border-left: 2px solid {color}33;
                        border-radius: 0 6px 6px 0; padding: 6px 10px;">
                <div style="font-size:1.1rem; margin-right:10px; flex-shrink:0;">{ev.get('icon','●')}</div>
                <div style="flex:1;">
                    <div style="font-family: Orbitron; font-size:0.62rem; color:{color}; 
                                letter-spacing:0.06em;">{ev['name']}</div>
                    <div style="font-family: Space Mono; font-size:0.62rem; color:#e8f0fe;">
                        {cal['display']}
                    </div>
                    <div style="font-family: Space Mono; font-size:0.58rem; color:#4a5270;">
                        {years_ago_to_human_readable(ev['age_years'])}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2: TIMELINE EXPLORER
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown(f"### Universe History — Compressed into {SCALES[scale_name]['label']}")
    st.markdown(f"""
    <div style="font-family: Space Mono; font-size:0.75rem; color:#8899bb; margin-bottom:12px;">
        Scale: 1 second of {SCALES[scale_name]['label']} = 
        {UNIVERSE_AGE_YEARS / (SCALES[scale_name]['duration_s'] / 1) / 1e9 * 1e9:.0f} years of real time
        · Hover events for details · Scroll/zoom to explore
    </div>
    """, unsafe_allow_html=True)

    # Scale info metrics
    s_col1, s_col2, s_col3 = st.columns(3)
    with s_col1:
        from src.timeline import SECONDS_PER_YEAR
        scale_duration = SCALES[scale_name]["duration_s"]
        ratio = UNIVERSE_AGE_YEARS * 365.25 * 24 * 3600 / scale_duration
        st.metric("Time Compression", f"{ratio/1e9:.2f} billion ×",
                  "Real seconds per scale second")
    with s_col2:
        human_life_s = 80 * 365.25 * 24 * 3600
        human_in_scale = human_life_s / ratio
        st.metric("Your 80-year life", f"{human_in_scale*1000:.4f} ms",
                  f"On this {SCALES[scale_name]['label']} scale")
    with s_col3:
        human_history_s = 10000 * 365.25 * 24 * 3600
        history_in_scale = human_history_s / ratio
        st.metric("All of human civilization", f"{history_in_scale:.4f}s",
                  f"On this {SCALES[scale_name]['label']} scale")

    st.markdown("<br>", unsafe_allow_html=True)

    timeline_fig = build_cosmic_timeline(
        events=[e for e in events],
        scale_name=scale_name,
        zoom_range=zoom_range,
        highlight_categories=selected_cats if selected_cats else None,
        user_birth_year=birth_year if use_personal else None,
    )
    st.plotly_chart(timeline_fig, use_container_width=True, config={
        "displayModeBar": True,
        "modeBarButtonsToRemove": ["lasso2d", "select2d"],
        "scrollZoom": True,
    })

    # Zoom hint
    st.markdown("""
    <div style="font-family: Space Mono; font-size:0.62rem; color:#2a2a5a; text-align:center; margin-top:-8px;">
        💡 Tip: Use the zoom controls above or scroll on the chart to zoom in · Pan by dragging
        · Change "View range" in sidebar for preset zoom levels
    </div>
    """, unsafe_allow_html=True)

    # Event details table
    st.markdown("### 📋 All Events — Sortable Reference")
    import pandas as pd

    event_rows = []
    for ev in events:
        if ev.get("category") not in selected_cats:
            continue
        cal = age_to_cosmic_year(ev["age_years"])
        scale_pos = age_to_scale(ev["age_years"], scale_name)
        event_rows.append({
            "Icon": ev.get("icon", "●"),
            "Event": ev["name"],
            "Category": CATEGORY_LABELS.get(ev.get("category",""), ev.get("category","")),
            "Years Ago": years_ago_to_human_readable(ev["age_years"]),
            "Cosmic Calendar": cal["display"],
            f"{scale_name} Position": scale_pos["display"],
        })

    df = pd.DataFrame(event_rows)
    st.dataframe(df, use_container_width=True, hide_index=True, height=400)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3: HUMAN ERA ZOOM
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### 🔬 Zooming into the Last Cosmic Second")
    st.markdown("""
    <div style="font-family: Space Mono; font-size:0.78rem; color:#8899bb; margin-bottom:20px; max-width:680px;">
        All of recorded human history — every civilization, every war, every discovery, 
        every human life ever lived — occurs within the last tiny fraction of the 
        last second of December 31st on the Cosmic Calendar.
        <br><br>
        Let's zoom in.
    </div>
    """, unsafe_allow_html=True)

    # Nested zoom levels showing the last moments
    zoom_levels = [
        ("Last 5 million years",  5e6,   "Hominins, ice ages, first humans"),
        ("Last 1 million years",  1e6,   "Homo erectus to Homo sapiens"),
        ("Last 100,000 years",    1e5,   "Anatomically modern humans"),
        ("Last 10,000 years",     1e4,   "Agriculture to industrial revolution"),
        ("Last 1,000 years",      1e3,   "Medieval to modern era"),
        ("Last 100 years",        100,   "20th century to present"),
    ]

    for label, years, desc in zoom_levels:
        pct_of_universe = years / UNIVERSE_AGE_YEARS * 100
        cosmic_seconds = (years / UNIVERSE_AGE_YEARS) * 365.25 * 24 * 3600
        cosmic_ms = cosmic_seconds * 1000

        st.markdown(f"""
        <div class="cosmic-card" style="margin:6px 0; padding:12px 16px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <div style="font-family: Orbitron; font-size:0.68rem; color:#4FC3F7; 
                                letter-spacing:0.08em;">{label}</div>
                    <div style="font-family: Space Mono; font-size:0.65rem; color:#6677aa; margin-top:2px;">{desc}</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-family: Space Mono; font-size:0.72rem; color:#e8f0fe;">
                        {'%.8f' % pct_of_universe}% of cosmic time
                    </div>
                    <div style="font-family: Space Mono; font-size:0.65rem; color:#CE93D8;">
                        = {'%.6f' % cosmic_seconds if cosmic_seconds >= 0.001 else f'{cosmic_ms:.6f} ms'} cosmic seconds
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Human history events only
    st.markdown("### Human History on the Cosmic Scale")

    human_events = [e for e in events if e.get("category") in ("human",) 
                    and e["age_years"] <= 1e6]
    human_events_all = [e for e in events if e.get("category") in ("human", "life")
                        and e["age_years"] <= 10e6]

    for ev in sorted(human_events, key=lambda x: x["age_years"], reverse=True):
        cal = age_to_cosmic_year(ev["age_years"])
        cosmic_seconds_ago = (ev["age_years"] / UNIVERSE_AGE_YEARS) * 365.25 * 24 * 3600
        color = CATEGORY_COLORS.get(ev.get("category"), "#aaaaaa")

        if cosmic_seconds_ago < 0.001:
            time_str = f"{cosmic_seconds_ago * 1e6:.4f} μs ago on Cosmic Calendar"
        elif cosmic_seconds_ago < 1:
            time_str = f"{cosmic_seconds_ago * 1000:.4f} ms ago on Cosmic Calendar"
        else:
            time_str = f"{cosmic_seconds_ago:.4f} s ago on Cosmic Calendar"

        st.markdown(f"""
        <div style="display:flex; gap:16px; align-items:flex-start; padding:10px 14px;
                    margin:4px 0; background:rgba(13,13,43,0.5);
                    border-radius:8px; border-left: 2px solid {color}66;">
            <div style="font-size:1.5rem; flex-shrink:0;">{ev.get('icon','●')}</div>
            <div style="flex:1;">
                <div style="display:flex; justify-content:space-between; flex-wrap:wrap; gap:8px;">
                    <div>
                        <div style="font-family:Orbitron; font-size:0.65rem; color:{color}; 
                                    letter-spacing:0.06em;">{ev['name']}</div>
                        <div style="font-family:Space Mono; font-size:0.65rem; color:#8899bb; 
                                    margin-top:3px; max-width:480px; line-height:1.5;">
                            {ev.get('description', '')}
                        </div>
                    </div>
                    <div style="text-align:right; flex-shrink:0;">
                        <div style="font-family:Space Mono; font-size:0.65rem; color:#e8f0fe;">
                            {years_ago_to_human_readable(ev['age_years'])}
                        </div>
                        <div style="font-family:Space Mono; font-size:0.6rem; color:{color}88;">
                            {time_str}
                        </div>
                        <div style="font-family:Space Mono; font-size:0.6rem; color:#4a5270;">
                            Cosmic Cal: {cal['display']}
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4: PERSONAL SCALE
# ═══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("### 🧬 Your Place in the Cosmos")

    col_input, col_stats = st.columns([1, 2])

    with col_input:
        st.markdown("""
        <div style="font-family: Orbitron; font-size:0.65rem; color:#81C784; 
                    letter-spacing:0.1em; margin-bottom:12px;">
            ENTER YOUR BIRTH YEAR
        </div>
        """, unsafe_allow_html=True)
        personal_year = st.number_input(
            "Birth Year",
            value=birth_year if birth_year else 1990,
            min_value=1900, max_value=2024, step=1,
            key="personal_birth_year"
        )

        your_name = st.text_input("Your name (optional)", value="", placeholder="e.g. Cosmos Explorer")

    with col_stats:
        stats = compute_personal_stats(personal_year)
        name_str = your_name if your_name else "You"

        st.markdown(f"""
        <div class="cosmic-card">
            <div style="font-family: Orbitron; font-size:0.7rem; color:#81C784; 
                        letter-spacing:0.08em; margin-bottom:14px;">
                ✨ {name_str.upper()}'S COSMIC PROFILE
            </div>
            <table style="width:100%; font-family: Space Mono; font-size:0.72rem; 
                          border-collapse: collapse;">
                <tr>
                    <td style="color:#6677aa; padding:5px 0; width:55%;">Age</td>
                    <td style="color:#e8f0fe; text-align:right;">{stats['age_years']} years</td>
                </tr>
                <tr>
                    <td style="color:#6677aa; padding:5px 0;">Your life on Cosmic Calendar</td>
                    <td style="color:#CE93D8; text-align:right; font-size:0.65rem;">
                        {stats['your_age_cosmic_seconds']:.6f} seconds
                    </td>
                </tr>
                <tr>
                    <td style="color:#6677aa; padding:5px 0;">Your birth on Cosmic Calendar</td>
                    <td style="color:#81C784; text-align:right; font-size:0.65rem;">
                        {stats['birth_cosmic_date']['display']}
                    </td>
                </tr>
                <tr>
                    <td style="color:#6677aa; padding:5px 0;">Your age in cosmic microseconds</td>
                    <td style="color:#FFD54F; text-align:right;">
                        {stats['your_age_cosmic_microseconds']:.0f} μs
                    </td>
                </tr>
                <tr>
                    <td style="color:#6677aa; padding:5px 0;">Your life / universe age</td>
                    <td style="color:#e8f0fe; text-align:right;">
                        {stats['pct_of_universe']:.12f}%
                    </td>
                </tr>
                <tr>
                    <td style="color:#6677aa; padding:5px 0;">Universes that fit in your life</td>
                    <td style="color:#e8f0fe; text-align:right;">
                        1 in {1/stats['universes_in_life']:.0f}
                    </td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Perspective statements
    st.markdown("### Perspective")

    age = stats["age_years"]
    cosmic_s = stats["your_age_cosmic_seconds"]
    cosmic_us = stats["your_age_cosmic_microseconds"]

    perspectives = [
        (
            "🌌", "You vs. The Universe",
            f"The universe is {UNIVERSE_AGE_YEARS/age:.0f} times older than you.",
            f"If the universe were a 80-year-old person, you would have been born in the last "
            f"{80 * age / UNIVERSE_AGE_YEARS * 365.25 * 24 * 3600:.2f} seconds of their life.",
        ),
        (
            "⭐", "You vs. The Stars",
            f"The first stars formed {13.5e9/age:.0f} times before you were born.",
            f"Billions of stars were born and died before your atoms were assembled into you.",
        ),
        (
            "🌍", "You vs. Earth",
            f"Earth is {4.54e9/age:.0f} times older than you.",
            f"In that time, Earth has completed {4.54e9/age:.0f} orbits around the Sun "
            f"before you arrived.",
        ),
        (
            "🦠", "You vs. Life",
            f"Life on Earth is {3.8e9/age:.0f} times older than you.",
            f"Billions of generations of evolution — from single cells to complex brains — "
            f"were required to produce you.",
        ),
        (
            "🧬", "Your atomic ancestry",
            "Every atom in your body was forged in the heart of a star.",
            "The iron in your blood was made in a supernova explosion billions of years before "
            "the Sun formed. You are, quite literally, made of stardust.",
        ),
        (
            "🕐", "The weight of now",
            f"In {cosmic_s:.6f} cosmic seconds, you have experienced your entire life.",
            f"Yet in those {cosmic_us:.0f} cosmic microseconds, you have felt wonder, love, "
            f"loss, and curiosity — things the universe has never experienced except through you.",
        ),
    ]

    p_cols = st.columns(2)
    for i, (icon, title, headline, body) in enumerate(perspectives):
        with p_cols[i % 2]:
            st.markdown(f"""
            <div class="cosmic-card" style="margin:6px 0;">
                <div style="font-size:1.6rem; margin-bottom:8px;">{icon}</div>
                <div style="font-family: Orbitron; font-size:0.65rem; color:#CE93D8; 
                            letter-spacing:0.08em; margin-bottom:8px;">{title}</div>
                <div style="font-family: Space Mono; font-size:0.73rem; color:#e8f0fe; 
                            margin-bottom:6px; line-height:1.5;">{headline}</div>
                <div style="font-family: Space Mono; font-size:0.65rem; color:#6677aa; 
                            line-height:1.7;">{body}</div>
            </div>
            """, unsafe_allow_html=True)

    # Carl Sagan quote
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    > *"Look again at that dot. That's here. That's home. That's us. On it everyone you love, everyone you know, 
    > everyone you ever heard of, every human being who ever was, lived out their lives... 
    > on a mote of dust suspended in a sunbeam."*
    > 
    > — Carl Sagan, *Pale Blue Dot*, 1994
    """)
