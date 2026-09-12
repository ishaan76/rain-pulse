"""AquaAlert AI — Agent 3: Hydrological & Physical Runoff Engine.

Computes domain-informed physical runoff vulnerability scores (0–100)
adapted from the Rational Method (Q = C * I * A) and surface depression pooling.
"""

from backend.contracts import EnvironmentalFeatures


def calculate_physical_runoff_score(features: EnvironmentalFeatures) -> float:
    """Calculate physics-informed environmental runoff and pooling risk score.

    Combines hydraulic head, topographical depression, and drainage egress capacity.

    Args:
        features: Target environmental parameters.

    Returns:
        Score between 0.0 (minimal runoff hazard) and 100.0 (severe hydraulic saturation).
    """
    # 1. Rainfall volume factor (normalized up to 100 mm in 3h)
    rain_factor = min(1.0, features.rainfall_3h / 80.0) * 0.40

    # 2. Intensity surge factor (normalized up to 50 mm/h)
    intensity_factor = min(1.0, features.rainfall_intensity / 40.0) * 0.20

    # 3. Slope ponding factor: Flat areas (< 1.5 deg) trap water; steep slopes drain
    # Inverse sigmoid-like decay for slope
    if features.slope < 1.0:
        slope_factor = 0.25
    elif features.slope < 2.0:
        slope_factor = 0.18
    elif features.slope < 4.0:
        slope_factor = 0.08
    else:
        slope_factor = 0.02

    # 4. Drainage egress impediment factor (distance + inverse density)
    dist_ratio = min(1.0, features.drainage_distance / 1000.0)
    density_deficit = 1.0 - max(0.0, min(1.0, features.drainage_density))
    drainage_factor = (0.5 * dist_ratio + 0.5 * density_deficit) * 0.15

    # Sum raw components (total sum up to 1.0)
    raw_sum = rain_factor + intensity_factor + slope_factor + drainage_factor

    # Scale to 0-100 range and clamp
    physical_score = round(min(100.0, max(0.0, raw_sum * 100.0)), 1)
    return physical_score
