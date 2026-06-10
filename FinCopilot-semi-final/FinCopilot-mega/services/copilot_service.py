"""
services/copilot_service.py
───────────────────────────
Copilot pipeline: query → intent detection → specialised LLM prompt → response.

Improvements over original:
  - Removed print("GROQ KEY FOUND:...") debug statements
  - Removed st.write("DEBUG RESULT:") calls
  - Returns structured response with intent metadata
"""

from copilot.intents import detect_intent
from copilot.feature_map import get_system_prompt
from services.groq_client import call_groq


def process_query(query: str) -> dict:
    """
    Process a user query through the copilot pipeline.

    Returns:
        dict with keys: intent, confidence, system_prompt, response
    """
    intent, confidence = detect_intent(query)
    system_prompt = get_system_prompt(intent)

    response = call_groq(
        prompt=query,
        system_instruction=system_prompt,
        temperature=0.3,
        max_tokens=1024,
    )

    return {
        "intent": intent,
        "confidence": confidence,
        "system_prompt": system_prompt,
        "response": response,
    }
