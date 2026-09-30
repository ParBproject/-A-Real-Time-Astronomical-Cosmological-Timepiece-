"""Astronomical time and coordinates, pinned to published and library values."""

import math
from datetime import datetime, timezone

import pytest
from astropy.coordinates import AltAz, EarthLocation, get_body, get_sun
from astropy.time import Time
import astropy.units as u

from src.astronomy import (
    _approx_equation_of_time_minutes,
    _approx_sidereal_time,
    _approx_sun_ecliptic_longitude,
    _ha_dec_to_altaz,
    equation_of_time_minutes,
    get_current_zodiac,
    get_moon_data,
    get_planet_positions,
    get_sidereal_time,
    get_solar_time,
    get_sun_position,
    julian_date,
    sun_ecliptic_longitude,
)


def _utc(year, month, day, hour=0, minute=0, second=0):
    return datetime(year, month, day, hour, minute, second, tzinfo=timezone.utc)


def _angular_distance_to_cardinal(longitude, cardinal):
    return min((longitude - cardinal) % 360.0, (cardinal - longitude) % 360.0)


def test_julian_date_epoch_and_leap_days():
    # Meeus / USNO: 2000-01-01 12:00 UT is the J2000 calendar epoch.
    assert julian_date(_utc(2000, 1, 1, 12)) == pytest.approx(2451545.0)
    # 2000 is a leap year; 1900 is not, even though both are divisible by 4.
    leap_gap = julian_date(_utc(2000, 3, 1)) - julian_date(_utc(2000, 2, 28))
    common_gap = julian_date(_utc(1900, 3, 1)) - julian_date(_utc(1900, 2, 28))
    assert leap_gap == pytest.approx(2.0)
    assert common_gap == pytest.approx(1.0)


def test_meeus_greenwich_sidereal_time_1987_april_10():
    # Astronomical Algorithms, Example 12.a: GMST = 13h 10m 46.3668s.
    expected = 13 + 10 / 60 + 46.3668 / 3600
    got = _approx_sidereal_time(0.0, _utc(1987, 4, 10))
    assert got == pytest.approx(expected, abs=1e-7)

    # Astropy's apparent value includes a newer GMST series and the equation
    # of the equinoxes. It stays inside a second of the published mean value.
    apparent = get_sidereal_time(0.0, _utc(1987, 4, 10))
    assert apparent == pytest.approx(expected, abs=1.0 / 3600)

    # Fifteen degrees of longitude is one sidereal hour.
    at_longitude = get_sidereal_time(15.0, _utc(1987, 4, 10))
    assert (at_longitude - apparent) % 24 == pytest.approx(1.0, abs=1e-6)


def test_hour_angle_to_horizon_coordinates():
    # On the equator, an object with HA +6h and dec 0 is setting due west.
    alt, az = _ha_dec_to_altaz(90.0, 0.0, 0.0)
    assert alt == pytest.approx(0.0, abs=1e-6)
    assert az == pytest.approx(270.0, abs=1e-6)

    # HA -6h is rising due east.
    alt, az = _ha_dec_to_altaz(-90.0, 0.0, 0.0)
    assert alt == pytest.approx(0.0, abs=1e-6)
    assert az == pytest.approx(90.0, abs=1e-6)

    # On the meridian, south of the zenith: azimuth 180°, altitude 90° − latitude.
    alt, az = _ha_dec_to_altaz(0.0, 0.0, 48.8)
    assert alt == pytest.approx(41.2, abs=1e-6)
    assert az == pytest.approx(180.0, abs=1e-6)


def test_equation_of_time_uses_day_of_year_across_leap_day():
    # 29 February 2024 and 1 March 2023 are both day-of-year 60.
    leap = _approx_equation_of_time_minutes(_utc(2024, 2, 29, 12))
    common = _approx_equation_of_time_minutes(_utc(2023, 3, 1, 12))
    assert leap == pytest.approx(common, abs=1e-9)
    # Early November the equation of time is large and positive.
    november = _approx_equation_of_time_minutes(_utc(2024, 11, 3, 12))
    assert november == pytest.approx(16.33, abs=0.05)


def test_ephemeris_equation_of_time_matches_an_independent_hour_angle():
    when = _utc(2024, 11, 3, 12)
    minutes, source = equation_of_time_minutes(when)
    assert source == "de421"
    # Published values for early November are about +16 to +18 minutes.
    assert 16.0 < minutes < 19.0

    import os
    from skyfield.api import Loader

    loader = Loader(os.path.join(os.path.expanduser("~"), "skyfield-data"))
    ts = loader.timescale()
    eph = loader("de421.bsp")
    t = ts.from_datetime(when)
    ra_hours = eph["earth"].at(t).observe(eph["sun"]).apparent().radec()[0].hours
    raw_hours = t.gast - ra_hours + 12.0 - 12.0
    independent = ((raw_hours + 12.0) % 24.0 - 12.0) * 60.0
    assert minutes == pytest.approx(independent, abs=0.02)

    solar = get_solar_time(0.0, when)
    expected_minute = 12 * 60 + minutes
    got_minute = solar.hour * 60 + solar.minute + solar.second / 60
    assert got_minute == pytest.approx(expected_minute, abs=0.05)


@pytest.mark.parametrize(
    ("when", "cardinal", "sign"),
    [
        (_utc(2024, 3, 20, 3, 7), 0.0, "Aries"),
        (_utc(2024, 6, 20, 20, 51), 90.0, "Cancer"),
        (_utc(2024, 9, 22, 12, 44), 180.0, "Libra"),
        (_utc(2024, 12, 21, 9, 21), 270.0, "Capricornus"),
    ],
)
def test_sun_sign_at_the_2024_equinoxes_and_solstices(when, cardinal, sign):
    longitude = sun_ecliptic_longitude(when)
    zodiac = get_current_zodiac(when)
    assert _angular_distance_to_cardinal(longitude, cardinal) < 0.05
    assert zodiac["name"] == sign
    # The old formula multiplied sin() by 180/π and missed Aries by ~100°.
    assert _angular_distance_to_cardinal(zodiac["sun_lon"], cardinal) < 0.05


def test_low_precision_sun_is_in_aries_at_the_march_equinox():
    longitude = _approx_sun_ecliptic_longitude(_utc(2024, 3, 20, 3, 6))
    assert _angular_distance_to_cardinal(longitude, 0.0) < 0.1


def test_naive_datetime_is_accepted_as_utc():
    zodiac = get_current_zodiac(datetime(2024, 6, 20, 20, 51))
    assert zodiac["name"] == "Cancer"


def test_sun_altitude_matches_astropy_in_paris():
    when = _utc(2024, 6, 21, 12)
    sun = get_sun_position(48.8566, 2.3522, when)
    assert sun["source"] == "de421"

    location = EarthLocation(lat=48.8566 * u.deg, lon=2.3522 * u.deg, height=0 * u.m)
    equatorial = get_sun(Time(when))
    horizontal = equatorial.transform_to(AltAz(obstime=Time(when), location=location))
    assert sun["alt"] == pytest.approx(horizontal.alt.deg, abs=0.02)
    assert sun["az"] == pytest.approx(horizontal.az.deg, abs=0.02)
    assert sun["dec"] == pytest.approx(equatorial.dec.deg, abs=0.02)


def test_moon_phase_at_the_2024_april_new_and_full_moons():
    new = get_moon_data(48.8566, 2.3522, _utc(2024, 4, 8, 18, 21))
    assert new["source"] == "de421"
    assert new["phase"] == pytest.approx(0.0, abs=0.01)
    assert new["illumination"] < 1.0
    assert "New" in new["phase_name"]

    full = get_moon_data(48.8566, 2.3522, _utc(2024, 4, 23, 23, 49))
    assert full["phase"] == pytest.approx(0.5, abs=0.01)
    assert full["illumination"] > 99.0
    assert "Full" in full["phase_name"]


def test_mars_altitude_matches_astropy():
    when = _utc(2024, 6, 21, 12)
    planets = get_planet_positions(48.8566, 2.3522, when)
    assert len(planets) == 7
    mars = next(planet for planet in planets if planet["name"] == "Mars")
    assert mars["source"] == "de421"

    location = EarthLocation(lat=48.8566 * u.deg, lon=2.3522 * u.deg, height=0 * u.m)
    reference = get_body("mars", Time(when), location).transform_to(
        AltAz(obstime=Time(when), location=location)
    )
    assert mars["alt"] == pytest.approx(reference.alt.deg, abs=0.05)
    assert mars["az"] == pytest.approx(reference.az.deg, abs=0.05)
    assert math.isfinite(mars["distance_au"])
