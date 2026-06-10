"""
fincopilot/intents.py
──────────────────────
Step 1: Intent Detection

What this file does:
  - Defines every intent FinCopilot can recognise.
  - Maps keyword signals to each intent.
  - Exposes one public function: detect_intent(user_query) -> str

Design decisions:
  - Keyword matching first (zero latency, zero API cost).
  - Groq LLM fallback only when keywords give no clear winner.
  - Intent names are constants — imported by feature_map.py and
    copilot_service.py so there is never a magic string anywhere.
  - Confidence score returned alongside intent so the UI can show
    "I think you want X" vs "I'm certain you want X".

No external dependencies beyond the standard library for this file.
"""

from __future__ import annotations
import re
from dataclasses import dataclass

# ── Intent constants ──────────────────────────────────────────────────────────
# Use these everywhere instead of raw strings.
# If you rename an intent, you change it in ONE place only.

INTENT_PURCHASE_DECISION = "purchase_decision"
INTENT_BOARDROOM_REVIEW = "boardroom_review"
INTENT_CASHFLOW_ANALYSIS = "cashflow_analysis"
INTENT_SPENDING_ANALYSIS = "spending_analysis"
INTENT_BILL_PROCESSING = "bill_processing"
INTENT_FINANCIAL_REPORT = "financial_report"
INTENT_GENERAL_FINANCE = "general_finance"  # catch-all

ALL_INTENTS = [
    INTENT_PURCHASE_DECISION,
    INTENT_BOARDROOM_REVIEW,
    INTENT_CASHFLOW_ANALYSIS,
    INTENT_SPENDING_ANALYSIS,
    INTENT_BILL_PROCESSING,
    INTENT_FINANCIAL_REPORT,
    INTENT_GENERAL_FINANCE,
]


# ── Keyword signal map ────────────────────────────────────────────────────────
# Each intent has a list of keyword phrases.
# Matching is case-insensitive and looks for whole words / phrases.
# Order inside each list does not matter — all matches are counted.
# The intent with the most keyword hits wins.

_KEYWORD_MAP: dict[str, list[str]] = {
    INTENT_PURCHASE_DECISION: [
        "buy",
        "buying",
        "purchase",
        "afford",
        "can i get",
        "should i get",
        "worth it",
        "worth buying",
        "spend on",
        "invest in",
        "get a",
        "order",
        "price",
        "cost",
        "laptop",
        "phone",
        "iphone",
        "macbook",
        "tablet",
        "gadget",
        "course fee",
        "rent",
        "subscription",
    ],
    INTENT_BOARDROOM_REVIEW: [
        "second opinion",
        "expert opinion",
        "boardroom",
        "debate",
        "agents",
        "multiple views",
        "different perspective",
        "think twice",
        "review my decision",
        "validate",
        "cross examine",
        "argue",
        "pros and cons",
        "should i really",
        "is it a good idea",
        "before buying",
        "before i buy",
        "before purchasing",
        "another opinion",
        "other opinion",
        "multiple opinions",
    ],
    INTENT_CASHFLOW_ANALYSIS: [
        "cash flow",
        "cashflow",
        "money coming in",
        "money going out",
        "income vs expense",
        "net flow",
        "monthly flow",
        "predict cash",
        "future balance",
        "will i run out",
        "runway",
        "burn rate",
        "how long will my money last",
        "next month money",
        "project my finances",
    ],
    INTENT_SPENDING_ANALYSIS: [
        "spending",
        "why am i spending",
        "where does my money go",
        "where is my money going",
        "where does my money go",
        "where did my money go",
        "where went my money",
        "overspending",
        "expenses too high",
        "spending pattern",
        "spending habit",
        "track spending",
        "analyse spend",
        "too much on food",
        "too much on entertainment",
        "reduce expenses",
        "cut costs",
        "budget breakdown",
        "spending behaviour",
        "money going",
        "money went",
    ],
    INTENT_BILL_PROCESSING: [
        "bill",
        "receipt",
        "invoice",
        "upload",
        "scan",
        "ocr",
        "read my bill",
        "process bill",
        "electricity bill",
        "water bill",
        "gas bill",
        "utility",
        "extract amount",
        "document",
        "image",
        "photo of",
        "picture of",
        "pdf",
    ],
    INTENT_FINANCIAL_REPORT: [
        "report",
        "summary",
        "monthly report",
        "financial summary",
        "end of month",
        "overview",
        "how did i do",
        "this month performance",
        "review my month",
        "monthly breakdown",
        "generate report",
        "financial health check",
        "net worth",
    ],
    INTENT_GENERAL_FINANCE: [
        "what is",
        "explain",
        "how does",
        "define",
        "financial advice",
        "money tip",
        "saving tip",
        "investment",
        "compound interest",
        "inflation",
        "emergency fund",
        "budgeting",
        "50 30 20",
        "sip",
        "mutual fund",
        "fd",
        "fixed deposit",
    ],
}

# ── Priority phrases (weight = 3) ─────────────────────────────────────────────
# These multi-word phrases are so specific to one intent that a single match
# should beat any combination of shorter keywords from another intent.
# Format: {intent: [phrases]}

_PRIORITY_PHRASES: dict[str, list[str]] = {
    INTENT_BOARDROOM_REVIEW: [
        "second opinion",
        "multiple views",
        "different perspective",
        "another opinion",
        "other opinion",
        "before buying",
        "before i buy",
        "cross examine",
        "pros and cons",
    ],
    INTENT_CASHFLOW_ANALYSIS: [
        "cash flow",
        "run out of money",
        "burn rate",
        "how long will my money last",
    ],
    INTENT_SPENDING_ANALYSIS: [
        "where is my money going",
        "where does my money go",
        "spending pattern",
        "spending habit",
    ],
}


# ── Result dataclass ──────────────────────────────────────────────────────────


@dataclass
class IntentResult:
    intent: str  # one of the INTENT_* constants above
    confidence: str  # "high" | "medium" | "low"
    matched_signals: list[str]  # which keywords triggered the match
    raw_scores: dict[str, int]  # full score table (useful for debugging)


# ── Core detection logic ──────────────────────────────────────────────────────


def detect_intent(query: str) -> IntentResult:
    """
    Detect the most likely intent from a free-text user query.

    Algorithm:
      1. Normalise the query (lowercase, strip punctuation).
      2. Apply priority phrase boost (+3 per match) for high-signal phrases.
      3. Count regular keyword matches (+1 each) for each intent.
      4. Sum both scores. Top intent wins.
      5. Confidence = "high" if lead ≥ 2, "medium" if lead = 1, "low" if tie.
      6. All-zero → INTENT_GENERAL_FINANCE with "low" confidence.

    Args:
        query: raw user input string.

    Returns:
        IntentResult with intent, confidence, matched signals, and raw scores.
    """
    normalised = _normalise(query)
    scores: dict[str, int] = {intent: 0 for intent in _KEYWORD_MAP}
    matched_signals: dict[str, list[str]] = {intent: [] for intent in _KEYWORD_MAP}

    # Step 1: priority phrase boost (weight = 3)
    for intent, phrases in _PRIORITY_PHRASES.items():
        for phrase in phrases:
            if _phrase_in_text(phrase, normalised):
                scores[intent] += 3
                matched_signals[intent].append(f"[priority] {phrase}")

    # Step 2: regular keyword scoring (weight = 1)
    for intent, keywords in _KEYWORD_MAP.items():
        for kw in keywords:
            if _phrase_in_text(kw, normalised):
                scores[intent] += 1
                matched_signals[intent].append(kw)

    # Sort by score descending
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_intent, top_score = ranked[0]
    second_score = ranked[1][1] if len(ranked) > 1 else 0

    if top_score == 0:
        return IntentResult(
            intent=INTENT_GENERAL_FINANCE,
            confidence="low",
            matched_signals=[],
            raw_scores=scores,
        )

    lead = top_score - second_score

    if lead >= 2:
        confidence = "high"
    elif lead >= 1:
        confidence = "medium"
    else:
        confidence = "low"

    return IntentResult(
        intent=top_intent,
        confidence=confidence,
        matched_signals=matched_signals[top_intent],
        raw_scores=scores,
    )


# ── Private helpers ───────────────────────────────────────────────────────────


def _normalise(text: str) -> str:
    """Lowercase and replace punctuation with spaces."""
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)  # remove punctuation
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _phrase_in_text(phrase: str, text: str) -> bool:
    """
    Check if a phrase (single word or multi-word) exists in text.
    For single words: whole-word match to avoid 'buy' matching 'buyer'.
    For multi-word phrases: substring match (already specific enough).
    """
    if " " in phrase:
        return phrase in text
    # Whole word match for single tokens
    return bool(re.search(rf"\b{re.escape(phrase)}\b", text))


# ── UI Labels ────────────────────────────────────────────────────────────────

INTENT_LABELS = {
    INTENT_PURCHASE_DECISION: "Purchase Decision",
    INTENT_BOARDROOM_REVIEW: "Boardroom Review",
    INTENT_CASHFLOW_ANALYSIS: "Cash Flow Analysis",
    INTENT_SPENDING_ANALYSIS: "Spending Analysis",
    INTENT_BILL_PROCESSING: "Bill Processing",
    INTENT_FINANCIAL_REPORT: "Financial Report",
    INTENT_GENERAL_FINANCE: "General Finance",
}
