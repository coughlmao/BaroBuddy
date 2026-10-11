# BaroBuddy 🏔️

**An offline-first outdoor awareness prototype that turns environmental readings into understandable assessments.**

BaroBuddy analyzes pressure and elevation readings with deterministic Python rules, then uses a locally running Gemma model through Ollama to explain the assessment in plain language. If the local model is unavailable or returns an unusable response, BaroBuddy falls back to deterministic guidance.

> **Demo limitation:** The current prototype uses simulated readings. It is not a weather forecast, storm predictor, or safety-warning system. Its thresholds are illustrative and have not been scientifically validated. Check an official local forecast before making weather-related decisions.

## Features

- **Six simulated scenarios:** Uphill climb, falling pressure, conflicting signals, steady conditions, pressure recovery, and abrupt pressure change.
- **Rule-based assessment:** Classifies observed patterns using explicit pressure, elevation, and data-quality checks.
- **Evidence and uncertainty:** Displays the assessment, supporting evidence, data-quality information, and uncertainty.
- **Time-series charts:** Plots pressure and elevation over the simulated observation window.
- **Local AI explanation:** Uses Gemma through Ollama to explain the detector's result without replacing the detector.
- **Graceful fallback:** Provides deterministic guidance when Ollama is unavailable or the model response cannot be used.
- **Automated tests:** Covers simulator patterns, detector behavior, and AI fallback handling.

## How It Works

```text
Simulated readings
       |
       v
Rule-based detector
       |
       v
Assessment + evidence + uncertainty
       |
       +------> Streamlit dashboard and charts
       |
       v
Local Gemma explanation via Ollama
       |
       +------> Deterministic fallback if unavailable
```

The detector is the source of the assessment. The language model explains that assessment; it does not independently establish weather conditions or confirm a storm.

## Requirements

- Windows, macOS, or Linux
- Python 3.13
- [uv](https://docs.astral.sh/uv/)
- [Ollama](https://ollama.com/) for local AI explanations

BaroBuddy's simulated scenarios and rule-based assessment can be explored without relying on a live weather API or physical sensor. The AI explanation feature requires a working local Ollama installation and the configured model; otherwise, the app should use its fallback.

## Setup

### 1. Clone the repository

Replace the placeholder with your actual GitHub repository URL.

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd BaroBuddy
```

### 2. Install dependencies

```bash
uv sync
```

### 3. Set up the local AI model

Install Ollama, then pull the model used by the project:

```bash
ollama pull gemma4:e2b
```

Make sure Ollama is running before requesting AI explanations. The application uses the local Ollama service at `http://localhost:11434` by default.

The default model is `gemma4:e2b`. The application also supports configuration through environment variables, including `OPEN_WEIGHT_MODEL`, `OLLAMA_BASE_URL`, and `DEFAULT_TIMEOUT_SECONDS`.

## Run the App

From the repository root, run:

```bash
uv run streamlit run app.py
```

Open the local URL displayed in your terminal, usually:

[http://localhost:8501](http://localhost:8501)

Choose a simulated scenario to view its assessment, evidence, uncertainty, data quality, and pressure/elevation charts. Select **Generate explanation with Gemma** to request a local explanation.

## Run the Tests

Run the automated test suite with:

```bash
uv run python -m pytest -q
```

## Project Structure

```text
BaroBuddy/
├── app.py
├── pyproject.toml
├── uv.lock
├── barobuddy/
│   ├── __init__.py
│   ├── models.py
│   ├── simulator.py
│   ├── detector.py
│   ├── ai_assistant.py
│   └── data/
│       ├── __init__.py
│       └── scenarios.py
└── tests/
    ├── test_simulator.py
    ├── test_detector.py
    └── test_ai_fallback.py
```

## Assessment Scenarios

| Scenario | What It Demonstrates |
|---|---|
| Uphill climb | Pressure changes alongside increasing elevation |
| Falling pressure | Pressure falls while elevation remains stable |
| Conflicting signals | Observed pressure and elevation signals do not align clearly |
| Steady conditions | The configured rules detect no significant change |
| Pressure recovery | Pressure rises after a lower-pressure interval |
| Abrupt pressure change | A large adjacent pressure change is flagged by the configured rule |

These are controlled demonstration scenarios, not real-world measurements.

## Design Principles

- **Offline-first:** No live weather API is required for the current demo.
- **Deterministic assessment:** Explicit Python rules produce the event classification.
- **Local AI:** Gemma is accessed through the local Ollama service.
- **Transparent uncertainty:** Evidence, data quality, and uncertainty remain visible alongside the explanation.
- **Graceful degradation:** A usable fallback is available when the model call fails.

## Limitations

- All current readings are simulated; no live sensors or weather feeds are connected.
- Pressure and elevation thresholds are illustrative and not validated for forecasting or outdoor safety.
- Pressure trends alone cannot determine the cause of a change or establish that conditions are safe or dangerous.
- AI explanations may be imperfect. The model is constrained to explain the detector's assessment and should not be treated as authoritative weather advice.
- The prototype does not replace official forecasts, emergency guidance, or local expertise.

## Roadmap

Potential next steps include improving the demo experience, expanding automated test coverage, and exploring optional accessibility features such as text-to-speech. Any future live-data or sensor integration should preserve clear data provenance, uncertainty, and privacy.
