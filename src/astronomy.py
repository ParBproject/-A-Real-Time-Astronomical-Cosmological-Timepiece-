"""
astronomy.py — Core astronomical calculations using Skyfield and Astropy.

Design choice: Skyfield is preferred over Astropy for planet/moon positions because:
1. Skyfield uses NASA JPL DE440 ephemeris (very accurate, sub-arcsecond)
2. Simpler API for alt/az horizon coordinates needed for sky map
3. Built-in moon phase calculation
4. No ERFA dependency issues on some platforms

Astropy is used for: sidereal time, coordinate transforms, and utility math.
"""

import numpy as np
import streamlit as st
from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple

# ── Skyfield ──────────────────────────────────────────────────────────────────
try:
    from skyfield.api import load, wgs84, Star
    from skyfield.data import mpc
    from skyfield import almanac
    SKYFIELD_OK = True
except ImportError:
    SKYFIELD_OK = False

# ── Astropy (fallback helpers) ────────────────────────────────────────────────
try:
    from astropy.time import Time
    from astropy.coordinates import (
        EarthLocation, AltAz, ICRS,
        get_body, get_body_barycentric, get_sun
    )
    import astropy.units as u
    ASTROPY_OK = True
except ImportError:
    ASTROPY_OK = False


# ─── Ephemeris loading (cached) ───────────────────────────────────────────────

@st.cache_resource(show_spinner="Loading star catalogs…")
def load_ephemeris():
    """Load the Skyfield DE421 ephemeris (small, fast, accurate enough for display)."""
    if not SKYFIELD_OK:
        return None, None
    ts = load.timescale()
    try:
        eph = load("de421.bsp")
    except Exception:
        try:
            from skyfield.api import Loader
            load2 = Loader(".")
            eph = load2("de421.bsp")
        except Exception:
            eph = None
    return ts, eph


# ─── Planet data ─────────────────────────────────────────────────────────────

PLANETS = {
    "Mercury": {"skyfield_name": "mercury", "symbol": "☿", "color": "#B5B5B5", "size": 6},
    "Venus":   {"skyfield_name": "venus",   "symbol": "♀", "color": "#E8D5A3", "size": 9},
    "Mars":    {"skyfield_name": "mars",    "symbol": "♂", "color": "#C1440E", "size": 7},
    "Jupiter": {"skyfield_name": "jupiter barycenter", "symbol": "♃", "color": "#C88B3A", "size": 18},
    "Saturn":  {"skyfield_name": "saturn barycenter",  "symbol": "♄", "color": "#E4D191", "size": 15},
    "Uranus":  {"skyfield_name": "uranus barycenter",  "symbol": "⛢", "color": "#7DE8E8", "size": 11},
    "Neptune": {"skyfield_name": "neptune barycenter", "symbol": "♆", "color": "#4B70DD", "size": 11},
}


def get_planet_positions(
    lat: float, lon: float, dt: Optional[datetime] = None
) -> list[dict]:
    """
    Return altitude, azimuth, and metadata for each planet at the given
    observer location and time.

    Returns list of dicts with keys:
        name, symbol, color, size, alt, az, ra, dec, visible, distance_au
    """
    ts, eph = load_ephemeris()

    if dt is None:
        dt = datetime.now(timezone.utc)
    elif dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    results = []

    if SKYFIELD_OK and ts and eph:
        t = ts.from_datetime(dt)
        observer = wgs84.latlon(lat, lon)
        earth = eph["earth"]

        for name, meta in PLANETS.items():
            try:
                planet = eph[meta["skyfield_name"]]
                obs_pos = earth + observer
                astrometric = obs_pos.at(t).observe(planet)
                apparent = astrometric.apparent()
                alt, az, distance = apparent.altaz()
                ra, dec, _ = apparent.radec()

                results.append({
                    "name": name,
                    "symbol": meta["symbol"],
                    "color": meta["color"],
                    "size": meta["size"],
                    "alt": alt.degrees,
                    "az": az.degrees,
                    "ra": ra.hours,
                    "dec": dec.degrees,
                    "visible": alt.degrees > 0,
                    "distance_au": distance.au,
                })
            except Exception:
                pass
    else:
        # Simplified fallback using rough orbital elements
        results = _fallback_planet_positions(lat, lon, dt)

    return results


def _fallback_planet_positions(lat, lon, dt):
    """Very rough planet positions for fallback (no skyfield)."""
    # Days since J2000.0
    j2000 = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    d = (dt - j2000).total_seconds() / 86400.0

    # Approximate mean longitudes (degrees) at J2000 + daily motion
    planet_data = {
        "Mercury": {"L0": 252.251, "dL": 4.092377,  "symbol": "☿", "color": "#B5B5B5", "size": 6},
        "Venus":   {"L0": 181.980, "dL": 1.602136,  "symbol": "♀", "color": "#E8D5A3", "size": 9},
        "Mars":    {"L0": 355.433, "dL": 0.524039,  "symbol": "♂", "color": "#C1440E", "size": 7},
        "Jupiter": {"L0":  34.351, "dL": 0.083056,  "symbol": "♃", "color": "#C88B3A", "size": 18},
        "Saturn":  {"L0":  50.077, "dL": 0.033371,  "symbol": "♄", "color": "#E4D191", "size": 15},
        "Uranus":  {"L0": 314.055, "dL": 0.011698,  "symbol": "⛢", "color": "#7DE8E8", "size": 11},
        "Neptune": {"L0": 304.349, "dL": 0.005965,  "symbol": "♆", "color": "#4B70DD", "size": 11},
    }

    lst_hours = _approx_sidereal_time(lon, dt)
    lst_deg = lst_hours * 15.0

    results = []
    for name, p in planet_data.items():
        ecliptic_lon = (p["L0"] + p["dL"] * d) % 360
        # Very rough RA ≈ ecliptic longitude (ignores inclination)
        ra = ecliptic_lon / 15.0  # hours
        dec = 23.4 * np.sin(np.radians(ecliptic_lon))  # rough

        ha = lst_deg - ecliptic_lon  # hour angle in degrees
        alt, az = _ha_dec_to_altaz(ha, dec, lat)

        results.append({
            "name": name,
            "symbol": p["symbol"],
            "color": p["color"],
            "size": p["size"],
            "alt": alt,
            "az": az,
            "ra": ra,
            "dec": dec,
            "visible": alt > 0,
            "distance_au": 1.5,
        })
    return results


# ─── Sun ──────────────────────────────────────────────────────────────────────

def get_sun_position(lat: float, lon: float, dt: Optional[datetime] = None) -> dict:
    """Return Sun's altitude, azimuth, RA, Dec."""
    if dt is None:
        dt = datetime.now(timezone.utc)
    elif dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    ts, eph = load_ephemeris()

    if SKYFIELD_OK and ts and eph:
        t = ts.from_datetime(dt)
        observer = wgs84.latlon(lat, lon)
        earth = eph["earth"]
        sun = eph["sun"]
        obs_pos = earth + observer
        apparent = obs_pos.at(t).observe(sun).apparent()
        alt, az, _ = apparent.altaz()
        ra, dec, _ = apparent.radec()
        return {
            "alt": alt.degrees, "az": az.degrees,
            "ra": ra.hours, "dec": dec.degrees,
            "above_horizon": alt.degrees > 0,
        }

    # Fallback
    j2000 = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    d = (dt - j2000).total_seconds() / 86400.0
    L = (280.461 + 0.9856474 * d) % 360
    g = np.radians((357.528 + 0.9856003 * d) % 360)
    lam = np.radians(L + 1.915 * np.sin(g) + 0.020 * np.sin(2 * g))
    eps = np.radians(23.439 - 0.0000004 * d)
    ra_rad = np.arctan2(np.cos(eps) * np.sin(lam), np.cos(lam))
    dec_rad = np.arcsin(np.sin(eps) * np.sin(lam))
    ra_h = np.degrees(ra_rad) / 15.0 % 24
    dec_d = np.degrees(dec_rad)

    lst = _approx_sidereal_time(lon, dt)
    ha = (lst - ra_h) * 15.0
    alt, az = _ha_dec_to_altaz(ha, dec_d, lat)
    return {"alt": alt, "az": az, "ra": ra_h, "dec": dec_d, "above_horizon": alt > 0}


# ─── Moon ─────────────────────────────────────────────────────────────────────

def get_moon_data(lat: float, lon: float, dt: Optional[datetime] = None) -> dict:
    """Return Moon position and phase (0–1, where 0/1=new, 0.5=full)."""
    if dt is None:
        dt = datetime.now(timezone.utc)
    elif dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    ts, eph = load_ephemeris()
    phase = 0.5
    illumination = 50.0

    if SKYFIELD_OK and ts and eph:
        t = ts.from_datetime(dt)
        observer = wgs84.latlon(lat, lon)
        earth = eph["earth"]
        moon = eph["moon"]
        sun = eph["sun"]

        obs_pos = earth + observer
        apparent = obs_pos.at(t).observe(moon).apparent()
        alt, az, _ = apparent.altaz()
        ra, dec, _ = apparent.radec()

        # Phase angle
        e = earth.at(t)
        _, mlon, _ = e.observe(moon).apparent().ecliptic_latlon()
        _, slon, _ = e.observe(sun).apparent().ecliptic_latlon()
        phase_angle = (mlon.degrees - slon.degrees) % 360
        phase = phase_angle / 360.0
        illumination = (1 - np.cos(np.radians(phase_angle))) / 2 * 100

        return {
            "alt": alt.degrees, "az": az.degrees,
            "ra": ra.hours, "dec": dec.degrees,
            "phase": phase, "illumination": illumination,
            "above_horizon": alt.degrees > 0,
            "phase_name": _phase_name(phase),
        }

    # Fallback
    j2000 = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    d = (dt - j2000).total_seconds() / 86400.0
    moon_lon = (218.316 + 13.176396 * d) % 360
    sun_lon = (280.461 + 0.9856474 * d) % 360
    phase_angle = (moon_lon - sun_lon) % 360
    phase = phase_angle / 360.0

    ra_h = moon_lon / 15.0
    dec_d = 5.13 * np.sin(np.radians(moon_lon))
    lst = _approx_sidereal_time(lon, dt)
    ha = (lst - ra_h) * 15.0
    alt, az = _ha_dec_to_altaz(ha, dec_d, lat)

    illumination = (1 - np.cos(np.radians(phase_angle))) / 2 * 100

    return {
        "alt": alt, "az": az,
        "ra": ra_h, "dec": dec_d,
        "phase": phase, "illumination": illumination,
        "above_horizon": alt > 0,
        "phase_name": _phase_name(phase),
    }


def _phase_name(phase: float) -> str:
    if phase < 0.03 or phase > 0.97:
        return "🌑 New Moon"
    elif phase < 0.22:
        return "🌒 Waxing Crescent"
    elif phase < 0.28:
        return "🌓 First Quarter"
    elif phase < 0.47:
        return "🌔 Waxing Gibbous"
    elif phase < 0.53:
        return "🌕 Full Moon"
    elif phase < 0.72:
        return "🌖 Waning Gibbous"
    elif phase < 0.78:
        return "🌗 Last Quarter"
    else:
        return "🌘 Waning Crescent"


def moon_phase_icon(phase: float) -> str:
    """Return emoji moon phase icon."""
    icons = ["🌑", "🌒", "🌓", "🌔", "🌕", "🌖", "🌗", "🌘"]
    idx = int((phase * 8) % 8)
    return icons[idx]


# ─── Sidereal Time ────────────────────────────────────────────────────────────

def get_sidereal_time(lon: float, dt: Optional[datetime] = None) -> float:
    """Return Local Sidereal Time in decimal hours."""
    if dt is None:
        dt = datetime.now(timezone.utc)
    elif dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    if ASTROPY_OK:
        t = Time(dt)
        lst = t.sidereal_time("apparent", longitude=f"{lon}d")
        return lst.hour
    return _approx_sidereal_time(lon, dt)


def _approx_sidereal_time(lon: float, dt: datetime) -> float:
    """Approximate Local Sidereal Time (hours)."""
    j2000 = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    d = (dt - j2000).total_seconds() / 86400.0
    gst = (18.697374558 + 24.06570982441908 * d) % 24
    lst = (gst + lon / 15.0) % 24
    return lst


def _ha_dec_to_altaz(ha_deg: float, dec_deg: float, lat_deg: float) -> Tuple[float, float]:
    """Convert Hour Angle + Declination to Altitude + Azimuth."""
    ha = np.radians(ha_deg)
    dec = np.radians(dec_deg)
    lat = np.radians(lat_deg)

    sin_alt = np.sin(dec) * np.sin(lat) + np.cos(dec) * np.cos(lat) * np.cos(ha)
    alt = np.degrees(np.arcsin(np.clip(sin_alt, -1, 1)))

    cos_az = (np.sin(dec) - np.sin(alt / 57.296) * np.sin(lat)) / \
             (np.cos(np.radians(alt)) * np.cos(lat) + 1e-10)
    az = np.degrees(np.arccos(np.clip(cos_az, -1, 1)))
    if np.sin(ha) > 0:
        az = 360 - az
    return alt, az


# ─── Sky Darkness ─────────────────────────────────────────────────────────────

def get_sky_state(sun_alt: float) -> dict:
    """Determine sky color and state based on Sun's altitude."""
    if sun_alt > 6:
        return {"name": "Day",    "sky_top": "#1a2d6e", "sky_bot": "#4a90d9",
                "star_opacity": 0.0, "glow": "#FFE87C"}
    elif sun_alt > 0:
        return {"name": "Day",    "sky_top": "#0d1b4a", "sky_bot": "#87ceeb",
                "star_opacity": 0.1, "glow": "#FFD700"}
    elif sun_alt > -6:
        return {"name": "Civil Twilight", "sky_top": "#0a0a2e", "sky_bot": "#FF6B35",
                "star_opacity": 0.4, "glow": "#FF8C42"}
    elif sun_alt > -12:
        return {"name": "Nautical Twilight", "sky_top": "#060621", "sky_bot": "#4B0082",
                "star_opacity": 0.7, "glow": "#9370DB"}
    elif sun_alt > -18:
        return {"name": "Astronomical Twilight", "sky_top": "#030316", "sky_bot": "#1a0535",
                "star_opacity": 0.9, "glow": "#6A0DAD"}
    else:
        return {"name": "Night",  "sky_top": "#000008", "sky_bot": "#050520",
                "star_opacity": 1.0, "glow": "#4169E1"}


# ─── Solar time ───────────────────────────────────────────────────────────────

def get_solar_time(lon: float, dt: Optional[datetime] = None) -> datetime:
    """Return approximate local solar time."""
    if dt is None:
        dt = datetime.now(timezone.utc)
    elif dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    # Equation of time (minutes)
    j2000 = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    d = (dt - j2000).total_seconds() / 86400.0
    B = np.radians(360 / 365.0 * (d - 81))
    eot = 9.87 * np.sin(2 * B) - 7.53 * np.cos(B) - 1.5 * np.sin(B)  # minutes

    solar_offset = timedelta(minutes=lon * 4 + eot)
    return dt + solar_offset


# ─── Current zodiac ───────────────────────────────────────────────────────────

def get_current_zodiac(dt: Optional[datetime] = None) -> dict:
    """Return current zodiac sign based on Sun's ecliptic longitude."""
    if dt is None:
        dt = datetime.now(timezone.utc)

    j2000 = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    d = (dt - j2000).total_seconds() / 86400.0
    g = np.radians((357.528 + 0.9856003 * d) % 360)
    L = (280.461 + 0.9856474 * d) % 360
    lam = (L + 1.915 * np.degrees(np.sin(g)) + 0.020 * np.degrees(np.sin(2 * g))) % 360

    signs = [
        (0, "Aries", "♈"), (30, "Taurus", "♉"), (60, "Gemini", "♊"),
        (90, "Cancer", "♋"), (120, "Leo", "♌"), (150, "Virgo", "♍"),
        (180, "Libra", "♎"), (210, "Scorpius", "♏"), (240, "Sagittarius", "♐"),
        (270, "Capricornus", "♑"), (300, "Aquarius", "♒"), (330, "Pisces", "♓"),
    ]
    for start, name, sym in reversed(signs):
        if lam >= start:
            return {"name": name, "symbol": sym, "sun_lon": lam}
    return {"name": "Pisces", "symbol": "♓", "sun_lon": lam}


# ─── Star positions for sky map ───────────────────────────────────────────────

def get_bright_stars_altaz(lat: float, lon: float, dt: Optional[datetime] = None) -> list[dict]:
    """Return alt/az for bright named stars from the constellations.json catalog."""
    import json, os
    if dt is None:
        dt = datetime.now(timezone.utc)
    elif dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    lst = get_sidereal_time(lon, dt)

    asset_path = os.path.join(os.path.dirname(__file__), "..", "assets", "constellations.json")
    try:
        with open(asset_path) as f:
            catalog = json.load(f)
        stars = catalog.get("bright_stars", [])
    except Exception:
        return []

    result = []
    for star in stars:
        ra_h = star["ra"]
        dec_d = star["dec"]
        ha_deg = (lst - ra_h) * 15.0
        alt, az = _ha_dec_to_altaz(ha_deg, dec_d, lat)
        result.append({
            **star,
            "alt": alt,
            "az": az,
            "above_horizon": alt > 0,
        })
    return result
