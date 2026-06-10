"""
shared/utils.py
───────────────
Shared helper functions used across all FinPilot modules.
"""


def money(value: float, symbol: str = "₹") -> str:
    """Format a number as currency with ₹ symbol."""
    sign = "-" if value < 0 else ""
    return f"{sign}{symbol}{abs(value):,.0f}"


def money_precise(value: float, symbol: str = "₹") -> str:
    """Format a number as currency with 2 decimal places."""
    sign = "-" if value < 0 else ""
    return f"{sign}{symbol}{abs(value):,.2f}"


def score_color(score: int) -> str:
    """Return colour hex for a 0-100 score."""
    if score >= 70:
        return "#10b981"
    if score >= 45:
        return "#f59e0b"
    return "#ef4444"


def flag_badge(flag: str) -> str:
    """Return an HTML badge for affordability flags."""
    mapping = {
        "OK": (
            "<span style='background:#064e3b;color:#10b981;padding:3px 10px;"
            "border-radius:999px;font-size:0.75rem;font-weight:700;'>✓ OK</span>"
        ),
        "TIGHT": (
            "<span style='background:#451a03;color:#f59e0b;padding:3px 10px;"
            "border-radius:999px;font-size:0.75rem;font-weight:700;'>⚠ TIGHT</span>"
        ),
        "OVEREXTENDED": (
            "<span style='background:#450a0a;color:#ef4444;padding:3px 10px;"
            "border-radius:999px;font-size:0.75rem;font-weight:700;'>✗ OVEREXTENDED</span>"
        ),
    }
    return mapping.get(flag, flag)
