"""
agents/risk_agent.py
────────────────────
LLM-powered risk agent for the AI Boardroom.
Identifies what could go wrong and quantifies downside risk.
"""

from services.groq_client import call_groq
from shared import money

SYSTEM = (
    "You are **Risk‑Radar**, a prudent financial risk advisor. "
    "Identify the top 3 risks of this loan decision. "
    "Quantify worst-case scenarios using the user's numbers. "
    "Assess emergency fund adequacy (target: 2–3 months of expenses). "
    "All amounts in ₹. Stay under 120 words. "
    "End with a one-word risk level: Manageable / Elevated / Critical."
)


def run(scenario: dict) -> str:
    """Run the Risk Agent on a financial scenario."""
    prompt = (
        f"Assess the risks of this loan decision:\n"
        f"- Monthly income: {money(scenario.get('income_monthly', 0))}\n"
        f"- Monthly expenses: {money(scenario.get('monthly_expenses', 0))}\n"
        f"- Savings: {money(scenario.get('savings', 0))}\n"
        f"- Emergency fund: {money(scenario.get('emergency_fund_amount', scenario.get('savings', 0)))}\n"
        f"- Existing EMI: {money(scenario.get('existing_debt_monthly_EMI', 0))}\n"
        f"- Proposed EMI: {money(scenario.get('proposed_EMI', 0))}\n"
        f"- Loan amount: {money(scenario.get('requested_loan_amount', 0))}\n\n"
        f"Identify key risks."
    )
    return call_groq(prompt, system_instruction=SYSTEM)
