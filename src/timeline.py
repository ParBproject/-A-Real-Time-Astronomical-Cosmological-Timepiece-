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
import math
import os
from datetime import datetime, timezone

# ── Constants ─────────────────────────────────────────────────────────────────

UNIVERSE_AGE_YEARS = 13.8e9        # years

# The Cosmic Calendar is one civil year: January has 31 days and February
# has 28. A mean year of 365.25 days has no 31 December that lines up with
# "seconds before midnight", so the analogy uses 365 days and the same
# length for every "cosmic second" below. Leap days are handled in the
# astronomical clock, not in this scale.
MONTH_DAYS = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
MONTH_NAMES = (
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
)
COSMIC_YEAR_DAYS = sum(MONTH_DAYS)  # 365
SECONDS_PER_DAY = 86400.0
SECONDS_PER_HOUR = 3600.0
SECONDS_PER_YEAR = COSMIC_YEAR_DAYS * SECONDS_PER_DAY
UNIVERSE_AGE_SECONDS = UNIVERSE_AGE_YEARS * SECONDS_PER_YEAR
_MICROS_PER_SECOND = 1_000_000
_YEAR_MICROS = int(SECONDS_PER_YEAR * _MICROS_PER_SECOND)
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
        # 1 at the Big Bang, 0 at the present.
        ev["pct_of_universe"] = (age_bya * 1e9) / UNIVERSE_AGE_YEARS
        # Timeline coordinate: 0 at the Big Bang, 1 at the present.
        ev["pct_from_start"] = 1.0 - ev["pct_of_universe"]

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

def _fraction_from_age(age_years: float) -> float:
    """0 at the Big Bang, 1 at the present."""
    fraction = 1.0 - (age_years / UNIVERSE_AGE_YEARS)
    return max(0.0, min(1.0, fraction))


def _calendar_from_elapsed_micros(elapsed_us: int) -> dict:
    """Map microseconds since 1 January 00:00 onto a 365-day civil year."""
    elapsed_us = min(max(int(elapsed_us), 0), _YEAR_MICROS - 1)
    micros_per_day = int(SECONDS_PER_DAY * _MICROS_PER_SECOND)
    day_of_year = elapsed_us // micros_per_day
    day_us = elapsed_us % micros_per_day

    month_index = 0
    day_in_month = day_of_year
    for i, length in enumerate(MONTH_DAYS):
        if day_in_month < length:
            month_index = i
            break
        day_in_month -= length

    hour = day_us // 3_600_000_000
    day_us %= 3_600_000_000
    minute = day_us // 60_000_000
    day_us %= 60_000_000
    whole_second = day_us // _MICROS_PER_SECOND
    millis = (day_us % _MICROS_PER_SECOND) // 1_000
    second = whole_second + millis / 1000.0
    month_name = MONTH_NAMES[month_index]
    return {
        "month": month_index + 1,
        "day": int(day_in_month) + 1,
        "hour": int(hour),
        "minute": int(minute),
        "second": second,
        "month_name": month_name,
        "display": (
            f"{month_name} {int(day_in_month) + 1}, "
            f"{int(hour):02d}:{int(minute):02d}:{int(whole_second):02d}.{int(millis):03d}"
        ),
    }


def age_to_cosmic_year(age_years: float) -> dict:
    """
    Convert years before the present to a Cosmic Calendar date.

    The Big Bang is 1 January 00:00:00.000. The present is the last
    millisecond of 31 December, not the start of January and not 1 December.
    Months have their real civil lengths.
    """
    fraction = _fraction_from_age(age_years)
    if fraction >= 1.0:
        # Last millisecond of the year. fraction * year-length is the first
        # instant of the next 1 January, which is not "now".
        elapsed_us = _YEAR_MICROS - 1_000
    elif fraction <= 0.0:
        elapsed_us = 0
    else:
        elapsed_us = int(math.floor(fraction * _YEAR_MICROS))

    result = _calendar_from_elapsed_micros(elapsed_us)
    result["fraction"] = fraction
    return result


def age_to_scale(age_years: float, scale_name: str) -> dict:
    """
    Convert cosmic age (years ago) to position on arbitrary time scale.
    Returns fraction (0=Big Bang, 1=now) and human-readable time string.
    """
    scale = SCALES.get(scale_name, SCALES["Cosmic Year"])
    duration = scale["duration_s"]

    fraction = _fraction_from_age(age_years)
    elapsed_s = fraction * duration
    if scale_name == "Cosmic Year":
        display = age_to_cosmic_year(age_years)["display"]
    else:
        display = _format_scale_time(elapsed_s, scale_name, duration)

    return {
        "fraction": fraction,
        "elapsed_seconds": elapsed_s,
        "display": display,
        "remaining_seconds": duration - elapsed_s,
    }


def _format_scale_time(elapsed_s: float, scale_name: str, duration: float) -> str:
    """Format elapsed seconds into human-readable time for a given scale."""
    # An exact end (fraction == 1) is the last instant of the scale, not
    # 24:00:00 or 60 minutes, which are the start of the next unit.
    at_end = elapsed_s >= duration - 1e-9
    if scale_name == "Cosmic Day" and at_end:
        return "23:59:59"
    if scale_name == "Cosmic Hour" and at_end:
        return "59m 59s 999ms"
    if scale_name == "Cosmic Day":
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

    # How many Cosmic Calendar seconds a human lifetime represents.
    lifespan_as_cosmic_seconds = (HUMAN_LIFESPAN_YEARS / UNIVERSE_AGE_YEARS) * SECONDS_PER_YEAR
    age_as_cosmic_seconds = (age_years / UNIVERSE_AGE_YEARS) * SECONDS_PER_YEAR
    age_as_cosmic_ms = age_as_cosmic_seconds * 1000
    age_as_cosmic_us = age_as_cosmic_ms * 1000

    # Born `age_years` before the present: the last moments of 31 December.
    birth_cosmic = age_to_cosmic_year(age_years)

    # Fraction of cosmic time occupied by an 80-year life.
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
