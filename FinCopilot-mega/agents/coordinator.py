"""
Coordinator Agent
Synthesizes the three specialist outputs into one clear recommendation.
Empathetic, student-friendly, max 150 words.
"""


def run(
    budgeter: dict,
    planner: dict,
    realist: dict,
    original_question: str,
    profile_summary: dict,
) -> dict:
    """Synthesize specialist outputs into one recommendation."""
    verdicts = {
        "budgeter": (budgeter or {}).get("verdict", "unknown"),
        "planner": (planner or {}).get("verdict", "unknown"),
        "realist": (realist or {}).get("verdict", "unknown"),
    }

    # ── Agreement ────────────────────────────────────────────────
    is_all_cautious = (
        verdicts["budgeter"] in ("Risky", "Caution")
        and verdicts["realist"] in ("Too_risky", "Proceed_with_caution")
    )
    is_all_positive = (
        verdicts["budgeter"] == "Safe"
        and verdicts["realist"] == "Manageable_risk"
        and verdicts["planner"] in ("High_impact", "Moderate")
    )

    if is_all_cautious:
        agrees = (
            "All agents agree the current financial cushion is thin — "
            "both Budget Analyst and Risk Assessor flag insufficient reserves."
        )
    elif is_all_positive:
        agrees = (
            "All agents agree the financial position can absorb this decision — "
            "numbers, goals, and risk levels are within safe bounds."
        )
    else:
        cautious, positive = [], []
        if verdicts["budgeter"] in ("Risky", "Caution"):
            cautious.append("Budget Analyst")
        else:
            positive.append("Budget Analyst")
        if verdicts["realist"] in ("Too_risky", "Proceed_with_caution"):
            cautious.append("Risk Assessor")
        else:
            positive.append("Risk Assessor")
        if verdicts["planner"] in ("High_impact", "Moderate"):
            positive.append("Long-Term Planner")
        else:
            cautious.append("Long-Term Planner")

        if len(cautious) >= 2:
            agrees = f"{' and '.join(cautious)} both flag financial strain as the primary concern."
        else:
            agrees = f"{' and '.join(positive)} see the decision as manageable or beneficial."

    # ── Tradeoff ─────────────────────────────────────────────────
    if (
        verdicts["planner"] in ("High_impact", "Moderate")
        and (verdicts["budgeter"] in ("Risky", "Too_risky") or verdicts["realist"] == "Too_risky")
    ):
        tradeoff = (
            "The long-term earning uplift is promising, but current cash reserves "
            "are too thin to absorb the new EMI safely right now."
        )
    elif verdicts["planner"] == "Low_impact":
        tradeoff = (
            "Even if affordable, the expected return on this investment is modest — "
            "consider whether the opportunity cost is worth it."
        )
    else:
        tradeoff = (
            "The core tension is between acting now for faster career growth "
            "versus building a stronger financial safety net first."
        )

    # ── Combined verdict ─────────────────────────────────────────
    risk_score = _compute_risk_score(verdicts)
    if risk_score <= 2:
        combined_verdict = "Go_now"
    elif risk_score <= 4:
        combined_verdict = "Delay_and_prepare"
    else:
        combined_verdict = "Decline"

    # ── Recommendation ───────────────────────────────────────────
    emi = profile_summary.get("proposed_EMI", 0)
    savings = profile_summary.get("savings", 0)
    expenses = profile_summary.get("monthly_expenses", 0)
    target_buffer = expenses * 2
    savings_gap = max(0, target_buffer - savings)

    if combined_verdict == "Go_now":
        recommendation = (
            f"Recommended: Proceed with the loan — your finances can support "
            f"the ₹{emi} EMI while maintaining adequate reserves."
        )
    elif combined_verdict == "Delay_and_prepare":
        recommendation = (
            f"Recommended: Build ₹{round(savings_gap)} in emergency savings first "
            f"(targeting 2 months of expenses), then take the loan; "
            f"consider a smaller loan amount if the need is urgent."
        )
    else:
        recommendation = (
            "Recommended: Decline this loan for now — the financial risk "
            "outweighs the potential benefit at your current income and savings level."
        )

    # ── Next steps ───────────────────────────────────────────────
    next_steps = _generate_next_steps(combined_verdict, profile_summary, savings_gap)

    return {
        "combined_verdict": combined_verdict,
        "agrees": agrees,
        "tradeoff": tradeoff,
        "coordinator_recommendation": recommendation,
        "next_steps": next_steps,
    }


def _compute_risk_score(verdicts: dict) -> int:
    score = 0
    if verdicts["budgeter"] == "Risky":
        score += 2
    elif verdicts["budgeter"] == "Caution":
        score += 1
    if verdicts["planner"] == "Low_impact":
        score += 2
    elif verdicts["planner"] == "Moderate":
        score += 1
    if verdicts["realist"] == "Too_risky":
        score += 2
    elif verdicts["realist"] == "Proceed_with_caution":
        score += 1
    return score


def _generate_next_steps(verdict: str, profile: dict, savings_gap: float) -> list:
    income = profile.get("income_monthly", 0)
    expenses = profile.get("monthly_expenses", 0)
    surplus = max(0, income - expenses)

    if verdict == "Go_now":
        return [
            {
                "action": (
                    f"Set up automatic EMI deduction and ensure ₹{round(surplus * 0.2)} "
                    f"monthly goes to emergency fund."
                ),
                "timeframe_days": 7,
            },
            {
                "action": "Begin the course and track weekly progress to maximize the earning uplift.",
                "timeframe_days": 30,
            },
            {
                "action": (
                    "Review budget after first EMI payment — adjust discretionary "
                    "spending if net surplus drops below 10% of income."
                ),
                "timeframe_days": 60,
            },
        ]

    if verdict == "Delay_and_prepare":
        weekly = round(savings_gap / 8) if savings_gap > 0 else round(surplus * 0.3)
        return [
            {
                "action": (
                    f"Save ₹{weekly} per week to build the emergency buffer "
                    f"to 2 months of expenses."
                ),
                "timeframe_days": 60,
            },
            {
                "action": (
                    "Apply for scholarships, fee waivers, or employer-sponsored "
                    "upskilling programs to reduce loan amount."
                ),
                "timeframe_days": 30,
            },
            {
                "action": (
                    "Re-evaluate loan decision after buffer is built; compare "
                    "at least 2 lender offers for best interest rate."
                ),
                "timeframe_days": 90,
            },
        ]

    # Decline
    return [
        {
            "action": (
                "Focus on increasing income through freelance, part-time, "
                "or skill-based gigs for the next 90 days."
            ),
            "timeframe_days": 90,
        },
        {
            "action": "Build emergency fund to at least 2 months of expenses before considering any debt.",
            "timeframe_days": 60,
        },
        {
            "action": (
                "Explore free or low-cost alternatives for the course "
                "(YouTube, open courseware, community programs)."
            ),
            "timeframe_days": 30,
        },
    ]
