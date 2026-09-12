"""AquaAlert AI — Agent 3: Feature Attribution & Explanation Engine.

Computes physical and model-derived feature contributions for the
"Why Is This High?" interactive dashboard panel.
"""

from typing import Dict
from backend.contracts import EnvironmentalFeatures


def explain_prediction_drivers(features: EnvironmentalFeatures) -> Dict[str, float]:
    """Calculate normalized contribution percentage for primary risk drivers.

    Args:
        features: Environmental parameters of the evaluated location.

    Returns:
        Dictionary mapping driver name to its percentage contribution (sums to 100%).
    """
    # 1. Rainfall volume & intensity drive
    rain_weight = (features.rainfall_3h / 60.0) * 0.45 + (features.rainfall_intensity / 35.0) * 0.25
    rain_weight = max(0.05, rain_weight)

    # 2. Drainage bottleneck drive (distance & low density)
    drain_dist_ratio = features.drainage_distance / 800.0
    drain_dens_deficit = 1.0 - features.drainage_density
    drain_weight = max(0.05, (0.5 * drain_dist_ratio + 0.5 * drain_dens_deficit) * 0.40)

    # 3. Slope vulnerability (flat depression traps water)
    slope_weight = max(0.05, (2.0 / max(0.5, features.slope)) * 0.30)

    # 4. Elevation vulnerability (lower elevation in catchment)
    # Normalized relative to 200m baseline
    elev_weight = max(0.05, max(0.0, (220.0 - features.elevation) / 30.0) * 0.20)

    total = rain_weight + drain_weight + slope_weight + elev_weight

    return {
        "Rainfall": round((rain_weight / total) * 100.0, 1),
        "Drainage": round((drain_weight / total) * 100.0, 1),
        "Slope": round((slope_weight / total) * 100.0, 1),
        "Elevation": round((elev_weight / total) * 100.0, 1),
    }


def generate_recommendation(risk_level: str, drivers: Dict[str, float]) -> str:
    """Generate concise operational advisory based on risk tier and primary driver.

    Args:
        risk_level: 'LOW', 'MEDIUM', or 'HIGH'.
        drivers: Dictionary of driver weights from explain_prediction_drivers.

    Returns:
        Actionable recommendation string.
    """
    if risk_level == "HIGH":
        primary = max(drivers.items(), key=lambda x: x[1])[0]
        if primary == "Rainfall":
            return "Severe flash waterlogging imminent: avoid low-lying underpasses & subterranean corridors."
        elif primary == "Drainage":
            return "Primary stormwater outfalls choked: divert transit away from underpass catchments."
        else:
            return "Low-lying basin accumulating runoff: barricade subterranean ramps & stage suction pumps."
    elif risk_level == "MEDIUM":
        return "Water accumulation likely in curb lanes: allow additional travel time and reduce transit speed."
    else:
        return "Normal operational status: stormwater network operating within safe hydraulic design capacity."
