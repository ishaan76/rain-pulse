"""Unit Tests for Agent 4 — Backend & Pipeline Orchestration."""

import pytest
from backend.validator import validate_area_name, parse_horizon_string
from backend.service import AquaAlertBackend, get_current_risk, get_grid_predictions


def test_validator():
    """Verify input validation and horizon parsing."""
    assert validate_area_name("Delhi NCR") == "Delhi NCR"
    with pytest.raises(ValueError):
        validate_area_name("Atlantis")

    assert parse_horizon_string("Now") == 0
    assert parse_horizon_string("+1 hour") == 1
    assert parse_horizon_string("+3 hours") == 3
    assert parse_horizon_string("+6 hours") == 6


def test_backend_current_risk():
    """Verify get_current_risk returns valid AreaRiskSummary."""
    summary = get_current_risk("Delhi NCR", use_demo=True)
    assert summary.area_name == "Delhi NCR"
    assert 0.0 <= summary.average_risk_score <= 100.0
    assert 0.0 <= summary.max_risk_score <= 100.0
    assert summary.overall_risk_level in ["LOW", "MEDIUM", "HIGH"]
    assert summary.top_recommendation != ""


def test_backend_grid_predictions():
    """Verify get_grid_predictions coordinates weather, terrain, and ML correctly."""
    grid_results = get_grid_predictions("Noida", horizon=1, use_demo=True)
    assert len(grid_results) > 0
    first = grid_results[0]
    assert first.cell.name != ""
    assert 0.0 <= first.prediction.risk_score <= 100.0
    assert "Rainfall" in first.drivers
    assert first.recommendation != ""


def test_backend_forecast_timeline():
    """Verify forecast timeline generates 6 distinct snapshots."""
    backend = AquaAlertBackend()
    timeline = backend.get_forecast_timeline("Delhi NCR", use_demo=True)
    assert len(timeline) == 6
    assert timeline[0]["time"] == "NOW"
    assert timeline[-1]["time"] == "+6h"
    assert all("max_risk" in snap for snap in timeline)
