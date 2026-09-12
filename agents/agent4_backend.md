# Agent 4 — Backend & Orchestration Playbook

## Responsibility
Connect Agents 1, 2, and 3 into one reliable service interface layer.

## Owned Files & Folders
- `backend/contracts.py`: Master typed data structures (`EnvironmentalFeatures`, `RiskPrediction`, `GridCell`, `GridPredictionResult`, `AreaRiskSummary`).
- `backend/config.py`: Pilot regions, coordinate centroids, risk thresholds, and constants.
- `backend/validator.py`: Area validation and forecast horizon parser.
- `backend/service.py`: `AquaAlertBackend` orchestrator providing clean API facade.
- `tests/test_backend.py`: Agent 4 unit test suite.

## Primary Service Methods
```python
get_current_risk(area: str, use_demo: bool = False) -> AreaRiskSummary
get_grid_predictions(area: str, horizon: int = 0, use_demo: bool = False) -> List[GridPredictionResult]
get_forecast_timeline(area: str, use_demo: bool = False) -> List[Dict[str, Any]]
```

## How to Test
```bash
python -m pytest tests/test_backend.py -v
```
