"""
cashflow/engine.py
──────────────────
Cash-flow data generation and chart builders.
Ported from FinCopilot-cash-flow-atif with ₹ standardisation.
"""

from __future__ import annotations
from datetime import date, timedelta
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# ── Colours ──────────────────────────────────────────────────────────────────
INDIGO = "#818cf8"
EMERALD = "#34d399"
AMBER = "#fbbf24"
RED = "#f87171"
SURFACE = "#111827"
LINE = "#1f2937"
TEXT = "#e5e7eb"


def generate_cash_flow_data(
    income: float = 42000,
    expenses: float = 34500,
    savings: float = 1260000,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Generate synthetic historical + forecasted cash-flow data.
    
    Uses the user's profile numbers as the base for realistic generation:
    - income → daily inflow mean
    - expenses → daily outflow mean
    - savings → starting balance
    """
    rng = np.random.default_rng(7)
    start = pd.Timestamp(date.today() - timedelta(days=150))
    hist_dates = pd.date_range(start, periods=151, freq="D")

    # Scale daily values from monthly profile (income/30, expenses/30)
    daily_income = income / 30
    daily_expense = expenses / 30

    inflow = rng.normal(daily_income * 30, daily_income * 4, len(hist_dates)).clip(daily_income * 18, daily_income * 48)
    outflow = rng.normal(daily_expense * 30, daily_expense * 5, len(hist_dates)).clip(daily_expense * 16, daily_expense * 42)
    seasonal = (daily_income * 3.5) * np.sin(np.linspace(0, 4.6 * np.pi, len(hist_dates)))
    net = inflow - outflow + seasonal
    balance = savings + np.cumsum(net)
    historical = pd.DataFrame({
        "date": hist_dates,
        "inflow": inflow,
        "outflow": outflow,
        "net_cash_flow": net,
        "balance": balance,
        "type": "Historical",
    })

    future_dates = pd.date_range(hist_dates[-1] + pd.Timedelta(days=1), periods=45, freq="D")
    drift = np.linspace(net[-1], daily_income * 8, len(future_dates))
    noise = rng.normal(0, daily_income * 1.5, len(future_dates))
    forecast_net = drift + noise
    forecast_balance = balance[-1] + np.cumsum(forecast_net)
    confidence = np.linspace(daily_income * 15, daily_income * 75, len(future_dates))
    forecast = pd.DataFrame({
        "date": future_dates,
        "inflow": rng.normal(daily_income * 32, daily_income * 3, len(future_dates)).clip(daily_income * 22, daily_income * 48),
        "outflow": rng.normal(daily_expense * 28, daily_expense * 3, len(future_dates)).clip(daily_expense * 16, daily_expense * 38),
        "net_cash_flow": forecast_net,
        "balance": forecast_balance,
        "lower": forecast_balance - confidence,
        "upper": forecast_balance + confidence,
        "type": "Predicted",
    })
    return historical, forecast


def generate_transactions(
    income: float = 42000,
    expenses: float = 34500,
    savings: float = 1260000,
) -> pd.DataFrame:
    """Generate synthetic transaction data based on user profile."""
    rng = np.random.default_rng(9)
    categories = ["Housing", "Food", "Transport", "Utilities", "Entertainment", "Healthcare", "Payroll", "Investments", "Software"]
    descriptions = {
        "Housing": "Rent payment", "Food": "Groceries & dining", "Transport": "Travel & fuel",
        "Utilities": "Electricity & internet", "Entertainment": "Subscriptions", "Healthcare": "Medical expenses",
        "Payroll": "Salary credit", "Investments": "SIP / FD returns", "Software": "SaaS tools",
    }
    rows = []
    balance = float(savings)
    income_scale = income / 15000  # scale relative to base profile
    for day in pd.date_range(date.today() - timedelta(days=120), periods=120, freq="D"):
        category = rng.choice(categories, p=[0.12, 0.12, 0.08, 0.1, 0.08, 0.06, 0.2, 0.12, 0.12])
        is_income = category in ["Payroll", "Investments"] or rng.random() < 0.18
        amount = float(rng.normal(income * 0.85, income * 0.25) if is_income else -rng.normal(expenses * 0.55, expenses * 0.22))
        balance += amount
        rows.append({
            "Date": day.date(), "Category": category, "Description": descriptions[category],
            "Amount": round(amount, 2), "Type": "Income" if amount >= 0 else "Expense",
            "Balance": round(balance, 2),
        })
    return pd.DataFrame(rows).sort_values("Date", ascending=False)


def cash_flow_chart(historical: pd.DataFrame, forecast: pd.DataFrame, granularity: str = "Daily") -> go.Figure:
    """Build the main cash-flow trend chart."""
    freq_map = {"Daily": "D", "Weekly": "W", "Monthly": "ME", "Yearly": "YE"}
    freq = freq_map.get(granularity, "D")
    hist = historical.set_index("date").resample(freq).agg({"balance": "last"}).dropna().reset_index()
    pred = forecast.set_index("date").resample(freq).agg({"balance": "last", "lower": "last", "upper": "last"}).dropna().reset_index()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hist["date"], y=hist["balance"], name="Historical", line=dict(color=INDIGO, width=3)))
    fig.add_trace(go.Scatter(x=pred["date"], y=pred["upper"], name="Confidence high", line=dict(width=0), hoverinfo="skip", showlegend=False))
    fig.add_trace(go.Scatter(x=pred["date"], y=pred["lower"], name="Confidence band", line=dict(width=0), fill="tonexty", fillcolor="rgba(129,140,248,0.14)", hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=pred["date"], y=pred["balance"], name="Predicted", line=dict(color=EMERALD, width=3, dash="dash")))
    fig.update_layout(
        height=430, margin=dict(l=8, r=8, t=8, b=12),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor=SURFACE,
        hovermode="x unified", font=dict(color=TEXT),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color=TEXT)),
        xaxis=dict(gridcolor=LINE, color=TEXT), yaxis=dict(gridcolor=LINE, tickprefix="₹", color=TEXT),
    )
    return fig


def gauge_chart(score: int) -> go.Figure:
    """Build a financial health gauge chart."""
    if score >= 85:
        label, color = "Excellent", EMERALD
    elif score >= 70:
        label, color = "Good", INDIGO
    elif score >= 50:
        label, color = "Average", AMBER
    else:
        label, color = "Risky", RED

    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=score,
        number={"suffix": "/100", "font": {"size": 38, "color": TEXT}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 0, "tickcolor": "rgba(0,0,0,0)"},
            "bar": {"color": color, "thickness": 0.28}, "bgcolor": LINE, "borderwidth": 0,
            "steps": [
                {"range": [0, 50], "color": "rgba(248,113,113,0.10)"},
                {"range": [50, 70], "color": "rgba(251,191,36,0.12)"},
                {"range": [70, 85], "color": "rgba(129,140,248,0.12)"},
                {"range": [85, 100], "color": "rgba(52,211,153,0.12)"},
            ],
        },
        title={"text": f"<b>{label}</b>", "font": {"size": 16, "color": TEXT}},
    ))
    fig.update_layout(height=320, margin=dict(l=6, r=6, t=24, b=8), paper_bgcolor="rgba(0,0,0,0)")
    return fig
