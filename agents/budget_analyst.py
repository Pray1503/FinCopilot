"""
Budget Analyst Agent
Evaluates the decision using the user's financial numbers.
Strictly quantitative, concise, numbers-first.
"""


def run(profile: dict) -> dict:
    """Run the Budget Analyst on a user profile and return strict JSON."""
    income = profile.get("income_monthly", 0)
    expenses = profile.get("monthly_expenses", 0)
    savings = profile.get("savings", 0)
    existing_emi = profile.get("existing_debt_monthly_EMI", 0)
    proposed_emi = profile.get("proposed_EMI", 0)
    other_outflows = profile.get("other_known_outflows", 0)
    predicted_spend = profile.get("predicted_next_month_spend")

    # ── Core ratios ──────────────────────────────────────────────
    total_debt = existing_emi + proposed_emi + other_outflows
    dti_pct = _r((total_debt / income) * 100) if income > 0 else 100.0
    emi_pct = _r((proposed_emi / income) * 100) if income > 0 else 100.0
    savings_months = _r(savings / expenses) if expenses > 0 else 0.0

    # ── 50/30/20 check ───────────────────────────────────────────
    eff_expenses = predicted_spend if predicted_spend is not None else expenses
    needs_pct = _r((eff_expenses / income) * 100) if income > 0 else 100.0
    debt_pct = _r((total_debt / income) * 100) if income > 0 else 0.0
    remaining_pct = max(0.0, _r(100 - needs_pct - debt_pct))

    # ── Cash-flow shortfall ──────────────────────────────────────
    net_monthly = income - eff_expenses - total_debt
    has_shortfall = net_monthly < 0

    # ── Verdict ──────────────────────────────────────────────────
    if dti_pct > 40 or has_shortfall or savings_months < 1:
        verdict = "Risky"
    elif dti_pct > 30 or net_monthly < income * 0.1 or savings_months < 2:
        verdict = "Caution"
    else:
        verdict = "Safe"

    # ── Analysis ─────────────────────────────────────────────────
    shortfall_note = (
        f"Monthly cash flow turns negative by ₹{abs(round(net_monthly))}."
        if has_shortfall
        else f"Net monthly surplus is ₹{round(net_monthly)}."
    )
    split_note = (
        f"Current split is roughly {needs_pct}/{debt_pct}/{remaining_pct} "
        f"(needs/debt/savings) vs the 50/30/20 guideline."
    )
    analysis = (
        f"Debt-to-income ratio would be {dti_pct}% with the new EMI at "
        f"{emi_pct}% of income. {shortfall_note} {split_note}"
    )

    return {
        "verdict": verdict,
        "key_numbers": {
            "debt_to_income_pct": dti_pct,
            "proposed_emi_pct": emi_pct,
            "savings_months_coverage": savings_months,
            "net_monthly_surplus": round(net_monthly),
            "needs_pct": needs_pct,
            "debt_obligations_pct": debt_pct,
            "remaining_for_savings_pct": remaining_pct,
        },
        "analysis": analysis,
    }


def _r(n: float) -> float:
    return round(n, 2)
