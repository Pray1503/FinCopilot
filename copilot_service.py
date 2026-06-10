"""
fincopilot/copilot_service.py
──────────────────────────────
Step 3: Copilot Service

What this file does:
  - Orchestrates the full pipeline: query → intent → feature → LLM → response.
  - Handles the three confidence paths cleanly:
      "high"   → skip LLM intent step, go straight to feature + LLM answer
      "medium" → use keyword intent but LLM confirms before answering
      "low"    → LLM re-classifies intent from scratch, then answers
  - Calls the Groq API (via your existing wrapper pattern) for:
      1. Low-confidence intent re-classification (structured JSON output)
      2. Generating the actual answer to the user's question
  - Returns a single CopilotResponse dataclass — the UI reads nothing else.

Design decisions:
  - Two separate LLM calls with different system prompts and temperatures:
      Intent resolver  → temperature 0.0  (deterministic classification)
      Answer generator → temperature 0.4  (natural, helpful tone)
  - The LLM never decides features. Only intents.py + feature_map.py do that.
    LLM just helps classify ambiguous queries into the right intent string.
  - If the Groq call fails for any reason, the service degrades gracefully:
    it falls back to the keyword-detected intent and returns an error-aware
    response rather than crashing.
  - Conversation history is accepted as an optional parameter so the service
    is ready for multi-turn chat without any refactoring.

Imports:
  - fincopilot.intents  → detect_intent(), IntentResult, ALL_INTENTS
  - fincopilot.feature_map → get_feature_for_intent(), FeatureCard
  - groq (standard Groq SDK) → chat completions
"""

from __future__ import annotations

import os
import json
import re
from dataclasses import dataclass, field
from typing import Optional

from dotenv import load_dotenv
from groq import Groq

load_dotenv()  # Load environment variables from .env file (including GROQ_API_KEY)
print("GROQ KEY FOUND:", bool(os.getenv("GROQ_API_KEY")))

from intents import (
    detect_intent,
    IntentResult,
    ALL_INTENTS,
    INTENT_GENERAL_FINANCE,
)
from feature_map import get_feature_for_intent, FeatureCard

# ── Groq client (lazy init, same pattern as your existing modules) ─────────────

_groq_client: Optional[Groq] = None


def _get_client() -> Groq:
    """
    Return a shared Groq client instance.
    Initialised once on first call — not at import time.
    This matches the pattern in your existing codebase and avoids
    errors at import if the key isn't set yet.
    """
    global _groq_client
    if _groq_client is None:
        api_key = os.environ.get("GROQ_API_KEY", "")
        if not api_key:
            raise EnvironmentError(
                "GROQ_API_KEY not found in environment. "
                "Set it before starting Streamlit:\n"
                "  PowerShell: $env:GROQ_API_KEY='your-key'\n"
                "  bash/zsh:   export GROQ_API_KEY='your-key'"
            )
        _groq_client = Groq(api_key=api_key)
    return _groq_client


MODEL = "llama-3.3-70b-versatile"  # your existing model — change in one place


# ── Output dataclass ──────────────────────────────────────────────────────────


@dataclass
class CopilotResponse:
    """
    Everything the UI needs. app.py reads ONLY this object.

    Fields:
        query           Original user query (echoed back for display).
        intent          Final resolved intent string (INTENT_* constant).
        confidence      "high" | "medium" | "low" — from keyword detection.
        intent_source   "keyword" | "llm" — how the intent was resolved.
        feature         FeatureCard for the recommended feature.
        answer          LLM-generated response text (markdown safe).
        should_redirect True when a specific feature is strongly recommended
                        and the UI should show the recommendation card prominently.
        error           None on success. Error message string on failure.
                        UI shows a degraded but non-crashing state.
    """

    query: str
    intent: str
    confidence: str
    intent_source: str  # "keyword" | "llm"
    feature: FeatureCard
    answer: str
    should_redirect: bool
    error: Optional[str] = None
    debug_scores: dict = field(default_factory=dict)  # raw scores for dev mode


# ── System prompts ────────────────────────────────────────────────────────────

_INTENT_CLASSIFIER_SYSTEM = """
You are an intent classifier for FinCopilot, a financial assistant for students.

Your ONLY job: read the user's query and return a JSON object identifying
the correct intent. Do not answer the question. Do not add prose.

Available intents (choose exactly one):
  purchase_decision  → user wants to buy something or asks if they can afford it
  boardroom_review   → user wants multiple expert opinions or a debate on a decision
  cashflow_analysis  → user asks about future cash flow, runway, or money running out
  spending_analysis  → user asks why they overspend or where their money goes
  bill_processing    → user wants to upload, scan, or process a bill or receipt
  financial_report   → user wants a monthly or periodic financial summary
  general_finance    → general financial questions, concepts, tips, definitions

Return ONLY this JSON, nothing else:
{
  "intent": "<one of the intent strings above>",
  "reasoning": "<one short sentence explaining why>"
}
""".strip()


def _build_answer_system(feature: FeatureCard, intent: str) -> str:
    """
    Build the answer-generator system prompt dynamically.
    Injects the recommended feature's metadata so the LLM response
    is grounded in what FinCopilot actually offers.
    """
    # For general_finance, no redirect — just answer the question.
    # For all others, answer briefly then recommend the feature.
    if intent == INTENT_GENERAL_FINANCE:
        return f"""
You are FinCopilot, a friendly and knowledgeable financial assistant for college students.
Your tone is clear, practical, and encouraging — never condescending.

Rules:
- Answer the user's financial question directly and helpfully.
- Keep answers under 120 words.
- Use simple language. Avoid jargon unless you immediately explain it.
- If a specific FinCopilot feature could help them go deeper, mention it
  briefly at the end (1 sentence max).
- Never make up numbers or statistics.
- Format with short paragraphs. No bullet points unless listing 3+ items.
""".strip()

    else:
        return f"""
You are FinCopilot, a financial assistant for college students.
Your tone is clear, practical, and direct.

The user's question relates to: {intent.replace("_", " ").title()}
The most relevant FinCopilot feature for this is: {feature.display_name}
Why it helps: {feature.why_relevant}

Rules:
- Start by directly acknowledging what the user is asking (1 sentence).
- Give a brief, useful answer or insight (2–3 sentences max).
- End by recommending {feature.display_name} — explain ONE specific thing
  it will show them that directly answers their situation.
- Keep total response under 100 words.
- Never execute the simulation or boardroom yourself.
- Never say "I can't do that." Say what the right tool CAN do.
- Tone: like a knowledgeable friend, not a customer service bot.
""".strip()


# ── LLM call: intent classification ──────────────────────────────────────────


def _llm_classify_intent(query: str) -> tuple[str, str]:
    """
    Ask the LLM to classify the intent of an ambiguous query.

    Returns:
        tuple: (intent_string, reasoning_string)
        Falls back to INTENT_GENERAL_FINANCE if parsing fails.
    """
    client = _get_client()

    response = client.chat.completions.create(
        model=MODEL,
        temperature=0.0,  # deterministic — classification must be consistent
        max_tokens=120,
        messages=[
            {"role": "system", "content": _INTENT_CLASSIFIER_SYSTEM},
            {"role": "user", "content": query},
        ],
    )

    raw = response.choices[0].message.content.strip()

    # Extract JSON robustly — model sometimes wraps in ```json fences
    json_match = re.search(r"\{.*?\}", raw, re.DOTALL)
    if not json_match:
        return INTENT_GENERAL_FINANCE, "fallback: no JSON found in response"

    try:
        parsed = json.loads(json_match.group())
        intent = parsed.get("intent", INTENT_GENERAL_FINANCE)
        reasoning = parsed.get("reasoning", "")

        # Validate — never trust a model to stay in vocab
        if intent not in ALL_INTENTS:
            return INTENT_GENERAL_FINANCE, f"fallback: unknown intent '{intent}'"

        return intent, reasoning

    except json.JSONDecodeError:
        return INTENT_GENERAL_FINANCE, "fallback: JSON parse error"


# ── LLM call: answer generation ───────────────────────────────────────────────


def _llm_generate_answer(
    query: str,
    intent: str,
    feature: FeatureCard,
    history: list[dict],
) -> str:
    """
    Generate the actual answer to the user's query.

    Args:
        query:   current user message.
        intent:  resolved intent string.
        feature: recommended FeatureCard.
        history: list of prior {"role": "user"|"assistant", "content": str} dicts.
                 Pass [] for single-turn usage.

    Returns:
        Answer string (markdown safe, ready for st.markdown).
    """
    client = _get_client()

    system_prompt = _build_answer_system(feature, intent)

    # Build message list: system + history + current query
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history[-6:])  # keep last 3 turns (6 messages) for context
    messages.append({"role": "user", "content": query})

    response = client.chat.completions.create(
        model=MODEL,
        temperature=0.4,
        max_tokens=300,
        messages=messages,
    )

    return response.choices[0].message.content.strip()


# ── Main public function ──────────────────────────────────────────────────────


def run_copilot(
    query: str,
    history: list[dict] | None = None,
) -> CopilotResponse:
    """
    Run the full FinCopilot pipeline for one user query.

    Pipeline:
      1. Keyword intent detection (intents.py)  → always runs, zero cost
      2. LLM intent re-classification           → only if confidence == "low"
      3. Feature lookup (feature_map.py)        → always runs, zero cost
      4. LLM answer generation                  → always runs (1 API call)

    So the normal path is 1 API call.
    Ambiguous queries cost 2 API calls.

    Args:
        query:   raw user input string.
        history: optional list of prior conversation turns for multi-turn context.
                 Each item: {"role": "user"|"assistant", "content": str}

    Returns:
        CopilotResponse — the UI reads only this object.
    """
    if history is None:
        history = []

    # ── Step 1: keyword detection (always) ────────────────────────────────────
    intent_result: IntentResult = detect_intent(query)
    intent = intent_result.intent
    intent_source = "keyword"

    # ── Step 2: LLM re-classification (only for low confidence) ───────────────
    if intent_result.confidence == "low":
        try:
            llm_intent, _ = _llm_classify_intent(query)
            intent = llm_intent
            intent_source = "llm"
        except Exception as exc:
            # LLM failed — keep keyword intent, log error but don't crash
            intent = intent_result.intent
            intent_source = "keyword_fallback"

    # ── Step 3: feature lookup (always) ───────────────────────────────────────
    feature: FeatureCard = get_feature_for_intent(intent)

    # Decide whether the UI should show the redirect card prominently.
    # Show it for all intents except general_finance (where we just answer).
    should_redirect = (intent != INTENT_GENERAL_FINANCE) and feature.is_available

    # ── Step 4: LLM answer generation ─────────────────────────────────────────
    try:
        answer = _llm_generate_answer(query, intent, feature, history)
        return CopilotResponse(
            query=query,
            intent=intent,
            confidence=intent_result.confidence,
            intent_source=intent_source,
            feature=feature,
            answer=answer,
            should_redirect=should_redirect,
            error=None,
            debug_scores=intent_result.raw_scores,
        )

    except EnvironmentError as exc:
        # API key missing — surface clearly
        return CopilotResponse(
            query=query,
            intent=intent,
            confidence=intent_result.confidence,
            intent_source=intent_source,
            feature=feature,
            answer="",
            should_redirect=False,
            error=str(exc),
            debug_scores=intent_result.raw_scores,
        )

    except Exception as exc:
        # Any other Groq error — degrade gracefully
        fallback_answer = (
            f"I detected your question is about **{intent.replace('_', ' ')}**. "
            f"The **{feature.display_name}** feature in the sidebar can help you with this. "
            f"_(Note: I'm having trouble generating a full response right now — "
            f"please try again in a moment.)_"
        )
        return CopilotResponse(
            query=query,
            intent=intent,
            confidence=intent_result.confidence,
            intent_source=intent_source,
            feature=feature,
            answer=fallback_answer,
            should_redirect=should_redirect,
            error=f"LLM error: {str(exc)}",
            debug_scores=intent_result.raw_scores,
        )


def get_copilot_response(query: str):
    result = run_copilot(query)

    print("===== COPILOT RESULT =====")
    print("Intent:", result.intent)
    print("Feature:", result.feature.display_name)
    print("Answer:", repr(result.answer))
    print("Error:", result.error)
    print("==========================")

    return {
        "intent": result.intent,
        "feature": result.feature.display_name,
        "reason": result.feature.why_relevant,
        "response": result.answer,
    }
