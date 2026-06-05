"""
agents/chairman_agent.py
─────────────────────────
Chairman — arbitrates the full debate into a structured JSON verdict.
"""

import re
import json
from services.gemini_client import call_gemini_agent

_SYSTEM = (
    "You are the Chairman — the Supreme Boardroom Arbitrator. "
    "Do NOT introduce yourself with any name. Do NOT sign off with a name. "
    "Do NOT use the name 'Vikram Nair' or any other personal name. "
    "You are simply 'Chairman'. "
    "You have heard all specialists: Budget Analyst, "
    "Risk Assessor and Long-Term Planner. "
    "Your function: deliver an impartial, data-grounded verdict as clean JSON. "
    "No markdown. No prose outside the JSON. "
    "The JSON must contain exactly these keys:\n"
    "{\n"
    '  "verdict": "APPROVED" | "PROCEED WITH CAUTION" | "REJECTED",\n'
    '  "confidence": "e.g. 78%",\n'
    '  "risk_level": "LOW" | "MEDIUM" | "HIGH",\n'
    '  "recommended_action": "One clear sentence of what to do next.",\n'
    '  "action_steps": ["Step 1", "Step 2", "Step 3"],\n'
    '  "key_reasoning": "2–3 sentence synthesis of the deciding factors.",\n'
    '  "winning_argument": "Budget Analyst" | "Risk Assessor" | "Long-Term Planner"\n'
    "}"
)

_FALLBACK = {
    "verdict": "AI UNAVAILABLE",
    "confidence": "0%",
    "risk_level": "UNKNOWN",
    "recommended_action": "Boardroom analysis could not be completed because the AI service is unavailable.",
    "action_steps": [
        "Check API key and quota.",
        "Retry later.",
        "Verify model availability.",
    ],
    "key_reasoning": "No valid agent responses were received.",
    "winning_argument": "None",
}


def _extract_json(raw: str) -> dict:
    """
    Robustly extract a JSON object from the model's raw output.
    Tries three strategies:
      1. Direct parse (clean JSON)
      2. Regex: find first {...} block (JSON wrapped in prose)
      3. Fallback dict
    """
    try:
        return json.loads(raw.strip())
    except Exception:

        pass

    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except Exception:
            pass

    return _FALLBACK.copy()


def chairman_agent(debate_history: str, financial_facts: str = "") -> dict:
    """
    Parse the full debate and financial facts into a structured verdict dict.
    """
    prompt = (
        f"Original financial data:\n{financial_facts}\n\n"
        f"Full boardroom debate transcript:\n{debate_history}\n\n"
        "Deliver your arbitration verdict as clean JSON now."
    )
    raw = call_gemini_agent(
        prompt,
        system_instruction=_SYSTEM,
        temperature=0.05,
        max_tokens=600,
    )
    result = _extract_json(raw)

    for key, val in _FALLBACK.items():
        result.setdefault(key, val)

    return result
