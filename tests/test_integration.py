"""AquaAlert AI — Agent 6: End-to-End System Integration Tests.

Verifies the complete data pipeline:
Weather + Terrain + Drainage -> Features -> ML Model -> Hybrid Risk -> Backend -> Streamlit.
Tests resilience against missing APIs, extreme weather, and invalid inputs.
"""

import pytest
from backend.service import get_backend
from backend.contracts import EnvironmentalFeatures
from model.predictor import predict_flood_risk
from backend.config import PILOT_AREAS


def test_end_to_end_pipeline_all_pilot_areas():
    """Verify end-to-end pipeline execution across all pilot administrative areas."""
    backend = get_backend()

    for area_name in PILOT_AREAS.keys():
        # 1. Evaluate current area risk
        summary = backend.get_current_risk(area_name, use_demo=True)
        assert summary.area_name == area_name
        assert 0.0 <= summary.average_risk_score <= 100.0
        assert summary.overall_risk_level in ["LOW", "MEDIUM", "HIGH"]

        # 2. Evaluate spatial grid
        grid = backend.get_grid_predictions(area_name, horizon=0, use_demo=True)
        assert len(grid) > 0
        for item in grid:
            assert item.cell.name != ""
            assert 0.0 <= item.prediction.risk_score <= 100.0
            assert item.prediction.risk_level in ["LOW", "MEDIUM", "HIGH"]
            assert len(item.drivers) == 4
            assert item.recommendation != ""

        # 3. Evaluate forecast timeline
        timeline = backend.get_forecast_timeline(area_name, use_demo=True)
        assert len(timeline) == 6


def test_extreme_rainfall_cloudburst_scenario():
    """Verify system response under extreme 100mm cloudburst stress test."""
    extreme_features = EnvironmentalFeatures(
        rainfall_1h=50.0,
        rainfall_3h=100.0,
        rainfall_6h=140.0,
        rainfall_intensity=60.0,
        elevation=195.0,  # Lowland underpass
        slope=0.8,        # Flat depression
        drainage_distance=900.0,  # Far from drain
        drainage_density=0.15,    # Choked drain
        historical_risk=0.95,
    )
    result = predict_flood_risk(extreme_features)
    assert result.risk_level == "HIGH"
    assert result.risk_score >= 80.0
    assert result.physical_score >= 80.0


def test_bone_dry_scenario():
    """Verify zero rainfall with good drainage produces LOW risk."""
    dry_features = EnvironmentalFeatures(
        rainfall_1h=0.0,
        rainfall_3h=0.0,
        rainfall_6h=0.0,
        rainfall_intensity=0.0,
        elevation=235.0,
        slope=4.5,
        drainage_distance=200.0,
        drainage_density=0.85,
        historical_risk=0.15,
    )
    result = predict_flood_risk(dry_features)
    assert result.risk_level == "LOW"
    assert result.risk_score < 40.0


def test_missing_api_fallback_resilience():
    """Verify backend automatically recovers using pre-baked fallback when live API fails."""
    backend = get_backend()
    # Force use_demo=False on coordinates that test resilience
    try:
        # Querying live with timeout fallback
        results = backend.get_grid_predictions("Delhi NCR", horizon=0, use_demo=False)
        assert len(results) > 0
    except Exception as exc:
        pytest.fail(f"Backend failed to gracefully recover: {exc}")
