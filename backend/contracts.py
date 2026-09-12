"""AquaAlert AI — Shared Data Contracts.

This module is the Single Source of Truth for data structures exchanged
between Agent 1 (Weather), Agent 2 (Terrain), Agent 3 (ML), Agent 4 (Backend),
and Agent 5 (UI/Map).
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class EnvironmentalFeatures:
    """Environmental inputs used by the AquaAlert prediction engine.

    Attributes:
        rainfall_1h: Rainfall accumulated in the past 1 hour (mm).
        rainfall_3h: Rainfall accumulated in the past 3 hours (mm).
        rainfall_6h: Rainfall accumulated in the past 6 hours (mm).
        rainfall_intensity: Peak rainfall intensity rate (mm/h).
        elevation: Elevation above sea level (meters).
        slope: Terrain slope angle (degrees).
        drainage_distance: Distance to closest primary storm drain or canal (meters).
        drainage_density: Density of stormwater conduits in the cell (0.0 to 1.0).
        historical_risk: Baseline historical waterlogging frequency index (0.0 to 1.0).
    """

    rainfall_1h: float
    rainfall_3h: float
    rainfall_6h: float
    rainfall_intensity: float
    elevation: float
    slope: float
    drainage_distance: float
    drainage_density: float
    historical_risk: float = 0.5


@dataclass
class RiskPrediction:
    """Risk output returned by the AquaAlert prediction engine.

    Attributes:
        risk_score: Normalized flood/waterlogging risk score (0.0 to 100.0).
        risk_level: Categorical risk tier ('LOW', 'MEDIUM', or 'HIGH').
        ml_probability: Model-derived probability proxy (0.0 to 1.0).
        physical_score: Physics/domain-informed hydrological runoff score (0.0 to 100.0).
    """

    risk_score: float
    risk_level: str
    ml_probability: float
    physical_score: float


@dataclass
class GridCell:
    """Geographical grid cell representation for localized hazard analysis.

    Attributes:
        cell_id: Unique identifier for the grid cell.
        name: Human-readable location or landmark name.
        latitude: Latitude of the cell center.
        longitude: Longitude of the cell center.
        elevation: Mean terrain elevation (meters).
        slope: Mean terrain slope (degrees).
        drainage_distance: Distance to primary storm drainage (meters).
        drainage_density: Drainage network density proxy (0.0 to 1.0).
        historical_risk: Historical waterlogging risk index (0.0 to 1.0).
    """

    cell_id: str
    name: str
    latitude: float
    longitude: float
    elevation: float
    slope: float
    drainage_distance: float
    drainage_density: float
    historical_risk: float = 0.5


@dataclass
class GridPredictionResult:
    """Evaluated risk prediction for a single grid cell.

    Attributes:
        cell: The underlying geographical grid cell.
        features: The merged environmental features for this cell.
        prediction: The calculated risk prediction output.
        is_hotspot: Flag indicating if the cell exceeds critical risk threshold.
        drivers: Key contributory features and their relative weights.
        recommendation: Human-actionable advisory instruction.
    """

    cell: GridCell
    features: EnvironmentalFeatures
    prediction: RiskPrediction
    is_hotspot: bool
    drivers: Dict[str, float] = field(default_factory=dict)
    recommendation: str = ""


@dataclass
class AreaRiskSummary:
    """Aggregated risk summary for an entire pilot administrative area.

    Attributes:
        area_name: Name of the pilot area (e.g. 'Delhi NCR').
        average_risk_score: Mean risk score across all constituent cells (0-100).
        max_risk_score: Peak localized risk score detected (0-100).
        overall_risk_level: Area-wide risk tier ('LOW', 'MEDIUM', 'HIGH').
        rainfall_3h: Current area-wide 3-hour rainfall accumulation (mm).
        rainfall_intensity: Current area-wide rainfall intensity (mm/h).
        hotspots_detected: Total count of high-risk hotspots.
        peak_forecast_text: Concise description of when risk peaks (e.g. '+3h peak').
        top_recommendation: Primary civil safety recommendation.
    """

    area_name: str
    average_risk_score: float
    max_risk_score: float
    overall_risk_level: str
    rainfall_3h: float
    rainfall_intensity: float
    hotspots_detected: int
    peak_forecast_text: str
    top_recommendation: str
