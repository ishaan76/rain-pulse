"""AquaAlert AI — Agent 5 Component: Forecast Timeline Charts & Table.

Renders temporal risk progression and rainfall intensity metrics across the 0–6h horizon.
"""

from typing import List, Dict, Any
import pandas as pd
import streamlit as st


def render_forecast_views(timeline_data: List[Dict[str, Any]]) -> None:
    """Render structured tabular and graphical forecast timeline.

    Args:
        timeline_data: List of snapshots from backend get_forecast_timeline.
    """
    df = pd.DataFrame(timeline_data)

    # 1. Tabular Summary matching Section 6.3 wireframe
    st.markdown("##### ⏱️ Horizon Risk Progression")
    table_rows = []
    for row in timeline_data:
        color = "#f85149" if row["risk_level"] == "HIGH" else ("#d29922" if row["risk_level"] == "MEDIUM" else "#2ea043")
        table_rows.append({
            "Time": row["time"],
            "Peak Risk": f"{row['max_risk']} / 100",
            "Risk Tier": row["risk_level"],
            "Rainfall (3h)": f"{row['rainfall_3h']} mm",
            "Intensity": f"{row['intensity']} mm/h",
        })

    st.dataframe(
        pd.DataFrame(table_rows),
        use_container_width=True,
        hide_index=True,
    )

    # 2. Charts for Risk & Rainfall Trends
    st.markdown("##### 📊 Risk & Precipitation Forecast Curve")
    col1, col2 = st.columns(2)

    with col1:
        st.caption("Maximum Peak Risk Score across Pilot Basin")
        chart_df = df.set_index("time")[["max_risk", "avg_risk"]]
        chart_df.columns = ["Peak Risk", "Average Risk"]
        st.line_chart(chart_df, color=["#f85149", "#58a6ff"])

    with col2:
        st.caption("Rainfall 3h Accumulation (mm) & Rate (mm/h)")
        rain_df = df.set_index("time")[["rainfall_3h", "intensity"]]
        rain_df.columns = ["Accumulation (3h)", "Intensity (mm/h)"]
        st.bar_chart(rain_df, color=["#58a6ff", "#d29922"])
