"""AquaAlert AI — Agent 5 Page: Full Risk Map Explorer.

Implements Section 6.2 wireframe:
- Full-screen geospatial map
- Standardized Risk Legend (LOW, MEDIUM, HIGH)
- Detailed Inspector Panel with terrain, elevation, and drainage quality
"""

from typing import List, Set
import streamlit as st

from backend.contracts import GridPredictionResult
from app.components.map_view import render_interactive_map
from data.terrain.drainage import classify_drainage_quality


def render_risk_map_page(
    grid_results: List[GridPredictionResult],
    selected_area: str,
    active_filters: Set[str],
) -> None:
    """Render the full-screen Risk Map stage view."""
    # Risk Color Legend
    col_t, col_leg = st.columns([2, 1])
    with col_t:
        st.subheader(f"🗺️ Spatial Hazard Analysis — {selected_area}")
    with col_leg:
        st.markdown(
            """
            <div style="display:flex; justify-content:flex-end; gap:12px; margin-top:8px; font-size:0.85rem; font-weight:600;">
                <span style="color:#2ea043;">● LOW (&lt; 40)</span>
                <span style="color:#d29922;">● MEDIUM (40–70)</span>
                <span style="color:#f85149;">● HIGH (&ge; 70)</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Large 3D PyDeck Map
    render_interactive_map(grid_results, selected_area, active_filters, height=520)

    # Bottom Inspector for Clicked / Selected Sector
    st.markdown("---")
    st.markdown("#### 📋 Sector Environmental Breakdown")

    cell_names = [r.cell.name for r in grid_results]
    chosen_cell_name = st.selectbox("Inspect Grid Location:", options=cell_names, key="map_page_cell_selector")
    res = next((r for r in grid_results if r.cell.name == chosen_cell_name), grid_results[0])

    drain_quality = classify_drainage_quality(res.cell.drainage_distance, res.cell.drainage_density)

    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        st.markdown(
            f"""
            <div class="stat-box">
                <div class="stat-label">Location & Hazard Tier</div>
                <div class="stat-value" style="font-size:1.15rem;">{res.cell.name}</div>
                <div style="margin-top:6px;">
                    <span class="risk-badge-{res.prediction.risk_level.lower()}">
                        {res.prediction.risk_level} · {int(res.prediction.risk_score)} / 100
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            f"""
            <div class="stat-box">
                <div class="stat-label">Precipitation Telemetry</div>
                <div style="font-size:0.95rem; color:#e6edf3; margin-top:6px;">
                    • <b>Accumulation (3h):</b> {res.features.rainfall_3h} mm<br/>
                    • <b>Peak Intensity:</b> {res.features.rainfall_intensity} mm/h<br/>
                    • <b>Accumulation (6h):</b> {res.features.rainfall_6h} mm
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            f"""
            <div class="stat-box">
                <div class="stat-label">Terrain & Drainage Physics</div>
                <div style="font-size:0.95rem; color:#e6edf3; margin-top:6px;">
                    • <b>Elevation:</b> {res.cell.elevation} m<br/>
                    • <b>Slope:</b> {res.cell.slope}°<br/>
                    • <b>Drainage Egress:</b> {drain_quality} ({int(res.cell.drainage_distance)} m)
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
