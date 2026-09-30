"""Figure builders accept the corrected calendar and sky records."""

from datetime import datetime, timezone

from src.astronomy import get_bright_stars_altaz, get_moon_data, get_planet_positions, get_sun_position
from src.timeline import load_events
from src.visuals import build_cosmic_calendar_wheel, build_planet_visibility_chart, build_sky_map


def test_calendar_wheel_and_sky_map_build():
    events = load_events()
    wheel = build_cosmic_calendar_wheel(events)
    assert len(wheel.data) > 0

    when = datetime(2024, 6, 21, 12, tzinfo=timezone.utc)
    lat, lon = 48.8566, 2.3522
    planets = get_planet_positions(lat, lon, when)
    sun = get_sun_position(lat, lon, when)
    moon = get_moon_data(lat, lon, when)
    stars = get_bright_stars_altaz(lat, lon, when)
    sky = build_sky_map(planets, stars, sun, moon, {"star_opacity": 1.0})
    bars = build_planet_visibility_chart(planets)
    assert len(sky.data) > 0
    assert len(bars.data) == 1
    assert any(star["name"] == "Sirius" for star in stars)
