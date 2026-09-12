"""AquaAlert AI — Agent 5 Page: Predictive Forecast Horizon.

Implements Section 6.3:
- Demonstrates predictive forecasting (0–6 hours) rather than static weather reports.
- Tabular forecast with time steps: NOW, +1h, +2h, +3h, +4h, +6h.
- Precipitation and risk accumulation curves.
"""

from typing import List, Dict, Any
import streamlit as st
from app.components.forecast_chart import render_forecast_views


def render_forecast_page(
    timeline_data: List[Dict[str, Any]],
    selected_area: str,
) -> None:
    """Render the 0-6 hour forecast progression view."""
    st.subheader(f"⏱️ 0–6 Hour Predictive Hazard Forecast — {selected_area}")
    st.info(
        "AquaAlert computes dynamic hydrological head and runoff accumulation to project "
        "how waterlogging vulnerability evolves over the next 6 hours."
    )

    render_forecast_views(timeline_data)
