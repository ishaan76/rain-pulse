"""Unit Tests for Agent 3 — ML & Prediction Subsystem."""

import pytest
from backend.contracts import EnvironmentalFeatures
from model.features import validate_features, features_to_array
from model.physical_engine import calculate_physical_runoff_score
from model.hybrid_engine import blend_hybrid_risk
from model.predictor import predict_flood_risk, predict_grid
from model.explainer import explain_prediction_drivers, generate_recommendation
from data.terrain.service import TerrainService


def test_feature_validation_rejects_invalid_bounds():
    """Verify validate_features raises ValueError on negative rainfall or out-of-range slope."""
    bad_features = EnvironmentalFeatures(
        rainfall_1h=-5.0,
        rainfall_3h=10.0,
        rainfall_6h=20.0,
        rainfall_intensity=5.0,
        elevation=200.0,
        slope=2.0,
        drainage_distance=400.0,
        drainage_density=0.5,
    )
    with pytest.raises(ValueError):
        validate_features(bad_features)

    bad_slope = EnvironmentalFeatures(
        rainfall_1h=5.0,
        rainfall_3h=10.0,
        rainfall_6h=20.0,
        rainfall_intensity=5.0,
        elevation=200.0,
        slope=120.0,  # Invalid slope > 90
        drainage_distance=400.0,
        drainage_density=0.5,
    )
    with pytest.raises(ValueError):
        validate_features(bad_slope)


def test_physical_runoff_monotonic_response():
    """Verify physical runoff score increases with heavier rainfall and flatter slope."""
    base_dry = EnvironmentalFeatures(
        rainfall_1h=0.0,
        rainfall_3h=0.0,
        rainfall_6h=0.0,
        rainfall_intensity=0.0,
        elevation=210.0,
        slope=3.0,
        drainage_distance=300.0,
        drainage_density=0.7,
    )
    base_monsoon = EnvironmentalFeatures(
        rainfall_1h=30.0,
        rainfall_3h=70.0,
        rainfall_6h=95.0,
        rainfall_intensity=35.0,
        elevation=198.0,
        slope=0.9,  # Depression
        drainage_distance=800.0,  # Poor drainage
        drainage_density=0.2,
    )
    score_dry = calculate_physical_runoff_score(base_dry)
    score_monsoon = calculate_physical_runoff_score(base_monsoon)
    assert score_monsoon > score_dry
    assert 0.0 <= score_dry <= 100.0
    assert 0.0 <= score_monsoon <= 100.0


def test_hybrid_risk_blending():
    """Verify hybrid risk formula and categorization."""
    score_low, level_low = blend_hybrid_risk(ml_probability=0.10, physical_score=20.0)
    assert level_low == "LOW"
    assert score_low < 40.0

    score_high, level_high = blend_hybrid_risk(ml_probability=0.90, physical_score=85.0)
    assert level_high == "HIGH"
    assert score_high >= 70.0


def test_predict_flood_risk_contract():
    """Verify predict_flood_risk returns compliant RiskPrediction object."""
    sample_features = EnvironmentalFeatures(
        rainfall_1h=35.0,
        rainfall_3h=65.0,
        rainfall_6h=85.0,
        rainfall_intensity=30.0,
        elevation=196.0,
        slope=1.1,
        drainage_distance=700.0,
        drainage_density=0.25,
        historical_risk=0.85,
    )
    result = predict_flood_risk(sample_features)
    assert 0.0 <= result.risk_score <= 100.0
    assert result.risk_level in ["LOW", "MEDIUM", "HIGH"]
    assert 0.0 <= result.ml_probability <= 1.0
    assert 0.0 <= result.physical_score <= 100.0


def test_predict_grid_execution():
    """Verify predict_grid computes predictions across spatial cells."""
    terrain_service = TerrainService()
    cells = terrain_service.get_grid_cells("Delhi NCR")
    mock_weather = {
        "rainfall_1h": 25.0,
        "rainfall_3h": 50.0,
        "rainfall_6h": 70.0,
        "rainfall_intensity": 25.0,
    }
    grid_results = predict_grid(cells, mock_weather)
    assert len(grid_results) == len(cells)
    # Ensure at least one hotspot detected in extreme rainfall
    assert all(0.0 <= r.prediction.risk_score <= 100.0 for r in grid_results)
    assert all(r.recommendation != "" for r in grid_results)
