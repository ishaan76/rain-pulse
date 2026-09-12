# Agent 1 — Weather & Rainfall Subsystem Playbook

## Responsibility
Build and maintain the meteorology data layer.

## Owned Files & Folders
- `data/weather/client.py`: Live Open-Meteo HTTP client with timeout, error handling, and structured logging.
- `data/weather/parser.py`: Moving window calculator for `rainfall_1h`, `rainfall_3h`, `rainfall_6h`, and `rainfall_intensity`.
- `data/weather/fallback.py`: Pre-baked realistic rainfall scenarios for pilot areas (Delhi NCR, Noida, Gurugram, Ghaziabad, Greater Noida).
- `data/weather/service.py`: `WeatherService` facade with logging and LRU caching to reduce redundant API calls.
- `tests/test_weather.py`: Agent 1 unit test suite.

## Primary Pilot Area
**Greater Noida** — lat: 28.4744, lon: 77.5040
- Live data fetched from Open-Meteo (no API key required).
- Fallback scenario name: "Yamuna Expressway Corridor Waterlogging".

## Supported Fallback Areas
| Area | Scenario Name |
|------|--------------|
| Greater Noida | Yamuna Expressway Corridor Waterlogging |
| Delhi NCR | Yamuna Basin Monsoon Surge & Cloudburst |
| Noida | Sector Expressway Drainage Saturation |
| Gurugram | Badshahpur Drain Overfill Event |
| Ghaziabad | Hindon Lowland Confluence Spate |

## Interface Contract Output
```python
{
    "rainfall_1h": float,        # mm
    "rainfall_3h": float,        # mm
    "rainfall_6h": float,        # mm
    "rainfall_intensity": float, # mm/h
    "is_fallback": bool,
    "scenario_name": str,
}
```

## Logging & Caching Behaviour
- `WeatherClient` emits `DEBUG` logs for every request/response and `WARNING`/`ERROR` on failure.
- `WeatherService` emits `INFO` logs when demo or fallback mode is triggered.
- Live fetches are wrapped in `functools.lru_cache(maxsize=32)` to avoid duplicate HTTP calls on Streamlit reruns.
- To see logs, add to `app/main.py`: `logging.basicConfig(level=logging.INFO)`

## How to Test
```bash
python -m pytest tests/test_weather.py -v
```
