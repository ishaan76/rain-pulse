"""Unit Tests for Agent 5 — UI & Map Subsystem."""

import pytest
from app.components.map_view import get_color_for_level
from backend.service import get_backend
from backend.contracts import GridPredictionResult


def test_get_color_for_level_semantics():
    """Verify exact color semantic compliance as per project spec."""
    # LOW -> green
    green = get_color_for_level("LOW")
    assert green[0] == 46 and green[1] == 160 and green[2] == 67

    # MEDIUM -> amber
    amber = get_color_for_level("MEDIUM")
    assert amber[0] == 210 and amber[1] == 153 and amber[2] == 34

    # HIGH -> red
    red = get_color_for_level("HIGH")
    assert red[0] == 248 and red[1] == 81 and red[2] == 73


def test_ui_data_binding():
    """Verify backend produces required fields consumed by UI views."""
    backend = get_backend()
    summary = backend.get_current_risk("Delhi NCR", use_demo=True)
    grid_results = backend.get_grid_predictions("Delhi NCR", horizon=0, use_demo=True)
    timeline = backend.get_forecast_timeline("Delhi NCR", use_demo=True)

    assert hasattr(summary, "max_risk_score")
    assert hasattr(summary, "overall_risk_level")
    assert len(grid_results) > 0
    assert len(timeline) == 6
