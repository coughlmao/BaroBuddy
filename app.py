import pandas as pd
import streamlit as st

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

# Scenario selection
scenario_options = {
    "Uphill climb": "uphill_climb",
    "Falling pressure": "falling_pressure",
    "Conflicting signals": "conflicting_signals",
}

selected_label = st.selectbox(
    "Choose a simulated scenario",
    options=list(scenario_options.keys()),
)

scenario = generate_scenario(scenario_options[selected_label])
assessment = assess_readings(list(scenario.readings))

st.subheader(selected_label)
st.write(scenario.description)

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
st.subheader("Field assessment")

st.write("**Detected event:**", assessment.event.replace("_", " ").title())
st.write(assessment.summary)

st.markdown("**Evidence**")
for item in assessment.evidence:
    st.markdown(f"- {item}")

st.markdown("**Uncertainty**")
st.warning(assessment.uncertainty)

st.markdown("**Data quality**")
st.write(assessment.data_quality)

with st.expander("Inspect simulated readings"):
    st.dataframe(chart_data, use_container_width=True)
    st.caption(
        f"{len(scenario.readings)} simulated readings. " "Times are shown in UTC."
    )

st.divider()

# AI integration will be added in a later milestone.
st.subheader("Local AI assistant")
st.write("Selected model: `gemma4:e2b`")
st.caption(
    "Next milestone: use the local model to explain the detector's "
    "evidence and uncertainty without changing its classification."
)

st.caption(
    "Prototype only — not a weather forecasting, navigation, "
    "or medical safety system."
)
