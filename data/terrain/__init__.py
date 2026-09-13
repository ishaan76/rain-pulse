"""Agent 2 — Terrain & Drainage Module."""

from data.terrain.service import TerrainService, TerrainDataUnavailableError
from data.terrain.elevation import calculate_slope, classify_slope_risk
from data.terrain.drainage import classify_drainage_quality, compute_drainage_vulnerability_score
from data.terrain.dem_client import CopernicusDEMClient, DEMUnavailableError
from data.terrain.osm_client import OSMDrainageClient, OSMUnavailableError

__all__ = [
    "TerrainService",
    "TerrainDataUnavailableError",
    "calculate_slope",
    "classify_slope_risk",
    "classify_drainage_quality",
    "compute_drainage_vulnerability_score",
    "CopernicusDEMClient",
    "DEMUnavailableError",
    "OSMDrainageClient",
    "OSMUnavailableError",
]