"""AquaAlert AI — Agent 1: Feature Engineering & Validation.

Converts structured EnvironmentalFeatures dataclass instances into
validated NumPy arrays compatible with scikit-learn estimators.
"""

from typing import List, Tuple
import numpy as np
import pandas as pd
from backend.contracts import EnvironmentalFeatures
FEATURE_NAMES: List[str] = [
    "rainfall_1h",
    "rainfall_3h",
    "rainfall_6h",
    "rainfall_intensity",
    "elevation",
    "slope",
    "drainage_distance",
    "drainage_density",
    "historical_risk",
]
def validate_features(features: EnvironmentalFeatures) -> None:
    """Validate numerical ranges of environmental features.

    Args:
        features: Input environmental features.

    Raises:
        ValueError: If any feature is outside physically plausible bounds.
    """
    if features.rainfall_1h < 0 or features.rainfall_3h < 0 or features.rainfall_6h < 0:
        raise ValueError("Rainfall accumulation cannot be negative.")
    if features.rainfall_intensity < 0:
        raise ValueError("Rainfall intensity cannot be negative.")
    if features.slope < 0 or features.slope > 90.0:
        raise ValueError(f"Slope angle must be between 0 and 90 degrees, got {features.slope}.")
    if features.drainage_distance < 0:
        raise ValueError("Drainage distance cannot be negative.")
    if not (0.0 <= features.drainage_density <= 1.0):
        raise ValueError("Drainage density must be in [0.0, 1.0].")
    if not (0.0 <= features.historical_risk <= 1.0):
        raise ValueError("Historical risk must be in [0.0, 1.0].")
def features_to_array(features: EnvironmentalFeatures) -> pd.DataFrame:
    """Convert an EnvironmentalFeatures instance into a feature dataframe with proper columns.

    Args:
        features: Target environmental parameters.

    Returns:
        pandas DataFrame of shape (1, n_features) with named columns.
    """
    validate_features(features)
    return pd.DataFrame(
        [[
            features.rainfall_1h,
            features.rainfall_3h,
            features.rainfall_6h,
            features.rainfall_intensity,
            features.elevation,
            features.slope,
            features.drainage_distance,
            features.drainage_density,
            features.historical_risk,
        ]],
        columns=FEATURE_NAMES,
    )
