"""AquaAlert AI — Agent 4: Backend Service & Pipeline Orchestration.

Coordinates Agent 1 (Weather), Agent 2 (Terrain), and Agent 3 (Model)
into a unified, reliable business service layer.
"""

from typing import List, Dict, Any, Optional
import numpy as np
from cachetools import TTLCache, cached

from backend.contracts import (
    GridCell,
    GridPredictionResult,
    AreaRiskSummary,
    EnvironmentalFeatures,
)
from backend.config import PILOT_AREAS, DEFAULT_AREA, HIGH_RISK_THRESHOLD
from backend.validator import validate_area_name
from data.weather.service import WeatherService
from data.terrain.service import TerrainService
from model.predictor import FloodPredictor, get_default_predictor

# Global cache for predictions (max 100 items, expires in 5 minutes)
_prediction_cache = TTLCache(maxsize=100, ttl=300)


class AquaAlertBackend:
    """Production backend orchestrator serving prediction requests."""

    def __init__(
        self,
        weather_service: Optional[WeatherService] = None,
        terrain_service: Optional[TerrainService] = None,
        predictor: Optional[FloodPredictor] = None,
    ) -> None:
        """Initialize backend with domain services."""
        self.weather = weather_service or WeatherService()
        self.terrain = terrain_service or TerrainService()
        self.predictor = predictor or get_default_predictor()

    @cached(cache=_prediction_cache)
    def get_grid_predictions(
        self,
        area: str = DEFAULT_AREA,
        horizon: int = 0,
        use_demo: bool = False,
    ) -> List[GridPredictionResult]:
        """Fetch weather and terrain data, execute model inference, and return grid results.

        Args:
            area: Name of the pilot area.
            horizon: Forecast horizon offset in hours (0, 1, 3, or 6).
            use_demo: Flag to force pre-baked hackathon scenario.

        Returns:
            List of evaluated GridPredictionResult instances.
        """
        clean_area = validate_area_name(area)
        area_meta = PILOT_AREAS[clean_area]

        # 1. Fetch weather from Agent 1
        weather_data = self.weather.get_weather_features(
            latitude=area_meta["latitude"],
            longitude=area_meta["longitude"],
            area_name=clean_area,
            horizon_hours=horizon,
            use_demo=use_demo,
        )

        # 2. Fetch spatial cells from Agent 2
        cells = self.terrain.get_grid_cells(clean_area)

        # 3. Call Agent 3 prediction engine
        results = self.predictor.predict_grid(cells, weather_data)
        return results

    def get_current_risk(
        self,
        area: str = DEFAULT_AREA,
        use_demo: bool = False,
    ) -> AreaRiskSummary:
        """Compute aggregated area-level summary for the dashboard overview.

        Args:
            area: Name of the pilot area.
            use_demo: Flag to force pre-baked hackathon scenario.

        Returns:
            AreaRiskSummary containing aggregate KPI metrics.
        """
        clean_area = validate_area_name(area)
        grid_results = self.get_grid_predictions(clean_area, horizon=0, use_demo=use_demo)

        scores = [r.prediction.risk_score for r in grid_results]
        avg_score = round(float(np.mean(scores)), 1) if scores else 0.0
        max_score = round(float(np.max(scores)), 1) if scores else 0.0

        if max_score >= HIGH_RISK_THRESHOLD:
            overall_level = "HIGH"
        elif avg_score >= 40.0:
            overall_level = "MEDIUM"
        else:
            overall_level = "LOW"

        hotspot_count = sum(1 for r in grid_results if r.is_hotspot)

        # Look at horizon +3h to determine peak timing
        h3_results = self.get_grid_predictions(clean_area, horizon=3, use_demo=use_demo)
        h3_max = max((r.prediction.risk_score for r in h3_results), default=0.0)
        peak_text = "+3h peak expected" if h3_max > max_score else "Current peak"

        # Determine primary action from worst affected cell
        worst_cell = max(grid_results, key=lambda r: r.prediction.risk_score) if grid_results else None
        recommendation = worst_cell.recommendation if worst_cell else "Conditions normal."

        # Get rainfall 3h from the first cell's features
        sample_features = grid_results[0].features if grid_results else None
        rain_3h = sample_features.rainfall_3h if sample_features else 0.0
        rain_intensity = sample_features.rainfall_intensity if sample_features else 0.0

        return AreaRiskSummary(
            area_name=clean_area,
            average_risk_score=avg_score,
            max_risk_score=max_score,
            overall_risk_level=overall_level,
            rainfall_3h=rain_3h,
            rainfall_intensity=rain_intensity,
            hotspots_detected=hotspot_count,
            peak_forecast_text=peak_text,
            top_recommendation=recommendation,
        )

    def get_forecast_timeline(
        self,
        area: str = DEFAULT_AREA,
        use_demo: bool = False,
    ) -> List[Dict[str, Any]]:
        """Generate timeline progression of area risk from 0 to 6 hours.

        Args:
            area: Name of the pilot area.
            use_demo: Flag to force demo scenario.

        Returns:
            List of timeline snapshots with time label, risk score, level, rainfall, and intensity.
        """
        timeline = []
        horizons = [(0, "NOW"), (1, "+1h"), (2, "+2h"), (3, "+3h"), (4, "+4h"), (6, "+6h")]

        for h, label in horizons:
            preds = self.get_grid_predictions(area, horizon=h, use_demo=use_demo)
            max_risk = max((r.prediction.risk_score for r in preds), default=0.0)
            avg_risk = float(np.mean([r.prediction.risk_score for r in preds])) if preds else 0.0
            
            if max_risk >= HIGH_RISK_THRESHOLD:
                tier = "HIGH"
            elif max_risk >= 40.0:
                tier = "MEDIUM"
            else:
                tier = "LOW"

            sample_features = preds[0].features if preds else None
            rain_3h = sample_features.rainfall_3h if sample_features else 0.0
            intensity = sample_features.rainfall_intensity if sample_features else 0.0

            timeline.append({
                "time": label,
                "hour_offset": h,
                "max_risk": round(max_risk, 1),
                "avg_risk": round(avg_risk, 1),
                "risk_level": tier,
                "rainfall_3h": rain_3h,
                "intensity": intensity,
            })

        return timeline


# Module-level backend instance for easy consumption by Agent 5 (UI)
_BACKEND_INSTANCE: Optional[AquaAlertBackend] = None


def get_backend() -> AquaAlertBackend:
    """Retrieve singleton AquaAlertBackend instance."""
    global _BACKEND_INSTANCE
    if _BACKEND_INSTANCE is None:
        _BACKEND_INSTANCE = AquaAlertBackend()
    return _BACKEND_INSTANCE


def get_current_risk(area: str = DEFAULT_AREA, use_demo: bool = False) -> AreaRiskSummary:
    """Retrieve current area summary risk."""
    return get_backend().get_current_risk(area, use_demo)


def get_grid_predictions(
    area: str = DEFAULT_AREA,
    horizon: int = 0,
    use_demo: bool = False,
) -> List[GridPredictionResult]:
    """Retrieve evaluated grid predictions."""
    return get_backend().get_grid_predictions(area, horizon, use_demo)
