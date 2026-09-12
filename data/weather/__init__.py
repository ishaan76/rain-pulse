"""Agent 1 — Weather & Rainfall Module."""

from data.weather.service import WeatherService
from data.weather.fallback import get_fallback_weather_scenario

__all__ = ["WeatherService", "get_fallback_weather_scenario"]
