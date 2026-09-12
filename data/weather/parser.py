"""AquaAlert AI — Agent 1: Weather Response Parser.

Extracts moving window accumulations: rainfall_1h, rainfall_3h, rainfall_6h,
and peak rainfall intensity from raw weather series.
"""

from typing import Any
def parse_weather_response(
    raw_data: dict[str, Any],
    horizon_hours: int = 0,
) -> dict[str, float]:
    """Parse raw Open-Meteo payload into structured rainfall features.

    Args:
        raw_data: JSON dictionary from Open-Meteo API.
        horizon_hours: Forecast offset (e.g. 0 for Now, 1, 3, or 6 hours ahead).

    Returns:
        Dictionary containing rainfall_1h, rainfall_3h, rainfall_6h, and rainfall_intensity.
    """
    hourly = raw_data.get("hourly", {})
    precip_list: list[float] = hourly.get("precipitation", [])

    if not precip_list:
        # Fallback to zero if empty
        return {
            "rainfall_1h": 0.0,
            "rainfall_3h": 0.0,
            "rainfall_6h": 0.0,
            "rainfall_intensity": 0.0,
        }

    # Identify the index offset corresponding to horizon_hours
    # Open-Meteo hourly output typically starts from hour 0 of current day.
    # We take current slice plus horizon
    current_idx = min(horizon_hours, len(precip_list) - 1)

    # Calculate 1h accumulation
    val_1h = float(precip_list[current_idx]) if current_idx < len(precip_list) else 0.0

    # Calculate 3h accumulation
    start_3h = max(0, current_idx - 2)
    slice_3h = precip_list[start_3h : current_idx + 1]
    val_3h = float(sum(slice_3h)) if slice_3h else val_1h

    # Calculate 6h accumulation
    start_6h = max(0, current_idx - 5)
    slice_6h = precip_list[start_6h : current_idx + 1]
    val_6h = float(sum(slice_6h)) if slice_6h else val_3h

    # Intensity (peak mm/h in recent window)
    intensity = float(max(slice_3h)) if slice_3h else val_1h

    return {
        "rainfall_1h": round(max(0.0, val_1h), 2),
        "rainfall_3h": round(max(0.0, val_3h), 2),
        "rainfall_6h": round(max(0.0, val_6h), 2),
        "rainfall_intensity": round(max(0.0, intensity), 2),
    }
