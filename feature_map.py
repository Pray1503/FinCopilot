"""
fincopilot/feature_map.py
──────────────────────────
Step 2: Feature Recommendation

What this file does:
  - Defines every feature in the FinCopilot ecosystem.
  - Maps each intent → the most relevant feature.
  - Provides full metadata per feature: name, description, why it helps,
    how to navigate to it, and example prompts that trigger it.

Design decisions:
  - FeatureCard dataclass is the single source of truth for all feature
    metadata. The UI, the LLM system prompt, and the recommendation panel
    all read from this one object — no duplication.
  - get_feature_for_intent() is the only public function. It never raises —
    always returns a valid FeatureCard (general_finance as fallback).
  - Adding a new feature = add one FeatureCard + one line in _INTENT_TO_FEATURE.
    Nothing else changes.

Imports:
  - intents.py constants (INTENT_*) — so intent strings are never typed raw.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from intents import (
    INTENT_PURCHASE_DECISION,
    INTENT_BOARDROOM_REVIEW,
    INTENT_CASHFLOW_ANALYSIS,
    INTENT_SPENDING_ANALYSIS,
    INTENT_BILL_PROCESSING,
    INTENT_FINANCIAL_REPORT,
    INTENT_GENERAL_FINANCE,
)

# ── FeatureCard ───────────────────────────────────────────────────────────────


@dataclass
class FeatureCard:
    feature_id: str  # unique slug, e.g. "decision_simulator"
    display_name: str  # shown in UI, e.g. "Financial Decision Simulator"
    icon: str  # emoji for the UI card
    tagline: str  # one sentence: what it does
    why_relevant: str  # one sentence: why it fits this intent
    what_it_shows: list[str]  # bullet points shown in the recommendation card
    navigation_hint: str  # tells user where to find it in the app
    example_triggers: list[str]  # example queries that lead here (for UI tooltips)
    is_available: bool = True  # set False for planned-but-not-built features


# ── Feature definitions ───────────────────────────────────────────────────────

_FEATURES: dict[str, FeatureCard] = {
    "decision_simulator": FeatureCard(
        feature_id="decision_simulator",
        display_name="Financial Decision Simulator",
        icon="💸",
        tagline="Simulate the financial impact of any purchase before you make it.",
        why_relevant="You're considering a purchase — this shows you exactly what it costs your future.",
        what_it_shows=[
            "Affordability score (0–100) based on your real surplus",
            "Months delayed on each of your savings goals",
            "12-month savings projection: with vs without the purchase",
            "Emergency fund safety check after the spend",
        ],
        navigation_hint="Open the **Financial Decision Simulator** tab in the sidebar.",
        example_triggers=[
            "Can I afford a ₹40,000 laptop?",
            "Should I buy an iPhone right now?",
            "Is it worth spending ₹15,000 on this course?",
        ],
    ),
    "financial_boardroom": FeatureCard(
        feature_id="financial_boardroom",
        display_name="Financial Boardroom",
        icon="🏛️",
        tagline="4 specialist AI agents debate your decision and deliver an arbitration verdict.",
        why_relevant="You want a second opinion — the Boardroom gives you 4 independent expert perspectives.",
        what_it_shows=[
            "Budget Analyst: short-term liquidity and cash-flow risk",
            "Risk Assessor: emergency fund health and worst-case exposure",
            "Long-Term Planner: ROI, goal impact, opportunity cost",
            "Devil's Advocate: challenges the consensus view",
            "Chairman: synthesises all views into a structured verdict",
        ],
        navigation_hint="Open the **Financial Boardroom** tab in the sidebar.",
        example_triggers=[
            "I need a second opinion before buying a gaming laptop.",
            "Multiple perspectives on whether I should take this loan.",
            "Run a boardroom review on my ₹50,000 decision.",
        ],
    ),
    "cashflow_engine": FeatureCard(
        feature_id="cashflow_engine",
        display_name="Cash Flow Prediction Engine",
        icon="📈",
        tagline="Predict your income, expenses, and net balance for the next 3–12 months.",
        why_relevant="You want to know where your money is going — this forecasts it month by month.",
        what_it_shows=[
            "Predicted monthly surplus or deficit for each future month",
            "Runway: how many months before savings reach zero",
            "Income vs expense trend lines",
            "Early warning if you're on track to run out of money",
        ],
        navigation_hint="Open the **Cash Flow Prediction** tab in the sidebar.",
        example_triggers=[
            "Will I run out of money next month?",
            "What will my balance look like in 6 months?",
            "Predict my cash flow for the next quarter.",
        ],
    ),
    "spending_predictor": FeatureCard(
        feature_id="spending_predictor",
        display_name="Spending Habit Analyser",
        icon="🔍",
        tagline="Analyse your spending patterns and predict where overspending will happen.",
        why_relevant="You're overspending somewhere — this identifies the category and predicts future patterns.",
        what_it_shows=[
            "Spending breakdown by category (food, transport, entertainment, etc.)",
            "Month-over-month spending trend per category",
            "Predicted next-month spend based on your history",
            "Top 3 categories where you're overspending vs your income",
        ],
        navigation_hint="Open the **Spending Analysis** tab in the sidebar.",
        example_triggers=[
            "Why am I spending so much money every month?",
            "Where is all my money going?",
            "Show me my spending patterns.",
        ],
    ),
    "bill_ocr": FeatureCard(
        feature_id="bill_ocr",
        display_name="OCR Bill Processing Pipeline",
        icon="📄",
        tagline="Upload any bill or receipt — AI extracts merchant, amount, date, and category automatically.",
        why_relevant="You have a physical or scanned bill — this extracts all the financial data from it instantly.",
        what_it_shows=[
            "Merchant name and contact details (NER extraction)",
            "Total amount, tax breakdown, line items",
            "Transaction date and payment method",
            "Auto-categorised expense type for your spending tracker",
        ],
        navigation_hint="Open the **Bill Processing** tab in the sidebar.",
        example_triggers=[
            "I have a bill I want to upload.",
            "Can you read this receipt for me?",
            "Process my electricity bill PDF.",
        ],
    ),
    "monthly_report": FeatureCard(
        feature_id="monthly_report",
        display_name="Monthly Financial Report",
        icon="📊",
        tagline="Get a complete AI-generated summary of your financial health for any month.",
        why_relevant="You want to review how you did this month — this gives you a structured financial report.",
        what_it_shows=[
            "Income vs expenses summary with surplus/deficit",
            "Goal progress: how close are you to each target?",
            "Spending category breakdown with month-over-month change",
            "Financial health score with personalised recommendations",
        ],
        navigation_hint="Open the **Monthly Report** tab in the sidebar.",
        example_triggers=[
            "Generate my monthly financial report.",
            "How did I do financially this month?",
            "Give me a summary of my October finances.",
        ],
        is_available=False,  # planned feature — not built yet
    ),
    "general_advice": FeatureCard(
        feature_id="general_advice",
        display_name="FinCopilot Chat",
        icon="🤖",
        tagline="Ask any financial question and get a clear, student-friendly answer.",
        why_relevant="You have a general financial question — FinCopilot answers it directly.",
        what_it_shows=[
            "Plain-English explanations of financial concepts",
            "Personalised tips based on your question",
            "Pointers to the right feature if a deeper analysis would help",
        ],
        navigation_hint="You're already here — just ask your question.",
        example_triggers=[
            "What is compound interest?",
            "How does a SIP work?",
            "What's the 50/30/20 budgeting rule?",
        ],
    ),
}


# ── Intent → Feature mapping ──────────────────────────────────────────────────
# One intent maps to exactly one primary feature.
# Keep this simple — one clear recommendation is better than a list.

_INTENT_TO_FEATURE: dict[str, str] = {
    INTENT_PURCHASE_DECISION: "decision_simulator",
    INTENT_BOARDROOM_REVIEW: "financial_boardroom",
    INTENT_CASHFLOW_ANALYSIS: "cashflow_engine",
    INTENT_SPENDING_ANALYSIS: "spending_predictor",
    INTENT_BILL_PROCESSING: "bill_ocr",
    INTENT_FINANCIAL_REPORT: "monthly_report",
    INTENT_GENERAL_FINANCE: "general_advice",
}


# ── Public API ────────────────────────────────────────────────────────────────


def get_feature_for_intent(intent: str) -> FeatureCard:
    """
    Return the FeatureCard recommended for a given intent string.

    Never raises — falls back to general_advice if intent is unknown.

    Args:
        intent: one of the INTENT_* constants from intents.py.

    Returns:
        FeatureCard with all metadata needed to render the recommendation UI.

    Example:
        >>> card = get_feature_for_intent(INTENT_PURCHASE_DECISION)
        >>> card.display_name
        'Financial Decision Simulator'
    """
    feature_id = _INTENT_TO_FEATURE.get(intent, "general_advice")
    return _FEATURES[feature_id]


def get_all_features() -> list[FeatureCard]:
    """
    Return all defined features.
    Used by the UI to render a feature directory / help panel.
    """
    return list(_FEATURES.values())


def get_available_features() -> list[FeatureCard]:
    """Return only features that are fully built and available."""
    return [f for f in _FEATURES.values() if f.is_available]
