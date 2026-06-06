import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

# ==========================================
# MACHINE LEARNING ENGINE (Background Setup)
# ==========================================
def train_spending_model():
    """Trains a model on historical patterns to predict seasonal student/prop spending."""
    np.random.seed(42)
    records = []
    for _ in range(1000):
        month = np.random.randint(1, 13)
        is_exam = 1 if month in [5, 11] else 0
        is_fest = 1 if month in [10, 11, 12] else 0
        base_spend = 0.60 # assume base spending takes up ~60% of basic expenses on average
        
        # Add seasonal volatility factors
        variance = (is_exam * 0.15) + (is_fest * 0.25) + np.random.normal(0, 0.05)
        spend_ratio = base_spend + variance
        
        records.append({
            "month_of_year": month,
            "is_exam_month": is_exam,
            "is_festival_season": is_fest,
            "spend_ratio": max(0.40, min(0.95, spend_ratio))
        })
    df = pd.DataFrame(records)
    model = RandomForestRegressor(n_estimators=50, random_state=42)
    model.fit(df[["month_of_year", "is_exam_month", "is_festival_season"]], df["spend_ratio"])
    return model

# Pre-train the model
ml_spending_model = train_spending_model()


# ==========================================
# THE CORE SIMULATOR
# ==========================================
class UserFinancialSimulator:
    def __init__(self, income, current_savings, base_expenses):
        self.income = income
        self.current_savings = current_savings
        self.base_expenses = base_expenses
        self.static_surplus = income - base_expenses

    def analyze_purchase(self, item_name, cost, goal_name, goal_target, goal_current, goal_alloc):
        print(f"\n" + "="*50)
        print(f"📊 FINANCIAL IMPACT REPORT: SYSTEM ANALYSIS")
        print("="*50)
        
        # Step 1: Baseline Check
        print(f"• Baseline Monthly Surplus: ₹{self.static_surplus:,}")
        if self.static_surplus <= 0:
            print("\n❌ CRITICAL: Your fixed expenses equal or exceed your income.")
            print("You have no structural surplus to support discretionary purchases or savings.")
            return

        # Step 2: Affordability Score
        months_to_save = cost / self.static_surplus
        if months_to_save <= 1:
            score, verdict = 95, "🟢 HIGH AFFORDABILITY (Safe to buy today)"
        elif months_to_save <= 3:
            score, verdict = 75, "🟡 MODERATE AFFORDABILITY (Good, but plan ahead)"
        elif months_to_save <= 6:
            score, verdict = 45, "🟠 LOW AFFORDABILITY (Save up specifically for this first)"
        else:
            score, verdict = 20, "🔴 HIGH RISK (Significantly outside your current budget)"

        print(f"• Affordability Score for {item_name}: {score}/100")
        print(f"  Verdict: {verdict}")
        print(f"  Time required to absorb cost: {months_to_save:.2f} months")

        # Step 3: Goal Delay Calculation
        remaining_goal = goal_target - goal_current
        original_months = remaining_goal / goal_alloc
        freeze_months = cost / self.static_surplus
        new_months = original_months + freeze_months
        
        print(f"\n🎯 IMPACT ON YOUR GOAL [{goal_name.upper()}]:")
        print(f"  - Original Timeline: {original_months:.1f} months remaining")
        print(f"  - Financial Freeze Period: {freeze_months:.1f} months (diverting surplus to pay for {item_name})")
        print(f"  - Delayed Timeline: {new_months:.1f} months to reach goal (+{freeze_months:.1f} month delay)")

        # Step 4, 5 & 6: 12-Month Projections (Static vs. ML-Dynamic)
        print(f"\n📈 12-MONTH SAVINGS TRACKER PROJECTION:")
        print(f"{'Month':<8}{'Control (Don\'t Buy)':<22}{'Static (Buy Now)':<20}{'ML-Dynamic Prediction (Buy Now)':<20}")
        print("-" * 75)
        
        current_control = self.current_savings
        current_static = self.current_savings - cost
        current_dynamic = self.current_savings - cost
        
        # Start tracking from current real-world calendar month
        start_month = 6 # June
        
        for m in range(1, 13):
            future_month = (start_month + m - 1) % 12 + 1
            is_exam = 1 if future_month in [5, 11] else 0
            is_fest = 1 if future_month in [10, 11, 12] else 0
            
            # Static calculations
            current_control += self.static_surplus
            current_static += self.static_surplus
            
            # ML Dynamic calculations (Predicting seasonal overhead adjustments)
            feat_df = pd.DataFrame([{"month_of_year": future_month, "is_exam_month": is_exam, "is_festival_season": is_fest}])
            predicted_ratio = ml_spending_model.predict(feat_df)[0]
            
            # Dynamic expenses scale up based on model prediction ratios
            dynamic_expense = self.base_expenses * (predicted_ratio / 0.60)
            dynamic_surplus = self.income - dynamic_expense
            current_dynamic += dynamic_surplus
            
            # Tag context milestones visually in the loop
            tag = ""
            if is_exam: tag = "📝 (Exams)"
            if is_fest: tag = "🎉 (Festivals)"
            
            print(f"Month {m:<3}{'₹'+f'{int(current_control):,}':<22}{'₹'+f'{int(current_static):,}':<20}{'₹'+f'{int(current_dynamic):,}':<20}{tag}")


# ==========================================
# INTERACTIVE USER INTERFACE CONSOLE
# ==========================================
def run_interactive_simulator():
    print("="*60)
    print("      Welcome to the Financial Decision Simulator Engine")
    print("="*60)
    print("Please enter your financial information below (numbers only):")
    
    try:
        # User Income Profile
        income = float(input("💰 Your Monthly Net Income (e.g., 15000): "))
        base_expenses = float(input("🏠 Total Fixed Monthly Expenses - Rent/Food (e.g., 9000): "))
        current_savings = float(input("🏦 Total Cash Savings Balance Right Now (e.g., 25000): "))
        
        print("\n🛍️ WHAT DO YOU WANT TO BUY?")
        item_name = input("Target Purchase Item Name (e.g., AirPods): ")
        purchase_cost = float(input(f"Total Cost of {item_name} (e.g., 20000): "))
        
        print("\n🎯 WHAT IS YOUR PRIMARY FINANCIAL GOAL?")
        goal_name = input("Goal Name (e.g., Laptop / Emergency Fund): ")
        goal_target = float(input(f"Target Cost/Amount for {goal_name}: "))
        goal_current = float(input(f"How much have you already saved specifically for {goal_name}?: "))
        goal_alloc = float(input(f"How much of your surplus do you add to {goal_name} monthly?: "))
        
        # Validation checks
        if goal_alloc > (income - base_expenses):
            print("\n⚠️ Warning: Your allocated goal savings amount is higher than your actual surplus.")
            print("Readjusting allocation to match maximum available surplus.")
            goal_alloc = max(1.0, income - base_expenses)

        # Execute calculations
        simulator = UserFinancialSimulator(income, current_savings, base_expenses)
        simulator.analyze_purchase(item_name, purchase_cost, goal_name, goal_target, goal_current, goal_alloc)
        
    except ValueError:
        print("\n❌ Input Error: Please enter valid numbers for financial metrics.")

if __name__ == "__main__":
    run_interactive_simulator()