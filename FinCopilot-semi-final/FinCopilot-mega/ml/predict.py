"""
ML Prediction Module
Loads the trained RandomForest model and exposes a predict function.
"""

import os
import joblib

_MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "model.joblib")
_model = None


def _ensure_model():
    global _model
    if _model is not None:
        return True
    if not os.path.exists(_MODEL_PATH):
        return False
    try:
        _model = joblib.load(_MODEL_PATH)
        return True
    except Exception:
        return False


def predict_spend(month_idx: int, is_exam: int, is_festival: int, avg_prev3: float) -> float | None:
    """Predict next month's spending. Returns None if model unavailable."""
    if not _ensure_model():
        return None
    pred = _model.predict([[month_idx, is_exam, is_festival, avg_prev3]])
    return round(float(pred[0]))


def is_model_available() -> bool:
    """Check if the ML model is loaded."""
    return _ensure_model()
