"""
Page 4 — Cash Flow Dashboard
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Interactive cash-flow monitoring, forecasting, budgets, and scenario analysis.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from datetime import date
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from shared.theme import inject_global_css, render_brand_sidebar
from shared import money
from cashflow.engine import (
    generate_cash_flow_data, generate_transactions,
    cash_flow_chart, gauge_chart,
    INDIGO, EMERALD, AMBER, RED, SURFACE, LINE, TEXT,
)

st.set_page_config(page_title="Cash Flow • FinPilot", page_icon="💰", layout="wide")
st.markdown(inject_global_css(), unsafe_allow_html=True)
render_brand_sidebar(st)

st.markdown(
    """
    <div style="padding:1.5rem 0 0.5rem;">
        <h1 style="font-size:2.2rem;font-weight:800;margin:0;
            background:linear-gradient(135deg,#34d399,#fbbf24);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
            💰 Cash Flow Dashboard
        </h1>
        <p style="color:#9ca3af;font-size:0.95rem;margin-top:6px;">
            Monitor, forecast, and stress-test your financial future.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Data ──────────────────────────────────────────────────────────────────
historical, forecast = generate_cash_flow_data()
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🔮 Forecasting", "📋 Transactions", "🎛️ Scenario Analysis"])

# ═══════════════════════ TAB 1 — Dashboard ═══════════════════════════════
with tab1:
    balance = historical["balance"].iloc[-1]
    inflow_30 = historical.tail(30)["inflow"].sum()
    outflow_30 = historical.tail(30)["outflow"].sum()
    predicted = forecast.tail(30)["balance"].iloc[-1]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Current Balance", money(balance), "↗ 8.4%")
    c2.metric("30-Day Inflow", money(inflow_30), "↗ 12.2%")
    c3.metric("30-Day Outflow", money(outflow_30), "↘ 4.7%")
    c4.metric("Predicted Balance", money(predicted), "94% confidence")

    left, right = st.columns([1.75, 1])
    with left:
        st.markdown("<div class='mega-card'>", unsafe_allow_html=True)
        period = st.segmented_control("Period", ["Daily", "Weekly", "Monthly", "Yearly"], default="Daily", label_visibility="collapsed")
        st.plotly_chart(cash_flow_chart(historical, forecast, period), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with right:
        st.markdown("<div class='mega-card'>", unsafe_allow_html=True)
        st.markdown("<div style='font-weight:700;color:#e5e7eb;margin-bottom:4px;'>Financial Health Score</div>", unsafe_allow_html=True)
        st.plotly_chart(gauge_chart(86), use_container_width=True)
        m1, m2 = st.columns(2)
        m1.metric("Runway", "8.7 mo", "+0.8")
        m2.metric("Burn Ratio", "0.74", "-3.1%")
        st.markdown("</div>", unsafe_allow_html=True)

# ═══════════════════════ TAB 2 — Forecasting ═════════════════════════════
with tab2:
    c1, c2, c3 = st.columns(3)
    horizon = c1.selectbox("Forecast Horizon", ["1 Month", "3 Months", "6 Months", "1 Year"], index=1)
    scenario_type = c2.selectbox("Scenario", ["Conservative", "Normal", "Aggressive"], index=1)
    inflation = c3.toggle("Inflation Adjustment", value=True)

    multiplier = {"Conservative": 0.92, "Normal": 1.0, "Aggressive": 1.1}[scenario_type]
    months = {"1 Month": 1, "3 Months": 3, "6 Months": 6, "1 Year": 12}[horizon]
    x = pd.date_range(date.today(), periods=months * 4 + 1, freq="W")
    revenue = np.linspace(132000, 154000 * multiplier, len(x))
    expenses_arr = np.linspace(96000, 102000 * (1.04 if inflation else 1), len(x))
    position = historical["balance"].iloc[-1] + np.cumsum(revenue - expenses_arr) / 4

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=revenue, name="Predicted Revenue", line=dict(color=EMERALD, width=3)))
    fig.add_trace(go.Scatter(x=x, y=expenses_arr, name="Predicted Expenses", line=dict(color=RED, width=3)))
    fig.add_trace(go.Scatter(x=x, y=position, name="Cash Position", line=dict(color=INDIGO, width=3)))
    fig.update_layout(
        height=430, margin=dict(l=8, r=8, t=20, b=12),
        hovermode="x unified", yaxis=dict(tickprefix="₹", color=TEXT, gridcolor=LINE),
        xaxis=dict(color=TEXT, gridcolor=LINE),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor=SURFACE, font=dict(color=TEXT),
    )
    st.plotly_chart(fig, use_container_width=True)

    a, b, c = st.columns(3)
    cases = [
        ("Best Case", position[-1] * 1.12, "31%"),
        ("Expected Case", position[-1], "54%"),
        ("Worst Case", position[-1] * 0.84, "15%"),
    ]
    for col, (name, amt, prob) in zip([a, b, c], cases):
        with col:
            st.markdown(
                f"""
                <div class="mega-card" style="text-align:center;padding:20px;">
                    <div style="color:#6b7280;font-size:0.8rem;text-transform:uppercase;font-weight:700;">{name}</div>
                    <div style="font-size:1.4rem;font-weight:800;color:#f3f4f6;margin:8px 0;">{money(amt)}</div>
                    <div style="color:#9ca3af;font-size:0.82rem;">{prob} probability</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

# ═══════════════════════ TAB 3 — Transactions ════════════════════════════
with tab3:
    txn = generate_transactions()
    c1, c2 = st.columns([2, 1])
    search = c1.text_input("Search Transactions", placeholder="Category, description...")
    type_filter = c2.multiselect("Type", ["Income", "Expense"], default=["Income", "Expense"])

    filtered = txn[txn["Type"].isin(type_filter)]
    if search:
        mask = filtered.astype(str).apply(lambda col: col.str.contains(search, case=False, na=False)).any(axis=1)
        filtered = filtered[mask]

    st.dataframe(filtered, use_container_width=True, height=400, hide_index=True)

# ═══════════════════════ TAB 4 — Scenario Analysis ═══════════════════════
with tab4:
    c1, c2, c3, c4 = st.columns(4)
    rev_up = c1.slider("Revenue ↑ %", 0, 40, 12)
    rev_down = c2.slider("Revenue ↓ %", 0, 40, 4)
    exp_up = c3.slider("Expense ↑ %", 0, 35, 8)
    exp_down = c4.slider("Expense ↓ %", 0, 35, 5)

    x = pd.date_range(date.today(), periods=32, freq="W")
    rev = np.linspace(118000, 149000 * (1 + rev_up / 100 - rev_down / 100), len(x))
    exp = np.linspace(87000, 101000 * (1 + exp_up / 100 - exp_down / 100), len(x))
    pos = historical["balance"].iloc[-1] + np.cumsum(rev - exp) / 4
    risk_score = int(np.clip(100 - ((exp[-1] / max(rev[-1], 1)) * 70) + (pos[-1] / 300000), 18, 96))

    left, right = st.columns([1.7, 1])
    with left:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x, y=pos, name="Cash Position", line=dict(color=INDIGO, width=3), fill="tozeroy", fillcolor="rgba(129,140,248,0.08)"))
        fig.add_trace(go.Scatter(x=x, y=rev, name="Revenue", line=dict(color=EMERALD, width=2)))
        fig.add_trace(go.Scatter(x=x, y=exp, name="Expenses", line=dict(color=RED, width=2)))
        fig.update_layout(
            height=420, margin=dict(l=8, r=8, t=12, b=8),
            yaxis=dict(tickprefix="₹", color=TEXT, gridcolor=LINE),
            xaxis=dict(color=TEXT, gridcolor=LINE),
            hovermode="x unified",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor=SURFACE, font=dict(color=TEXT),
        )
        st.plotly_chart(fig, use_container_width=True)
    with right:
        st.plotly_chart(gauge_chart(risk_score), use_container_width=True)
        st.metric("Ending Cash Position", money(pos[-1]), f"{risk_score}% health score")
