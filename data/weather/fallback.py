"""AquaAlert AI — Agent 1: Weather Fallback Scenarios.

Provides guaranteed, realistic weather scenarios for pilot areas when
offline or running in hackathon demo mode.
"""

from typing import Dict, Any


DEMO_WEATHER_SCENARIOS: Dict[str, Dict[str, Any]] = {
    "Delhi NCR": {
        "scenario_name": "Yamuna Basin Monsoon Surge & Cloudburst",
        "horizons": {
            0: {"rainfall_1h": 24.5, "rainfall_3h": 42.0, "rainfall_6h": 58.0, "rainfall_intensity": 25.0},
            1: {"rainfall_1h": 32.0, "rainfall_3h": 56.5, "rainfall_6h": 72.0, "rainfall_intensity": 32.0},
            3: {"rainfall_1h": 45.0, "rainfall_3h": 72.0, "rainfall_6h": 98.0, "rainfall_intensity": 45.0},
            6: {"rainfall_1h": 12.0, "rainfall_3h": 35.0, "rainfall_6h": 110.0, "rainfall_intensity": 14.0},
        },
    },
    "Noida": {
        "scenario_name": "Sector Expressway Drainage Saturation",
        "horizons": {
            0: {"rainfall_1h": 18.0, "rainfall_3h": 34.0, "rainfall_6h": 45.0, "rainfall_intensity": 20.0},
            1: {"rainfall_1h": 28.0, "rainfall_3h": 46.0, "rainfall_6h": 60.0, "rainfall_intensity": 28.0},
            3: {"rainfall_1h": 38.0, "rainfall_3h": 64.0, "rainfall_6h": 84.0, "rainfall_intensity": 38.0},
            6: {"rainfall_1h": 10.0, "rainfall_3h": 28.0, "rainfall_6h": 94.0, "rainfall_intensity": 12.0},
        },
    },
    "Gurugram": {
        "scenario_name": "Badshahpur Drain Overfill Event",
        "horizons": {
            0: {"rainfall_1h": 28.0, "rainfall_3h": 48.0, "rainfall_6h": 62.0, "rainfall_intensity": 30.0},
            1: {"rainfall_1h": 36.0, "rainfall_3h": 62.0, "rainfall_6h": 80.0, "rainfall_intensity": 36.0},
            3: {"rainfall_1h": 52.0, "rainfall_3h": 82.0, "rainfall_6h": 105.0, "rainfall_intensity": 52.0},
            6: {"rainfall_1h": 14.0, "rainfall_3h": 38.0, "rainfall_6h": 119.0, "rainfall_intensity": 16.0},
        },
    },
    "Ghaziabad": {
        "scenario_name": "Hindon Lowland Confluence Spate",
        "horizons": {
            0: {"rainfall_1h": 16.0, "rainfall_3h": 30.0, "rainfall_6h": 40.0, "rainfall_intensity": 18.0},
            1: {"rainfall_1h": 22.0, "rainfall_3h": 40.0, "rainfall_6h": 52.0, "rainfall_intensity": 24.0},
            3: {"rainfall_1h": 32.0, "rainfall_3h": 54.0, "rainfall_6h": 70.0, "rainfall_intensity": 34.0},
            6: {"rainfall_1h": 8.0, "rainfall_3h": 22.0, "rainfall_6h": 78.0, "rainfall_intensity": 10.0},
        },
    },
}


def get_fallback_weather_scenario(area_name: str, horizon_hours: int = 0) -> Dict[str, Any]:
    """Retrieve pre-computed weather metrics for offline / demo mode.

    Args:
        area_name: Name of the pilot area.
        horizon_hours: Forecast offset in hours (0, 1, 3, or 6).

    Returns:
        Dictionary with rainfall accumulation and peak intensity figures.
    """
    area_data = DEMO_WEATHER_SCENARIOS.get(area_name, DEMO_WEATHER_SCENARIOS["Delhi NCR"])
    horizons = area_data["horizons"]
    
    # Map to nearest supported horizon key
    available_horizons = sorted(horizons.keys())
    closest_horizon = min(available_horizons, key=lambda h: abs(h - horizon_hours))
    
    metrics = horizons[closest_horizon].copy()
    metrics["scenario_name"] = area_data["scenario_name"]
    metrics["is_fallback"] = True
    return metrics
