"""
agents/budget_agent.py
──────────────────────
LLM-powered budget agent for the AI Boardroom.
Evaluates loan affordability from a quantitative budget perspective.
"""

from services.groq_client import call_groq
from shared import money

SYSTEM = (
    "You are **Budget‑Bot**, a razor-sharp quantitative budget analyst. "
    "Focus only on the numbers the user provides. "
    "Compute debt-to-income ratio, EMI-to-income ratio, and net monthly surplus. "
    "Apply the 50/30/20 rule. All amounts must be in ₹. "
    "Keep your reply under 120 words. End with a one-word verdict: Safe / Caution / Risky."
)


def run(scenario: dict) -> str:
    """Run the Budget Agent on a financial scenario."""
    prompt = (
        f"Evaluate this student's loan decision:\n"
        f"- Monthly income: {money(scenario.get('income_monthly', 0))}\n"
        f"- Monthly expenses: {money(scenario.get('monthly_expenses', 0))}\n"
        f"- Existing EMI: {money(scenario.get('existing_debt_monthly_EMI', 0))}\n"
        f"- Proposed new EMI: {money(scenario.get('proposed_EMI', 0))}\n"
        f"- Savings: {money(scenario.get('savings', 0))}\n"
        f"- Loan amount: {money(scenario.get('requested_loan_amount', 0))}\n\n"
        f"Give your budget analysis."
    )
    return call_groq(prompt, system_instruction=SYSTEM)
