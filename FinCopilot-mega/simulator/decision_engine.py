"""
simulator/decision_engine.py
─────────────────────────────
Purchase decision simulator with ML-powered seasonal spending prediction.
Ported from Raj's console-based simulator into a reusable class.

Improvements over original:
  - Uses datetime.now().month instead of hardcoded start_month = 6
  - Returns structured dict instead of printing to console
  - ML model trained once on import (cached)
  - All currency in ₹
"""

from datetime import datetime
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor


# ── ML Engine ────────────────────────────────────────────────────────────────

def _train_spending_model() -> RandomForestRegressor:
    """Train a model on synthetic seasonal spending patterns."""
    np.random.seed(42)
    records = []
    for _ in range(1000):
        month = np.random.randint(1, 13)
        is_exam = 1 if month in [5, 11] else 0
        is_fest = 1 if month in [10, 11, 12] else 0
        base_spend = 0.60
        variance = (is_exam * 0.15) + (is_fest * 0.25) + np.random.normal(0, 0.05)
        spend_ratio = max(0.40, min(0.95, base_spend + variance))
        records.append({
            "month_of_year": month,
            "is_exam_month": is_exam,
            "is_festival_season": is_fest,
            "spend_ratio": spend_ratio,
        })
    df = pd.DataFrame(records)
    model = RandomForestRegressor(n_estimators=50, random_state=42)
    model.fit(
        df[["month_of_year", "is_exam_month", "is_festival_season"]],
        df["spend_ratio"],
    )
    return model


_ml_model = _train_spending_model()


# ── Core Simulator ───────────────────────────────────────────────────────────

def simulate_purchase(
    income: float,
    current_savings: float,
    base_expenses: float,
    item_name: str,
    cost: float,
    goal_name: str,
    goal_target: float,
    goal_current: float,
    goal_alloc: float,
) -> dict:
    """
    Run a full purchase decision simulation.

    Returns a structured dict with:
      - affordability score and verdict
      - goal delay analysis
      - 12-month projection (control vs static vs ML-dynamic)
    """
    surplus = income - base_expenses
    if surplus <= 0:
        return {
            "error": True,
            "message": "Your fixed expenses equal or exceed your income. No surplus available.",
            "surplus": surplus,
        }

    # ── Affordability Score ───────────────────────────────────────
    months_to_save = cost / surplus
    if months_to_save <= 1:
        score, verdict = 95, "🟢 HIGH AFFORDABILITY — Safe to buy today"
    elif months_to_save <= 3:
        score, verdict = 75, "🟡 MODERATE — Plan ahead, doable in ~3 months"
    elif months_to_save <= 6:
        score, verdict = 45, "🟠 LOW — Save up specifically for this first"
    else:
        score, verdict = 20, "🔴 HIGH RISK — Significantly outside your current budget"

    # ── Goal Delay ───────────────────────────────────────────────
    remaining_goal = max(0, goal_target - goal_current)
    safe_alloc = max(1.0, min(goal_alloc, surplus))
    original_months = remaining_goal / safe_alloc if safe_alloc > 0 else 999
    freeze_months = cost / surplus
    delayed_months = original_months + freeze_months

    # ── 12-Month Projections ─────────────────────────────────────
    start_month = datetime.now().month  # FIX: was hardcoded to 6
    projections = []

    control_bal = current_savings
    static_bal = current_savings - cost
    dynamic_bal = current_savings - cost

    for m in range(1, 13):
        future_month = (start_month + m - 1) % 12 + 1
        is_exam = 1 if future_month in [5, 11] else 0
        is_fest = 1 if future_month in [10, 11, 12] else 0

        control_bal += surplus
        static_bal += surplus

        feat_df = pd.DataFrame([{
            "month_of_year": future_month,
            "is_exam_month": is_exam,
            "is_festival_season": is_fest,
        }])
        predicted_ratio = _ml_model.predict(feat_df)[0]
        dynamic_expense = base_expenses * (predicted_ratio / 0.60)
        dynamic_surplus = income - dynamic_expense
        dynamic_bal += dynamic_surplus

        tag = ""
        if is_exam:
            tag = "📝 Exams"
        if is_fest:
            tag = "🎉 Festivals"

        projections.append({
            "month": m,
            "calendar_month": future_month,
            "control": round(control_bal),
            "static": round(static_bal),
            "ml_dynamic": round(dynamic_bal),
            "tag": tag,
        })

    return {
        "error": False,
        "surplus": round(surplus),
        "item_name": item_name,
        "cost": cost,
        "affordability_score": score,
        "verdict": verdict,
        "months_to_absorb": round(months_to_save, 1),
        "goal_name": goal_name,
        "original_timeline": round(original_months, 1),
        "freeze_months": round(freeze_months, 1),
        "delayed_timeline": round(delayed_months, 1),
        "projections": projections,
    }
