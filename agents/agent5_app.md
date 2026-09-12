# Agent 5 — Streamlit UI & Interactive Map Playbook

## Responsibility
Build and maintain the user-facing Streamlit dashboard and 3D spatial map visualizations.

## Owned Files & Folders
- `app/main.py`: Main application layout, sidebar controls, header bar, and tab routing.
- `app/pages/overview.py`: Default overview view with KPI cards, 3D map, and hotspot inspector.
- `app/pages/map.py`: Dedicated large-format risk map with color legend and sector breakdown.
- `app/pages/forecast.py`: 0–6 hour predictive hazard progression table and trend charts.
- `app/pages/alerts.py`: Tactical civil defense bulletins and commuter safety recommendations.
- `app/components/`: Reusable UI modules (`risk_card.py`, `map_view.py`, `forecast_chart.py`, `alert_card.py`).
- `app/styles/theme.css`: Custom emergency response / climate-tech stylesheet.
- `tests/test_app.py`: Agent 5 unit test suite.

## Important Rule
The UI must call backend service functions (`get_current_risk`, `get_grid_predictions`, `get_forecast_timeline`).
Never duplicate ML inference or raw API logic inside Streamlit files.

## How to Test & Run
```bash
python -m pytest tests/test_app.py -v
streamlit run app/main.py
```
