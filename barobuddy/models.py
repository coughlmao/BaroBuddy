from dataclasses import dataclass
from datetime import datetime
from typing import Literal

ScenarioName = Literal[
    "uphill_climb",
    "falling_pressure",
    "conflicting_signals",
]

EventType = Literal[
    "elevation_associated_pressure_change",
    "falling_pressure_trend",
    "conflicting_signals",
    "no_significant_change",
    "insufficient_data",
]


@dataclass(frozen=True)
class Reading:
    timestamp: datetime
    pressure_hpa: float | None
    elevation_m: float | None


@dataclass(frozen=True)
class Scenario:
    name: ScenarioName
    description: str
    readings: tuple[Reading, ...]
    is_simulated: bool = True


@dataclass(frozen=True)
class Assessment:
    event: EventType
    summary: str
    evidence: tuple[str, ...]
    uncertainty: str
    pressure_change_hpa: float | None
    elevation_change_m: float | None
    data_quality: str
