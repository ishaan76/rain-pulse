"""AquaAlert AI — Agent 3: Prediction Subsystem Interface.

Implements the official prediction contracts:
- predict_flood_risk(input_data) -> RiskPrediction
- predict_grid(grid_data) -> List[GridPredictionResult]
"""

import os
from typing import List, Dict, Any, Optional
import joblib

from backend.contracts import (
    EnvironmentalFeatures,
    RiskPrediction,
    GridCell,
    GridPredictionResult,
)
from model.features import features_to_array
from model.physical_engine import calculate_physical_runoff_score
from model.hybrid_engine import blend_hybrid_risk
from model.explainer import explain_prediction_drivers, generate_recommendation
from backend.config import HIGH_RISK_THRESHOLD


MODEL_PATH = os.path.join(os.path.dirname(__file__), "weights", "flood_model.joblib")


class FloodPredictor:
    """Production predictor loading the trained ML model and hybrid fusion pipeline."""

    def __init__(self, model_path: str = MODEL_PATH) -> None:
        """Initialize predictor by loading the serialized model artifact."""
        if os.path.exists(model_path):
            self.model = joblib.load(model_path)
        else:
            # Lazy import and train if weights are not yet present
            from model.train import train_and_persist_model
            train_and_persist_model()
            self.model = joblib.load(model_path)

    def predict_flood_risk(self, features: EnvironmentalFeatures) -> RiskPrediction:
        """Predict localized waterlogging hazard for an individual site.

        Args:
            features: Validated EnvironmentalFeatures data instance.

        Returns:
            RiskPrediction containing risk_score, risk_level, ml_probability, and physical_score.
        """
        # 1. ML inference
        feat_matrix = features_to_array(features)
        proba_array = self.model.predict_proba(feat_matrix)
        ml_prob = float(proba_array[0][1])

        # 2. Physics / domain hydrological runoff score (0-100)
        phys_score = calculate_physical_runoff_score(features)

        # 3. Hybrid fusion
        final_score, risk_level = blend_hybrid_risk(ml_prob, phys_score)

        return RiskPrediction(
            risk_score=final_score,
            risk_level=risk_level,
            ml_probability=round(ml_prob, 3),
            physical_score=phys_score,
        )

    def predict_grid(
        self,
        grid_cells: List[GridCell],
        weather_features: Dict[str, Any],
    ) -> List[GridPredictionResult]:
        """Evaluate flood risk for all grid cells across a geographical region.

        Args:
            grid_cells: List of spatial GridCell instances.
            weather_features: Weather dictionary from Agent 1.

        Returns:
            List of GridPredictionResult instances with hotspot flags and explanations.
        """
        results: List[GridPredictionResult] = []

        for cell in grid_cells:
            # Merge cell geospatial attributes with current weather
            features = EnvironmentalFeatures(
                rainfall_1h=float(weather_features.get("rainfall_1h", 0.0)),
                rainfall_3h=float(weather_features.get("rainfall_3h", 0.0)),
                rainfall_6h=float(weather_features.get("rainfall_6h", 0.0)),
                rainfall_intensity=float(weather_features.get("rainfall_intensity", 0.0)),
                elevation=cell.elevation,
                slope=cell.slope,
                drainage_distance=cell.drainage_distance,
                drainage_density=cell.drainage_density,
                historical_risk=cell.historical_risk,
            )

            pred = self.predict_flood_risk(features)
            drivers = explain_prediction_drivers(features)
            recommendation = generate_recommendation(pred.risk_level, drivers)
            is_hotspot = pred.risk_score >= HIGH_RISK_THRESHOLD

            results.append(
                GridPredictionResult(
                    cell=cell,
                    features=features,
                    prediction=pred,
                    is_hotspot=is_hotspot,
                    drivers=drivers,
                    recommendation=recommendation,
                )
            )

        return results


# Module-level convenience functions adhering to the spec contract
_DEFAULT_PREDICTOR: Optional[FloodPredictor] = None


def get_default_predictor() -> FloodPredictor:
    """Retrieve or lazily initialize the singleton predictor instance."""
    global _DEFAULT_PREDICTOR
    if _DEFAULT_PREDICTOR is None:
        _DEFAULT_PREDICTOR = FloodPredictor()
    return _DEFAULT_PREDICTOR


def predict_flood_risk(features: EnvironmentalFeatures) -> RiskPrediction:
    """Predict localized flood risk for a set of environmental features.

    Args:
        features: Environmental conditions for the target location.

    Returns:
        Risk prediction containing score, level, and model details.
    """
    return get_default_predictor().predict_flood_risk(features)


def predict_grid(
    grid_cells: List[GridCell],
    weather_features: Dict[str, Any],
) -> List[GridPredictionResult]:
    """Predict flood risk for a collection of spatial grid cells.

    Args:
        grid_cells: Grid cells to evaluate.
        weather_features: Weather attributes from Agent 1.

    Returns:
        List of prediction results per cell.
    """
    return get_default_predictor().predict_grid(grid_cells, weather_features)
