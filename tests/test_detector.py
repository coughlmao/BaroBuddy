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


def test_abrupt_pressure_drop_and_recovery_is_detected():
    start = datetime(2026, 10, 10, 12, 0, tzinfo=UTC)

    readings = [
        Reading(start, 1013.0, 100.0),
        Reading(start + timedelta(minutes=5), 1010.0, 101.0),
        Reading(start + timedelta(minutes=10), 1012.8, 100.5),
    ]

    result = assess_readings(readings)

    assert result.event == "abrupt_pressure_change"
    assert result.pressure_change_hpa == -0.2
    assert any(
        "Largest adjacent pressure change was -3.00 hPa over 5.0 minute(s)." in item
        for item in result.evidence
    )
    assert any(
        "Largest observed pressure-change rate was 0.600 hPa/min." in item
        for item in result.evidence
    )
    assert "cause cannot" in result.uncertainty


def test_out_of_order_readings_are_sorted_before_assessment():
    start = datetime(2026, 10, 10, 12, 0, tzinfo=UTC)

    readings = [
        Reading(start + timedelta(minutes=10), 1010.0, 100.0),
        Reading(start, 1013.0, 100.0),
        Reading(start + timedelta(minutes=5), 1011.5, 100.0),
    ]

    result = assess_readings(readings)

    assert result.event == "falling_pressure_trend"
    assert result.pressure_change_hpa == -3.0


def test_pressure_change_over_longer_interval_is_not_called_abrupt():
    start = datetime(2026, 10, 10, 12, 0, tzinfo=UTC)

    readings = [
        Reading(start, 1013.0, 100.0),
        Reading(start + timedelta(minutes=10), 1010.5, 100.0),
    ]

    result = assess_readings(readings)

    assert result.event == "falling_pressure_trend"
    assert result.pressure_change_hpa == -2.5


def test_mixed_timezone_aware_and_naive_timestamps_return_insufficient_data():
    start = datetime(2026, 10, 10, 12, 0, tzinfo=UTC)

    readings = [
        Reading(start, 1013.0, 100.0),
        Reading(
            datetime(2026, 10, 10, 12, 5),
            1012.0,
            100.0,
        ),
    ]

    result = assess_readings(readings)

    assert result.event == "insufficient_data"
    assert any("timezone" in item.lower() for item in result.evidence)


def test_invalid_pressure_and_elevation_readings_are_ignored():
    start = datetime(2026, 10, 10, 12, 0, tzinfo=UTC)

    readings = [
        Reading(start, 1013.0, 100.0),
        Reading(start + timedelta(minutes=5), 1200.0, 105.0),
        Reading(start + timedelta(minutes=10), 1011.0, 110.0),
        Reading(start + timedelta(minutes=15), 1010.0, 9500.0),
    ]

    result = assess_readings(readings)

    assert result.event == "falling_pressure_trend"
    assert result.pressure_change_hpa == -2.0
    assert result.elevation_change_m == 10.0
    assert "2 invalid or incomplete reading(s) ignored." == result.data_quality
