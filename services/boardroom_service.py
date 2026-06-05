"""
services/boardroom_service.py
──────────────────────────────
Orchestrates the 8-turn boardroom debate and streams events to the UI.

FIX: Removed all personal names (Vikram Nair, Marcus Chen, etc.).
     Agent labels are now simple role names only.
"""

import time
from agents.budget_agent import budget_agent
from agents.risk_agent import risk_agent
from agents.planner_agent import planner_agent
from agents.chairman_agent import chairman_agent

# ── Agent identity — simple role names only, no personal names ────────────────
AGENTS = {
    "chairman": {"icon": "🏛️", "label": "Chairman", "color": "#1e3a8a"},
    "budget": {"icon": "📊", "label": "Budget Analyst", "color": "#2563eb"},
    "risk": {"icon": "🛡️", "label": "Risk Assessor", "color": "#d97706"},
    "planner": {"icon": "🎯", "label": "Long-Term Planner", "color": "#7c3aed"},
}

PAUSE = 0.4  # seconds between agent calls


def _emit(cb, event_type, content, agent_key="chairman"):
    """Emit an event to the UI callback with agent icon + label."""
    a = AGENTS[agent_key]
    cb(event_type, content, f"{a['icon']} {a['label']}", a["color"])


def execute_boardroom_debate_stream(
    financial_facts: str,
    ui_callback,
) -> dict:
    """
    Run the full 8-turn boardroom debate and return the Chairman's verdict dict.

    Turn order:
      0  Chairman   — opens the session
      1  Budget     — opening statement
      2  Risk       — opening statement
      3  Planner    — opening statement
      4  Devil      — contrarian challenge
      5  Budget     — rebuttal
      6  Risk       — rebuttal
      7  Planner    — closing argument
      8  Chairman   — final verdict (JSON)
    """
    history: list[str] = []

    # ── Turn 0: Chairman opens ────────────────────────────────────────────────
    _emit(ui_callback, "STATUS", "Chairman is convening the boardroom...", "chairman")
    intro = (
        "The boardroom is now in session. We are here to evaluate a student "
        "financial decision. I call upon our specialists to examine "
        "the financial profile from their respective lenses. "
        "Budget Analyst — your opening assessment."
    )
    history.append(f"🏛️ Chairman: {intro}")
    _emit(ui_callback, "MESSAGE", intro, "chairman")
    time.sleep(PAUSE)

    # ── Turn 1: Budget — opening ──────────────────────────────────────────────
    _emit(
        ui_callback, "STATUS", "Budget Analyst computing cash-flow vectors...", "budget"
    )
    b_open = budget_agent(financial_facts, round_label="opening")
    history.append(f"📊 Budget Analyst: {b_open}")
    _emit(ui_callback, "MESSAGE", b_open, "budget")
    time.sleep(PAUSE)

    # ── Turn 2: Risk — opening ────────────────────────────────────────────────
    _emit(
        ui_callback,
        "STATUS",
        "Risk Assessor stress-testing runway thresholds...",
        "risk",
    )
    r_open = risk_agent(
        financial_facts, round_label="opening", debate_history="\n".join(history)
    )
    history.append(f"🛡️ Risk Assessor: {r_open}")
    _emit(ui_callback, "MESSAGE", r_open, "risk")
    time.sleep(PAUSE)

    # ── Turn 3: Planner — opening ─────────────────────────────────────────────
    _emit(
        ui_callback,
        "STATUS",
        "Long-Term Planner modelling opportunity cost curves...",
        "planner",
    )
    p_open = planner_agent(
        financial_facts, round_label="opening", debate_history="\n".join(history)
    )
    history.append(f"🎯 Long-Term Planner: {p_open}")
    _emit(ui_callback, "MESSAGE", p_open, "planner")
    time.sleep(PAUSE)

    # ── Turn 4: Devil's Advocate — contrarian challenge ───────────────────────

    # ── Turn 5: Budget — rebuttal ─────────────────────────────────────────────
    _emit(ui_callback, "STATUS", "Budget Analyst firing counter-arguments...", "budget")
    b_rebut = budget_agent(
        financial_facts, round_label="rebuttal", debate_history="\n".join(history)
    )
    history.append(f"📊 Budget Analyst [Rebuttal]: {b_rebut}")
    _emit(ui_callback, "MESSAGE", b_rebut, "budget")
    time.sleep(PAUSE)

    # ── Turn 6: Risk — rebuttal ───────────────────────────────────────────────
    _emit(
        ui_callback,
        "STATUS",
        "Risk Assessor compiling worst-case exposure alerts...",
        "risk",
    )
    r_rebut = risk_agent(
        financial_facts, round_label="rebuttal", debate_history="\n".join(history)
    )
    history.append(f"🛡️ Risk Assessor [Rebuttal]: {r_rebut}")
    _emit(ui_callback, "MESSAGE", r_rebut, "risk")
    time.sleep(PAUSE)

    # ── Turn 7: Planner — closing ─────────────────────────────────────────────
    _emit(
        ui_callback,
        "STATUS",
        "Long-Term Planner delivering closing argument...",
        "planner",
    )
    p_close = planner_agent(
        financial_facts, round_label="closing", debate_history="\n".join(history)
    )
    history.append(f"🎯 Long-Term Planner [Closing]: {p_close}")
    _emit(ui_callback, "MESSAGE", p_close, "planner")
    time.sleep(PAUSE)

    # ── Turn 8: Chairman — arbitration verdict ────────────────────────────────
    _emit(ui_callback, "STATUS", "Chairman synthesising final verdict...", "chairman")
    verdict = chairman_agent(
        debate_history="\n".join(history),
        financial_facts=financial_facts,
    )

    closing = (
        f"The boardroom has deliberated. Based on the full cross-examination, "
        f"I render the following settlement: "
        f"**{verdict.get('verdict', 'PROCEED WITH CAUTION')}** "
        f"with {verdict.get('confidence', '—')} confidence. "
        f"The decisive argument came from {verdict.get('winning_argument', 'the panel')}."
    )
    history.append(f"🏛️ Chairman [Verdict]: {closing}")
    _emit(ui_callback, "MESSAGE", closing, "chairman")

    return verdict
