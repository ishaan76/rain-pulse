"""AquaAlert AI — Agent 5 Page: Overview (Default Landing View).

Implements Section 4 wireframe:
- Current Area Risk KPI
- Rainfall / Hotspots / Forecast Stats
- 3D PyDeck Interactive Risk Map
- Selected Hotspot Inspector & "Why Is This High?" Attribution Breakdown
- Actionable Recommendations
"""

from typing import List, Set
import streamlit as st

from backend.contracts import AreaRiskSummary, GridPredictionResult
from app.components.risk_card import render_current_risk_card
from app.components.map_view import render_interactive_map


def render_overview_page(
    summary: AreaRiskSummary,
    grid_results: List[GridPredictionResult],
    selected_area: str,
    active_filters: Set[str],
) -> None:
    """Render the default Overview main stage view."""
    # 1. High-Priority Risk Header
    col_kpi, col_stats = st.columns([1.1, 2.0])

    with col_kpi:
        render_current_risk_card(summary)

    with col_stats:
        s1, s2, s3 = st.columns(3)
        with s1:
            st.markdown(
                f"""
                <div class="stat-box">
                    <div class="stat-label">Rainfall (3h)</div>
                    <div class="stat-value">{summary.rainfall_3h} <span style="font-size:0.9rem; color:#8b949e;">mm</span></div>
                    <div style="font-size:0.75rem; color:#8b949e; margin-top:2px;">Rate: {summary.rainfall_intensity} mm/h</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with s2:
            st.markdown(
                f"""
                <div class="stat-box">
                    <div class="stat-label">Hotspots</div>
                    <div class="stat-value" style="color: {'#f85149' if summary.hotspots_detected > 0 else '#2ea043'};">
                        {summary.hotspots_detected} <span style="font-size:0.9rem; color:#8b949e;">critical</span>
                    </div>
                    <div style="font-size:0.75rem; color:#8b949e; margin-top:2px;">Threshold: &ge; 70</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with s3:
            st.markdown(
                f"""
                <div class="stat-box">
                    <div class="stat-label">Peak Forecast</div>
                    <div class="stat-value" style="font-size:1.15rem; color:#58a6ff;">
                        {summary.peak_forecast_text}
                    </div>
                    <div style="font-size:0.75rem; color:#8b949e; margin-top:2px;">0–6h horizon</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # 2. Interactive Risk Map
    st.markdown("##### 🗺️ Real-Time Waterlogging & Inundation Risk Map")
    render_interactive_map(grid_results, selected_area, active_filters, height=380)

    # 3. Selected Hotspot Details & "Why Is This High?" Breakdown
    st.markdown("---")
    st.markdown("##### 🔍 Localized Sector Risk Inspector & Explainability")

    cell_names = [r.cell.name for r in grid_results]
    # Default selection to the highest risk cell
    worst_idx = 0
    if grid_results:
        scores = [r.prediction.risk_score for r in grid_results]
        worst_idx = scores.index(max(scores))

    selected_name = st.selectbox(
        "Select Sector / Landmark to Inspect:",
        options=cell_names,
        index=worst_idx,
        help="Choose a location to inspect topographical drivers and recommended actions.",
    )

    selected_result = next((r for r in grid_results if r.cell.name == selected_name), grid_results[0])

    c_left, c_right = st.columns([1.2, 1.0])

    with c_left:
        level = selected_result.prediction.risk_level
        score = int(selected_result.prediction.risk_score)
        badge_class = f"risk-badge-{level.lower()}"

        st.markdown(
            f"""
            <div style="background: #151d28; border: 1px solid #233042; border-radius: 8px; padding: 16px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h4 style="margin:0; color:#e6edf3;">{selected_result.cell.name}</h4>
                    <span class="{badge_class}">{level} · {score} / 100</span>
                </div>
                <p style="margin: 8px 0 12px 0; font-size:0.92rem; color:#8b949e;">
                    <b>Terrain:</b> Elevation {selected_result.cell.elevation} m | Slope {selected_result.cell.slope}° | Trunk Drain Dist: {int(selected_result.cell.drainage_distance)} m
                </p>
                <div class="{'action-box-warning' if level == 'HIGH' else 'action-box-info'}">
                    ⚠️ <b>Operational Action:</b> {selected_result.recommendation}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c_right:
        st.markdown(
            """
            <div style="background: #151d28; border: 1px solid #233042; border-radius: 8px; padding: 16px;">
                <span style="font-size:0.8rem; font-weight:700; color:#8b949e; text-transform:uppercase;">
                    Why Is This {level}? (Feature Contributions)
                </span>
            </div>
            """.replace("{level}", level),
            unsafe_allow_html=True,
        )
        for driver, weight in selected_result.drivers.items():
            st.write(f"**{driver}** ({weight}%)")
            st.progress(int(weight))
