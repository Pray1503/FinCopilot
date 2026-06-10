"""
Page 3 — Smart Boardroom
━━━━━━━━━━━━━━━━━━━━━━━━
Pure-Python multi-agent boardroom — no API key needed.
Budget Analyst → Risk Assessor → Long-Term Planner → Coordinator
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
from shared.theme import inject_global_css, render_brand_sidebar
from shared import money, score_color

st.set_page_config(page_title="Smart Boardroom • FinPilot", page_icon="📊", layout="wide")
st.markdown(inject_global_css(), unsafe_allow_html=True)
render_brand_sidebar(st)

st.markdown(
    """
    <div style="padding:1.5rem 0 0.5rem;">
        <h1 style="font-size:2.2rem;font-weight:800;margin:0;
            background:linear-gradient(135deg,#34d399,#60a5fa);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
            📊 Smart Boardroom
        </h1>
        <p style="color:#9ca3af;font-size:0.95rem;margin-top:6px;">
            Instant multi-agent analysis using pure math — no API key needed. Results in milliseconds.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Input Form ────────────────────────────────────────────────────────────
with st.expander("📝 Financial Profile", expanded=True):
    c1, c2, c3 = st.columns(3)
    income = c1.number_input("Monthly Income (₹)", value=15000, step=1000, min_value=0, key="sb_income")
    expenses = c2.number_input("Monthly Expenses (₹)", value=9000, step=500, min_value=0, key="sb_expenses")
    savings = c3.number_input("Total Savings (₹)", value=25000, step=1000, min_value=0, key="sb_savings")

    c4, c5, c6 = st.columns(3)
    existing_emi = c4.number_input("Existing EMI (₹)", value=0, step=500, min_value=0, key="sb_emi")
    loan_amount = c5.number_input("Loan Amount (₹)", value=50000, step=5000, min_value=0, key="sb_loan")
    proposed_emi = c6.number_input("Proposed EMI (₹)", value=2500, step=250, min_value=0, key="sb_pemi")

    c7, c8 = st.columns(2)
    emergency = c7.number_input("Emergency Fund (₹)", value=10000, step=1000, min_value=0, key="sb_ef")
    uplift = c8.slider("Earning Uplift (%)", 0, 100, 20, key="sb_uplift")

    question = st.text_input("Your Question", value="Should I take this education loan?", key="sb_q")

    goal_name = st.text_input("Goal Name", value="Placement preparation", key="sb_gn")
    goal_amount = st.number_input("Goal Target (₹)", value=100000, step=5000, min_value=0, key="sb_ga")
    goal_date = st.text_input("Goal Date (YYYY-MM)", value="2027-06", key="sb_gd")

profile = {
    "income_monthly": income,
    "monthly_expenses": expenses,
    "savings": savings,
    "existing_debt_monthly_EMI": existing_emi,
    "requested_loan_amount": loan_amount,
    "proposed_EMI": proposed_emi,
    "expected_skill_earning_uplift_pct": uplift,
    "emergency_fund_amount": emergency,
    "course_length_months": 6,
    "goals": [{"name": goal_name, "required_amount": goal_amount, "target_date": goal_date}],
}

# ── Run ───────────────────────────────────────────────────────────────────
if st.button("⚡  Run Smart Analysis", use_container_width=True, key="sb_run"):
    from agents.budget_analyst import run as run_budget
    from agents.risk_assessor import run as run_risk
    from agents.long_term_planner import run as run_planner
    from agents.coordinator import run as run_coordinator

    budget = run_budget(profile)
    risk = run_risk(profile)
    planner = run_planner(profile)
    coord = run_coordinator(budget, planner, risk, question, profile)

    # ── Verdict Banner ────────────────────────────────────────
    verdict = coord.get("combined_verdict", "unknown")
    verdict_class = {"Go_now": "vh-go", "Delay_and_prepare": "vh-delay", "Decline": "vh-decline"}.get(verdict, "vh-delay")
    verdict_label = {"Go_now": "✅ GO NOW", "Delay_and_prepare": "⏸️ DELAY & PREPARE", "Decline": "🛑 DECLINE"}.get(verdict, verdict)
    st.markdown(f"<div class='verdict-header {verdict_class}'>{verdict_label}</div>", unsafe_allow_html=True)

    # ── Coordinator Summary ───────────────────────────────────
    st.markdown(
        f"""
        <div class="mega-card">
            <div style="font-weight:700;color:#f59e0b;margin-bottom:8px;">👑 Coordinator's Verdict</div>
            <p style="color:#e2e8f0;font-size:0.92rem;line-height:1.65;">{coord.get('agrees', '')}</p>
            <p style="color:#94a3b8;font-size:0.88rem;line-height:1.55;margin-top:8px;">{coord.get('tradeoff', '')}</p>
            <p style="color:#cbd5e1;font-size:0.92rem;line-height:1.65;margin-top:12px;font-weight:600;">
                {coord.get('coordinator_recommendation', '')}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Agent Details ─────────────────────────────────────────
    col1, col2, col3 = st.columns(3)

    with col1:
        bv = budget.get("verdict", "?")
        kn = budget.get("key_numbers", {})
        st.markdown(
            f"""
            <div class="explain-card">
                <h4>📊 Budget Analyst — {bv}</h4>
                <p>
                    DTI: <strong>{kn.get('debt_to_income_pct', 0)}%</strong> |
                    EMI share: <strong>{kn.get('proposed_emi_pct', 0)}%</strong><br>
                    Savings runway: <strong>{kn.get('savings_months_coverage', 0)} months</strong><br>
                    Net surplus: <strong>{money(kn.get('net_monthly_surplus', 0))}</strong><br>
                    Split: {kn.get('needs_pct', 0)}/{kn.get('debt_obligations_pct', 0)}/{kn.get('remaining_for_savings_pct', 0)}
                </p>
                <p style="margin-top:8px;">{budget.get('analysis', '')}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        rv = risk.get("verdict", "?")
        st.markdown(
            f"""
            <div class="explain-card">
                <h4>🛡️ Risk Assessor — {rv}</h4>
                <p>
                    Emergency fund: <strong>{risk.get('emergency_fund_months', 0)} months</strong><br>
                    Worst-case coverage: <strong>{risk.get('worst_case_months_coverage', 0)} months</strong>
                </p>
                <p style="margin-top:8px;">{risk.get('analysis', '')}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        pv = planner.get("verdict", "?")
        st.markdown(
            f"""
            <div class="explain-card">
                <h4>🔭 Long-Term Planner — {pv}</h4>
                <p>
                    ROI breakeven: <strong>~{planner.get('roi_months_estimate', '?')} months</strong>
                </p>
                <p style="margin-top:8px;">{planner.get('analysis', '')}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── Next Steps ────────────────────────────────────────────
    st.markdown("### 📋 Recommended Next Steps")
    for idx, step in enumerate(coord.get("next_steps", []), 1):
        st.markdown(
            f"""
            <div class="action-step">
                <div class="action-num">{idx}</div>
                <div class="action-text">
                    {step.get('action', '')}
                    <span style="color:#6b7280;font-size:0.78rem;"> — within {step.get('timeframe_days', '?')} days</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
else:
    st.markdown(
        "<div class='info-box'>⚡ This module runs entirely offline — no API key needed. Fill in your profile and click <strong>Run Smart Analysis</strong>.</div>",
        unsafe_allow_html=True,
    )
