# Agent 1 — Weather & Rainfall Subsystem Playbook

## Responsibility
Build and maintain the meteorology data layer.

## Owned Files & Folders
- `data/weather/client.py`: Live Open-Meteo HTTP client with timeout & error handling.
- `data/weather/parser.py`: Moving window calculator for `rainfall_1h`, `rainfall_3h`, `rainfall_6h`, and `rainfall_intensity`.
- `data/weather/fallback.py`: Pre-baked realistic rainfall scenarios for pilot areas.
- `data/weather/service.py`: `WeatherService` facade connecting live and fallback data.
- `tests/test_weather.py`: Agent 1 unit test suite.

## Interface Contract Output
```python
{
    "rainfall_1h": float,       # mm
    "rainfall_3h": float,       # mm
    "rainfall_6h": float,       # mm
    "rainfall_intensity": float, # mm/h
    "is_fallback": bool,
    "scenario_name": str,
}
```

## How to Test
```bash
python -m pytest tests/test_weather.py -v
```
