from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

try:
    from streamlit_option_menu import option_menu
except Exception:  # pragma: no cover - graceful fallback for minimal installs
    option_menu = None


st.set_page_config(
    page_title="CashFlowAI",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)


NAV_ITEMS = [
    "Dashboard",
    "Forecasting",
    "Transactions",
    "Budget Planner",
    "Scenario Analysis",
    "Reports",
    "AI Insights",
    "Settings",
]

NAV_ICONS = [
    "speedometer2",
    "graph-up-arrow",
    "receipt",
    "wallet2",
    "sliders",
    "file-earmark-bar-graph",
    "stars",
    "gear",
]

PRIMARY = "#0F172A"
INDIGO = "#4F46E5"
EMERALD = "#10B981"
AMBER = "#F59E0B"
RED = "#EF4444"
LIGHT = "#F8FAFC"
MUTED = "#475569"


def inject_css() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        :root {
            --navy: #0F172A;
            --indigo: #4F46E5;
            --emerald: #10B981;
            --amber: #F59E0B;
            --red: #EF4444;
            --light: #F8FAFC;
            --muted: #475569;
            --line: #E2E8F0;
        }

        html, body, [class*="css"] {
            font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            color: var(--navy);
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(79, 70, 229, 0.10), transparent 28rem),
                linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 54%, #EEF2FF 100%);
        }

        [data-testid="stSidebar"] {
            background: #0F172A;
            border-right: 1px solid rgba(255, 255, 255, 0.08);
        }

        [data-testid="stSidebar"] * {
            color: #E5E7EB;
        }

        [data-testid="stSidebar"] .stSelectbox label,
        [data-testid="stSidebar"] .stRadio label {
            color: #E5E7EB !important;
        }

        .block-container {
            padding-top: 1.15rem;
            padding-bottom: 2.5rem;
            max-width: 1480px;
        }

        .app-logo {
            display: flex;
            align-items: center;
            gap: 0.7rem;
            padding: 0.45rem 0.25rem 1.1rem;
            color: #FFFFFF;
            font-weight: 800;
            font-size: 1.28rem;
            letter-spacing: 0;
        }

        .topbar {
            display: grid;
            grid-template-columns: 1fr auto auto;
            gap: 0.75rem;
            align-items: center;
            margin-bottom: 1.1rem;
        }

        .searchbox {
            min-height: 46px;
            display: flex;
            align-items: center;
            gap: 0.65rem;
            padding: 0 0.95rem;
            background: rgba(255, 255, 255, 0.88);
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            color: #64748B;
            box-shadow: 0 12px 32px rgba(15, 23, 42, 0.06);
        }

        .top-pill {
            min-height: 46px;
            display: inline-flex;
            align-items: center;
            gap: 0.55rem;
            padding: 0 0.9rem;
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            color: #334155;
            font-weight: 700;
            box-shadow: 0 12px 32px rgba(15, 23, 42, 0.06);
        }

        .page-title {
            margin: 0 0 0.25rem;
            color: #0F172A;
            font-size: clamp(1.8rem, 3vw, 2.75rem);
            line-height: 1.05;
            font-weight: 800;
            letter-spacing: 0;
        }

        .subtitle {
            margin: 0 0 1.1rem;
            color: #475569;
            font-size: 1rem;
            line-height: 1.45;
        }

        .metric-card, .panel, .mini-card, .budget-card, .alert-card, .report-card {
            position: relative;
            overflow: hidden;
            background: rgba(255, 255, 255, 0.92);
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            box-shadow: 0 18px 46px rgba(15, 23, 42, 0.08);
            transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
        }

        .metric-card:hover, .panel:hover, .mini-card:hover, .budget-card:hover, .alert-card:hover, .report-card:hover {
            transform: translateY(-2px);
            border-color: rgba(79, 70, 229, 0.32);
            box-shadow: 0 22px 58px rgba(15, 23, 42, 0.12);
        }

        .metric-card {
            min-height: 178px;
            padding: 1rem 1rem 0.45rem;
        }

        .metric-head {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 0.8rem;
        }

        .metric-icon {
            width: 42px;
            height: 42px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: 8px;
            background: #EEF2FF;
            color: #4F46E5;
            font-size: 1.2rem;
        }

        .metric-label {
            margin: 0;
            color: #64748B;
            font-size: 0.82rem;
            font-weight: 800;
            text-transform: uppercase;
        }

        .metric-value {
            margin: 0.42rem 0 0;
            color: #0F172A;
            font-size: clamp(1.45rem, 2.4vw, 2.05rem);
            font-weight: 800;
            line-height: 1.1;
        }

        .trend {
            display: inline-flex;
            align-items: center;
            gap: 0.3rem;
            padding: 0.32rem 0.52rem;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 800;
        }

        .trend.good { background: rgba(16, 185, 129, 0.10); color: #047857; }
        .trend.warn { background: rgba(245, 158, 11, 0.12); color: #B45309; }
        .trend.bad { background: rgba(239, 68, 68, 0.10); color: #B91C1C; }

        .panel {
            padding: 1rem;
            min-height: 380px;
        }

        .section-head {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 1rem;
            margin-bottom: 0.7rem;
        }

        .section-title {
            margin: 0;
            color: #0F172A;
            font-size: 1.03rem;
            font-weight: 800;
        }

        .section-note {
            color: #64748B;
            font-size: 0.82rem;
            font-weight: 700;
        }

        .mini-card, .budget-card, .alert-card, .report-card {
            padding: 1rem;
            min-height: 132px;
        }

        .mini-label {
            margin: 0 0 0.5rem;
            color: #64748B;
            font-size: 0.82rem;
            font-weight: 800;
            text-transform: uppercase;
        }

        .mini-value {
            color: #0F172A;
            font-size: 1.55rem;
            font-weight: 800;
        }

        .progress-track {
            width: 100%;
            height: 10px;
            border-radius: 999px;
            background: #E2E8F0;
            overflow: hidden;
            margin: 0.9rem 0 0.65rem;
        }

        .progress-fill {
            height: 100%;
            border-radius: 999px;
        }

        .chat-bubble {
            max-width: 900px;
            padding: 0.95rem 1rem;
            margin: 0 0 0.7rem;
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            box-shadow: 0 12px 32px rgba(15, 23, 42, 0.06);
        }

        .chat-bubble.ai {
            border-left: 4px solid #4F46E5;
        }

        .chip {
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            padding: 0.35rem 0.55rem;
            border-radius: 999px;
            background: #EEF2FF;
            color: #4338CA;
            font-size: 0.78rem;
            font-weight: 800;
        }

        .skeleton {
            min-height: 42px;
            border-radius: 8px;
            background: linear-gradient(90deg, #EEF2F7, #FFFFFF, #EEF2F7);
            background-size: 240% 100%;
            animation: shimmer 1.35s ease-in-out infinite;
        }

        @keyframes shimmer {
            0% { background-position: 100% 0; }
            100% { background-position: -100% 0; }
        }

        button[kind="primary"], .stButton > button {
            border-radius: 8px !important;
            min-height: 44px;
            border: 0 !important;
            background: #4F46E5 !important;
            color: #FFFFFF !important;
            font-weight: 800 !important;
            box-shadow: 0 14px 30px rgba(79, 70, 229, 0.22);
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 0.35rem;
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 8px;
            padding: 0.55rem 0.8rem;
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
        }

        [data-testid="stDataFrame"] {
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 18px 46px rgba(15, 23, 42, 0.06);
        }

        @media (max-width: 760px) {
            .topbar {
                grid-template-columns: 1fr;
            }
            .metric-card, .panel, .mini-card, .budget-card, .alert-card, .report-card {
                min-height: auto;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data
def cash_flow_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(7)
    start = pd.Timestamp(date.today() - timedelta(days=150))
    hist_dates = pd.date_range(start, periods=151, freq="D")

    inflow = rng.normal(4200, 520, len(hist_dates)).clip(2800, 6200)
    outflow = rng.normal(3450, 610, len(hist_dates)).clip(2100, 5600)
    seasonal = 520 * np.sin(np.linspace(0, 4.6 * np.pi, len(hist_dates)))
    net = inflow - outflow + seasonal
    balance = 126000 + np.cumsum(net)
    historical = pd.DataFrame(
        {
            "date": hist_dates,
            "inflow": inflow,
            "outflow": outflow,
            "net_cash_flow": net,
            "balance": balance,
            "type": "Historical",
        }
    )

    future_dates = pd.date_range(hist_dates[-1] + pd.Timedelta(days=1), periods=45, freq="D")
    drift = np.linspace(net[-1], 1180, len(future_dates))
    forecast_noise = rng.normal(0, 220, len(future_dates))
    forecast_net = drift + forecast_noise
    forecast_balance = balance[-1] + np.cumsum(forecast_net)
    confidence = np.linspace(2200, 10800, len(future_dates))
    forecast = pd.DataFrame(
        {
            "date": future_dates,
            "inflow": rng.normal(4550, 430, len(future_dates)).clip(3300, 6700),
            "outflow": rng.normal(3300, 420, len(future_dates)).clip(2200, 5200),
            "net_cash_flow": forecast_net,
            "balance": forecast_balance,
            "lower": forecast_balance - confidence,
            "upper": forecast_balance + confidence,
            "type": "Predicted",
        }
    )
    return historical, forecast


@st.cache_data
def transactions_data() -> pd.DataFrame:
    rng = np.random.default_rng(9)
    categories = ["Housing", "Food", "Transport", "Utilities", "Entertainment", "Healthcare", "Payroll", "Investments", "Software"]
    descriptions = {
        "Housing": "Office lease",
        "Food": "Team meals",
        "Transport": "Travel reimbursement",
        "Utilities": "Cloud and utilities",
        "Entertainment": "Client event",
        "Healthcare": "Benefits premium",
        "Payroll": "Payroll deposit",
        "Investments": "Treasury yield",
        "Software": "SaaS subscription",
    }
    rows = []
    balance = 226000.0
    for idx, day in enumerate(pd.date_range(date.today() - timedelta(days=120), periods=120, freq="D")):
        category = rng.choice(categories, p=[0.12, 0.12, 0.08, 0.1, 0.08, 0.06, 0.2, 0.12, 0.12])
        is_income = category in ["Payroll", "Investments"] or rng.random() < 0.18
        amount = float(rng.normal(12200, 3700) if is_income else -rng.normal(5200, 2100))
        balance += amount
        rows.append(
            {
                "Date": day.date(),
                "Category": category,
                "Description": descriptions[category],
                "Amount": round(amount, 2),
                "Type": "Income" if amount >= 0 else "Expense",
                "Balance": round(balance, 2),
            }
        )
    return pd.DataFrame(rows).sort_values("Date", ascending=False)


def money(value: float) -> str:
    symbol = "$"
    sign = "-" if value < 0 else ""
    return f"{sign}{symbol}{abs(value):,.0f}"


def topbar() -> None:
    st.markdown(
        """
        <div class="topbar" aria-label="Top navigation">
            <div class="searchbox" role="search">⌕ Search transactions, reports, budgets...</div>
            <div class="top-pill" title="Notifications">🔔 3 alerts</div>
            <div class="top-pill" title="User profile">Ava Patel ▾</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str) -> None:
    topbar()
    st.markdown(f"<h1 class='page-title'>{title}</h1><p class='subtitle'>{subtitle}</p>", unsafe_allow_html=True)


def plot_sparkline(values: np.ndarray, color: str) -> None:
    def transparent(hex_color: str, alpha: float = 0.12) -> str:
        stripped = hex_color.lstrip("#")
        red, green, blue = (int(stripped[idx : idx + 2], 16) for idx in (0, 2, 4))
        return f"rgba({red},{green},{blue},{alpha})"

    fig = go.Figure()
    fig.add_trace(go.Scatter(y=values, mode="lines", line=dict(color=color, width=2.4), fill="tozeroy", fillcolor=transparent(color)))
    fig.update_layout(
        height=62,
        margin=dict(l=0, r=0, t=4, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def metric_card(label: str, value: str, delta: str, trend: str, icon: str, spark: np.ndarray, color: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-head">
                <div>
                    <div class="metric-icon" aria-hidden="true">{icon}</div>
                    <p class="metric-label">{label}</p>
                    <p class="metric-value">{value}</p>
                </div>
                <span class="trend {trend}">{delta}</span>
            </div>
        """,
        unsafe_allow_html=True,
    )
    plot_sparkline(spark, color)
    st.markdown("</div>", unsafe_allow_html=True)


def cash_flow_chart(historical: pd.DataFrame, forecast: pd.DataFrame, granularity: str = "Daily") -> go.Figure:
    freq_map = {"Daily": "D", "Weekly": "W", "Monthly": "M", "Yearly": "Y"}
    freq = freq_map[granularity]
    hist = historical.set_index("date").resample(freq).agg({"balance": "last"}).dropna().reset_index()
    pred = forecast.set_index("date").resample(freq).agg({"balance": "last", "lower": "last", "upper": "last"}).dropna().reset_index()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hist["date"], y=hist["balance"], name="Historical cash flow", line=dict(color=INDIGO, width=3)))
    fig.add_trace(
        go.Scatter(
            x=pred["date"],
            y=pred["upper"],
            name="Confidence high",
            line=dict(width=0),
            hoverinfo="skip",
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=pred["date"],
            y=pred["lower"],
            name="Confidence band",
            line=dict(width=0),
            fill="tonexty",
            fillcolor="rgba(79,70,229,0.16)",
            hoverinfo="skip",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=pred["date"],
            y=pred["balance"],
            name="Predicted cash flow",
            line=dict(color=EMERALD, width=3, dash="dash"),
        )
    )
    fig.update_layout(
        height=430,
        margin=dict(l=8, r=8, t=8, b=12),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(248,250,252,0.7)",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(gridcolor="#E2E8F0"),
        yaxis=dict(gridcolor="#E2E8F0", tickprefix="$"),
    )
    return fig


def gauge(score: int) -> go.Figure:
    if score >= 85:
        label, color = "Excellent", EMERALD
    elif score >= 70:
        label, color = "Good", INDIGO
    elif score >= 50:
        label, color = "Average", AMBER
    else:
        label, color = "Risky", RED

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            number={"suffix": "/100", "font": {"size": 38, "color": PRIMARY}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 0, "tickcolor": "rgba(0,0,0,0)"},
                "bar": {"color": color, "thickness": 0.28},
                "bgcolor": "#E2E8F0",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 50], "color": "rgba(239,68,68,0.12)"},
                    {"range": [50, 70], "color": "rgba(245,158,11,0.16)"},
                    {"range": [70, 85], "color": "rgba(79,70,229,0.14)"},
                    {"range": [85, 100], "color": "rgba(16,185,129,0.14)"},
                ],
            },
            title={"text": f"<b>{label}</b>", "font": {"size": 16, "color": MUTED}},
        )
    )
    fig.update_layout(height=320, margin=dict(l=6, r=6, t=24, b=8), paper_bgcolor="rgba(0,0,0,0)")
    return fig


def dashboard_page() -> None:
    historical, forecast = cash_flow_data()
    page_header("Cash Flow Overview", "Monitor and predict your financial future.")

    balance = historical["balance"].iloc[-1]
    inflow = historical.tail(30)["inflow"].sum()
    outflow = historical.tail(30)["outflow"].sum()
    predicted = forecast.tail(30)["balance"].iloc[-1]

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Current Balance", money(balance), "↗ 8.4%", "good", "💳", historical.tail(24)["balance"].to_numpy(), INDIGO)
    with c2:
        metric_card("Monthly Inflow", money(inflow), "↗ 12.2%", "good", "⬇", historical.tail(24)["inflow"].to_numpy(), EMERALD)
    with c3:
        metric_card("Monthly Outflow", money(outflow), "↘ 4.7%", "warn", "⬆", historical.tail(24)["outflow"].to_numpy(), AMBER)
    with c4:
        metric_card("Predicted Next Month Balance", money(predicted), "94% confidence", "good", "✦", forecast.tail(24)["balance"].to_numpy(), EMERALD)

    left, right = st.columns([1.75, 1])
    with left:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        head_l, head_r = st.columns([1, 1])
        with head_l:
            st.markdown("<div class='section-title'>Cash Flow Trend Chart</div>", unsafe_allow_html=True)
        with head_r:
            period = st.segmented_control("Period", ["Daily", "Weekly", "Monthly", "Yearly"], default="Daily", label_visibility="collapsed")
        st.plotly_chart(cash_flow_chart(historical, forecast, period), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Financial Health Score</div><div class='section-note'>Liquidity, runway, debt load, and spend volatility</div>", unsafe_allow_html=True)
        st.plotly_chart(gauge(86), use_container_width=True)
        m1, m2 = st.columns(2)
        with m1:
            st.metric("Runway", "8.7 mo", "+0.8")
        with m2:
            st.metric("Burn Ratio", "0.74", "-3.1%")
        st.markdown("</div>", unsafe_allow_html=True)


def forecasting_page() -> None:
    historical, forecast = cash_flow_data()
    page_header("Forecasting", "Model revenue, expense, and cash position across planning horizons.")

    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns([1, 1, 0.9, 0.9, 1])
    with c1:
        horizon = st.selectbox("Forecast horizon", ["1 Month", "3 Months", "6 Months", "1 Year"], index=1)
    with c2:
        scenario = st.selectbox("Scenario type", ["Conservative", "Normal", "Aggressive"], index=1)
    with c3:
        inflation = st.toggle("Inflation adjustment", value=True)
    with c4:
        seasonality = st.toggle("Seasonality", value=True)
    with c5:
        st.write("")
        st.button("Generate Forecast", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    multiplier = {"Conservative": 0.92, "Normal": 1.0, "Aggressive": 1.1}[scenario]
    months = {"1 Month": 1, "3 Months": 3, "6 Months": 6, "1 Year": 12}[horizon]
    x = pd.date_range(date.today(), periods=months * 4 + 1, freq="W")
    revenue = np.linspace(132000, 154000 * multiplier, len(x))
    expenses = np.linspace(96000, 102000 * (1.04 if inflation else 1), len(x))
    if seasonality:
        revenue += 6000 * np.sin(np.linspace(0, months * np.pi / 2, len(x)))
        expenses += 3500 * np.cos(np.linspace(0, months * np.pi / 2, len(x)))
    position = historical["balance"].iloc[-1] + np.cumsum(revenue - expenses) / 4

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=revenue, name="Predicted Revenue", line=dict(color=EMERALD, width=3)))
    fig.add_trace(go.Scatter(x=x, y=expenses, name="Predicted Expenses", line=dict(color=RED, width=3)))
    fig.add_trace(go.Scatter(x=x, y=position, name="Predicted Cash Position", line=dict(color=INDIGO, width=3)))
    fig.update_layout(height=430, margin=dict(l=8, r=8, t=20, b=12), hovermode="x unified", yaxis=dict(tickprefix="$"), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor=LIGHT)
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Forecast Results</div>", unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    a, b, c = st.columns(3)
    summaries = [("Best Case", position[-1] * 1.12, "31%", "↗"), ("Expected Case", position[-1], "54%", "→"), ("Worst Case", position[-1] * 0.84, "15%", "↘")]
    for col, (name, amount, prob, arrow) in zip([a, b, c], summaries):
        with col:
            st.markdown(f"<div class='mini-card'><p class='mini-label'>{name}</p><div class='mini-value'>{money(amount)}</div><span class='trend good'>{arrow} {prob} probability</span></div>", unsafe_allow_html=True)


def transactions_page() -> None:
    df = transactions_data()
    page_header("Transactions", "Explore inflows, outflows, balances, and category-level activity.")

    f1, f2, f3 = st.columns([1.2, 1, 1])
    with f1:
        query = st.text_input("Search", placeholder="Category, description, type...")
    with f2:
        type_filter = st.multiselect("Type", ["Income", "Expense"], default=["Income", "Expense"])
    with f3:
        category_filter = st.multiselect("Category", sorted(df["Category"].unique()))

    filtered = df[df["Type"].isin(type_filter)]
    if category_filter:
        filtered = filtered[filtered["Category"].isin(category_filter)]
    if query:
        mask = filtered.astype(str).apply(lambda col: col.str.contains(query, case=False, na=False)).any(axis=1)
        filtered = filtered[mask]

    st.dataframe(filtered, use_container_width=True, height=390, hide_index=True)

    chart_df = df.copy()
    expense = chart_df[chart_df["Amount"] < 0].assign(AmountAbs=lambda data: data["Amount"].abs())
    income = chart_df[chart_df["Amount"] > 0]
    c1, c2, c3 = st.columns(3)
    with c1:
        fig = go.Figure(go.Pie(labels=expense["Category"], values=expense["AmountAbs"], hole=0.58, marker=dict(colors=[INDIGO, EMERALD, AMBER, RED, "#06B6D4", "#64748B"])))
        fig.update_layout(title="Spending by Category", height=330, margin=dict(l=8, r=8, t=40, b=8), paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = go.Figure(go.Pie(labels=income["Category"], values=income["Amount"], marker=dict(colors=[EMERALD, INDIGO, "#06B6D4"])))
        fig.update_layout(title="Income Sources", height=330, margin=dict(l=8, r=8, t=40, b=8), paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
    with c3:
        monthly = expense.assign(Date=pd.to_datetime(expense["Date"])).set_index("Date").resample("M")["AmountAbs"].sum().reset_index()
        fig = go.Figure(go.Bar(x=monthly["Date"], y=monthly["AmountAbs"], marker_color=INDIGO, name="Spend"))
        fig.update_layout(title="Monthly Spending Trend", height=330, margin=dict(l=8, r=8, t=40, b=8), yaxis=dict(tickprefix="$"), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor=LIGHT)
        st.plotly_chart(fig, use_container_width=True)


def budget_page() -> None:
    page_header("Budget Planner", "Track category limits, remaining budget, and overspend risk.")
    budgets = [
        ("Housing", 62000, 51000),
        ("Food", 22000, 19400),
        ("Transport", 16000, 9100),
        ("Utilities", 18000, 18750),
        ("Entertainment", 9000, 5600),
        ("Healthcare", 12000, 7200),
    ]
    cols = st.columns(3)
    for idx, (name, limit, spent) in enumerate(budgets):
        pct = min(spent / limit, 1.25)
        color = EMERALD if pct < 0.75 else AMBER if pct <= 1 else RED
        remaining = limit - spent
        with cols[idx % 3]:
            st.markdown(
                f"""
                <div class="budget-card">
                    <p class="mini-label">{name}</p>
                    <div class="metric-head"><div class="mini-value">{money(spent)}</div><span class="chip">{money(limit)} limit</span></div>
                    <div class="progress-track"><div class="progress-fill" style="width: {min(pct, 1) * 100:.1f}%; background: {color};"></div></div>
                    <div class="section-note">{money(remaining)} remaining</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def scenario_page() -> None:
    historical, _ = cash_flow_data()
    page_header("Scenario Analysis", "Stress-test cash flow with real-time planning controls.")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        revenue_up = st.slider("Revenue increase %", 0, 40, 12)
    with c2:
        revenue_down = st.slider("Revenue decrease %", 0, 40, 4)
    with c3:
        expense_up = st.slider("Expense increase %", 0, 35, 8)
    with c4:
        expense_down = st.slider("Expense decrease %", 0, 35, 5)

    x = pd.date_range(date.today(), periods=32, freq="W")
    revenue = np.linspace(118000, 149000 * (1 + revenue_up / 100 - revenue_down / 100), len(x))
    expenses = np.linspace(87000, 101000 * (1 + expense_up / 100 - expense_down / 100), len(x))
    position = historical["balance"].iloc[-1] + np.cumsum(revenue - expenses) / 4
    risk = int(np.clip(100 - ((expenses[-1] / max(revenue[-1], 1)) * 70) + (position[-1] / 30000), 18, 96))

    left, right = st.columns([1.7, 1])
    with left:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x, y=position, name="Ending cash position", line=dict(color=INDIGO, width=3), fill="tozeroy", fillcolor="rgba(79,70,229,0.12)"))
        fig.add_trace(go.Scatter(x=x, y=revenue, name="Revenue", line=dict(color=EMERALD, width=2)))
        fig.add_trace(go.Scatter(x=x, y=expenses, name="Expenses", line=dict(color=RED, width=2)))
        fig.update_layout(height=420, margin=dict(l=8, r=8, t=12, b=8), yaxis=dict(tickprefix="$"), hovermode="x unified", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor=LIGHT)
        st.plotly_chart(fig, use_container_width=True)
    with right:
        st.plotly_chart(gauge(risk), use_container_width=True)
        st.metric("Ending Cash Position", money(position[-1]), f"{risk}% risk score")


def ai_insights_page() -> None:
    page_header("AI Insights", "Prioritized recommendations, financial alerts, and optimization ideas.")
    st.markdown(
        """
        <div class="chat-bubble ai"><b>AI Recommendations</b><br>Reduce food expenses by 12% to free an estimated $2,640 this quarter without affecting core operations.</div>
        <div class="chat-bubble ai"><b>Savings Allocation</b><br>Move $18,000 from idle checking into a short-duration treasury ladder to increase monthly yield visibility.</div>
        <div class="chat-bubble ai"><b>Cash Shortage Watch</b><br>Expected cash pressure may appear in August if two large vendor renewals land in the same billing cycle.</div>
        """,
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns(3)
    alerts = [
        ("Unusual spending", "Cloud utilities are 18% above the 90-day average.", RED),
        ("Budget overruns", "Utilities exceeded the limit by $750 this month.", AMBER),
        ("Cash flow risks", "Receivable concentration is elevated for one client.", RED),
        ("Investment opportunities", "Excess cash can cover a 3-month treasury ladder.", EMERALD),
        ("Savings opportunities", "Annual SaaS prepay could save $4,200.", EMERALD),
        ("Expense optimization", "Travel spend has dropped enough to lower reserve targets.", INDIGO),
    ]
    for idx, (title, body, color) in enumerate(alerts):
        with [c1, c2, c3][idx % 3]:
            st.markdown(f"<div class='alert-card' style='border-top: 4px solid {color};'><p class='mini-label'>{title}</p><p class='subtitle'>{body}</p></div>", unsafe_allow_html=True)


def reports_page() -> None:
    page_header("Reports", "Export executive-ready financial reporting packages.")
    reports = ["Monthly Report", "Quarterly Report", "Annual Report", "Forecast Report"]
    cols = st.columns(4)
    for col, report in zip(cols, reports):
        with col:
            st.markdown(f"<div class='report-card'><p class='mini-label'>{report}</p><div class='mini-value'>Ready</div><span class='chip'>Updated today</span></div>", unsafe_allow_html=True)
            b1, b2, b3 = st.columns(3)
            with b1:
                st.button("PDF", key=f"{report}-pdf", use_container_width=True)
            with b2:
                st.button("Excel", key=f"{report}-excel", use_container_width=True)
            with b3:
                st.button("Email", key=f"{report}-email", use_container_width=True)


def settings_page() -> None:
    page_header("Settings", "Configure workspace preferences and dashboard behavior.")
    c1, c2 = st.columns(2)
    with c1:
        st.selectbox("Default currency", ["USD", "INR", "EUR", "GBP"])
        st.selectbox("Dashboard density", ["Comfortable", "Compact"])
        st.toggle("High contrast support", value=True)
    with c2:
        st.toggle("Email financial alerts", value=True)
        st.toggle("Enable skeleton loaders", value=True)
        st.toggle("Keyboard navigation hints", value=True)
        st.markdown("<div class='skeleton'></div>", unsafe_allow_html=True)


def sidebar_nav() -> str:
    with st.sidebar:
        st.markdown("<div class='app-logo'>💰 CashFlowAI</div>", unsafe_allow_html=True)
        if option_menu:
            return option_menu(
                menu_title=None,
                options=NAV_ITEMS,
                icons=NAV_ICONS,
                default_index=0,
                styles={
                    "container": {"padding": "0", "background-color": "transparent"},
                    "icon": {"color": "#CBD5E1", "font-size": "1rem"},
                    "nav-link": {
                        "font-size": "0.94rem",
                        "font-weight": "700",
                        "color": "#CBD5E1",
                        "padding": "0.72rem 0.75rem",
                        "border-radius": "8px",
                        "margin": "0.15rem 0",
                    },
                    "nav-link-selected": {"background-color": "#4F46E5", "color": "#FFFFFF"},
                },
            )
        return st.radio("Navigation", NAV_ITEMS, label_visibility="collapsed")


def main() -> None:
    inject_css()
    page = sidebar_nav()
    pages = {
        "Dashboard": dashboard_page,
        "Forecasting": forecasting_page,
        "Transactions": transactions_page,
        "Budget Planner": budget_page,
        "Scenario Analysis": scenario_page,
        "Reports": reports_page,
        "AI Insights": ai_insights_page,
        "Settings": settings_page,
    }
    pages[page]()


if __name__ == "__main__":
    main()
