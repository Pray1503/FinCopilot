"""
agents/devil_agent.py
──────────────────────
Devil's Advocate — contrarian analyst who challenges the prevailing consensus.
"""

from services.gemini_client import call_gemini_agent

_SYSTEM = (
    "You are the Devil's Advocate — a contrarian analyst whose job is to "
    "challenge the prevailing consensus in the room. "
    "Do NOT introduce yourself with any name. Do NOT sign off with a name. "
    "Do NOT start with 'As [Name]' or 'I am [Name]'. "
    "Speak only as 'Devil's Advocate'. "
    "Whatever direction the majority leans, you find the strongest steel-man "
    "argument for the opposite view. "
    "You cite second-order effects and angles the other analysts missed. "
    "Respond in exactly 3–4 punchy sentences. No bullet points. "
    "Start with 'The panel is missing the bigger picture.' "
    "End with your one-word stance: APPROVE / CAUTION / REJECT."
)


def _detect_consensus(debate_history: str) -> str:
    """Crude consensus detector — counts REJECT vs APPROVE mentions."""
    low = debate_history.lower()
    rejects = low.count("reject")
    approves = low.count("approve")
    if rejects > approves:
        return "REJECT"
    elif approves > rejects:
        return "APPROVE"
    return "CAUTION"


def devil_agent(
    financial_facts: str,
    debate_history: str = "",
) -> str:
    consensus = _detect_consensus(debate_history)
    flip_target = "APPROVE" if consensus == "REJECT" else "REJECT"

    prompt = (
        f"Financial data:\n{financial_facts}\n\n"
        f"Debate so far (the room is leaning {consensus}):\n{debate_history}\n\n"
        f"Your job: make the strongest possible case for {flip_target}. "
        "Find the argument the other three analysts completely ignored. "
        "Cite a specific number from the data to anchor your contrarian view."
    )

    return call_gemini_agent(prompt, system_instruction=_SYSTEM, temperature=0.55)
