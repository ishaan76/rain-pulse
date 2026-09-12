"""AquaAlert AI — System Configuration & Area Definitions.

Defines pilot administrative regions, geospatial coordinates, default thresholds,
and operational parameters.
"""

from typing import Dict, Any

# Pilot monitoring areas supported for SIH demonstration
PILOT_AREAS: Dict[str, Dict[str, Any]] = {
    "Delhi NCR": {
        "latitude": 28.6139,
        "longitude": 77.2090,
        "zoom": 11,
        "description": "National Capital Region core basin (Yamuna floodplains & urban centers)",
    },
    "Noida": {
        "latitude": 28.5355,
        "longitude": 77.3910,
        "zoom": 12,
        "description": "Gautam Buddha Nagar planned urban sectors & expressways",
    },
    "Gurugram": {
        "latitude": 28.4595,
        "longitude": 77.0266,
        "zoom": 12,
        "description": "Millennium City drainage corridors (Badshahpur drain catchment)",
    },
    "Ghaziabad": {
        "latitude": 28.6692,
        "longitude": 77.4538,
        "zoom": 12,
        "description": "Hindon river basin and industrial-residential lowlands",
    },
}

DEFAULT_AREA: str = "Delhi NCR"

# Risk Tier Categorization Thresholds
LOW_RISK_THRESHOLD: float = 40.0
HIGH_RISK_THRESHOLD: float = 70.0

# Forecast horizon options (hours)
FORECAST_HORIZONS = ["Now", "+1 hour", "+3 hours", "+6 hours"]

# Hybrid fusion weightings: (0.65 * ML) + (0.35 * Hydrological Physics)
ML_WEIGHT: float = 0.65
PHYSICS_WEIGHT: float = 0.35
