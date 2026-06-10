"""
Page 7 — Spending Predictor
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Analyse student spending habits and predict next week's budget.
"""

import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from shared.theme import inject_global_css, render_brand_sidebar
from shared import money

st.set_page_config(page_title="Spending Predictor • FinPilot", page_icon="📈", layout="wide")
st.markdown(inject_global_css(), unsafe_allow_html=True)
render_brand_sidebar(st)

st.markdown(
    """
    <div style="padding:1.5rem 0 0.5rem;">
        <h1 style="font-size:2.2rem;font-weight:800;margin:0;
            background:linear-gradient(135deg,#f472b6,#fbbf24);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
            📈 Spending Predictor
        </h1>
        <p style="color:#9ca3af;font-size:0.95rem;margin-top:6px;">
            Analyse your spending habits — identify weekend burns, top categories, and predict next week's budget.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Data path ─────────────────────────────────────────────────────────────
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CSV_PATH = DATA_DIR / "student_spending.csv"


def generate_sample_data():
    """Generate synthetic student spending data if CSV doesn't exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(42)
    categories = ["Food", "Transport", "Shopping", "Entertainment", "Education", "Utilities"]
    rows = []
    base_date = pd.Timestamp.today() - pd.Timedelta(days=90)
    for i in range(90):
        day = base_date + pd.Timedelta(days=i)
        n_txn = rng.integers(1, 5)
        for _ in range(n_txn):
            cat = rng.choice(categories, p=[0.30, 0.15, 0.20, 0.12, 0.13, 0.10])
            base = {"Food": 250, "Transport": 150, "Shopping": 800, "Entertainment": 400, "Education": 500, "Utilities": 300}[cat]
            # Weekend spike
            if day.weekday() >= 4:
                base *= 1.35
            amount = max(50, round(rng.normal(base, base * 0.3)))
            rows.append({"date": day.strftime("%Y-%m-%d"), "category": cat, "amount": amount})
    pd.DataFrame(rows).to_csv(CSV_PATH, index=False)


# ── Auto-generate sample data ────────────────────────────────────────────
if not CSV_PATH.exists():
    generate_sample_data()
    st.markdown(
        "<div class='info-box'>📊 Generated 90 days of synthetic spending data for demonstration.</div>",
        unsafe_allow_html=True,
    )

# ── Load & Analyse ───────────────────────────────────────────────────────
try:
    from ml.spending_predictor import SpendingPredictor
    predictor = SpendingPredictor(str(CSV_PATH))
    summary = predictor.get_summary()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# ── Metrics ──────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Tracked", money(summary["total_tracked"]))
c2.metric("Days Tracked", f"{summary['days_tracked']}")
c3.metric("Daily Average", money(summary["avg_daily"]))
c4.metric("Next Week Prediction", money(summary["prediction_next_week"]))

# ── Insights ─────────────────────────────────────────────────────────────
st.markdown("### 🧠 AI Insights")
for insight in summary["insights"]:
    st.markdown(
        f"<div class='mega-card' style='padding:16px;min-height:auto;'><div style='color:#e5e7eb;font-size:0.92rem;'>{insight}</div></div>",
        unsafe_allow_html=True,
    )

# ── Charts ───────────────────────────────────────────────────────────────
df = predictor.df.copy()
col1, col2 = st.columns(2)

with col1:
    # Daily spending trend
    daily = df.groupby(df["date"].dt.date)["amount"].sum().reset_index()
    daily.columns = ["date", "amount"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily["date"], y=daily["amount"],
        mode="lines+markers", name="Daily Spend",
        line=dict(color="#818cf8", width=2), marker=dict(size=4),
    ))
    fig.update_layout(
        title="Daily Spending Trend", height=380,
        margin=dict(l=8, r=8, t=40, b=12),
        yaxis=dict(tickprefix="₹", color="#e5e7eb", gridcolor="#1f2937"),
        xaxis=dict(color="#e5e7eb", gridcolor="#1f2937"),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#111827",
        font=dict(color="#e5e7eb"),
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Category breakdown
    if "category" in df.columns:
        cat_totals = df.groupby("category")["amount"].sum().sort_values(ascending=True).reset_index()
        colors = ["#818cf8", "#34d399", "#fbbf24", "#f87171", "#a78bfa", "#06b6d4", "#f472b6", "#fb923c"]
        fig = go.Figure(go.Bar(
            x=cat_totals["amount"], y=cat_totals["category"],
            orientation="h", marker_color=colors[:len(cat_totals)],
        ))
        fig.update_layout(
            title="Spending by Category", height=380,
            margin=dict(l=8, r=8, t=40, b=12),
            xaxis=dict(tickprefix="₹", color="#e5e7eb", gridcolor="#1f2937"),
            yaxis=dict(color="#e5e7eb"),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#111827",
            font=dict(color="#e5e7eb"),
        )
        st.plotly_chart(fig, use_container_width=True)

# ── Weekday vs Weekend ───────────────────────────────────────────────────
st.markdown("### 📊 Weekday vs Weekend Comparison")
df["is_weekend"] = df["date"].dt.weekday >= 4
weekend_avg = df[df["is_weekend"]]["amount"].mean()
weekday_avg = df[~df["is_weekend"]]["amount"].mean()

c1, c2, c3 = st.columns(3)
c1.metric("Weekday Avg/Transaction", money(weekday_avg))
c2.metric("Weekend Avg/Transaction", money(weekend_avg))
diff_pct = round(((weekend_avg - weekday_avg) / weekday_avg) * 100, 1) if weekday_avg > 0 else 0
c3.metric("Weekend Premium", f"+{diff_pct}%" if diff_pct > 0 else f"{diff_pct}%")

# ── Upload custom data ───────────────────────────────────────────────────
with st.expander("📤 Upload Your Own Spending Data"):
    st.markdown(
        """
        Upload a CSV with columns: `date`, `category`, `amount`

        Example:
        ```
        date,category,amount
        2026-01-01,Food,350
        2026-01-01,Transport,120
        ```
        """
    )
    uploaded = st.file_uploader("Upload CSV", type=["csv"], key="sp_upload")
    if uploaded:
        try:
            custom_df = pd.read_csv(uploaded)
            custom_df.to_csv(CSV_PATH, index=False)
            st.success("Data uploaded! Refresh the page to see updated analysis.")
        except Exception as e:
            st.error(f"Error: {e}")
