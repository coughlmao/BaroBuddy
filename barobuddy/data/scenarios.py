
from dataclasses import dataclass

from barobuddy.models import ScenarioName


@dataclass(frozen=True)
class ScenarioDefinition:
    name: ScenarioName
    label: str
    description: str
    pattern: str


SCENARIOS: tuple[ScenarioDefinition, ...] = (
    ScenarioDefinition(
        name="uphill_climb",
        label="Uphill climb",
        description=(
            "Simulated elevation gain accompanied by falling pressure."
        ),
        pattern="uphill",
    ),
    ScenarioDefinition(
        name="falling_pressure",
        label="Falling pressure",
        description=(
            "Simulated falling pressure while elevation remains stable."
        ),
        pattern="falling",
    ),
    ScenarioDefinition(
        name="conflicting_signals",
        label="Conflicting signals",
        description=(
            "Simulated inconsistent pressure and elevation signals."
        ),
        pattern="conflicting",
    ),
    ScenarioDefinition(
        name="steady_conditions",
        label="Steady conditions",
        description=(
            "Simulated small pressure variations at stable elevation."
        ),
        pattern="steady",
    ),
    ScenarioDefinition(
        name="pressure_recovery",
        label="Pressure drop and recovery",
        description=(
            "Simulated pressure drop followed by recovery at stable elevation."
        ),
        pattern="recovery",
    ),
    ScenarioDefinition(
        name="abrupt_pressure_change",
        label="Abrupt pressure change",
        description=(
            "Simulated rapid pressure change at stable elevation."
        ),
        pattern="abrupt",
    ),
)


def get_scenario(name: ScenarioName) -> ScenarioDefinition:
    """Return a scenario definition by its stable identifier."""
    for scenario in SCENARIOS:
        if scenario.name == name:
            return scenario

    raise ValueError(f"Unknown scenario: {name}")
