import pandas as pd
import streamlit as st

from barobuddy.ai_assistant import explain_assessment
from barobuddy.data.scenarios import SCENARIOS
from barobuddy.detector import assess_readings
from barobuddy.simulator import generate_scenario

st.set_page_config(
    page_title="BaroBuddy",
    page_icon="🏔️",
    layout="wide",
)

st.title("🏔️ BaroBuddy")
st.caption("Your offline-first outdoor awareness companion")

st.info(
    "Demo mode: all environmental readings are simulated. "
    "This prototype does not provide weather forecasts or safety warnings."
)

selected_scenario = st.selectbox(
    "Choose a simulated scenario",
    options=SCENARIOS,
    format_func=lambda scenario: scenario.label,
)

scenario = generate_scenario(selected_scenario.name)
assessment = assess_readings(list(scenario.readings))

st.subheader(selected_scenario.label)
st.write(selected_scenario.description)

# Convert the simulated readings into chart-friendly data.
chart_data = pd.DataFrame(
    [
        {
            "timestamp": reading.timestamp,
            "pressure_hpa": reading.pressure_hpa,
            "elevation_m": reading.elevation_m,
        }
        for reading in scenario.readings
    ]
)

# Environmental readings
pressure_col, elevation_col = st.columns(2)

with pressure_col:
    st.subheader("Atmospheric pressure")
    st.line_chart(
        chart_data,
        x="timestamp",
        y="pressure_hpa",
        x_label="Time",
        y_label="Pressure (hPa)",
    )

    if assessment.pressure_change_hpa is not None:
        st.metric(
            "Change over the displayed window",
            f"{assessment.pressure_change_hpa:+.2f} hPa",
        )

with elevation_col:
    st.subheader("Elevation")
    st.line_chart(
        chart_data,
        x="timestamp",
        y="elevation_m",
        x_label="Time",
        y_label="Elevation (m)",
    )

    if assessment.elevation_change_m is not None:
        st.metric(
            "Change over the displayed window",
            f"{assessment.elevation_change_m:+.2f} m",
        )

st.divider()

# Detector assessment
# Detector assessment — show the main finding first.
st.subheader("Field assessment")

st.markdown("### " + assessment.event.replace("_", " ").title())
st.write(assessment.summary)

if assessment.event == "insufficient_data":
    st.warning("There is not enough reliable data for a useful assessment.")
elif assessment.event == "conflicting_signals":
    st.warning("The observed signals conflict; interpret this result cautiously.")
elif assessment.event == "abrupt_pressure_change":
    st.warning("A rapid pressure change was detected; its cause is unknown.")
elif assessment.event == "falling_pressure_trend":
    st.info("Pressure fell while elevation remained relatively stable.")
elif assessment.event == "elevation_associated_pressure_change":
    st.info("Pressure changed alongside elevation.")
else:
    st.success("No significant change was detected by the current rules.")

evidence_col, quality_col = st.columns(2)

with evidence_col:
    st.markdown("**Evidence**")
    for item in assessment.evidence:
        st.markdown(f"- {item}")

with quality_col:
    st.markdown("**Data quality**")
    st.write(assessment.data_quality)

st.markdown("**Uncertainty**")
st.warning(assessment.uncertainty)

st.divider()

# Environmental readings
st.subheader("Measurements over time")

chart_data = pd.DataFrame(
    [
        {
            "timestamp": reading.timestamp,
            "pressure_hpa": reading.pressure_hpa,
            "elevation_m": reading.elevation_m,
        }
        for reading in scenario.readings
    ]
)

pressure_col, elevation_col = st.columns(2)

with pressure_col:
    st.subheader("Atmospheric pressure")
    st.line_chart(
        chart_data,
        x="timestamp",
        y="pressure_hpa",
        x_label="Time",
        y_label="Pressure (hPa)",
    )

    if assessment.pressure_change_hpa is not None:
        st.metric(
            "Change over the displayed window",
            f"{assessment.pressure_change_hpa:+.2f} hPa",
        )

with elevation_col:
    st.subheader("Elevation")
    st.line_chart(
        chart_data,
        x="timestamp",
        y="elevation_m",
        x_label="Time",
        y_label="Elevation (m)",
    )

    if assessment.elevation_change_m is not None:
        st.metric(
            "Change over the displayed window",
            f"{assessment.elevation_change_m:+.2f} m",
        )

with st.expander("Inspect simulated readings"):
    st.dataframe(chart_data, use_container_width=True)
    st.caption(
        f"{len(scenario.readings)} simulated readings. " "Times are shown in UTC."
    )

st.divider()

# Local AI explanation with a deterministic fallback.
st.subheader("Local AI assistant")
st.caption("Model: `gemma4:e2b` from Google")

if st.button("Generate explanation with Gemma"):
    with st.spinner("Generating a local explanation..."):
        explanation = explain_assessment(assessment)

    st.session_state["ai_explanation"] = explanation
    st.session_state["ai_scenario"] = selected_scenario

if (
    "ai_explanation" in st.session_state
    and st.session_state.get("ai_scenario") == selected_scenario
):
    explanation = st.session_state["ai_explanation"]

    if explanation.used_fallback:
        st.info(
            "Local AI is unavailable or returned an unusable response. "
            "Showing the deterministic fallback instead."
        )
    else:
        st.success("Explanation generated locally.")

    st.markdown("**What this means**")
    st.write(explanation.explanation)

    st.markdown("**Suggested next step**")
    st.write(explanation.next_step)

    # Keep the detector's uncertainty visible regardless of AI output.
    st.markdown("**Detector's uncertainty**")
    st.warning(assessment.uncertainty)
else:
    st.write(
        "The detector is ready. Select this button when you want "
        "Gemma to explain the current assessment."
    )
