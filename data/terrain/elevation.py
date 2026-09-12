"""AquaAlert AI — Agent 2: Elevation & Topographical Slope Processing.

Provides terrain elevation models and slope gradient calculations
based on Copernicus DEM benchmarks.
"""

from typing import Tuple


def calculate_slope(elevation_center: float, elevation_neighbor: float, distance_meters: float) -> float:
    """Calculate slope in degrees between two elevation points.

    Args:
        elevation_center: Elevation at target center in meters.
        elevation_neighbor: Elevation at neighboring reference point in meters.
        distance_meters: Horizontal distance between points in meters.

    Returns:
        Slope angle in degrees (>= 0.0).
    """
    if distance_meters <= 0:
        return 0.0
    rise = abs(elevation_center - elevation_neighbor)
    # tan(theta) = rise / run
    import math
    radians = math.atan(rise / distance_meters)
    return round(math.degrees(radians), 2)


def classify_slope_risk(slope_degrees: float) -> str:
    """Classify waterlogging vulnerability based on slope.

    Areas with slope < 1.5 degrees suffer from severe pooling and slow runoff.

    Args:
        slope_degrees: Terrain slope in degrees.

    Returns:
        Descriptive classification ('FLAT_DEPRESSION', 'GENTLE_SLOPE', 'STEEP_RUNOFF').
    """
    if slope_degrees < 1.5:
        return "FLAT_DEPRESSION"
    elif slope_degrees < 4.0:
        return "GENTLE_SLOPE"
    else:
        return "STEEP_RUNOFF"
