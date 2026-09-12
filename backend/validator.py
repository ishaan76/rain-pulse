"""AquaAlert AI — Agent 4: Request Validation.

Validates administrative area selection, coordinates, and forecast parameters.
"""

from typing import Tuple
from backend.config import PILOT_AREAS, FORECAST_HORIZONS


def validate_area_name(area_name: str) -> str:
    """Validate and sanitize area selection against configured pilot regions.

    Args:
        area_name: Requested pilot area name.

    Returns:
        Sanitized matching area name.

    Raises:
        ValueError: If area_name is not supported.
    """
    if area_name not in PILOT_AREAS:
        valid_areas = list(PILOT_AREAS.keys())
        raise ValueError(f"Unknown area '{area_name}'. Supported areas are: {valid_areas}")
    return area_name


def parse_horizon_string(horizon_str: str) -> int:
    """Convert horizon string (e.g. 'Now', '+1 hour', '+3 hours', '+6 hours') to hour integer.

    Args:
        horizon_str: UI horizon selector string.

    Returns:
        Integer offset in hours (0, 1, 3, or 6).
    """
    if "1" in horizon_str:
        return 1
    elif "3" in horizon_str:
        return 3
    elif "6" in horizon_str:
        return 6
    return 0
