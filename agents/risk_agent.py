"""
agents/risk_agent.py
─────────────────────
Risk Assessor — emergency fund, runway degradation, worst-case exposure.
"""

from services.gemini_client import call_gemini_agent

_SYSTEM = (
    "You are the Risk Assessor — a stress-test analyst and student "
    "financial risk consultant. "
    "Do NOT introduce yourself with any name. Do NOT sign off with a name. "
    "Do NOT start with 'As [Name]' or 'I am [Name]'. "
    "Speak only as 'Risk Assessor'. "
    "You think in worst-case scenarios: job loss, medical emergencies, unexpected fee hikes. "
    "Cite the emergency runway figure and compare it to the 3-month minimum standard. "
    "Respond in exactly 3–4 direct sentences. No bullet points. "
    "End with your one-word stance: APPROVE / CAUTION / REJECT."
)


def risk_agent(
    financial_facts: str,
    round_label: str = "opening",
    debate_history: str = "",
) -> str:
    if round_label == "opening":
        prompt = (
            f"Financial data:\n{financial_facts}\n\n"
            f"Debate so far:\n{debate_history}\n\n"
            "The Budget Analyst has spoken. Now respond as Risk Assessor. "
            "Validate OR challenge their cash-flow view by adding your perspective "
            "on emergency runway degradation and worst-case insolvency triggers. "
            "Cite the exact runway figures."
        )
    elif round_label == "rebuttal":
        prompt = (
            f"Financial data:\n{financial_facts}\n\n"
            f"Debate so far:\n{debate_history}\n\n"
            "The Long-Term Planner has argued for the upside scenario. "
            "Challenge them directly: if the student loses income during the EMI "
            "period, what happens to the runway? "
            "Use numbers from the data. Be specific about the insolvency risk."
        )
    else:  # closing
        prompt = (
            f"Financial data:\n{financial_facts}\n\n"
            f"Full debate:\n{debate_history}\n\n"
            "CLOSING STATEMENT: What is the single most dangerous number in this "
            "profile? Explain why it matters and deliver your final verdict."
        )

    return call_gemini_agent(prompt, system_instruction=_SYSTEM, temperature=0.25)
