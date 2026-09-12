# Agent 6 — Testing, QA & Final Integration Playbook

## Responsibility
Test the complete end-to-end AquaAlert system, enforce architectural contracts, and guarantee demo reliability.

## Owned Files & Folders
- `tests/test_integration.py`: End-to-end data pipeline tests (Weather + Terrain -> Features -> Model -> Backend -> UI).
- `tests/test_weather.py`: Agent 1 integration & fallback checks.
- `tests/test_terrain.py`: Agent 2 geospatial elevation & drainage checks.
- `tests/test_model.py`: Agent 3 monotonicity, bounds, and schema checks.
- `tests/test_backend.py`: Agent 4 service & timeline checks.
- `tests/test_app.py`: Agent 5 UI color semantics and data binding checks.

## Verification Checklist
- [x] Zero API key hardcoding (environment variables & local fallback).
- [x] Resilient offline demo mode (no network failure crashes).
- [x] Monotonic response to rainfall surges and low-slope depressions.
- [x] 100% test pass rate across all 6 subsystems.

## How to Run Complete QA Suite
```bash
python -m pytest -v
```
