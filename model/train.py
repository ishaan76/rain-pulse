"""AquaAlert AI — Agent 3: ML Model Training & Persistence Pipeline.

Generates a representative prototype training dataset reflecting urban hydrological
dynamics, trains Random Forest and Gradient Boosting estimators, evaluates performance,
and serializes the winning model artifact.
"""

import os
import json
from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import joblib

from model.features import FEATURE_NAMES


MODEL_DIR = os.path.join(os.path.dirname(__file__), "weights")
MODEL_PATH = os.path.join(MODEL_DIR, "flood_model.joblib")
METADATA_PATH = os.path.join(MODEL_DIR, "metadata.json")


def generate_synthetic_dataset(num_samples: int = 1500, random_seed: int = 42) -> Tuple[pd.DataFrame, pd.Series]:
    """Generate representative synthetic hydrological samples for model bootstrapping.

    Note: As per project rules, this dataset models deterministic physical relationships
    and is designed for rapid prototype validation.

    Args:
        num_samples: Number of training instances to synthesize.
        random_seed: Random seed for deterministic reproducibility.

    Returns:
        Tuple of (feature_dataframe, labels_series).
    """
    rng = np.random.RandomState(random_seed)

    # Sample realistic parameter distributions
    rain_3h = rng.uniform(0.0, 90.0, num_samples)
    rain_1h = rain_3h * rng.uniform(0.2, 0.6, num_samples)
    rain_6h = rain_3h * rng.uniform(1.1, 1.8, num_samples)
    rain_intensity = rain_1h * rng.uniform(0.8, 1.4, num_samples)

    elevation = rng.uniform(190.0, 240.0, num_samples)
    slope = rng.exponential(scale=2.0, size=num_samples)
    slope = np.clip(slope, 0.5, 12.0)

    drain_dist = rng.uniform(100.0, 950.0, num_samples)
    drain_dens = rng.uniform(0.15, 0.85, num_samples)
    hist_risk = rng.uniform(0.1, 0.95, num_samples)

    # Physical heuristic for ground-truth waterlogging label:
    # High rainfall + flat slope (< 1.5) + poor drainage (> 500m / < 0.35 density)
    risk_indicator = (
        (rain_3h / 50.0) * 0.40
        + (rain_intensity / 30.0) * 0.20
        + (1.5 / np.maximum(slope, 0.5)) * 0.20
        + (drain_dist / 600.0) * 0.10
        + (1.0 - drain_dens) * 0.10
        + hist_risk * 0.15
    )

    # Add minor stochastic variation
    noisy_indicator = risk_indicator + rng.normal(0, 0.05, num_samples)
    labels = (noisy_indicator > 0.60).astype(int)

    df = pd.DataFrame({
        "rainfall_1h": rain_1h,
        "rainfall_3h": rain_3h,
        "rainfall_6h": rain_6h,
        "rainfall_intensity": rain_intensity,
        "elevation": elevation,
        "slope": slope,
        "drainage_distance": drain_dist,
        "drainage_density": drain_dens,
        "historical_risk": hist_risk,
    })

    return df, pd.Series(labels, name="waterlogging_occurred")


def train_and_persist_model() -> Dict[str, Any]:
    """Train candidate models, evaluate metrics, and save winning model artifact.

    Returns:
        Dictionary containing evaluation summary metrics and winning model type.
    """
    X, y = generate_synthetic_dataset(num_samples=1600, random_seed=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

    # Candidate 1: Random Forest
    rf = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42)
    rf.fit(X_train, y_train)
    rf_preds = rf.predict(X_test)
    rf_f1 = f1_score(y_test, rf_preds, average="macro")

    # Candidate 2: Gradient Boosting
    gb = GradientBoostingClassifier(n_estimators=100, max_depth=4, random_state=42)
    gb.fit(X_train, y_train)
    gb_preds = gb.predict(X_test)
    gb_f1 = f1_score(y_test, gb_preds, average="macro")

    # Select model with superior macro F1
    if gb_f1 > rf_f1:
        chosen_model = gb
        model_name = "GradientBoostingClassifier"
        preds = gb_preds
    else:
        chosen_model = rf
        model_name = "RandomForestClassifier"
        preds = rf_preds

    acc = accuracy_score(y_test, preds)
    prec = precision_score(y_test, preds, zero_division=0)
    rec = recall_score(y_test, preds, zero_division=0)
    cm = confusion_matrix(y_test, preds).tolist()

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(chosen_model, MODEL_PATH)

    metadata = {
        "model_type": model_name,
        "features": FEATURE_NAMES,
        "accuracy": round(float(acc), 4),
        "precision": round(float(prec), 4),
        "recall": round(float(rec), 4),
        "macro_f1": round(float(max(rf_f1, gb_f1)), 4),
        "confusion_matrix": cm,
        "dataset_samples": len(X),
        "is_synthetic": True,
    }

    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    return metadata


if __name__ == "__main__":
    results = train_and_persist_model()
    print("Training complete:", results)
