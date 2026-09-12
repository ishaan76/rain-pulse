"""AquaAlert AI — Agent 5 Component: Risk Score & KPI Card.

Renders primary risk score, categorical tier badge, and peak forecast indicator.
"""

import streamlit as st
from backend.contracts import AreaRiskSummary


def render_current_risk_card(summary: AreaRiskSummary) -> None:
    """Render high-priority Current Risk panel for default Overview view.

    Args:
        summary: Aggregated AreaRiskSummary from backend.
    """
    badge_class = f"risk-badge-{summary.overall_risk_level.lower()}"
    score_class = f"kpi-score-{summary.overall_risk_level.lower()}"

    st.markdown(
        f"""
        <div class="risk-kpi-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-size: 0.85rem; color: #8b949e; text-transform: uppercase; letter-spacing: 0.08em; font-weight: 600;">
                    Area Flood Hazard Index
                </span>
                <span class="{badge_class}">{summary.overall_risk_level}</span>
            </div>
            <div style="display: flex; align-items: baseline; gap: 8px; margin-bottom: 4px;">
                <span class="{score_class}">{int(summary.max_risk_score)}</span>
                <span style="color: #8b949e; font-size: 1.1rem; font-weight: 500;">/ 100</span>
            </div>
            <div style="font-size: 0.9rem; color: #8b949e; margin-top: 4px;">
                ⏱️ {summary.peak_forecast_text}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
