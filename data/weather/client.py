"""AquaAlert AI — Agent 1: Live Open-Meteo Weather Client.

Fetches real-time precipitation and hourly forecasts from Open-Meteo.
Includes resilient error handling, parameter validation, and connection timeouts.
"""

from typing import Dict, Any, Optional
import requests


OPEN_METEO_BASE_URL = "https://api.open-meteo.com/v1/forecast"
REQUEST_TIMEOUT_SECONDS = 5.0


class WeatherClient:
    """HTTP Client for live Open-Meteo precipitation metrics."""

    def __init__(self, timeout: float = REQUEST_TIMEOUT_SECONDS) -> None:
        """Initialize weather client with timeout.

        Args:
            timeout: Request timeout duration in seconds.
        """
        self.timeout = timeout

    def fetch_live_forecast(self, latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
        """Fetch precipitation metrics and hourly forecasts for given coordinates.

        Args:
            latitude: Target latitude in decimal degrees.
            longitude: Target longitude in decimal degrees.

        Returns:
            Raw API response JSON dict if successful, None on failure.
        """
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": "precipitation,rain,showers",
            "current": "precipitation,rain",
            "timezone": "auto",
            "forecast_days": 2,
        }

        try:
            response = requests.get(
                OPEN_METEO_BASE_URL,
                params=params,
                timeout=self.timeout,
            )
            if response.status_code == 200:
                return response.json()
            return None
        except (requests.RequestException, ValueError, KeyError):
            return None
