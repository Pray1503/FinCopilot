"""
agents/devil_agent.py
─────────────────────
LLM-powered devil's advocate for the AI Boardroom.
Challenges assumptions and forces rigorous thinking.

NOTE: This agent was commented out (Turn 4) in the original boardroom service.
Now properly integrated as an optional challenge round.
"""

from services.groq_client import call_groq

SYSTEM = (
    "You are **Devil's Advocate**, a sharp financial critic. "
    "Your job is to stress-test the chairman's recommendation. "
    "Find the weakest assumption, the most optimistic projection, "
    "or the risk nobody mentioned. Be respectful but ruthless. "
    "All amounts in ₹. Stay under 100 words. "
    "End with: 'Despite this, I [agree/disagree] with the recommendation.'"
)


def run(chairman_verdict: str, scenario_summary: str) -> str:
    """Challenge the chairman's recommendation."""
    prompt = (
        f"The Chairman just recommended:\n{chairman_verdict}\n\n"
        f"Financial context: {scenario_summary}\n\n"
        f"Now challenge this recommendation. What's the weakest link?"
    )
    return call_groq(prompt, system_instruction=SYSTEM, max_tokens=400)
