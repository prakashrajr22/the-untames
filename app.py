"""
app.py
SmartMess AI — entry point / sidebar shell.
Pages live under pages/ and are auto-discovered by Streamlit's native
multipage nav. This file intentionally stays thin.
"""

import streamlit as st

st.set_page_config(
    page_title="SmartMess AI",
    page_icon="🍽️",
    layout="wide",
)

st.title("🍽️ SmartMess AI")
st.caption("AI-Powered Food Waste Prevention & Adaptive Meal Planning")

st.markdown(
    """
    Use the sidebar to navigate:
    - **Dashboard** — today's preparation recommendation
    - **Prediction** — demand model details
    - **Simulator** — what-if planning
    - **Kitchen** — log actuals (prepared/consumed)
    - **Analytics** — historical trends
    - **Model Performance** — MAE / accuracy tracking
    """
)
