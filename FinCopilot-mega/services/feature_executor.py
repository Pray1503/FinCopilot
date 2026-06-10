"""
services/feature_executor.py
─────────────────────────────
Connects the chatbot to ALL FinPilot features.
When a user asks a question, this module:
  1. Detects intent
  2. Runs the actual feature module if applicable
  3. Formats live results for display in the chat
  4. Sends context to LLM for a natural language summary
"""

from __future__ import annotations
import traceback
from copilot.intents import detect_intent
from copilot.feature_map import get_system_prompt
from services.groq_client import call_groq


def _try_smart_boardroom(profile: dict, question: str) -> dict | None:
    """Run the pure-Python boardroom agents."""
    try:
        from agents.budget_analyst import run as run_budget
        from agents.risk_assessor import run as run_risk
        from agents.long_term_planner import run as run_planner
        from agents.coordinator import run as run_coordinator

        budget = run_budget(profile)
        risk = run_risk(profile)
        planner = run_planner(profile)
        coord = run_coordinator(budget, planner, risk, question, profile)

        return {
            "type": "boardroom",
            "verdict": coord.get("combined_verdict", "unknown"),
            "budget": budget,
            "risk": risk,
            "planner": planner,
            "coordinator": coord,
        }
    except Exception:
        return None


def _try_decision_sim(query: str, profile: dict) -> dict | None:
    """Run the decision simulator if the user mentions buying something."""
    try:
        from simulator.decision_engine import simulate_purchase

        income = profile.get("income_monthly", 15000)
        expenses = profile.get("monthly_expenses", 9000)
        savings = profile.get("savings", 20000)

        # Try to extract cost from query
        import re
        cost_match = re.search(r'₹?\s*(\d[\d,]*)', query)
        cost = int(cost_match.group(1).replace(",", "")) if cost_match else 5000

        # Extract item name
        buy_match = re.search(r'(?:buy|afford|purchase|get)\s+(?:a\s+|an\s+)?(.+?)(?:\s+for|\s+at|\s+worth|\s*\?|$)', query, re.I)
        item = buy_match.group(1).strip().rstrip("?., ") if buy_match else "this item"

        result = simulate_purchase(
            income=income, current_savings=savings, base_expenses=expenses,
            item_name=item, cost=cost,
            goal_name="Savings Goal", goal_target=100000,
            goal_current=savings, goal_alloc=3000,
        )

        if result.get("error"):
            return None
        return {"type": "decision", "result": result, "item": item, "cost": cost}
    except Exception:
        return None


def _try_cashflow_summary() -> dict | None:
    """Generate cash-flow metrics."""
    try:
        from cashflow.engine import generate_cash_flow_data
        hist, forecast = generate_cash_flow_data()

        balance = hist["balance"].iloc[-1]
        inflow_30 = hist.tail(30)["inflow"].sum()
        outflow_30 = hist.tail(30)["outflow"].sum()
        predicted = forecast.tail(30)["balance"].iloc[-1]
        net_30 = inflow_30 - outflow_30

        return {
            "type": "cashflow",
            "balance": round(balance),
            "inflow_30d": round(inflow_30),
            "outflow_30d": round(outflow_30),
            "net_30d": round(net_30),
            "predicted": round(predicted),
        }
    except Exception:
        return None


def _try_spending_prediction() -> dict | None:
    """Run spending predictor."""
    try:
        from pathlib import Path
        csv_path = Path(__file__).resolve().parent.parent / "data" / "student_spending.csv"
        if not csv_path.exists():
            return None
        from ml.spending_predictor import SpendingPredictor
        pred = SpendingPredictor(str(csv_path))
        return {"type": "spending", "summary": pred.get_summary()}
    except Exception:
        return None


def _try_ml_predict(profile: dict) -> dict | None:
    """Run the ML spending prediction."""
    try:
        from ml.predict import predict_spend, is_model_available
        if not is_model_available():
            return None
        month_idx = __import__("datetime").datetime.now().month
        pred = predict_spend(month_idx, 0, 0, profile.get("monthly_expenses", 9000))
        if pred is None:
            return None
        return {"type": "ml_predict", "predicted_spend": pred, "month": month_idx}
    except Exception:
        return None


def _format_feature_result(feature_data: dict) -> str:
    """Format feature execution result as an HTML card for the chat."""
    ft = feature_data.get("type")

    if ft == "boardroom":
        coord = feature_data["coordinator"]
        verdict = feature_data["verdict"]
        emoji = {"Go_now": "✅", "Delay_and_prepare": "⏸️", "Decline": "🛑"}.get(verdict, "📋")
        cls = "result-inline" if verdict == "Go_now" else ("result-inline warn" if verdict == "Delay_and_prepare" else "result-inline danger")

        budget = feature_data["budget"]
        kn = budget.get("key_numbers", {})

        html = f"""
        <div class="{cls}">
            <div style="font-weight:700;font-size:1rem;margin-bottom:8px;">
                {emoji} Smart Boardroom Verdict: <strong>{verdict.replace('_', ' ').title()}</strong>
            </div>
            <div style="display:flex;flex-wrap:wrap;gap:6px;margin:8px 0;">
                <div class="result-metric"><div class="label">DTI Ratio</div><div class="value">{kn.get('debt_to_income_pct', 0)}%</div></div>
                <div class="result-metric"><div class="label">Monthly Surplus</div><div class="value">₹{kn.get('net_monthly_surplus', 0):,}</div></div>
                <div class="result-metric"><div class="label">Savings Runway</div><div class="value">{kn.get('savings_months_coverage', 0)} mo</div></div>
                <div class="result-metric"><div class="label">Emergency Fund</div><div class="value">{feature_data['risk'].get('emergency_fund_months', 0)} mo</div></div>
            </div>
            <div style="margin-top:8px;font-size:0.88rem;color:#334155;line-height:1.55;">
                {coord.get('coordinator_recommendation', '')}
            </div>
        </div>"""
        return html

    elif ft == "decision":
        r = feature_data["result"]
        sc = r["affordability_score"]
        color = "#059669" if sc >= 70 else ("#d97706" if sc >= 45 else "#dc2626")
        cls = "result-inline" if sc >= 70 else ("result-inline warn" if sc >= 45 else "result-inline danger")

        html = f"""
        <div class="{cls}">
            <div style="font-weight:700;font-size:1rem;margin-bottom:8px;">
                💸 Decision Simulator — {feature_data['item']}
            </div>
            <div style="display:flex;flex-wrap:wrap;gap:6px;margin:8px 0;">
                <div class="result-metric"><div class="label">Affordability</div><div class="value" style="color:{color};">{sc}/100</div></div>
                <div class="result-metric"><div class="label">Cost</div><div class="value">₹{r['cost']:,}</div></div>
                <div class="result-metric"><div class="label">Time to Absorb</div><div class="value">{r['months_to_absorb']} mo</div></div>
                <div class="result-metric"><div class="label">Surplus</div><div class="value">₹{r['surplus']:,}</div></div>
            </div>
            <div style="margin-top:6px;font-size:0.9rem;font-weight:600;color:{color};">{r['verdict']}</div>
        </div>"""
        return html

    elif ft == "cashflow":
        d = feature_data
        html = f"""
        <div class="result-inline">
            <div style="font-weight:700;font-size:1rem;margin-bottom:8px;">💰 Cash Flow Summary (30 days)</div>
            <div style="display:flex;flex-wrap:wrap;gap:6px;margin:8px 0;">
                <div class="result-metric"><div class="label">Balance</div><div class="value">₹{d['balance']:,}</div></div>
                <div class="result-metric"><div class="label">Inflow</div><div class="value" style="color:#059669;">₹{d['inflow_30d']:,}</div></div>
                <div class="result-metric"><div class="label">Outflow</div><div class="value" style="color:#dc2626;">₹{d['outflow_30d']:,}</div></div>
                <div class="result-metric"><div class="label">Predicted</div><div class="value">₹{d['predicted']:,}</div></div>
            </div>
        </div>"""
        return html

    elif ft == "spending":
        s = feature_data["summary"]
        html = f"""
        <div class="result-inline">
            <div style="font-weight:700;font-size:1rem;margin-bottom:8px;">📈 Spending Analysis</div>
            <div style="display:flex;flex-wrap:wrap;gap:6px;margin:8px 0;">
                <div class="result-metric"><div class="label">Total Tracked</div><div class="value">₹{s['total_tracked']:,}</div></div>
                <div class="result-metric"><div class="label">Daily Avg</div><div class="value">₹{s['avg_daily']:,}</div></div>
                <div class="result-metric"><div class="label">Next Week</div><div class="value">₹{s['prediction_next_week']:,}</div></div>
                <div class="result-metric"><div class="label">Days</div><div class="value">{s['days_tracked']}</div></div>
            </div>
        </div>"""
        return html

    elif ft == "ml_predict":
        html = f"""
        <div class="result-inline">
            <div style="font-weight:700;font-size:1rem;margin-bottom:8px;">🤖 ML Prediction</div>
            <div class="result-metric"><div class="label">Predicted Spend (Month {feature_data['month']})</div><div class="value">₹{feature_data['predicted_spend']:,}</div></div>
        </div>"""
        return html

    return ""


def execute_query(query: str, profile: dict | None = None) -> dict:
    """
    Main entry: detect intent → run features → generate LLM response.

    Returns:
        dict with: intent, confidence, response (text), feature_html (HTML cards or ""),
                   feature_data (raw dict or None)
    """
    if profile is None:
        profile = {
            "income_monthly": 15000,
            "monthly_expenses": 9000,
            "savings": 20000,
            "existing_debt_monthly_EMI": 0,
            "requested_loan_amount": 50000,
            "proposed_EMI": 2500,
            "expected_skill_earning_uplift_pct": 20,
            "emergency_fund_amount": 10000,
            "course_length_months": 6,
            "goals": [{"name": "Savings", "required_amount": 100000, "target_date": "2027-06"}],
        }

    intent, confidence = detect_intent(query)
    feature_data = None
    feature_html = ""
    context_for_llm = ""

    # ── Route to actual features ──────────────────────────────────
    if intent in ("budget", "loan_check", "risk", "goal"):
        feature_data = _try_smart_boardroom(profile, query)
        if feature_data:
            feature_html = _format_feature_result(feature_data)
            coord = feature_data["coordinator"]
            context_for_llm = (
                f"\n\n[LIVE ANALYSIS RESULTS]\n"
                f"Verdict: {feature_data['verdict']}\n"
                f"Budget: {feature_data['budget'].get('analysis', '')}\n"
                f"Risk: {feature_data['risk'].get('analysis', '')}\n"
                f"Recommendation: {coord.get('coordinator_recommendation', '')}\n"
            )

    elif intent == "scenario":
        feature_data = _try_decision_sim(query, profile)
        if feature_data:
            feature_html = _format_feature_result(feature_data)
            r = feature_data["result"]
            context_for_llm = (
                f"\n\n[DECISION SIMULATOR RESULTS]\n"
                f"Item: {feature_data['item']}, Cost: ₹{feature_data['cost']:,}\n"
                f"Affordability Score: {r['affordability_score']}/100\n"
                f"Verdict: {r['verdict']}\n"
                f"Monthly surplus: ₹{r['surplus']:,}, Time to absorb: {r['months_to_absorb']} months\n"
            )

    elif intent == "cashflow":
        feature_data = _try_cashflow_summary()
        if feature_data:
            feature_html = _format_feature_result(feature_data)
            context_for_llm = (
                f"\n\n[CASH FLOW DATA]\n"
                f"Balance: ₹{feature_data['balance']:,}\n"
                f"30-day inflow: ₹{feature_data['inflow_30d']:,}\n"
                f"30-day outflow: ₹{feature_data['outflow_30d']:,}\n"
                f"Predicted balance: ₹{feature_data['predicted']:,}\n"
            )

    elif intent == "ocr":
        feature_html = (
            '<div class="feature-card">'
            '<h5>📄 Bill Scanner Available</h5>'
            '<p>Navigate to the <strong>Bill Scanner</strong> page from the sidebar to upload and scan your receipts!</p>'
            '</div>'
        )

    # Also try spending prediction for budget/general queries
    if intent in ("budget", "general") and not feature_data:
        spending = _try_spending_prediction()
        if spending:
            feature_data = spending
            feature_html = _format_feature_result(spending)
            s = spending["summary"]
            context_for_llm = (
                f"\n\n[SPENDING ANALYSIS]\n"
                f"Total tracked: ₹{s['total_tracked']:,} over {s['days_tracked']} days\n"
                f"Daily average: ₹{s['avg_daily']:,}\n"
                f"Next week prediction: ₹{s['prediction_next_week']:,}\n"
                f"Insights: {' | '.join(s['insights'])}\n"
            )

    # ── Generate LLM response with context ────────────────────────
    system_prompt = get_system_prompt(intent)
    if context_for_llm:
        system_prompt += (
            "\n\nIMPORTANT: I have already run the analysis and the results are shown to the user. "
            "Reference these results in your response. Don't repeat the numbers verbatim — "
            "instead explain what they mean and give actionable advice."
        )

    enriched_query = query + context_for_llm
    response = call_groq(enriched_query, system_instruction=system_prompt, temperature=0.3)

    return {
        "intent": intent,
        "confidence": confidence,
        "response": response,
        "feature_html": feature_html,
        "feature_data": feature_data,
    }
