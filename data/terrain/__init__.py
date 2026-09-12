"""Agent 2 — Terrain & Drainage Module."""

from data.terrain.service import TerrainService
from data.terrain.elevation import calculate_slope, classify_slope_risk
from data.terrain.drainage import classify_drainage_quality, compute_drainage_vulnerability_score

__all__ = [
    "TerrainService",
    "calculate_slope",
    "classify_slope_risk",
    "classify_drainage_quality",
    "compute_drainage_vulnerability_score",
]
