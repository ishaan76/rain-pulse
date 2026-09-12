"""AquaAlert AI — Agent 5 Component: Actionable Alert Cards.

Renders high and medium priority hazard bulletins with tactical civil advisories.
"""

from typing import List
import streamlit as st
from backend.contracts import GridPredictionResult


def render_alert_cards(grid_results: List[GridPredictionResult]) -> None:
    """Render prioritized operational alerts for high and medium risk locations.

    Args:
        grid_results: Evaluated GridPredictionResult items from backend.
    """
    critical_cells = [r for r in grid_results if r.prediction.risk_level in ["HIGH", "MEDIUM"]]

    if not critical_cells:
        st.success("✅ All pilot sectors reporting normal operational conditions. No active flood alerts.")
        return

    # Sort so highest risk appears first
    critical_cells.sort(key=lambda r: r.prediction.risk_score, reverse=True)

    for res in critical_cells:
        level = res.prediction.risk_level
        is_high = level == "HIGH"
        box_class = "action-box-warning" if is_high else "action-box-info"
        badge_class = f"risk-badge-{level.lower()}"

        st.markdown(
            f"""
            <div class="{box_class}" style="margin-bottom: 12px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span style="font-weight: 700; font-size: 1.05rem;">{res.cell.name}</span>
                    <span class="{badge_class}">{level} · {int(res.prediction.risk_score)} / 100</span>
                </div>
                <div style="font-size: 0.9rem; color: #c9d1d9; margin-bottom: 6px;">
                    <b>Environmental Drivers:</b> Rain: {res.features.rainfall_3h} mm | Slope: {res.cell.slope}° | Elev: {res.cell.elevation} m
                </div>
                <div style="font-size: 0.92rem; font-weight: 600; color: {'#ffa198' if is_high else '#79c0ff'};">
                    ⚠️ Recommendation: {res.recommendation}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
