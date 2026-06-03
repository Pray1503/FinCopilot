"""
Train a RandomForest regressor on synthetic student spending data.
Uses scikit-learn. Saves model with joblib.
"""

import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import joblib


def train(csv_path: str, model_path: str):
    """Train and save the model."""
    df = pd.read_csv(csv_path)
    features = ["month_idx", "is_exam", "is_festival", "avg_prev3"]
    X = df[features].values
    y = df["total_spend"].values

    print(f"Training RandomForest on {len(X)} samples...")
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)

    # Quick in-sample check
    preds = model.predict(X)
    rmse = round(np.sqrt(mean_squared_error(y, preds)))
    print(f"In-sample RMSE: Rs.{rmse}")

    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump(model, model_path)
    print(f"[OK] Model saved -> {model_path}")


if __name__ == "__main__":
    base = os.path.join(os.path.dirname(__file__), "..", "data")
    train(
        csv_path=os.path.join(base, "training_data.csv"),
        model_path=os.path.join(base, "model.joblib"),
    )
