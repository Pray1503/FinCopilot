"""
Page 5 — Decision Simulator
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Should you buy it? ML-powered 12-month projection with seasonal spending prediction.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from shared.theme import inject_global_css, render_brand_sidebar
from shared import money, score_color

st.set_page_config(page_title="Decision Simulator • FinPilot", page_icon="💸", layout="wide")
st.markdown(inject_global_css(), unsafe_allow_html=True)
render_brand_sidebar(st)

st.markdown(
    """
    <div style="padding:1.5rem 0 0.5rem;">
        <h1 style="font-size:2.2rem;font-weight:800;margin:0;
            background:linear-gradient(135deg,#a78bfa,#f472b6);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
            💸 Decision Simulator
        </h1>
        <p style="color:#9ca3af;font-size:0.95rem;margin-top:6px;">
            Should you buy it? Enter your numbers and see the 12-month ML projection.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Input ─────────────────────────────────────────────────────────────────
with st.expander("📝 Your Financial Snapshot", expanded=True):
    c1, c2, c3 = st.columns(3)
    income = c1.number_input("Monthly Income (₹)", value=15000, step=1000, min_value=1, key="ds_inc")
    expenses = c2.number_input("Fixed Expenses (₹)", value=9000, step=500, min_value=0, key="ds_exp")
    savings = c3.number_input("Current Savings (₹)", value=25000, step=1000, min_value=0, key="ds_sav")

    st.markdown("---")
    st.markdown("**🛍️ What do you want to buy?**")
    c4, c5 = st.columns(2)
    item_name = c4.text_input("Item Name", value="AirPods", key="ds_item")
    cost = c5.number_input("Cost (₹)", value=20000, step=1000, min_value=1, key="ds_cost")

    st.markdown("**🎯 Your Primary Goal**")
    c6, c7 = st.columns(2)
    goal_name = c6.text_input("Goal Name", value="Laptop Fund", key="ds_goal")
    goal_target = c7.number_input("Goal Target (₹)", value=60000, step=5000, min_value=0, key="ds_gt")

    c8, c9 = st.columns(2)
    goal_saved = c8.number_input("Already Saved for Goal (₹)", value=15000, step=1000, min_value=0, key="ds_gs")
    goal_monthly = c9.number_input("Monthly Goal Allocation (₹)", value=3000, step=500, min_value=1, key="ds_gm")

# ── Run ───────────────────────────────────────────────────────────────────
if st.button("🔮  Simulate Decision", use_container_width=True, key="ds_run"):
    from simulator.decision_engine import simulate_purchase

    result = simulate_purchase(
        income=income, current_savings=savings, base_expenses=expenses,
        item_name=item_name, cost=cost,
        goal_name=goal_name, goal_target=goal_target,
        goal_current=goal_saved, goal_alloc=goal_monthly,
    )

    if result.get("error"):
        st.markdown(f"<div class='error-box'>❌ {result['message']}</div>", unsafe_allow_html=True)
    else:
        # ── Affordability Score ───────────────────────────────
        sc = result["affordability_score"]
        col = score_color(sc)
        st.markdown(
            f"""
            <div class="mega-card" style="text-align:center;padding:28px;">
                <div style="color:#6b7280;font-size:0.8rem;text-transform:uppercase;font-weight:700;margin-bottom:8px;">
                    Affordability Score for {item_name}
                </div>
                <div style="font-size:3rem;font-weight:800;color:{col};" class="mono">{sc}/100</div>
                <div style="color:#e5e7eb;font-size:1rem;margin-top:8px;font-weight:600;">{result['verdict']}</div>
                <div class="score-bar-bg" style="margin-top:16px;">
                    <div class="score-bar-fill" style="width:{sc}%;background:{col};"></div>
                </div>
                <div style="color:#6b7280;font-size:0.82rem;margin-top:8px;">
                    Time to absorb cost: <strong>{result['months_to_absorb']} months</strong> |
                    Monthly surplus: <strong>{money(result['surplus'])}</strong>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── Goal Impact ──────────────────────────────────────
        st.markdown(
            f"""
            <div class="mega-card">
                <div style="font-weight:700;color:#f59e0b;margin-bottom:8px;">
                    🎯 Impact on {result['goal_name']}
                </div>
                <div style="display:flex;gap:24px;flex-wrap:wrap;">
                    <div class="explain-card" style="flex:1;min-width:200px;">
                        <h4>Original Timeline</h4>
                        <p class="mono" style="font-size:1.3rem;color:#34d399;">{result['original_timeline']} months</p>
                    </div>
                    <div class="explain-card" style="flex:1;min-width:200px;">
                        <h4>Freeze Period</h4>
                        <p class="mono" style="font-size:1.3rem;color:#fbbf24;">{result['freeze_months']} months</p>
                    </div>
                    <div class="explain-card" style="flex:1;min-width:200px;">
                        <h4>Delayed Timeline</h4>
                        <p class="mono" style="font-size:1.3rem;color:#f87171;">{result['delayed_timeline']} months</p>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── 12-Month Projection Chart ────────────────────────
        proj = result["projections"]
        df = pd.DataFrame(proj)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["month"], y=df["control"], name="Don't Buy", line=dict(color="#34d399", width=3)))
        fig.add_trace(go.Scatter(x=df["month"], y=df["static"], name="Buy (Static)", line=dict(color="#fbbf24", width=3)))
        fig.add_trace(go.Scatter(x=df["month"], y=df["ml_dynamic"], name="Buy (ML Dynamic)", line=dict(color="#818cf8", width=3, dash="dash")))

        # Add tags
        for row in proj:
            if row["tag"]:
                fig.add_annotation(
                    x=row["month"], y=row["ml_dynamic"],
                    text=row["tag"], showarrow=True, arrowhead=2,
                    font=dict(size=10, color="#e5e7eb"),
                    arrowcolor="#6b7280",
                )

        fig.update_layout(
            title="12-Month Savings Projection",
            height=450, margin=dict(l=8, r=8, t=40, b=12),
            xaxis=dict(title="Month", dtick=1, color="#e5e7eb", gridcolor="#1f2937"),
            yaxis=dict(title="Savings (₹)", tickprefix="₹", color="#e5e7eb", gridcolor="#1f2937"),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#111827",
            font=dict(color="#e5e7eb"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            hovermode="x unified",
        )
        st.plotly_chart(fig, use_container_width=True)

        # ── Projection Table ─────────────────────────────────
        with st.expander("📋 Detailed Monthly Breakdown"):
            display_df = df[["month", "control", "static", "ml_dynamic", "tag"]].copy()
            display_df.columns = ["Month", "Don't Buy (₹)", "Buy Static (₹)", "Buy ML Dynamic (₹)", "Season"]
            st.dataframe(display_df, use_container_width=True, hide_index=True)
else:
    st.markdown(
        "<div class='info-box'>💡 Enter your income, expenses, and the item you want to buy. The ML model predicts seasonal spending patterns to give you a realistic 12-month projection.</div>",
        unsafe_allow_html=True,
    )
