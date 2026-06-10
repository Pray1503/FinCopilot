"""
Page 2 — AI Boardroom
━━━━━━━━━━━━━━━━━━━━━
5-agent LLM debate for loan decisions.
Budget-Bot → Risk-Radar → Horizon-Planner → Chairman → Devil's Advocate
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
from shared.theme import inject_global_css, render_brand_sidebar
from shared import money

st.set_page_config(page_title="AI Boardroom • FinPilot", page_icon="🏛️", layout="wide")
st.markdown(inject_global_css(), unsafe_allow_html=True)
render_brand_sidebar(st)

st.markdown(
    """
    <div style="padding:1.5rem 0 0.5rem;">
        <h1 style="font-size:2.2rem;font-weight:800;margin:0;
            background:linear-gradient(135deg,#60a5fa,#f59e0b);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
            🏛️ AI Boardroom
        </h1>
        <p style="color:#9ca3af;font-size:0.95rem;margin-top:6px;">
            5 AI agents debate your loan decision. Each brings a different perspective.
            <em>Requires GROQ_API_KEY in .env</em>
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Input Form ────────────────────────────────────────────────────────────
with st.expander("📝 Enter Your Financial Profile", expanded=True):
    c1, c2, c3 = st.columns(3)
    income = c1.number_input("Monthly Income (₹)", value=15000, step=1000, min_value=0)
    expenses = c2.number_input("Monthly Expenses (₹)", value=9000, step=500, min_value=0)
    savings = c3.number_input("Total Savings (₹)", value=25000, step=1000, min_value=0)

    c4, c5, c6 = st.columns(3)
    existing_emi = c4.number_input("Existing Monthly EMI (₹)", value=0, step=500, min_value=0)
    loan_amount = c5.number_input("Requested Loan Amount (₹)", value=50000, step=5000, min_value=0)
    proposed_emi = c6.number_input("Proposed EMI (₹)", value=2500, step=250, min_value=0)

    c7, c8 = st.columns(2)
    uplift = c7.slider("Expected earning uplift after course (%)", 0, 100, 20)
    question = c8.text_input("Your Question", value="Should I take this education loan?")

    goal_name = st.text_input("Primary Goal", value="Placement preparation")
    goal_amount = st.number_input("Goal Target Amount (₹)", value=100000, step=5000, min_value=0)
    goal_date = st.text_input("Goal Target Date (YYYY-MM)", value="2027-06")

scenario = {
    "income_monthly": income,
    "monthly_expenses": expenses,
    "savings": savings,
    "existing_debt_monthly_EMI": existing_emi,
    "requested_loan_amount": loan_amount,
    "proposed_EMI": proposed_emi,
    "expected_skill_earning_uplift_pct": uplift,
    "emergency_fund_amount": savings,
    "goals": [{"name": goal_name, "required_amount": goal_amount, "target_date": goal_date}],
}

# ── Run ───────────────────────────────────────────────────────────────────
if st.button("🚀  Convene the Boardroom", use_container_width=True):
    # Agent timeline
    agents_info = [
        ("📊", "Budget-Bot", "#2563eb"),
        ("🛡️", "Risk-Radar", "#ef4444"),
        ("🔭", "Planner", "#10b981"),
        ("👑", "Chairman", "#f59e0b"),
        ("😈", "Devil", "#7c3aed"),
    ]
    timeline_html = "".join(
        f"<div class='tl-node'><span>{e}</span>{n}</div>"
        for e, n, _ in agents_info
    )
    st.markdown(f"<div class='timeline-wrap'>{timeline_html}</div>", unsafe_allow_html=True)

    try:
        from services.boardroom_service import run_boardroom

        with st.spinner("Agents are deliberating..."):
            result = run_boardroom(scenario, question)

        for turn in result["turns"]:
            st.markdown(
                f"""
                <div class="debate-card" style="border-left-color:{turn['color']};">
                    <div style="font-weight:700;color:{turn['color']};margin-bottom:6px;">
                        {turn['emoji']} {turn['agent']}
                    </div>
                    <div style="color:#cbd5e1;font-size:0.92rem;line-height:1.65;">
                        {turn['response']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    except Exception as e:
        st.markdown(
            f"<div class='error-box'>❌ Failed to run boardroom: {e}</div>",
            unsafe_allow_html=True,
        )
else:
    st.markdown(
        "<div class='info-box'>💡 Fill in your financial profile above, then click <strong>Convene the Boardroom</strong> to start the 5-agent debate.</div>",
        unsafe_allow_html=True,
    )
