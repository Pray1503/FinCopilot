"""
fincopilot/__init__.py
───────────────────────
Public API for the fincopilot module.

Other modules in the repo can do:
    from fincopilot import run_copilot, CopilotResponse
    from fincopilot import detect_intent, get_feature_for_intent
"""

from fincopilot.intents import (
    detect_intent,
    IntentResult,
    INTENT_PURCHASE_DECISION,
    INTENT_BOARDROOM_REVIEW,
    INTENT_CASHFLOW_ANALYSIS,
    INTENT_SPENDING_ANALYSIS,
    INTENT_BILL_PROCESSING,
    INTENT_FINANCIAL_REPORT,
    INTENT_GENERAL_FINANCE,
    ALL_INTENTS,
)

from fincopilot.feature_map import (
    get_feature_for_intent,
    get_all_features,
    get_available_features,
    FeatureCard,
)

from fincopilot.copilot_service import (
    run_copilot,
    CopilotResponse,
)

__all__ = [
    "run_copilot",
    "CopilotResponse",
    "detect_intent",
    "IntentResult",
    "get_feature_for_intent",
    "get_all_features",
    "get_available_features",
    "FeatureCard",
    "INTENT_PURCHASE_DECISION",
    "INTENT_BOARDROOM_REVIEW",
    "INTENT_CASHFLOW_ANALYSIS",
    "INTENT_SPENDING_ANALYSIS",
    "INTENT_BILL_PROCESSING",
    "INTENT_FINANCIAL_REPORT",
    "INTENT_GENERAL_FINANCE",
    "ALL_INTENTS",
]
