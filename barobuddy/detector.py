from barobuddy.models import Assessment, Reading

MIN_PRESSURE_CHANGE_HPA = 1.5
MIN_ELEVATION_CHANGE_M = 30.0


def assess_readings(readings: list[Reading]) -> Assessment:
    """Classify a simple trend using the first and last valid readings."""
    if len(readings) < 2:
        return _insufficient("At least two readings are required.")

    ordered = sorted(readings, key=lambda reading: reading.timestamp)

    if any(
        reading.timestamp.tzinfo is None
        or reading.timestamp.utcoffset() is None
        for reading in ordered
    ):
        return _insufficient("Timestamps must include a timezone.")

    valid = [
        reading
        for reading in ordered
        if reading.pressure_hpa is not None
        and reading.elevation_m is not None
        and 300.0 <= reading.pressure_hpa <= 1100.0
        and -500.0 <= reading.elevation_m <= 9000.0
    ]

    if len(valid) < 2:
        return _insufficient(
            "Fewer than two readings contain valid pressure and elevation."
        )

    first = valid[0]
    last = valid[-1]

    pressure_change = round(
        last.pressure_hpa - first.pressure_hpa, 2
    )
    elevation_change = round(
        last.elevation_m - first.elevation_m, 2
    )

    missing_count = len(readings) - len(valid)
    quality = (
        f"{missing_count} invalid or incomplete reading(s) ignored."
        if missing_count
        else "All readings used in the assessment are valid."
    )

    pressure_falling = pressure_change <= -MIN_PRESSURE_CHANGE_HPA
    pressure_rising = pressure_change >= MIN_PRESSURE_CHANGE_HPA
    elevation_rising = elevation_change >= MIN_ELEVATION_CHANGE_M
    elevation_falling = elevation_change <= -MIN_ELEVATION_CHANGE_M

    evidence = (
        f"Pressure changed by {pressure_change:+.2f} hPa.",
        f"Elevation changed by {elevation_change:+.2f} m.",
    )

    if elevation_rising and pressure_falling:
        return Assessment(
            event="elevation_associated_pressure_change",
            summary=(
                "Elevation increased while atmospheric pressure decreased. "
                "The pressure change may be associated with the climb."
            ),
            evidence=evidence,
            uncertainty=(
                "These readings alone cannot separate elevation effects "
                "from independent weather-related pressure changes."
            ),
            pressure_change_hpa=pressure_change,
            elevation_change_m=elevation_change,
            data_quality=quality,
        )

    if elevation_falling and pressure_rising:
        return Assessment(
            event="elevation_associated_pressure_change",
            summary=(
                "Elevation decreased while pressure increased, a pattern "
                "that may be associated with the elevation change."
            ),
            evidence=evidence,
            uncertainty=(
                "The readings do not establish the cause of the pressure "
                "change or indicate future weather."
            ),
            pressure_change_hpa=pressure_change,
            elevation_change_m=elevation_change,
            data_quality=quality,
        )

    if abs(elevation_change) < MIN_ELEVATION_CHANGE_M and pressure_falling:
        return Assessment(
            event="falling_pressure_trend",
            summary=(
                "Pressure decreased while elevation remained broadly stable."
            ),
            evidence=evidence,
            uncertainty=(
                "A falling pressure trend does not by itself confirm a storm "
                "or predict local weather."
            ),
            pressure_change_hpa=pressure_change,
            elevation_change_m=elevation_change,
            data_quality=quality,
        )

    if (
        (pressure_rising and elevation_rising)
        or (pressure_falling and elevation_falling)
    ):
        return Assessment(
            event="conflicting_signals",
            summary=(
                "Pressure and elevation changed in a pattern that this "
                "simple detector cannot confidently interpret."
            ),
            evidence=evidence,
            uncertainty=(
                "The cause is uncertain. More context or better-quality "
                "readings are needed."
            ),
            pressure_change_hpa=pressure_change,
            elevation_change_m=elevation_change,
            data_quality=quality,
        )

    if not pressure_falling and not pressure_rising:
        return Assessment(
            event="no_significant_change",
            summary="No significant pressure change was detected over this window.",
            evidence=evidence,
            uncertainty=(
                "Small changes can still matter in context; this prototype "
                "uses a fixed threshold."
            ),
            pressure_change_hpa=pressure_change,
            elevation_change_m=elevation_change,
            data_quality=quality,
        )

    return Assessment(
        event="conflicting_signals",
        summary="The readings do not fit a confident classification.",
        evidence=evidence,
        uncertainty="The cause is uncertain; do not infer a weather event.",
        pressure_change_hpa=pressure_change,
        elevation_change_m=elevation_change,
        data_quality=quality,
    )


def _insufficient(reason: str) -> Assessment:
    return Assessment(
        event="insufficient_data",
        summary="There is not enough valid data to assess a trend.",
        evidence=(reason,),
        uncertainty="No environmental conclusion should be drawn.",
        pressure_change_hpa=None,
        elevation_change_m=None,
        data_quality="Insufficient data.",
    )