"""
Risk Assessor Agent
Surfaces what could go wrong and what assumptions this decision depends on.
Pragmatic and candid, not alarmist.
"""


def run(profile: dict) -> dict:
    """Run the Risk Assessor on a user profile and return strict JSON."""
    emergency_fund = profile.get("emergency_fund_amount", 0)
    expenses = profile.get("monthly_expenses", 0)
    income = profile.get("income_monthly", 0)
    existing_emi = profile.get("existing_debt_monthly_EMI", 0)
    proposed_emi = profile.get("proposed_EMI", 0)
    savings = profile.get("savings", 0)
    volatility = profile.get("expense_volatility", "medium")
    credit = profile.get("credit_history", "limited")
    seasonality = profile.get("seasonality_flags", {})

    # ── Emergency fund assessment ────────────────────────────────
    TARGET = 2
    ef_months = round(emergency_fund / expenses, 2) if expenses > 0 else 0.0

    if ef_months >= TARGET:
        fund_status = "adequate"
    elif ef_months >= 1:
        fund_status = "marginal"
    else:
        fund_status = "insufficient"

    # ── Key risks ────────────────────────────────────────────────
    key_risks = [
        (
            "Income must remain stable throughout the loan tenure; any disruption "
            "(job loss, reduced freelance work) directly threatens EMI payments."
        ),
    ]

    if fund_status != "adequate":
        key_risks.append(
            f"Emergency fund covers only {ef_months} months of expenses — "
            f"well below the {TARGET}-month safety target."
        )
    else:
        key_risks.append(
            "Emergency fund meets the 2-month target, but any large "
            "unexpected expense would deplete it."
        )

    if volatility == "high" or seasonality.get("is_festival_month"):
        key_risks.append(
            "Expense volatility is elevated (festival/seasonal spend likely to spike), "
            "which could cause a temporary cash-flow crunch."
        )
    else:
        key_risks.append(
            "Assumes monthly expenses remain near current levels with no major "
            "unplanned costs."
        )

    # ── Worst-case scenario ──────────────────────────────────────
    total_obligation = expenses + existing_emi + proposed_emi
    wc_months = round(savings / total_obligation, 2) if total_obligation > 0 else 0.0

    emi_note = (
        f"₹{proposed_emi}/month EMI defaults begin"
        if proposed_emi > 0
        else "expenses become unmet"
    )
    worst_case = (
        f"If income stops entirely, current savings (₹{savings}) would cover "
        f"only {wc_months} months of expenses + EMI obligations. "
        f"After that, {emi_note}, potentially damaging credit."
    )

    # ── Verdict ──────────────────────────────────────────────────
    if fund_status == "insufficient" or wc_months < 1:
        verdict = "Too_risky"
    elif fund_status == "marginal" or volatility == "high":
        verdict = "Proceed_with_caution"
    else:
        verdict = "Manageable_risk"

    # ── Analysis ─────────────────────────────────────────────────
    credit_note = {
        "poor": "Poor credit history adds refinancing risk.",
        "limited": "Limited credit history means less negotiating power if restructuring is needed.",
    }.get(credit, "")

    analysis = (
        f"Emergency fund stands at {ef_months} months (target: {TARGET}). "
        f"{worst_case} {credit_note}"
    ).strip()

    return {
        "verdict": verdict,
        "key_risks": key_risks,
        "emergency_fund_months": ef_months,
        "worst_case_months_coverage": wc_months,
        "analysis": analysis,
    }
