"""
services/boardroom_service.py
─────────────────────────────
Orchestrates the AI Boardroom debate.
Runs Budget-Bot → Risk-Radar → Horizon-Planner → Chairman → Devil's Advocate.

Improvement: Turn 4 (Devil's Advocate) is now properly included.
"""

from agents import budget_agent, risk_agent, planner_agent, chairman_agent, devil_agent


def run_boardroom(scenario: dict, question: str) -> dict:
    """
    Execute a full boardroom debate and return all turns.

    Returns dict with keys: budget, risk, planner, chairman, devil, turns
    """
    turns = []

    # Turn 1 — Budget-Bot
    budget_response = budget_agent.run(scenario)
    turns.append({"agent": "Budget-Bot", "emoji": "📊", "color": "#2563eb", "response": budget_response})

    # Turn 2 — Risk-Radar
    risk_response = risk_agent.run(scenario)
    turns.append({"agent": "Risk-Radar", "emoji": "🛡️", "color": "#ef4444", "response": risk_response})

    # Turn 3 — Horizon-Planner
    planner_response = planner_agent.run(scenario)
    turns.append({"agent": "Horizon-Planner", "emoji": "🔭", "color": "#10b981", "response": planner_response})

    # Turn 4 — Chairman
    chairman_response = chairman_agent.run(
        budget_opinion=budget_response,
        risk_opinion=risk_response,
        planner_opinion=planner_response,
        question=question,
    )
    turns.append({"agent": "The Chairman", "emoji": "👑", "color": "#f59e0b", "response": chairman_response})

    # Turn 5 — Devil's Advocate (was commented out in original — now active!)
    scenario_summary = (
        f"Income: ₹{scenario.get('income_monthly', 0):,}, "
        f"Expenses: ₹{scenario.get('monthly_expenses', 0):,}, "
        f"Savings: ₹{scenario.get('savings', 0):,}, "
        f"Proposed EMI: ₹{scenario.get('proposed_EMI', 0):,}"
    )
    devil_response = devil_agent.run(chairman_response, scenario_summary)
    turns.append({"agent": "Devil's Advocate", "emoji": "😈", "color": "#7c3aed", "response": devil_response})

    return {
        "budget": budget_response,
        "risk": risk_response,
        "planner": planner_response,
        "chairman": chairman_response,
        "devil": devil_response,
        "turns": turns,
    }
