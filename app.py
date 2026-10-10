import streamlit as st

st.set_page_config(
    page_title="BaroBuddy",
    page_icon="🏔️",
    layout="wide",
)

st.title("🏔️ BaroBuddy")
st.caption("Your offline-first outdoor awareness companion")

st.info(
    "MVP development is underway. Environmental readings "
    "will be simulated until real sensor support is implemented."
)

left, right = st.columns(2)

with left:
    st.subheader("Environmental monitoring")
    st.metric("Atmospheric pressure", "—", help="Measured in hPa")
    st.metric("Elevation", "—", help="Measured in metres")

with right:
    st.subheader("Field assessment")
    st.write("**Status:** Awaiting scenario data")
    st.write("**Evidence:** Not yet available")
    st.write("**Uncertainty:** Not yet evaluated")

st.divider()

st.subheader("Local AI assistant")
st.write("Selected model: `gemma4:e2b`")
st.caption("Local AI explanations will be connected in a later milestone.")

st.subheader("Coming next")
st.markdown(
    """
    - Reproducible environmental scenarios
    - Pressure and elevation trend detection
    - Explicit uncertainty handling
    - Local explanations powered by Gemma
    """
)

st.caption(
    "Prototype only — not a weather forecasting, "
    "navigation, or medical safety system."
)
