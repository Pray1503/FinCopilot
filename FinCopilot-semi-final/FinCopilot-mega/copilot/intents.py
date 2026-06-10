"""
copilot/intents.py
──────────────────
Intent detection module. Classifies user queries into financial intents
using keyword signals, then falls back to LLM if no strong match is found.

Ported from FinCopilot-fincopilot-feature/intents.py with improvements:
  - Added SCENARIO intent for decision simulator
  - Added OCR intent for bill scanner
  - Better threshold scoring
"""

from __future__ import annotations

# ── Intent definitions ────────────────────────────────────────────────────────

INTENTS: dict[str, dict] = {
    "loan_check": {
        "keywords": [
            "loan", "borrow", "emi", "interest rate", "repayment",
            "credit", "should i take", "afford loan", "debt",
            "tenure", "moratorium", "equated monthly",
        ],
        "description": "Evaluate loan affordability and repayment capacity",
    },
    "budget": {
        "keywords": [
            "budget", "spending", "expense", "save", "cut cost",
            "monthly plan", "savings plan", "track expense", "overspend",
            "allocation", "50 30 20", "frugal",
        ],
        "description": "Budgeting advice, 50/30/20 analysis, expense control",
    },
    "investment": {
        "keywords": [
            "invest", "mutual fund", "sip", "stock", "portfolio",
            "return", "compound", "nifty", "etf", "equity",
            "fixed deposit", "fd", "ppf", "nps", "gold",
        ],
        "description": "Investment advice and portfolio analysis",
    },
    "scenario": {
        "keywords": [
            "what if", "scenario", "simulate", "impact", "decide",
            "should i buy", "afford", "purchase", "compare",
            "decision", "tradeoff",
        ],
        "description": "Financial scenario modelling and decision analysis",
    },
    "goal": {
        "keywords": [
            "goal", "target", "dream", "plan for", "save for",
            "house", "car", "wedding", "education fund", "retirement",
            "emergency fund",
        ],
        "description": "Long-term goal planning and progress tracking",
    },
    "risk": {
        "keywords": [
            "risk", "emergency", "insurance", "volatility",
            "worst case", "contingency", "safety net", "hedge",
        ],
        "description": "Risk assessment and mitigation",
    },
    "cashflow": {
        "keywords": [
            "cash flow", "cashflow", "inflow", "outflow",
            "forecast", "runway", "burn rate", "liquidity",
            "projection", "revenue",
        ],
        "description": "Cash-flow monitoring and forecasting",
    },
    "ocr": {
        "keywords": [
            "scan", "bill", "receipt", "ocr", "upload",
            "extract", "invoice", "vendor",
        ],
        "description": "Bill scanning and expense extraction",
    },
}


def detect_intent(query: str) -> tuple[str, float]:
    """
    Detect the financial intent of a user query.

    Returns (intent_name, confidence) where confidence is 0.0–1.0.
    Falls back to 'general' if no intent scores above threshold.
    """
    lowered = query.lower()
    scores: dict[str, int] = {}

    for intent_name, config in INTENTS.items():
        score = 0
        for keyword in config["keywords"]:
            if keyword in lowered:
                score += 3 if len(keyword.split()) > 1 else 2
        scores[intent_name] = score

    best_intent = max(scores, key=scores.get) if scores else "general"
    best_score = scores.get(best_intent, 0)

    # Normalize to confidence
    max_possible = max(len(INTENTS.get(best_intent, {}).get("keywords", [])) * 2, 1)
    confidence = min(best_score / max_possible, 1.0)

    if best_score < 2:
        return "general", 0.0

    return best_intent, round(confidence, 2)
