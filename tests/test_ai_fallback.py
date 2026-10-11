import json
from unittest.mock import patch

from barobuddy import ai_assistant
from barobuddy.ai_assistant import explain_assessment
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


def test_fallback_gives_specific_advice_for_insufficient_data():
    from barobuddy.ai_assistant import _fallback
    from barobuddy.models import Assessment

    assessment = Assessment(
        event="insufficient_data",
        summary="Not enough valid readings to assess the trend.",
        evidence=("Only one valid reading was available.",),
        uncertainty="The trend cannot be determined.",
        pressure_change_hpa=None,
        elevation_change_m=None,
        data_quality="Several readings were invalid.",
    )

    result = _fallback(assessment)

    assert result.used_fallback is True
    assert result.explanation == assessment.summary
    assert "more valid" in result.next_step.lower()


def test_fallback_gives_specific_advice_for_conflicting_signals():
    from barobuddy.ai_assistant import _fallback
    from barobuddy.models import Assessment

    assessment = Assessment(
        event="conflicting_signals",
        summary="Pressure and elevation signals conflict.",
        evidence=("The observed trends do not align.",),
        uncertainty="The cause is unclear.",
        pressure_change_hpa=-1.0,
        elevation_change_m=40.0,
        data_quality="All readings passed basic validation.",
    )

    result = _fallback(assessment)

    assert result.used_fallback is True
    assert "conflict" in result.explanation.lower()
    assert "more observations" in result.next_step.lower()


def make_assessment() -> Assessment:
    return Assessment(
        event="falling_pressure_trend",
        summary="Pressure is falling while elevation remains stable.",
        evidence=("Pressure fell by 2.0 hPa.",),
        uncertainty="Pressure changes alone do not establish future weather.",
        pressure_change_hpa=-2.0,
        elevation_change_m=0.0,
        data_quality="All readings passed basic validation.",
    )


def test_malformed_model_json_uses_fallback():
    assessment = make_assessment()
    response_payload = {"message": {"content": "{not valid json"}}

    with patch("barobuddy.ai_assistant.urlopen") as mock_urlopen:
        mock_response = mock_urlopen.return_value.__enter__.return_value
        mock_response.read.return_value = json.dumps(response_payload).encode("utf-8")

        result = explain_assessment(assessment)

    assert result.used_fallback is True
    assert result.explanation == assessment.summary


def test_missing_model_field_uses_fallback():
    assessment = make_assessment()
    response_payload = {
        "message": {"content": json.dumps({"explanation": "Pressure is falling."})}
    }

    with patch("barobuddy.ai_assistant.urlopen") as mock_urlopen:
        mock_response = mock_urlopen.return_value.__enter__.return_value
        mock_response.read.return_value = json.dumps(response_payload).encode("utf-8")

        result = explain_assessment(assessment)

    assert result.used_fallback is True
    assert result.explanation == assessment.summary
