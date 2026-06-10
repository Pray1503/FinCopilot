"""
agents/chairman_agent.py
────────────────────────
LLM-powered chairman / arbiter for the AI Boardroom.
Synthesizes all agent opinions into a final recommendation.
"""

from services.groq_client import call_groq

SYSTEM = (
    "You are **The Chairman**, a wise and empathetic financial mentor. "
    "You've just heard three expert opinions from Budget-Bot, Risk-Radar, and Horizon-Planner. "
    "Synthesize their views into ONE clear recommendation for the student. "
    "Acknowledge where experts agree and where they disagree. "
    "Be warm, student-friendly, and action-oriented. All amounts in ₹. "
    "Keep it under 150 words. End with a clear verdict: Proceed / Delay / Decline."
)


def run(budget_opinion: str, risk_opinion: str, planner_opinion: str, question: str) -> str:
    """Synthesize specialist opinions into a final recommendation."""
    prompt = (
        f"The student asked: '{question}'\n\n"
        f"=== BUDGET-BOT's Analysis ===\n{budget_opinion}\n\n"
        f"=== RISK-RADAR's Analysis ===\n{risk_opinion}\n\n"
        f"=== HORIZON-PLANNER's Analysis ===\n{planner_opinion}\n\n"
        f"Now give your chairman's verdict and recommendation."
    )
    return call_groq(prompt, system_instruction=SYSTEM, max_tokens=512)
