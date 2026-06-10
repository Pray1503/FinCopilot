"""
agents/planner_agent.py
───────────────────────
LLM-powered strategic planner for the AI Boardroom.
Evaluates long-term goal impact and ROI of the loan.
"""

from services.groq_client import call_groq
from shared import money

SYSTEM = (
    "You are **Horizon‑Planner**, a forward-looking strategic financial advisor. "
    "Evaluate how the loan affects the student's long-term goals. "
    "Estimate ROI timeline if this is a skill/education investment. "
    "Compare opportunity cost of borrowing vs saving. "
    "All amounts in ₹. Stay under 120 words. "
    "End with a one-word impact rating: High_impact / Moderate / Low_impact."
)


def run(scenario: dict) -> str:
    """Run the Planner Agent on a financial scenario."""
    goals_text = ""
    for goal in scenario.get("goals", []):
        goals_text += (
            f"  - {goal.get('name', 'Goal')}: ₹{goal.get('required_amount', 0):,} "
            f"by {goal.get('target_date', 'N/A')}\n"
        )

    prompt = (
        f"Evaluate the long-term impact of this loan:\n"
        f"- Monthly income: {money(scenario.get('income_monthly', 0))}\n"
        f"- Savings: {money(scenario.get('savings', 0))}\n"
        f"- Loan amount: {money(scenario.get('requested_loan_amount', 0))}\n"
        f"- Proposed EMI: {money(scenario.get('proposed_EMI', 0))}\n"
        f"- Expected skill uplift: {scenario.get('expected_skill_earning_uplift_pct', 20)}%\n"
        f"- Goals:\n{goals_text}\n"
        f"Give your strategic assessment."
    )
    return call_groq(prompt, system_instruction=SYSTEM)
