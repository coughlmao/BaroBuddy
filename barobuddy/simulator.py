from datetime import UTC, datetime, timedelta

from barobuddy.models import Reading, Scenario, ScenarioName


def generate_scenario(
    name: ScenarioName,
    start: datetime | None = None,
    count: int = 13,
    interval_minutes: int = 5,
) -> Scenario:
    """Generate deterministic simulated pressure and elevation readings."""
    if count < 2:
        raise ValueError("count must be at least 2")

    if interval_minutes <= 0:
        raise ValueError("interval_minutes must be positive")

    start = start or datetime(2026, 10, 10, 12, 0, tzinfo=UTC)

    if start.tzinfo is None or start.utcoffset() is None:
        raise ValueError("start must be timezone-aware")

    readings: list[Reading] = []

    for index in range(count):
        timestamp = start + timedelta(minutes=index * interval_minutes)

        if name == "uphill_climb":
            # Elevation rises steadily. Pressure falls mainly alongside
            # the simulated elevation gain.
            elevation = 100.0 + index * 25.0
            pressure = 1013.2 - index * 2.9

        elif name == "falling_pressure":
            # Elevation stays constant while pressure falls steadily.
            elevation = 100.0
            pressure = 1013.2 - index * (4.0 / 12.0)

        elif name == "conflicting_signals":
            # Deliberately inconsistent readings: elevation rises overall,
            # but pressure rises too, with short oscillations.
            elevation = 100.0 + index * 8.0 + (5.0 if index % 2 else 0.0)
            pressure = 1013.2 + index * 0.15 + (0.8 if index % 2 else -0.5)

        else:
            raise ValueError(f"Unknown scenario: {name}")

        readings.append(
            Reading(
                timestamp=timestamp,
                pressure_hpa=round(pressure, 2),
                elevation_m=round(elevation, 2),
            )
        )

    descriptions = {
        "uphill_climb": (
            "Simulated uphill climb: elevation rises while pressure falls."
        ),
        "falling_pressure": ("Simulated falling-pressure trend with stable elevation."),
        "conflicting_signals": (
            "Simulated inconsistent pressure and elevation signals."
        ),
    }

    return Scenario(
        name=name,
        description=descriptions[name],
        readings=tuple(readings),
    )
