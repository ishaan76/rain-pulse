"""Unit Tests for Agent 1 — Weather & Rainfall Subsystem."""

import pytest
from data.weather.fallback import get_fallback_weather_scenario
from data.weather.parser import parse_weather_response
from data.weather.service import WeatherService


def test_fallback_weather_delhi():
    """Verify fallback weather generation returns valid numerical bounds."""
    weather = get_fallback_weather_scenario("Delhi NCR", horizon_hours=3)
    assert weather["rainfall_1h"] > 0
    assert weather["rainfall_3h"] >= weather["rainfall_1h"]
    assert weather["rainfall_6h"] >= weather["rainfall_3h"]
    assert weather["rainfall_intensity"] > 0
    assert weather["is_fallback"] is True


def test_weather_parser_empty():
    """Verify parser handles empty responses gracefully."""
    parsed = parse_weather_response({})
    assert parsed["rainfall_1h"] == 0.0
    assert parsed["rainfall_3h"] == 0.0
    assert parsed["rainfall_6h"] == 0.0
    assert parsed["rainfall_intensity"] == 0.0


def test_weather_parser_mock_payload():
    """Verify parser computes correct moving window accumulations."""
    mock_payload = {
        "hourly": {
            "precipitation": [5.0, 10.0, 15.0, 20.0, 10.0, 5.0]
        }
    }
    # At horizon 2 (index 2: values [5.0, 10.0, 15.0])
    parsed = parse_weather_response(mock_payload, horizon_hours=2)
    assert parsed["rainfall_1h"] == 15.0
    assert parsed["rainfall_3h"] == 30.0  # 5 + 10 + 15
    assert parsed["rainfall_intensity"] == 15.0


def test_weather_service_demo_mode():
    """Verify WeatherService respects demo mode."""
    service = WeatherService()
    weather = service.get_weather_features(28.61, 77.20, area_name="Delhi NCR", use_demo=True)
    assert weather["is_fallback"] is True
    assert "Yamuna" in weather["scenario_name"]
