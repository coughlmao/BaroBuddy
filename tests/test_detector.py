from datetime import UTC, datetime, timedelta

from barobuddy.detector import assess_readings
from barobuddy.models import Reading
from barobuddy.simulator import generate_scenario


def test_uphill_is_not_mislabelled_as_weather_pressure_drop():
    scenario = generate_scenario("uphill_climb")

    result = assess_readings(list(scenario.readings))

    assert result.event == "elevation_associated_pressure_change"
    assert result.pressure_change_hpa < 0
    assert result.elevation_change_m > 0
    assert "cannot separate elevation effects" in result.uncertainty


def test_falling_pressure_at_stable_elevation():
    scenario = generate_scenario("falling_pressure")

    result = assess_readings(list(scenario.readings))

    assert result.event == "falling_pressure_trend"
    assert result.pressure_change_hpa < 0
    assert result.elevation_change_m == 0
    assert "does not by itself confirm a storm" in result.uncertainty


def test_conflicting_signals_are_reported_as_uncertain():
    scenario = generate_scenario("conflicting_signals")

    result = assess_readings(list(scenario.readings))

    assert result.event == "conflicting_signals"
    assert "uncertain" in result.uncertainty.lower()


def test_insufficient_data_does_not_make_a_claim():
    now = datetime(2026, 10, 10, 12, 0, tzinfo=UTC)

    readings = [
        Reading(now, 1013.0, 100.0),
        Reading(now + timedelta(minutes=5), None, 105.0),
    ]

    result = assess_readings(readings)

    assert result.event == "insufficient_data"
    assert result.pressure_change_hpa is None
    assert result.elevation_change_m is None
