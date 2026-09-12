"""AquaAlert AI — Agent 2: Drainage & Stormwater Channel Processing.

Models proximity to major drainage canals, stormwater conduit density,
and drainage vulnerability proxies.
"""

from typing import Tuple


def classify_drainage_quality(drainage_distance_m: float, drainage_density: float) -> str:
    """Determine drainage performance category.

    Args:
        drainage_distance_m: Distance to nearest primary drain in meters.
        drainage_density: Drainage network density (0.0 to 1.0).

    Returns:
        Qualitative tier ('Poor', 'Moderate', 'Good').
    """
    if drainage_distance_m > 600.0 or drainage_density < 0.35:
        return "Poor"
    elif drainage_distance_m > 300.0 or drainage_density < 0.65:
        return "Moderate"
    return "Good"


def compute_drainage_vulnerability_score(drainage_distance_m: float, drainage_density: float) -> float:
    """Compute a normalized 0-100 drainage vulnerability score.

    Higher scores indicate higher risk (far from drains, low density).

    Args:
        drainage_distance_m: Distance to nearest primary drain in meters.
        drainage_density: Drainage density ratio between 0.0 and 1.0.

    Returns:
        Vulnerability score between 0.0 (optimal drainage) and 100.0 (severely choked/distant).
    """
    # Distance factor: cap at 1000m
    norm_dist = min(1.0, max(0.0, drainage_distance_m / 1000.0))
    # Density factor: inverse of density
    norm_inv_density = 1.0 - min(1.0, max(0.0, drainage_density))

    # 60% weight on distance to trunk drain, 40% on localized network density
    score = (0.60 * norm_dist + 0.40 * norm_inv_density) * 100.0
    return round(score, 1)
