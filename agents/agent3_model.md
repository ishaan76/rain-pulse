# Agent 3 — ML & Prediction Subsystem Playbook

## Responsibility
Own the complete machine-learning and hydrological physics prediction subsystem.

## Owned Files & Folders
- `model/features.py`: Feature schema, validation, and conversion to DataFrame.
- `model/physical_engine.py`: Domain hydrological runoff physics engine (0–100).
- `model/hybrid_engine.py`: Fusion equation: $(0.65 \times P_{\text{ML}} \times 100) + (0.35 \times \text{Physical Score})$.
- `model/explainer.py`: Driver attribution calculation for "Why Is This High?" interaction.
- `model/train.py`: Reproducible synthetic training pipeline and model serialization.
- `model/predictor.py`: Implements core contracts `predict_flood_risk` and `predict_grid`.
- `model/weights/`: Serialized model artifact (`flood_model.joblib`) and evaluation metadata.
- `tests/test_model.py`: Agent 3 unit test suite.

## Required Prediction Interface
```python
predict_flood_risk(features: EnvironmentalFeatures) -> RiskPrediction
predict_grid(grid_cells: List[GridCell], weather_features: dict) -> List[GridPredictionResult]
```

## How to Test & Re-train
```bash
python -m model.train
python -m pytest tests/test_model.py -v
```
