from datetime import UTC, datetime

from barobuddy.simulator import generate_scenario


def test_simulator_is_reproducible():
    start = datetime(2026, 10, 10, 12, 0, tzinfo=UTC)

    first = generate_scenario("uphill_climb", start=start)
    second = generate_scenario("uphill_climb", start=start)

    assert first == second
    assert first.is_simulated is True


def test_uphill_scenario_increases_elevation():
    scenario = generate_scenario("uphill_climb")

    assert scenario.readings[-1].elevation_m > scenario.readings[0].elevation_m
    assert scenario.readings[-1].pressure_hpa < scenario.readings[0].pressure_hpa


def test_failing_pressure_scenario_keeps_evaluation_stable():
    scenario = generate_scenario("falling_pressure")

    elevations = {reading.elevation_m for reading in scenario.readings}

    assert len(elevations) == 1
    assert scenario.readings[-1].pressure_hpa < scenario.readings[0].pressure_hpa


def test_conflicting_scenario_has_inconsistent_direction():
    scenario = generate_scenario("conflicting_signals")

    first, last = scenario.readings[0], scenario.readings[-1]

    assert last.elevation_m > first.elevation_m
    assert last.pressure_hpa > first.elevation_m


def test_simulator_rejects_too_few_readings():
    import pytest

    with pytest.raises(ValueError):
        generate_scenario("uphill_climb", count=1)


def test_steady_conditions_has_small_pressure_variations() -> None:
    scenario = generate_scenario("steady_conditions")

    pressures = [reading.pressure_hpa for reading in scenario.readings]

    assert scenario.is_simulated is True
    assert len(pressures) == 13
    assert all(value is not None for value in pressures)
    assert max(pressures) - min(pressures) <= 0.3
    assert all(reading.elevation_m == 100.0 for reading in scenario.readings)


def test_pressure_recovery_returns_to_baseline() -> None:
    scenario = generate_scenario("pressure_recovery")

    pressures = [reading.pressure_hpa for reading in scenario.readings]

    assert scenario.is_simulated is True
    assert pressures[0] == 1013.2
    assert pressures[5] == 1010.2
    assert pressures[7] == 1012.2
    assert pressures[-1] == 1013.2
    assert all(reading.elevation_m == 100.0 for reading in scenario.readings)


def test_abrupt_pressure_change_has_a_single_pressure_drop() -> None:
    scenario = generate_scenario("abrupt_pressure_change")

    pressures = [reading.pressure_hpa for reading in scenario.readings]

    assert scenario.is_simulated is True
    assert pressures[:6] == [1013.2] * 6
    assert pressures[6:] == [1010.2] * 7
    assert all(reading.elevation_m == 100.0 for reading in scenario.readings)
