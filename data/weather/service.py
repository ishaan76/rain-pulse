"""AquaAlert AI — Agent 1: Weather Service Interface.

Main entrypoint for Agent 1. Provides clean, structured weather data
with automatic fallback if offline or during demo mode.
"""

from typing import Any, Optional, Dict
import logging
import functools
from data.weather.client import WeatherClient
from data.weather.fallback import get_fallback_weather_scenario
from data.weather.parser import parse_weather_response
class WeatherService:
    """Service providing standardized weather and rainfall intelligence."""

    def __init__(self, client: WeatherClient = None) -> None:
        """Initialize weather service."""
        self.client = client or WeatherClient()
        self.logger = logging.getLogger(__name__)
        # Cached wrapper for live forecast to avoid duplicate API calls within a short period
        @functools.lru_cache(maxsize=32)
        def _cached(lat: float, lon: float) -> Optional[Dict[str, Any]]:
            return self.client.fetch_live_forecast(lat, lon)
        self._cached_fetch = _cached
    def get_weather_features(
        self,
        latitude: float,
        longitude: float,
        area_name: str = "Delhi NCR",
        horizon_hours: int = 0,
        use_demo: bool = False,
    ) -> dict[str, Any]:
        """Obtain rainfall features for a given location and horizon.

        Args:
            latitude: Target latitude in decimal degrees.
            longitude: Target longitude in decimal degrees.
            area_name: Pilot area name for fallback lookups.
            horizon_hours: Forecast offset (0, 1, 3, or 6 hours).
            use_demo: Force use of pre-baked hackathon scenario.

        Returns:
            Dictionary containing rainfall_1h, rainfall_3h, rainfall_6h,
            rainfall_intensity, is_fallback flag, and scenario name.
        """
        if use_demo:
            self.logger.info("Using demo fallback scenario for area %s, horizon %d", area_name, horizon_hours)
            return get_fallback_weather_scenario(area_name, horizon_hours)

        # Use cached fetch to reduce duplicate API calls
        raw = self._cached_fetch(latitude, longitude)
        if raw is not None:
            features = parse_weather_response(raw, horizon_hours)
            features["is_fallback"] = False
            features["scenario_name"] = (
                f"Live Open-Meteo ({latitude:.2f}, {longitude:.2f})"
            )
            return features

        # Automatic graceful fallback when API fails or offline
        self.logger.info("Falling back to demo scenario for area %s, horizon %d", area_name, horizon_hours)
        return get_fallback_weather_scenario(area_name, horizon_hours)
