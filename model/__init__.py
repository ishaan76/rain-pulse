"""AquaAlert AI — Model & Intelligence Subsystem."""

from model.predictor import (
    FloodPredictor,
    predict_flood_risk,
    predict_grid,
    get_default_predictor,
)
from model.physical_engine import calculate_physical_runoff_score
from model.hybrid_engine import blend_hybrid_risk
from model.explainer import explain_prediction_drivers, generate_recommendation

__all__ = [
    "FloodPredictor",
    "predict_flood_risk",
    "predict_grid",
    "get_default_predictor",
    "calculate_physical_runoff_score",
    "blend_hybrid_risk",
    "explain_prediction_drivers",
    "generate_recommendation",
]
