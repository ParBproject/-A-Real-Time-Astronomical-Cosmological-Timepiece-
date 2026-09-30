"""Cosmic Calendar dates, pinned to a 365-day civil year."""

import pytest

from src.timeline import (
    COSMIC_YEAR_DAYS,
    MONTH_DAYS,
    SECONDS_PER_YEAR,
    UNIVERSE_AGE_YEARS,
    age_to_cosmic_year,
    age_to_scale,
    get_current_cosmic_position,
    load_events,
)


def test_year_length_is_a_civil_year_without_a_leap_day():
    assert COSMIC_YEAR_DAYS == 365
    assert sum(MONTH_DAYS) == 365
    assert MONTH_DAYS[1] == 28
    assert SECONDS_PER_YEAR == 365 * 86400


def test_present_is_the_last_millisecond_of_december_31():
    now = age_to_cosmic_year(0.0)
    assert now["month"] == 12
    assert now["day"] == 31
    assert now["hour"] == 23
    assert now["minute"] == 59
    assert now["second"] == pytest.approx(59.999, abs=1e-9)
    assert now["display"].startswith("Dec 31, 23:59:59")
    # The old equal-month code wrapped this instant to 1 December.
    assert now["day"] != 1


def test_big_bang_is_january_first():
    bang = age_to_cosmic_year(UNIVERSE_AGE_YEARS)
    assert bang["display"] == "Jan 1, 00:00:00.000"
    assert bang["fraction"] == 0.0


def test_march_first_falls_on_the_real_month_boundary():
    # 31 + 28 days precede 1 March in a non-leap year.
    fraction = 59 / 365
    age = (1.0 - fraction) * UNIVERSE_AGE_YEARS
    march = age_to_cosmic_year(age)
    assert march["month_name"] == "Mar"
    assert march["day"] == 1
    assert march["hour"] == 0
    assert march["minute"] == 0
    assert march["second"] == pytest.approx(0.0, abs=1e-3)


def test_agriculture_is_half_a_minute_before_midnight():
    # 12,000 / 13.8e9 of a 365-day year, counted back from the next midnight.
    seconds_before_midnight = 12_000 / UNIVERSE_AGE_YEARS * SECONDS_PER_YEAR
    cal = age_to_cosmic_year(12_000)
    assert seconds_before_midnight == pytest.approx(27.4226, abs=1e-3)
    assert cal["month"] == 12
    assert cal["day"] == 31
    assert cal["hour"] == 23
    assert cal["minute"] == 59
    assert cal["second"] == pytest.approx(60.0 - seconds_before_midnight, abs=0.002)


def test_chicxulub_is_december_30_morning():
    days_before_end = 66e6 / UNIVERSE_AGE_YEARS * COSMIC_YEAR_DAYS
    # One full day of that remainder is 31 December, so the clock time is on the 30th.
    into_dec_30 = (1.0 - (days_before_end - 1.0)) * 86400.0
    cal = age_to_cosmic_year(66e6)
    assert cal["month"] == 12
    assert cal["day"] == 30
    assert cal["hour"] == int(into_dec_30 // 3600)
    assert cal["minute"] == int((into_dec_30 % 3600) // 60)
    assert cal["second"] == pytest.approx(into_dec_30 % 60, abs=0.002)


def test_scale_endpoints_do_not_roll_into_the_next_unit():
    assert age_to_scale(0.0, "Cosmic Day")["display"] == "23:59:59"
    assert age_to_scale(0.0, "Cosmic Hour")["display"] == "59m 59s 999ms"
    assert get_current_cosmic_position()["cosmic_year"]["month"] == 12


def test_recombination_precedes_the_dark_ages_and_the_first_stars():
    events = load_events()
    by_name = {event["name"]: event for event in events}
    assert len(events) == 45
    ages = [event["age_bya"] for event in events]
    assert ages == sorted(ages, reverse=True)

    big_bang = by_name["Big Bang"]["age_years"]
    atoms = by_name["First Atoms Form"]["age_years"]
    # The description is 380,000 years after the Big Bang, not 380 million.
    assert big_bang - atoms == pytest.approx(380_000, abs=1)
    assert (
        by_name["First Atoms Form"]["age_bya"]
        > by_name["Cosmic Dark Ages"]["age_bya"]
        > by_name["First Stars Born"]["age_bya"]
    )
