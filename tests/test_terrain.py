"""Unit Tests for Agent 2 — Terrain & Drainage Subsystem."""

import pytest
from data.terrain.elevation import calculate_slope, classify_slope_risk
from data.terrain.drainage import classify_drainage_quality, compute_drainage_vulnerability_score
from data.terrain.service import TerrainService


def test_calculate_slope():
    """Verify slope computation math."""
    # 10m rise over 100m run
    slope = calculate_slope(200.0, 210.0, 100.0)
    assert 5.0 < slope < 6.0
    # Zero distance should return 0.0 without division by zero
    assert calculate_slope(200.0, 210.0, 0.0) == 0.0


def test_classify_slope_risk():
    """Verify slope risk classification."""
    assert classify_slope_risk(1.0) == "FLAT_DEPRESSION"
    assert classify_slope_risk(2.5) == "GENTLE_SLOPE"
    assert classify_slope_risk(5.0) == "STEEP_RUNOFF"


def test_drainage_quality_and_score():
    """Verify drainage quality classification and vulnerability scoring."""
    poor = classify_drainage_quality(drainage_distance_m=800.0, drainage_density=0.2)
    assert poor == "Poor"

    good = classify_drainage_quality(drainage_distance_m=150.0, drainage_density=0.8)
    assert good == "Good"

    score_poor = compute_drainage_vulnerability_score(800.0, 0.2)
    score_good = compute_drainage_vulnerability_score(150.0, 0.8)
    assert score_poor > score_good
    assert 0.0 <= score_good <= 100.0
    assert 0.0 <= score_poor <= 100.0


def test_terrain_service_grid_generation():
    """Verify TerrainService generates valid GridCell contracts for pilot areas."""
    service = TerrainService()
    delhi_cells = service.get_grid_cells("Delhi NCR")
    assert len(delhi_cells) > 0
    assert delhi_cells[0].cell_id.startswith("DEL_")
    assert delhi_cells[0].elevation > 0
    assert 0.0 <= delhi_cells[0].slope <= 90.0
