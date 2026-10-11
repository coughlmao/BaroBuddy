import json
import os
from dataclasses import dataclass
from urllib.request import Request, urlopen

from dotenv import load_dotenv

from barobuddy.models import Assessment

load_dotenv()

OPEN_WEIGHT_MODEL = os.getenv("OPEN_WEIGHT_MODEL", "gemma4:e2b")
DEFAULT_BASE_URL = os.getenv("DEFAULT_BASE_URL", "http://localhost:11434")
DEFAULT_TIMEOUT_SECONDS = int(os.getenv("DEFAULT_TIMEOUT_SECONDS", "120"))


@dataclass(frozen=True)
class AIExplanation:
    explanation: str
    next_step: str
    used_fallback: bool


def _fallback(assessment: Assessment) -> AIExplanation:
    """Return a useful explanation without calling the model."""
    return AIExplanation(
        explanation=assessment.summary,
        next_step=(
            "Keep monitoring the readings. Check an official local forecast "
            "before making weather-related decisions."
        ),
        used_fallback=True,
    )


def explain_assessment(
    assessment: Assessment,
    *,
    model: str = OPEN_WEIGHT_MODEL,
    base_url: str | None = None,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
) -> AIExplanation:
    """Explain a detector assessment using local Ollama, with safe fallback."""
    base_url = (base_url or os.getenv("OLLAMA_BASE_URL", DEFAULT_BASE_URL)).rstrip("/")

    prompt_data = {
        "detected_event": assessment.event,
        "detector_summary": assessment.summary,
        "evidence": list(assessment.evidence),
        "uncertainty": assessment.uncertainty,
        "data_quality": assessment.data_quality,
        "pressure_change_hpa": assessment.pressure_change_hpa,
        "elevation_change_m": assessment.elevation_change_m,
    }

    prompt = f"""
You are BaroBuddy, an offline outdoor-awareness assistant.

Explain the supplied detector assessment in plain, concise language.
Use only the facts in the JSON input. Do not invent readings or causes.
Do not predict storms or claim that a storm is confirmed.
Do not diagnose, give guarantees, or override the detector.
If the data is uncertain or insufficient, say so.
Recommend a cautious, practical next step. For weather decisions,
recommend checking an official local forecast.

Return only a JSON object with exactly these string fields:
- explanation
- next_step

Assessment:
{json.dumps(prompt_data, ensure_ascii=False)}
""".strip()

    request_body = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Follow the user's data and constraints. " "Return valid JSON only."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "stream": False,
        "format": "json",
        "options": {"temperature": 0},
    }

    try:
        request = Request(
            f"{base_url}/api/chat",
            data=json.dumps(request_body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))

        content = payload["message"]["content"]
        parsed = json.loads(content)

        explanation = parsed.get("explanation")
        next_step = parsed.get("next_step")

        if not isinstance(explanation, str) or not explanation.strip():
            return _fallback(assessment)

        if not isinstance(next_step, str) or not next_step.strip():
            return _fallback(assessment)

        # Keep responses bounded and avoid rendering arbitrary long output.
        explanation = explanation.strip()[:1000]
        next_step = next_step.strip()[:500]

        return AIExplanation(
            explanation=explanation,
            next_step=next_step,
            used_fallback=False,
        )

    # except (OSError, TimeoutError, ValueError, KeyError, TypeError):
    #     return _fallback(assessment)

    except (OSError, TimeoutError, ValueError, KeyError, TypeError) as exc:
        print(f"[BaroBuddy AI debug] {type(exc).__name__}: {exc}")
        return _fallback(assessment)
