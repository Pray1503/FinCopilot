"""
agents/budget_agent.py
───────────────────────
Budget Analyst — short-term cash-flow and liquidity specialist.
"""

from services.gemini_client import call_gemini_agent

# FIX: Added "Do NOT introduce yourself with any name." to prevent the model
# from generating persona names like "Marcus Chen" in its response.
_SYSTEM = (
    "You are the Budget Analyst — a hard-nosed financial controller "
    "and student budget specialist. "
    "Do NOT introduce yourself with any name. Do NOT sign off with a name. "
    "Do NOT start with 'As [Name]' or 'I am [Name]'. "
    "Speak only as 'Budget Analyst'. "
    "You speak with sharp precision: cite the exact numbers from the data, "
    "use percentage ratios, and flag when cash buffers fall below safe thresholds. "
    "You are deeply skeptical of optimistic growth projections. "
    "Respond in exactly 3–4 punchy sentences. Never use bullet points. "
    "End your statement with your one-word stance: APPROVE / CAUTION / REJECT."
)


def budget_agent(
    financial_facts: str,
    round_label: str = "opening",
    debate_history: str = "",
) -> str:
    if round_label == "opening":
        prompt = (
            f"You are delivering your OPENING STATEMENT to the boardroom.\n\n"
            f"Financial data:\n{financial_facts}\n\n"
            "Analyze the monthly surplus, emergency runway, and debt-to-income ratio. "
            "State clearly whether the proposed allocation is safe from a pure "
            "short-term liquidity standpoint."
        )
    elif round_label == "rebuttal":
        prompt = (
            f"Financial data:\n{financial_facts}\n\n"
            f"Debate so far:\n{debate_history}\n\n"
            "The Long-Term Planner has made optimistic claims about career ROI. "
            "REBUT their argument directly. "
            "Show how their growth assumptions fail to protect against immediate "
            "cash-flow collapse if income drops even 20%."
        )
    else:  # closing
        prompt = (
            f"Financial data:\n{financial_facts}\n\n"
            f"Full debate transcript:\n{debate_history}\n\n"
            "Deliver your CLOSING STATEMENT. Synthesize the key cash-flow risk "
            "you have been arguing. Acknowledge any valid point from the opposition, "
            "then reaffirm your final stance with your verdict word."
        )

    return call_gemini_agent(prompt, system_instruction=_SYSTEM, temperature=0.25)
