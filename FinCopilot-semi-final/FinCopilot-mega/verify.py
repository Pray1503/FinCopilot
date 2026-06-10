"""Quick verification script for all FinPilot modules."""
import sys
sys.path.insert(0, ".")

passed = 0
failed = 0

def check(name, fn):
    global passed, failed
    try:
        fn()
        print(f"  [PASS] {name}")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] {name}: {e}")
        failed += 1

print("=" * 50)
print("  FinPilot — Module Verification")
print("=" * 50)

check("Financial Engine", lambda: __import__("simulator.financial_engine", fromlist=["compute_scenario_matrices"]))
check("Decision Engine", lambda: __import__("simulator.decision_engine", fromlist=["simulate_purchase"]))
check("Intent Detection", lambda: __import__("copilot.intents", fromlist=["detect_intent"]))
check("Feature Map", lambda: __import__("copilot.feature_map", fromlist=["get_system_prompt"]))
check("Groq Client", lambda: __import__("services.groq_client", fromlist=["call_groq"]))
check("Copilot Service", lambda: __import__("services.copilot_service", fromlist=["process_query"]))
check("Boardroom Service", lambda: __import__("services.boardroom_service", fromlist=["run_boardroom"]))
check("Budget Analyst", lambda: __import__("agents.budget_analyst", fromlist=["run"]))
check("Risk Assessor", lambda: __import__("agents.risk_assessor", fromlist=["run"]))
check("Long-Term Planner", lambda: __import__("agents.long_term_planner", fromlist=["run"]))
check("Coordinator", lambda: __import__("agents.coordinator", fromlist=["run"]))
check("ML Predict", lambda: __import__("ml.predict", fromlist=["is_model_available"]))
check("Spending Predictor", lambda: __import__("ml.spending_predictor", fromlist=["SpendingPredictor"]))
check("Cashflow Engine", lambda: __import__("cashflow.engine", fromlist=["generate_cash_flow_data"]))
check("Shared Utils", lambda: __import__("shared", fromlist=["money"]))
check("Shared Theme", lambda: __import__("shared.theme", fromlist=["inject_global_css"]))

# Functional checks
from copilot.intents import detect_intent
intent, conf = detect_intent("should I take a loan?")
check(f"Intent 'loan' detection (got: {intent})", lambda: None if intent == "loan_check" else (_ for _ in ()).throw(ValueError(intent)))

from ml.predict import is_model_available
check("ML model loaded", lambda: None if is_model_available() else (_ for _ in ()).throw(ValueError("model not available")))

from simulator.decision_engine import simulate_purchase
r = simulate_purchase(15000, 25000, 9000, "Test", 5000, "Goal", 50000, 10000, 3000)
check(f"Decision simulation (score={r.get('affordability_score', '?')})", lambda: None if r.get("affordability_score") else (_ for _ in ()).throw(ValueError("no score")))

print("=" * 50)
print(f"  Results: {passed} passed, {failed} failed")
print("=" * 50)
