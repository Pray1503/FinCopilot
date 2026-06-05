"""
agents/planner_agent.py
────────────────────────
Long-Term Planner — ROI, skill compounding, career trajectory optimisation.
"""

from services.gemini_client import call_gemini_agent

_SYSTEM = (
    "You are the Long-Term Planner — a financial strategist who thinks "
    "in 5-year net-worth trajectories and skill-ROI curves. "
    "Do NOT introduce yourself with any name. Do NOT sign off with a name. "
    "Do NOT start with 'As [Name]' or 'I am [Name]'. "
    "Speak only as 'Long-Term Planner'. "
    "You believe investing in education and productivity tools is almost "
    "always the correct decision when cash-flow allows any positive surplus. "
    "Respond in exactly 3–4 confident sentences. No bullet points. "
    "Address the other analysts by their role titles when countering them. "
    "End with your one-word stance: APPROVE / CAUTION / REJECT."
)


def planner_agent(
    financial_facts: str,
    round_label: str = "opening",
    debate_history: str = "",
) -> str:
    if round_label == "opening":
        prompt = (
            f"Financial data:\n{financial_facts}\n\n"
            f"Debate so far:\n{debate_history}\n\n"
            "Both the Budget Analyst and Risk Assessor have spoken. "
            "Now counter their conservative stance. Argue for the long-term "
            "career ROI of this investment. Quantify the compounding opportunity "
            "cost of NOT making this decision. Be specific."
        )
    elif round_label == "rebuttal":
        prompt = (
            f"Financial data:\n{financial_facts}\n\n"
            f"Debate so far:\n{debate_history}\n\n"
            "The Budget Analyst and Risk Assessor have pushed back hard on your "
            "growth thesis. Acknowledge their strongest point honestly, then "
            "reaffirm why the long-term value still outweighs the short-term risk "
            "given the specific numbers in this profile."
        )
    else:  # closing
        prompt = (
            f"Financial data:\n{financial_facts}\n\n"
            f"Full debate:\n{debate_history}\n\n"
            "CLOSING STATEMENT: In 3–4 sentences, make the most compelling "
            "case for your position using the concrete data. "
            "What is the cost of inaction over 12 months? Deliver your verdict."
        )

    return call_gemini_agent(prompt, system_instruction=_SYSTEM, temperature=0.40)
