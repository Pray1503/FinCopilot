"""
Long-Term Planner Agent
Evaluates how the decision affects the user's stated goals and earning potential.
Forward-looking, optimistic but anchored in feasible timelines.
"""

import re
from datetime import datetime


def run(profile: dict) -> dict:
    """Run the Long-Term Planner on a user profile and return strict JSON."""
    goals = profile.get("goals", [])
    uplift = profile.get("expected_skill_earning_uplift_pct", 20)
    uplift_provided = "expected_skill_earning_uplift_pct" in profile and profile["expected_skill_earning_uplift_pct"]
    course_months = profile.get("course_length_months", 6)
    income = profile.get("income_monthly", 0)
    expenses = profile.get("monthly_expenses", 0)
    savings = profile.get("savings", 0)
    loan_amount = profile.get("requested_loan_amount", 0)
    proposed_emi = profile.get("proposed_EMI", 0)

    # ── ROI estimate ─────────────────────────────────────────────
    monthly_gain = income * (uplift / 100)
    roi_months = round(loan_amount / monthly_gain, 1) if monthly_gain > 0 else 999

    # ── Monthly surplus before / after ───────────────────────────
    current_surplus = income - expenses
    surplus_with_loan = current_surplus - proposed_emi
    post_course_income = income * (1 + uplift / 100)
    post_course_surplus = post_course_income - expenses - proposed_emi

    # ── Goal impact analysis ─────────────────────────────────────
    now = datetime.now()
    goal_impacts = []
    for goal in goals:
        target_date = _parse_date(goal.get("target_date", "2026-12-31"))
        months_to_goal = max(1, _month_diff(now, target_date))
        amount_needed = goal.get("required_amount", 0)

        # Savings trajectory without / with loan
        savings_without = current_surplus * months_to_goal + savings
        course_end = min(course_months, months_to_goal)
        post_months = max(0, months_to_goal - course_end)
        savings_with = (
            surplus_with_loan * course_end
            + post_course_surplus * post_months
            + savings
        )

        is_skill_goal = bool(
            re.search(r"prep|skill|course|certif|learn|train|place", goal.get("name", ""), re.I)
        )

        if is_skill_goal:
            impact = "helps"
            notes = (
                f"Directly supports {goal['name']} by funding skill development; "
                f"ROI expected in ~{round(roi_months)} months."
            )
        elif savings_with >= amount_needed and savings_without >= amount_needed:
            impact = "neutral"
            notes = f"Goal remains achievable within the {months_to_goal}-month timeline."
        elif savings_with >= amount_needed > savings_without:
            impact = "helps"
            notes = (
                f"Higher post-course income makes this goal reachable; "
                f"without the course it would fall short by ₹{round(amount_needed - savings_without)}."
            )
        elif savings_with < savings_without:
            fallback = max(1, post_course_surplus)
            impact = "delays"
            notes = (
                f"Loan EMI reduces monthly surplus by ₹{proposed_emi}, "
                f"pushing this goal back by ~{round((amount_needed - savings_with) / fallback)} months."
            )
        else:
            impact = "neutral"
            notes = "Marginal effect on this goal's timeline."

        goal_impacts.append({
            "goal_name": goal.get("name", "Unnamed"),
            "impact": impact,
            "notes": notes,
        })

    # ── Verdict ──────────────────────────────────────────────────
    help_count = sum(1 for g in goal_impacts if g["impact"] == "helps")
    delay_count = sum(1 for g in goal_impacts if g["impact"] == "delays")

    if roi_months <= 12 and help_count > delay_count:
        verdict = "High_impact"
    elif roi_months > 24 or delay_count > help_count:
        verdict = "Low_impact"
    else:
        verdict = "Moderate"

    # ── Analysis ─────────────────────────────────────────────────
    uplift_note = (
        f"Using industry-default {uplift}% earning uplift (not user-provided)."
        if not uplift_provided
        else f"Expected {uplift}% earning uplift after course completion."
    )
    opp_cost = (
        f"If invested instead of borrowed, ₹{loan_amount} at 8% annual return "
        f"would grow to ~₹{round(loan_amount * 1.08)} in one year."
        if loan_amount > 0
        else ""
    )
    analysis = (
        f"{uplift_note} Breakeven on the ₹{loan_amount} investment is "
        f"~{round(roi_months)} months post-course. {opp_cost}"
    )

    return {
        "verdict": verdict,
        "roi_months_estimate": round(roi_months),
        "goal_impacts": goal_impacts,
        "analysis": analysis,
    }


def _parse_date(s: str) -> datetime:
    for fmt in ("%Y-%m-%d", "%Y-%m"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return datetime(2026, 12, 31)


def _month_diff(a: datetime, b: datetime) -> int:
    return (b.year - a.year) * 12 + (b.month - a.month)
