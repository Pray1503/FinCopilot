"""
ml/spending_predictor.py
────────────────────────
Student spending habit analysis engine.
Ported from FinCopilot-feature-raj/spending_prediction.

Loads a CSV of student spending data and provides:
  1. Next-week spending prediction via Linear Regression
  2. Behavioral insights (weekend burn rate, top category)
"""

import os
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


class SpendingPredictor:
    """Analyse student spending data and predict future patterns."""

    def __init__(self, csv_filepath: str):
        self.csv_filepath = csv_filepath
        self.df = self._load_and_prepare()

    def _load_and_prepare(self) -> pd.DataFrame:
        """Load CSV and engineer date features."""
        if not os.path.exists(self.csv_filepath):
            raise FileNotFoundError(
                f"Missing dataset at: '{os.path.abspath(self.csv_filepath)}'\n"
                f"Run the app once to auto-generate sample data."
            )
        df = pd.read_csv(self.csv_filepath)
        df["date"] = pd.to_datetime(df["date"])
        df["amount"] = pd.to_numeric(df["amount"])
        df["week_index"] = df["date"].dt.isocalendar().week
        df["day_of_week"] = df["date"].dt.weekday
        return df

    def predict_next_week(self) -> float:
        """Predict total spending for the next 7 days via Linear Regression."""
        weekly = self.df.groupby("week_index")["amount"].sum().reset_index()
        if len(weekly) < 2:
            daily_avg = self.df["amount"].sum() / max(1, self.df["date"].nunique())
            return round(daily_avg * 7, 2)

        X = np.array(range(len(weekly))).reshape(-1, 1)
        y = weekly["amount"].values
        model = LinearRegression().fit(X, y)
        predicted = model.predict([[len(weekly)]])[0]
        return max(0.0, round(predicted, 2))

    def get_insights(self) -> list[str]:
        """Generate behavioral insights from spending patterns."""
        insights = []

        # Weekend burn rate
        weekend_mask = self.df["day_of_week"].isin([4, 5, 6])
        weekend_total = self.df[weekend_mask]["amount"].sum()
        weekday_total = self.df[~weekend_mask]["amount"].sum()
        weekend_days = max(1, self.df[weekend_mask]["date"].nunique())
        weekday_days = max(1, self.df[~weekend_mask]["date"].nunique())
        daily_weekend = weekend_total / weekend_days
        daily_weekday = weekday_total / weekday_days

        if daily_weekend > (daily_weekday * 1.25):
            spike = int(((daily_weekend - daily_weekday) / daily_weekday) * 100)
            insights.append(
                f"🚨 **Weekend Burn Alert:** You spend **{spike}% more** per day on "
                f"weekends (₹{round(daily_weekend)}/ day) vs weekdays (₹{round(daily_weekday)}/day)."
            )

        # Top spending category
        if "category" in self.df.columns:
            category_totals = self.df.groupby("category")["amount"].sum()
            if not category_totals.empty:
                top_cat = category_totals.idxmax()
                top_amt = category_totals.max()
                total = self.df["amount"].sum()
                pct = int((top_amt / total) * 100)
                insights.append(
                    f"💡 **Top Category:** **{top_cat}** takes up "
                    f"**{pct}%** of total expenses (₹{round(top_amt)})."
                )

        # Daily trend
        daily = self.df.groupby(self.df["date"].dt.date)["amount"].sum()
        if len(daily) >= 7:
            recent_avg = daily.tail(7).mean()
            older_avg = daily.head(7).mean()
            if recent_avg > older_avg * 1.15:
                insights.append(
                    f"📈 **Spending is trending up:** Recent 7-day average "
                    f"(₹{round(recent_avg)}/day) is higher than your earlier average (₹{round(older_avg)}/day)."
                )

        if not insights:
            insights.append("✅ Your spending patterns look consistent — keep it up!")

        return insights

    def get_summary(self) -> dict:
        """Return a summary dict of spending analysis."""
        total = self.df["amount"].sum()
        avg_daily = total / max(1, self.df["date"].nunique())
        return {
            "total_tracked": round(total),
            "days_tracked": int(self.df["date"].nunique()),
            "avg_daily": round(avg_daily),
            "prediction_next_week": self.predict_next_week(),
            "insights": self.get_insights(),
        }
