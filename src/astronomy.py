"""
astronomy.py — Sky positions, sidereal time, and solar time.

Planet, Sun, and Moon positions come from Skyfield and the JPL DE421
ephemeris (the kernel this app actually loads). Astropy supplies apparent
sidereal time. If those libraries or the ephemeris file are unavailable,
the module falls back to published low-precision formulas: Meeus for
sidereal time, and a short solar theory for the Sun. Fallback results are
for the sky map, not for observing.
"""

import math
import os
import numpy as np
import streamlit as st
from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple

# ── Skyfield ──────────────────────────────────────────────────────────────────
try:
    from skyfield.api import Loader, wgs84
    SKYFIELD_OK = True
except ImportError:
    SKYFIELD_OK = False

# ── Astropy (sidereal time) ───────────────────────────────────────────────────
try:
    from astropy.time import Time
    ASTROPY_OK = True
except ImportError:
    ASTROPY_OK = False


# ─── Ephemeris loading (cached) ───────────────────────────────────────────────

def _ensure_utc(dt: Optional[datetime]) -> datetime:
    """Return a UTC datetime. Naive values are taken to be UTC, not local time."""
    if dt is None:
        return datetime.now(timezone.utc)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _active_ephemeris():
    """Return (timescale, ephemeris) when DE421 is loaded, else (None, None)."""
    ts, eph = load_ephemeris()
    if SKYFIELD_OK and ts is not None and eph is not None:
        return ts, eph
    return None, None


@st.cache_resource(show_spinner="Loading ephemeris…")
def load_ephemeris():
    """Load the Skyfield DE421 ephemeris (small, fast, accurate enough for display)."""
    if not SKYFIELD_OK:
        return None, None
    # Skyfield's default loader writes into the working directory. Keep the
    # 16 MB kernel in the home cache so it is not dropped into the repository.
    cache = os.path.join(os.path.expanduser("~"), "skyfield-data")
    os.makedirs(cache, exist_ok=True)
    loader = Loader(cache)
    ts = loader.timescale()
    try:
        eph = loader("de421.bsp")
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
    dt = _ensure_utc(dt)
    ts, eph = _active_ephemeris()
    results = []

    if ts is not None and eph is not None:
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
                    "source": "de421",
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
            "source": "approximate",
        })
    return results


# ─── Sun ──────────────────────────────────────────────────────────────────────

def get_sun_position(lat: float, lon: float, dt: Optional[datetime] = None) -> dict:
    """Return Sun's altitude, azimuth, RA, Dec."""
    dt = _ensure_utc(dt)
    ts, eph = _active_ephemeris()

    if ts is not None and eph is not None:
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
            "source": "de421",
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
    return {
        "alt": alt, "az": az, "ra": ra_h, "dec": dec_d,
        "above_horizon": alt > 0, "source": "approximate",
    }


# ─── Moon ─────────────────────────────────────────────────────────────────────

def get_moon_data(lat: float, lon: float, dt: Optional[datetime] = None) -> dict:
    """Return Moon position and phase (0–1, where 0/1=new, 0.5=full)."""
    dt = _ensure_utc(dt)
    ts, eph = _active_ephemeris()
    phase = 0.5
    illumination = 50.0

    if ts is not None and eph is not None:
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
            "source": "de421",
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
        "source": "approximate",
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


# ─── Sidereal Time ────────────────────────────────────────────────────────────

def julian_date(dt: datetime) -> float:
    """Julian Date on the UTC scale for a Gregorian datetime.

    2000-01-01 12:00 UT is JD 2451545.0. January and February are treated as
    months 13 and 14 of the previous year, which is what makes the leap-day
    count (including 1900 and 2000) come out right.
    """
    dt = _ensure_utc(dt)
    year = dt.year
    month = dt.month
    day = (
        dt.day
        + (
            dt.hour
            + (dt.minute + (dt.second + dt.microsecond / 1e6) / 60.0) / 60.0
        )
        / 24.0
    )
    if month <= 2:
        year -= 1
        month += 12
    century = year // 100
    gregorian = 2 - century + century // 4
    return (
        math.floor(365.25 * (year + 4716))
        + math.floor(30.6001 * (month + 1))
        + day
        + gregorian
        - 1524.5
    )


def get_sidereal_time(lon: float, dt: Optional[datetime] = None) -> float:
    """Return local apparent sidereal time in decimal hours.

    Uses Astropy when it is installed. The fallback is local mean sidereal
    time from Meeus (equation of the equinoxes omitted, under 1.2 seconds).
    """
    dt = _ensure_utc(dt)

    if ASTROPY_OK:
        t = Time(dt)
        lst = t.sidereal_time("apparent", longitude=f"{lon}d")
        return float(lst.hour)
    return _approx_sidereal_time(lon, dt)


def _approx_sidereal_time(lon: float, dt: datetime) -> float:
    """Local mean sidereal time in hours (Meeus, Astronomical Algorithms)."""
    days = julian_date(dt) - 2451545.0
    centuries = days / 36525.0
    gmst_deg = (
        280.46061837
        + 360.98564736629 * days
        + 0.000387933 * centuries ** 2
        - centuries ** 3 / 38710000.0
    ) % 360.0
    return (gmst_deg / 15.0 + lon / 15.0) % 24.0


def _ha_dec_to_altaz(ha_deg: float, dec_deg: float, lat_deg: float) -> Tuple[float, float]:
    """Convert hour angle and declination to altitude and azimuth.

    Azimuth is measured from north through east.
    """
    ha = np.radians(ha_deg)
    dec = np.radians(dec_deg)
    lat = np.radians(lat_deg)

    sin_alt = np.sin(dec) * np.sin(lat) + np.cos(dec) * np.cos(lat) * np.cos(ha)
    alt = np.degrees(np.arcsin(np.clip(sin_alt, -1.0, 1.0)))

    # Azimuth from north through east. atan2 keeps the quadrant without the
    # 1/cos(altitude) division that breaks down at the zenith.
    east = -np.cos(dec) * np.sin(ha)
    north = np.sin(dec) * np.cos(lat) - np.cos(dec) * np.sin(lat) * np.cos(ha)
    az = np.degrees(np.arctan2(east, north)) % 360.0
    return float(alt), float(az)


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

def _approx_equation_of_time_minutes(dt: datetime) -> float:
    """Low-precision equation of time in minutes (apparent minus mean).

    N is the UTC day of year, so 29 February shifts the following days.
    Days since J2000 are not a day-of-year and drift by about a quarter
    day per year.
    """
    day_of_year = _ensure_utc(dt).timetuple().tm_yday
    b = math.radians(360.0 * (day_of_year - 81) / 365.0)
    return 9.87 * math.sin(2 * b) - 7.53 * math.cos(b) - 1.5 * math.sin(b)


def equation_of_time_minutes(dt: Optional[datetime] = None) -> tuple[float, str]:
    """Equation of time in minutes, and whether it came from DE421.

    Apparent solar time minus mean solar time. Longitude cancels, so the
    value is the same at every meridian.
    """
    dt = _ensure_utc(dt)
    ts, eph = _active_ephemeris()
    if ts is not None and eph is not None:
        t = ts.from_datetime(dt)
        ra_hours = eph["earth"].at(t).observe(eph["sun"]).apparent().radec()[0].hours
        utc_hours = (
            dt.hour
            + dt.minute / 60.0
            + dt.second / 3600.0
            + dt.microsecond / 3_600_000_000.0
        )
        # Greenwich apparent sidereal time minus the Sun's right ascension
        # is the Sun's hour angle; apparent noon is hour angle zero.
        raw_hours = t.gast - ra_hours + 12.0 - utc_hours
        eot_hours = (raw_hours + 12.0) % 24.0 - 12.0
        return float(eot_hours) * 60.0, "de421"
    return _approx_equation_of_time_minutes(dt), "approximate"


def get_solar_time(lon: float, dt: Optional[datetime] = None) -> datetime:
    """Return local apparent solar time.

    The returned datetime keeps UTC as its timezone label. Its wall-clock
    fields are the solar time, which is what the sky page formats.
    """
    dt = _ensure_utc(dt)
    eot_min, _source = equation_of_time_minutes(dt)
    return dt + timedelta(minutes=float(lon) * 4.0 + float(eot_min))


# ─── Current zodiac ───────────────────────────────────────────────────────────

_ZODIAC = (
    (0, "Aries", "♈"), (30, "Taurus", "♉"), (60, "Gemini", "♊"),
    (90, "Cancer", "♋"), (120, "Leo", "♌"), (150, "Virgo", "♍"),
    (180, "Libra", "♎"), (210, "Scorpius", "♏"), (240, "Sagittarius", "♐"),
    (270, "Capricornus", "♑"), (300, "Aquarius", "♒"), (330, "Pisces", "♓"),
)


def _approx_sun_ecliptic_longitude(dt: datetime) -> float:
    """Low-precision apparent ecliptic longitude of the Sun, in degrees.

    The 1.915° and 0.020° terms are already in degrees. Applying
    ``degrees()`` to the sine inflates them by 180/π and moves the Sun
    into the wrong sign.
    """
    j2000 = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    day = (_ensure_utc(dt) - j2000).total_seconds() / 86400.0
    mean_anomaly = math.radians((357.528 + 0.9856003 * day) % 360.0)
    mean_longitude = (280.461 + 0.9856474 * day) % 360.0
    return (
        mean_longitude
        + 1.915 * math.sin(mean_anomaly)
        + 0.020 * math.sin(2 * mean_anomaly)
    ) % 360.0


def sun_ecliptic_longitude(dt: Optional[datetime] = None) -> float:
    """Apparent ecliptic longitude of the Sun, of date, in degrees."""
    dt = _ensure_utc(dt)
    ts, eph = _active_ephemeris()
    if ts is not None and eph is not None:
        t = ts.from_datetime(dt)
        longitude = (
            eph["earth"].at(t).observe(eph["sun"]).apparent()
            .ecliptic_latlon(epoch="date")[1].degrees
        )
        return float(longitude) % 360.0
    return _approx_sun_ecliptic_longitude(dt)


def get_current_zodiac(dt: Optional[datetime] = None) -> dict:
    """Tropical zodiac sign from the Sun's ecliptic longitude of date."""
    lam = sun_ecliptic_longitude(dt)
    for start, name, sym in reversed(_ZODIAC):
        if lam >= start:
            return {"name": name, "symbol": sym, "sun_lon": float(lam)}
    return {"name": "Aries", "symbol": "♈", "sun_lon": float(lam)}


# ─── Star positions for sky map ───────────────────────────────────────────────

def get_bright_stars_altaz(lat: float, lon: float, dt: Optional[datetime] = None) -> list[dict]:
    """Return alt/az for bright named stars from the constellations.json catalog."""
    import json, os
    dt = _ensure_utc(dt)
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
