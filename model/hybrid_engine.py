"""AquaAlert AI — Agent 3: Hybrid ML & Physics Risk Fusion.

Blends statistical pattern recognition from the ML classifier with deterministic
hydrological physics principles into a single unified 0–100 risk score.
"""

from typing import Tuple
from backend.config import ML_WEIGHT, PHYSICS_WEIGHT, LOW_RISK_THRESHOLD, HIGH_RISK_THRESHOLD


def blend_hybrid_risk(ml_probability: float, physical_score: float) -> Tuple[float, str]:
    """Calculate blended 0-100 risk score and categorize into standard risk tiers.

    Formula:
        Final Risk = (0.65 * ml_probability * 100) + (0.35 * physical_score)

    Args:
        ml_probability: Probability score output by the ML model (0.0 to 1.0).
        physical_score: Physics/domain-informed runoff score (0.0 to 100.0).

    Returns:
        Tuple of (risk_score: float, risk_level: str) where risk_level is 'LOW', 'MEDIUM', or 'HIGH'.
    """
    # Scale ML probability to 0-100
    ml_scaled = ml_probability * 100.0

    # Weighted blend
    raw_score = (ML_WEIGHT * ml_scaled) + (PHYSICS_WEIGHT * physical_score)
    clamped_score = round(min(100.0, max(0.0, raw_score)), 1)

    if clamped_score >= HIGH_RISK_THRESHOLD:
        level = "HIGH"
    elif clamped_score >= LOW_RISK_THRESHOLD:
        level = "MEDIUM"
    else:
        level = "LOW"

    return clamped_score, level
