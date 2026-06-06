import os
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

class StudentWealthCoachEngine:
    def __init__(self, csv_filepath):
        self.csv_filepath = csv_filepath
        self.df = self.load_and_prepare_data()

    def load_and_prepare_data(self):
        """Loads dataset from CSV and engineers date/time dimensions."""
        if not os.path.exists(self.csv_filepath):
            raise FileNotFoundError(
                f"Missing dataset! Looked for it at: '{os.path.abspath(self.csv_filepath)}'\n"
                f"Please make sure the file is named correctly inside that folder."
            )
        
        # Load data
        df = pd.read_csv(self.csv_filepath)
        
        # Clean and match exact datatypes
        df['date'] = pd.to_datetime(df['date'])
        df['amount'] = pd.to_numeric(df['amount'])
        
        # Extract features for time-series and pattern recognition
        df['week_index'] = df['date'].dt.isocalendar().week
        df['day_of_week'] = df['date'].dt.weekday  # 0=Monday, 6=Sunday
        return df

    def predict_next_week_spending(self):
        """
        Groups data chronologically by week and trains a Linear Regression
        model to forecast the total spending for the upcoming 7-day period.
        """
        weekly_totals = self.df.groupby('week_index')['amount'].sum().reset_index()
        
        if len(weekly_totals) < 2:
            daily_avg = self.df['amount'].sum() / max(1, self.df['date'].nunique())
            return round(daily_avg * 7, 2)
            
        X = np.array(range(len(weekly_totals))).reshape(-1, 1)
        y = weekly_totals['amount'].values
        
        model = LinearRegression()
        model.fit(X, y)
        
        next_week_id = np.array([[len(weekly_totals)]])
        predicted_value = model.predict(next_week_id)[0]
        
        return max(0.0, round(predicted_value, 2))

    def generate_behavioral_insights(self):
        """Analyzes student spending data patterns to extract dynamic warnings."""
        insights = []
        
        # 1. Weekend Burn Rate Evaluation (Friday, Saturday, Sunday)
        weekend_mask = self.df['day_of_week'].isin([4, 5, 6])
        
        weekend_total = self.df[weekend_mask]['amount'].sum()
        weekday_total = self.df[~weekend_mask]['amount'].sum()
        
        weekend_days = max(1, self.df[weekend_mask]['date'].nunique())
        weekday_days = max(1, self.df[~weekend_mask]['date'].nunique())
        
        daily_weekend_avg = weekend_total / weekend_days
        daily_weekday_avg = weekday_total / weekday_days
        
        if daily_weekend_avg > (daily_weekday_avg * 1.25):
            spike_percentage = int(((daily_weekend_avg - daily_weekday_avg) / daily_weekday_avg) * 100)
            insights.append(
                f"🚨 **Weekend Burn Alert:** You spend **{spike_percentage}% more** cash per day on weekends "
                f"(₹{round(daily_weekend_avg, 2)}/day) compared to your weekdays (₹{round(daily_weekday_avg, 2)}/day)."
            )
            
        # 2. Main Budget Drainer Identification
        category_breakdown = self.df.groupby('category')['amount'].sum()
        if not category_breakdown.empty:
            top_category = category_breakdown.idxmax()
            top_amount = category_breakdown.max()
            total_expenses = self.df['amount'].sum()
            ratio_pct = int((top_amount / total_expenses) * 100)
            
            insights.append(
                f"💡 **Top Habit Category:** **{top_category}** represents your biggest drain, taking up "
                f"**{ratio_pct}%** of your total tracked expenses (₹{round(top_amount, 2)} total)."
            )
            
        return insights

# =====================================================================
# RUNNING THE BACKEND ENGINE WITH THE RELATIVE PATH
# =====================================================================
if __name__ == "__main__":
    # Points to parent directory's 'data' folder
    CSV_FILE = os.path.join("data", "student_spending.csv")
    
    print(f"⏳ Initializing AI Wealth Coach engine using data from: {CSV_FILE}")
    try:
        coach = StudentWealthCoachEngine(CSV_FILE)
        
        # Process Machine Learning Predictions & Insights
        forecasted_amount = coach.predict_next_week_spending()
        active_insights = coach.generate_behavioral_insights()
        
        # Output Dashboard
        print("\n" + "="*50)
        print("    🇮🇳 STUDENT AI WEALTH COACH - INR HABIT ENGINE")
        print("="*50)
        print(f"🔮 Predicted Budget Needed Next 7 Days : ₹{forecasted_amount}")
        print("-"*50)
        print("📋 DYNAMIC COACH INSIGHTS FOR THE STUDENT:")
        for idx, insight in enumerate(active_insights, 1):
            print(f" {idx}. {insight}")
        print("="*50 + "\n")
        
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")