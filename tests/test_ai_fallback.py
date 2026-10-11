import json

from barobuddy import ai_assistant
from barobuddy.models import Assessment


def sample_assessment() -> Assessment:
    return Assessment(
        event="falling_pressure_trend",
        summary="Pressure decreased while elevation remained stable.",
        evidence=(
            "Pressure changed by -4.00 hPa.",
            "Elevation changed by +0.00 m.",
        ),
        uncertainty="A falling pressure trend does not confirm a storm.",
        pressure_change_hpa=-4.0,
        elevation_change_m=0.0,
        data_quality="All readings used in the assessment are valid.",
    )


def test_ollama_failure_returns_fallback(monkeypatch):
    def fail_request(*args, **kwargs):
        raise OSError("Ollama is not running")

    monkeypatch.setattr(ai_assistant, "urlopen", fail_request)

    result = ai_assistant.explain_assessment(sample_assessment())

    assert result.used_fallback is True
    assert result.explanation == sample_assessment().summary
    assert "official local forecast" in result.next_step


def test_invalid_model_response_returns_fallback(monkeypatch):
    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return json.dumps({"message": {"content": "not valid JSON"}}).encode(
                "utf-8"
            )

    monkeypatch.setattr(
        ai_assistant,
        "urlopen",
        lambda *args, **kwargs: FakeResponse(),
    )

    result = ai_assistant.explain_assessment(sample_assessment())

    assert result.used_fallback is True
    assert result.explanation == sample_assessment().summary


def test_valid_local_response_is_used(monkeypatch):
    content = json.dumps(
        {
            "explanation": "Pressure fell while elevation stayed stable.",
            "next_step": "Check the official local forecast.",
        }
    )

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return json.dumps({"message": {"content": content}}).encode("utf-8")

    monkeypatch.setattr(
        ai_assistant,
        "urlopen",
        lambda *args, **kwargs: FakeResponse(),
    )

    result = ai_assistant.explain_assessment(sample_assessment())

    assert result.used_fallback is False
    assert result.explanation == ("Pressure fell while elevation stayed stable.")
