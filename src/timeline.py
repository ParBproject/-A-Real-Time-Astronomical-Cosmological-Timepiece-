"""
timeline.py — Cosmic Calendar logic and event scaling utilities.

The Cosmic Calendar (popularized by Carl Sagan) compresses the 13.8-billion-year
history of the universe into a single Earth year. This module handles:
- Loading and enriching timeline events from events.json
- Scaling to different reference frames (year, day, hour, human lifetime)
- Computing where "now" falls on each scale
- Positioning historical events for display
"""

import json
import os
import numpy as np
from datetime import datetime, timezone
from typing import Optional

# ── Constants ─────────────────────────────────────────────────────────────────

UNIVERSE_AGE_YEARS = 13.8e9        # years
UNIVERSE_AGE_SECONDS = UNIVERSE_AGE_YEARS * 365.25 * 24 * 3600

SECONDS_PER_YEAR = 365.25 * 24 * 3600
SECONDS_PER_DAY = 86400.0
SECONDS_PER_HOUR = 3600.0
HUMAN_LIFESPAN_YEARS = 80.0
HUMAN_LIFESPAN_SECONDS = HUMAN_LIFESPAN_YEARS * SECONDS_PER_YEAR

# Scale names and their durations in real seconds (maps to full universe age)
SCALES = {
    "Cosmic Year":     {"duration_s": SECONDS_PER_YEAR,              "label": "1 Year"},
    "Cosmic Day":      {"duration_s": SECONDS_PER_DAY,               "label": "1 Day"},
    "Cosmic Hour":     {"duration_s": SECONDS_PER_HOUR,              "label": "1 Hour"},
    "Human Lifetime":  {"duration_s": HUMAN_LIFESPAN_SECONDS,        "label": "80 Years"},
}


# ─── Load events ──────────────────────────────────────────────────────────────

def load_events() -> list[dict]:
    """Load cosmic timeline events from assets/events.json and compute derived fields."""
    asset_path = os.path.join(
        os.path.dirname(__file__), "..", "assets", "events.json"
    )
    try:
        with open(asset_path) as f:
            events = json.load(f)
    except Exception:
        events = _fallback_events()

    # Enrich each event
    for ev in events:
        age_bya = ev.get("age_bya", 0.0)
        ev["age_years"] = age_bya * 1e9
        ev["years_ago"] = age_bya * 1e9
        ev["pct_of_universe"] = (age_bya * 1e9) / UNIVERSE_AGE_YEARS  # 0=Big Bang, 0→1 means older
        ev["pct_from_start"] = 1.0 - ev["pct_of_universe"]           # 0=Big Bang,  1=now

    # Sort oldest first
    events.sort(key=lambda e: -e["age_bya"])
    return events


def _fallback_events():
    """Minimal fallback if JSON file is missing."""
    return [
        {"name": "Big Bang", "age_bya": 13.8, "category": "cosmological",
         "icon": "💥", "description": "The universe begins.", "color": "#FF6B35"},
        {"name": "Earth Forms", "age_bya": 4.54, "category": "solar",
         "icon": "🌍", "description": "Earth coalesces.", "color": "#4FC3F7"},
        {"name": "First Life", "age_bya": 3.8, "category": "life",
         "icon": "🦠", "description": "Life emerges.", "color": "#81C784"},
        {"name": "Present Moment", "age_bya": 0.0, "category": "human",
         "icon": "⏱️", "description": "You are here.", "color": "#FFFFFF"},
    ]


# ─── Cosmic Calendar conversions ─────────────────────────────────────────────

def age_to_cosmic_year(age_years: float) -> dict:
    """
    Convert a cosmic age (years before present) to a position on the Cosmic Calendar.
    Returns month (1-12), day (1-31), hour (0-23), minute (0-59), second (0-59).
    """
    fraction = 1.0 - (age_years / UNIVERSE_AGE_YEARS)  # 0 = Big Bang, 1 = now
    fraction = max(0.0, min(1.0, fraction))

    total_seconds = fraction * SECONDS_PER_YEAR
    # Month (1-indexed)
    month_seconds = SECONDS_PER_YEAR / 12.0
    month = min(12, int(total_seconds / month_seconds) + 1)

    remaining = total_seconds % month_seconds
    day_seconds = month_seconds / 31.0  # approx
    day = min(31, int(remaining / day_seconds) + 1)

    remaining2 = remaining % day_seconds
    hour = int(remaining2 / 3600) % 24
    minute = int((remaining2 % 3600) / 60)
    second = int(remaining2 % 60)

    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    return {
        "month": month,
        "day": day,
        "hour": hour,
        "minute": minute,
        "second": second,
        "month_name": month_names[month - 1],
        "display": f"{month_names[month-1]} {day}, {hour:02d}:{minute:02d}:{second:02d}",
        "fraction": fraction,
    }


def age_to_scale(age_years: float, scale_name: str) -> dict:
    """
    Convert cosmic age (years ago) to position on arbitrary time scale.
    Returns fraction (0=Big Bang, 1=now) and human-readable time string.
    """
    scale = SCALES.get(scale_name, SCALES["Cosmic Year"])
    duration = scale["duration_s"]

    fraction = 1.0 - (age_years / UNIVERSE_AGE_YEARS)
    fraction = max(0.0, min(1.0, fraction))
    elapsed_s = fraction * duration

    return {
        "fraction": fraction,
        "elapsed_seconds": elapsed_s,
        "display": _format_scale_time(elapsed_s, scale_name),
        "remaining_seconds": duration - elapsed_s,
    }


def _format_scale_time(elapsed_s: float, scale_name: str) -> str:
    """Format elapsed seconds into human-readable time for a given scale."""
    if scale_name == "Cosmic Year":
        month_s = SECONDS_PER_YEAR / 12.0
        m = min(12, int(elapsed_s / month_s) + 1)
        rem = elapsed_s % month_s
        d = min(31, int(rem / (month_s / 31)) + 1)
        h = int((rem % (month_s / 31)) / 3600) % 24
        mi = int(((rem % (month_s / 31)) % 3600) / 60)
        names = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        return f"{names[m-1]} {d}, {h:02d}:{mi:02d}"
    elif scale_name == "Cosmic Day":
        h = int(elapsed_s / 3600)
        m = int((elapsed_s % 3600) / 60)
        s = int(elapsed_s % 60)
        return f"{h:02d}:{m:02d}:{s:02d}"
    elif scale_name == "Cosmic Hour":
        m = int(elapsed_s / 60)
        s = int(elapsed_s % 60)
        ms = int((elapsed_s % 1) * 1000)
        return f"{m:02d}m {s:02d}s {ms:03d}ms"
    elif scale_name == "Human Lifetime":
        years = elapsed_s / SECONDS_PER_YEAR
        if years < 1:
            days = int(elapsed_s / 86400)
            return f"{days} days old"
        return f"Age {years:.1f}"
    return f"{elapsed_s:.2f}s"


# ─── Human history timescale ──────────────────────────────────────────────────

def years_ago_to_human_readable(years: float) -> str:
    """Convert a 'years ago' number to a readable string."""
    if years == 0:
        return "Right now"
    elif years < 1:
        months = int(years * 12)
        return f"{months} month{'s' if months != 1 else ''} ago"
    elif years < 100:
        return f"{years:.1f} years ago"
    elif years < 10_000:
        return f"{int(years):,} years ago"
    elif years < 1_000_000:
        ky = years / 1000
        return f"{ky:.1f} thousand years ago"
    elif years < 1_000_000_000:
        my = years / 1_000_000
        return f"{my:.0f} million years ago"
    else:
        by = years / 1_000_000_000
        return f"{by:.2f} billion years ago"


def format_cosmic_fraction(fraction: float) -> str:
    """
    Given a fraction of universe history (0=Big Bang, 1=now),
    express how close to the end (now) it is in human terms.
    """
    remaining = 1.0 - fraction
    remaining_years = remaining * UNIVERSE_AGE_YEARS

    if remaining_years < 1:
        secs = remaining_years * SECONDS_PER_YEAR
        return f"~{secs:.6f} seconds before 'now' on Cosmic Calendar"
    return years_ago_to_human_readable(remaining_years)


# ─── What second of the Cosmic Year are we at? ───────────────────────────────

def get_current_cosmic_position() -> dict:
    """
    Return the current position in the Cosmic Calendar and all scales.
    'now' = Dec 31, 23:59:59.xxx on the Cosmic Year.
    """
    # We ARE at the present moment — fraction = 1.0 exactly
    cosmic = age_to_cosmic_year(0.0)
    day_pos = age_to_scale(0.0, "Cosmic Day")
    hour_pos = age_to_scale(0.0, "Cosmic Hour")
    lifetime_pos = age_to_scale(0.0, "Human Lifetime")
    return {
        "cosmic_year": cosmic,
        "cosmic_day": day_pos,
        "cosmic_hour": hour_pos,
        "human_lifetime": lifetime_pos,
    }


# ─── User personal timeline ───────────────────────────────────────────────────

def compute_personal_stats(birth_year: int) -> dict:
    """Compute how a person's life fits into the cosmic timeline."""
    current_year = datetime.now(timezone.utc).year
    age_years = current_year - birth_year

    # How many 'Cosmic Calendar seconds' does a human lifetime represent?
    lifespan_as_cosmic_seconds = (HUMAN_LIFESPAN_YEARS / UNIVERSE_AGE_YEARS) * SECONDS_PER_YEAR
    age_as_cosmic_seconds = (age_years / UNIVERSE_AGE_YEARS) * SECONDS_PER_YEAR
    age_as_cosmic_ms = age_as_cosmic_seconds * 1000
    age_as_cosmic_us = age_as_cosmic_ms * 1000

    # What cosmic date were you born?
    birth_years_ago = UNIVERSE_AGE_YEARS - (UNIVERSE_AGE_YEARS - age_years)  # = age_years
    # Born 'age_years' years before present = very close to Dec 31 23:59:59
    birth_cosmic = age_to_cosmic_year(age_years)

    # How many Big Bang equivalents fit in a human life?
    universes_in_life = HUMAN_LIFESPAN_YEARS / UNIVERSE_AGE_YEARS

    return {
        "age_years": age_years,
        "birth_year": birth_year,
        "lifespan_cosmic_seconds": lifespan_as_cosmic_seconds,
        "your_age_cosmic_seconds": age_as_cosmic_seconds,
        "your_age_cosmic_ms": age_as_cosmic_ms,
        "your_age_cosmic_microseconds": age_as_cosmic_us,
        "universes_in_life": universes_in_life,
        "birth_cosmic_date": birth_cosmic,
        "pct_of_universe": (age_years / UNIVERSE_AGE_YEARS) * 100,
    }


# ─── Category colors ──────────────────────────────────────────────────────────

CATEGORY_COLORS = {
    "cosmological": "#FF6B35",
    "stellar":      "#FFD700",
    "solar":        "#FFA726",
    "life":         "#66BB6A",
    "human":        "#64B5F6",
}

CATEGORY_LABELS = {
    "cosmological": "🌌 Cosmological",
    "stellar":      "⭐ Stellar",
    "solar":        "☀️  Solar System",
    "life":         "🦠 Life on Earth",
    "human":        "🧠 Human History",
}
