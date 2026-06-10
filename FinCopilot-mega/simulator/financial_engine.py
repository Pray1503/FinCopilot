"""
simulator/financial_engine.py
──────────────────────────────
Pure algorithmic financial math — zero AI, zero I/O.

Limitations fixed vs original:
  1. Division-by-zero when surplus ≤ 0 (goal_delay blew up).  Fixed: safe_div().
  2. goal_delay used round() without int() — returned a float in edge cases that
     broke f-string formatting downstream.  Fixed: always int.
  3. Scoring was a single shared function with magic constants buried inside.
     Fixed: explicit named sub-scores so the explainability panel can surface them.
  4. No validation — negative expenses or income would silently produce garbage.
     Fixed: clamp all inputs.
  5. future projections assumed EMI never ends — for a 12-month EMI plan a 13-month
     projection was wrong.  Fixed: emi_months parameter respected.
"""

from dataclasses import dataclass, field
from typing import List


# ── Utilities ─────────────────────────────────────────────────────────────────

def _clamp(value: float, lo: float = 0.0) -> float:
    return max(value, lo)

def _safe_div(numerator: float, denominator: float, fallback: float = 0.0) -> float:
    return numerator / denominator if denominator > 1e-9 else fallback


# ── Output data-class ─────────────────────────────────────────────────────────

@dataclass
class ScenarioResult:
    # Scenario A — status quo (no purchase, no EMI)
    base_surplus: float = 0.0
    base_runway: float = 0.0
    base_score: int = 0
    base_goal_months: float = 0.0

    # Scenario B — after the proposed purchase / EMI
    simulated_surplus: float = 0.0
    active_runway: float = 0.0
    active_score: int = 0
    active_goal_months: float = 0.0
    goal_delay: int = 0          # always int — safe for f-strings
    remaining_savings: float = 0.0

    # Forward projections (Scenario B)
    future_3m: float = 0.0
    future_6m: float = 0.0
    future_12m: float = 0.0

    # Sub-score breakdown (used by explainability panel)
    score_breakdown: dict = field(default_factory=dict)

    # Derived ratios
    debt_to_income: float = 0.0          # EMI / income
    savings_rate_base: float = 0.0       # base_surplus / income
    savings_rate_active: float = 0.0     # simulated_surplus / income
    affordability_flag: str = "OK"       # "OK" | "TIGHT" | "OVEREXTENDED"


# ── Score engine ──────────────────────────────────────────────────────────────

def _compute_score(
    runway: float,
    surplus: float,
    goal_delay: int,
    debt_to_income: float,
) -> tuple[int, dict]:
    """
    Returns (total_score, breakdown_dict).
    Max 100 points — subtract penalty for each risk factor.
    """
    breakdown: dict[str, int] = {}

    # 1. Emergency runway (max 40 pts)
    if runway >= 6:
        runway_pts = 40
    elif runway >= 3:
        runway_pts = 30
    elif runway >= 1:
        runway_pts = 15
    else:
        runway_pts = 0
    breakdown["emergency_runway"] = runway_pts

    # 2. Monthly surplus health (max 30 pts)
    if surplus > 5000:
        surplus_pts = 30
    elif surplus > 2000:
        surplus_pts = 20
    elif surplus > 0:
        surplus_pts = 10
    else:
        surplus_pts = 0
    breakdown["surplus_health"] = surplus_pts

    # 3. Goal delay impact (max 20 pts)
    if goal_delay == 0:
        delay_pts = 20
    elif goal_delay <= 3:
        delay_pts = 14
    elif goal_delay <= 6:
        delay_pts = 7
    else:
        delay_pts = 0
    breakdown["goal_delay_impact"] = delay_pts

    # 4. Debt-to-income ratio (max 10 pts)
    if debt_to_income <= 0.10:
        dti_pts = 10
    elif debt_to_income <= 0.20:
        dti_pts = 6
    elif debt_to_income <= 0.35:
        dti_pts = 2
    else:
        dti_pts = 0
    breakdown["debt_to_income"] = dti_pts

    total = runway_pts + surplus_pts + delay_pts + dti_pts
    return max(0, min(100, total)), breakdown


# ── Main entry point ──────────────────────────────────────────────────────────

def compute_scenario_matrices(
    income: float,
    expenses: float,
    savings: float,
    goal_name: str,
    goal_cost: float,
    goal_deadline: int,
    item_cost: float,
    proposed_emi: float,
    emi_months: int = 12,          # NEW: how many months the EMI runs
) -> ScenarioResult:
    """
    Compute financial scenario matrices for both baseline and active variants.

    All monetary inputs are treated as ≥ 0.  Negative values are clamped.
    """
    income   = _clamp(income)
    expenses = _clamp(expenses)
    savings  = _clamp(savings)
    item_cost   = _clamp(item_cost)
    proposed_emi = _clamp(proposed_emi)

    # ── Scenario A: Status quo ────────────────────────────────────────────────
    base_surplus = income - expenses
    base_runway  = round(_safe_div(savings, expenses, fallback=99.0), 1)
    base_goal_months = _safe_div(
        _clamp(goal_cost - savings), _clamp(base_surplus, 1.0), fallback=9999.0
    )

    # ── Scenario B: With purchase / EMI ──────────────────────────────────────
    # If paying outright (no EMI), deduct from savings immediately.
    # If on EMI, savings stay intact but monthly surplus shrinks.
    if proposed_emi > 0:
        remaining_savings = savings          # cash not used upfront
    else:
        remaining_savings = _clamp(savings - item_cost)   # outright purchase

    simulated_surplus = income - expenses - proposed_emi
    active_runway = round(
        _safe_div(remaining_savings, _clamp(expenses + proposed_emi, 1.0), fallback=99.0), 1
    )
    active_goal_months = _safe_div(
        _clamp(goal_cost - remaining_savings),
        _clamp(simulated_surplus, 1.0),
        fallback=9999.0,
    )

    goal_delay = int(max(0, round(active_goal_months - base_goal_months)))

    # ── Ratios ────────────────────────────────────────────────────────────────
    debt_to_income   = _safe_div(proposed_emi, income)
    savings_rate_base   = _safe_div(base_surplus, income)
    savings_rate_active = _safe_div(simulated_surplus, income)

    # Affordability flag
    if debt_to_income > 0.35 or simulated_surplus < 0:
        affordability_flag = "OVEREXTENDED"
    elif debt_to_income > 0.20 or active_runway < 1.0:
        affordability_flag = "TIGHT"
    else:
        affordability_flag = "OK"

    # ── Scores ────────────────────────────────────────────────────────────────
    base_score, _ = _compute_score(base_runway, base_surplus, 0, 0.0)
    active_score, score_breakdown = _compute_score(
        active_runway, simulated_surplus, goal_delay, debt_to_income
    )

    # ── Forward projections ───────────────────────────────────────────────────
    # Monthly contribution after EMI ends reverts to base_surplus
    def _project(months: int) -> float:
        bal = remaining_savings
        for m in range(1, months + 1):
            monthly = simulated_surplus if m <= emi_months else base_surplus
            bal += monthly
        return round(bal, 2)

    return ScenarioResult(
        base_surplus=base_surplus,
        base_runway=base_runway,
        base_score=base_score,
        base_goal_months=round(base_goal_months, 1),
        simulated_surplus=simulated_surplus,
        active_runway=active_runway,
        active_score=active_score,
        active_goal_months=round(active_goal_months, 1),
        goal_delay=goal_delay,
        remaining_savings=remaining_savings,
        future_3m=_project(3),
        future_6m=_project(6),
        future_12m=_project(12),
        score_breakdown=score_breakdown,
        debt_to_income=round(debt_to_income * 100, 1),   # stored as percentage
        savings_rate_base=round(savings_rate_base * 100, 1),
        savings_rate_active=round(savings_rate_active * 100, 1),
        affordability_flag=affordability_flag,
    )
