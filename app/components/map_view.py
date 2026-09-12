"""AquaAlert AI — Agent 5 Component: PyDeck Interactive 3D Spatial Map.

Renders geospatial grid cells, hotspot markers, and risk layers using PyDeck.
"""

from typing import List, Set
import pandas as pd
import pydeck as pdk
import streamlit as st

from backend.contracts import GridPredictionResult
from backend.config import PILOT_AREAS


def get_color_for_level(level: str) -> List[int]:
    """Map risk level to RGB color list as specified by project guidelines.

    LOW -> green [46, 160, 67]
    MEDIUM -> amber [210, 153, 34]
    HIGH -> red [248, 81, 73]
    """
    if level == "HIGH":
        return [248, 81, 73, 220]
    elif level == "MEDIUM":
        return [210, 153, 34, 200]
    else:
        return [46, 160, 67, 180]


def render_interactive_map(
    grid_results: List[GridPredictionResult],
    selected_area: str,
    active_filters: Set[str],
    show_hotspots_only: bool = False,
    height: int = 440,
) -> None:
    """Render 3D PyDeck chart inside Streamlit.

    Args:
        grid_results: Evaluated GridPredictionResult items.
        selected_area: Name of active area for map center coordinates.
        active_filters: Set containing allowed levels, e.g. {'Low', 'Medium', 'High'}.
        show_hotspots_only: Filter strictly for critical hotspots.
        height: Pixel height of map canvas.
    """
    area_meta = PILOT_AREAS.get(selected_area, PILOT_AREAS["Delhi NCR"])
    center_lat = area_meta["latitude"]
    center_lon = area_meta["longitude"]
    zoom_level = area_meta.get("zoom", 11)

    # Transform results into pandas DataFrame for PyDeck
    records = []
    for r in grid_results:
        # Check active filters
        tier_title = r.prediction.risk_level.capitalize()
        if tier_title not in active_filters:
            continue
        if show_hotspots_only and not r.is_hotspot:
            continue

        color = get_color_for_level(r.prediction.risk_level)
        records.append({
            "name": r.cell.name,
            "latitude": r.cell.latitude,
            "longitude": r.cell.longitude,
            "risk_score": r.prediction.risk_score,
            "risk_level": r.prediction.risk_level,
            "elevation": r.cell.elevation,
            "slope": r.cell.slope,
            "rainfall_3h": r.features.rainfall_3h,
            "intensity": r.features.rainfall_intensity,
            "color": color,
            "elevation_scale": r.prediction.risk_score * 12.0,  # 3D column extrusion height
        })

    if not records:
        st.info("No grid cells match the currently selected risk filters.")
        return

    df = pd.DataFrame(records)

    # 1. 3D Column Layer for Risk Visualization
    column_layer = pdk.Layer(
        "ColumnLayer",
        data=df,
        get_position=["longitude", "latitude"],
        get_elevation="elevation_scale",
        elevation_scale=1,
        radius=400,
        get_fill_color="color",
        pickable=True,
        auto_highlight=True,
    )

    # 2. Scatterplot Halo Layer for visibility
    scatter_layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position=["longitude", "latitude"],
        get_color="color",
        get_radius=500,
        pickable=True,
    )

    view_state = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=zoom_level,
        pitch=35,
        bearing=0,
    )

    tooltip = {
        "html": """
            <div style="font-family: sans-serif; font-size: 12px; padding: 6px; background: #0d131a; color: #fff; border-radius: 4px; border: 1px solid #233042;">
                <b>{name}</b><br/>
                Risk: <b>{risk_level}</b> ({risk_score} / 100)<br/>
                Rainfall 3h: <b>{rainfall_3h} mm</b> (Rate: {intensity} mm/h)<br/>
                Elevation: <b>{elevation} m</b> | Slope: <b>{slope}°</b>
            </div>
        """,
        "style": {"color": "white"},
    }

    deck = pdk.Deck(
        layers=[scatter_layer, column_layer],
        initial_view_state=view_state,
        tooltip=tooltip,
        map_style="mapbox://styles/mapbox/dark-v10",
    )

    st.pydeck_chart(deck, use_container_width=True, height=height)
