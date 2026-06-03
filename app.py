"""
Financial Boardroom — Multi-Agent Decision Engine
Pure Python Streamlit application. No HTML files.
"""

import streamlit as st
import json
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from agents import budget_analyst, long_term_planner, risk_assessor, coordinator
from ml.predict import predict_spend, is_model_available

# ═══════════════════════════════════════════════════════════════════
# Page config & custom styling
# ═══════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Financial Boardroom",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Premium light theme via CSS injection ────────────────────────
st.markdown("""
<style>
    /* ── Global overrides ──────────────────────────────────────── */
    .stApp {
        background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 50%, #e8ecf2 100%);
    }
    .stApp::before {
        content: '';
        position: fixed;
        inset: 0;
        background:
            linear-gradient(rgba(59,130,246,0.04) 1px, transparent 1px),
            linear-gradient(90deg, rgba(59,130,246,0.04) 1px, transparent 1px);
        background-size: 60px 60px;
        pointer-events: none;
        z-index: 0;
    }
    section[data-testid="stSidebar"] { background: #f1f5f9; }

    /* Fix input/text colors for light bg */
    .stNumberInput input, .stTextArea textarea, .stTextInput input {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        color: #1e293b !important;
        border-radius: 8px !important;
    }
    .stNumberInput input:focus, .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59,130,246,0.12) !important;
    }
    label, .stMarkdown p, .stMarkdown li { color: #475569 !important; }
    h1, h2, h3, h4, h5, h6 { color: #0f172a !important; }

    /* ── Header styling ────────────────────────────────────────── */
    .hero-badge {
        display: inline-flex; align-items: center; gap: 8px;
        padding: 6px 16px; border-radius: 999px;
        background: rgba(59,130,246,0.08); border: 1px solid rgba(59,130,246,0.18);
        font-size: 0.72rem; font-weight: 700; color: #2563eb;
        text-transform: uppercase; letter-spacing: 1.5px;
        margin-bottom: 12px;
    }
    .hero-badge .dot {
        width: 6px; height: 6px; background: #2563eb;
        border-radius: 50%; animation: pulse-dot 2s ease-in-out infinite;
    }
    @keyframes pulse-dot {
        0%,100% { opacity:1; transform:scale(1); }
        50% { opacity:0.4; transform:scale(0.7); }
    }
    .hero-title {
        font-size: clamp(2rem,5vw,3.2rem); font-weight: 800; line-height: 1.15;
        background: linear-gradient(135deg, #0f172a 0%, #2563eb 50%, #7c3aed 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text; margin-bottom: 8px;
    }
    .hero-sub { color: #64748b !important; font-size: 1.05rem; max-width: 620px; }

    /* ── Agent card ─────────────────────────────────────────────── */
    .agent-card {
        background: rgba(255,255,255,0.85); backdrop-filter: blur(16px);
        border: 1px solid rgba(0,0,0,0.06); border-radius: 16px;
        padding: 24px; margin-bottom: 16px; position: relative;
        overflow: hidden; transition: all 0.4s cubic-bezier(0.16,1,0.3,1);
        box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.03);
    }
    .agent-card:hover {
        border-color: rgba(0,0,0,0.1);
        box-shadow: 0 4px 16px rgba(0,0,0,0.06), 0 8px 24px rgba(0,0,0,0.04);
    }
    .agent-card .top-bar {
        position: absolute; top: 0; left: 0; right: 0; height: 3px;
    }
    .top-bar.blue { background: linear-gradient(90deg, #3b82f6, #06b6d4); }
    .top-bar.purple { background: linear-gradient(90deg, #8b5cf6, #a855f7); }
    .top-bar.amber { background: linear-gradient(90deg, #f59e0b, #f97316); }
    .top-bar.rainbow {
        background: linear-gradient(90deg, #3b82f6, #8b5cf6, #f59e0b, #10b981);
    }

    .agent-header { display: flex; align-items: center; gap: 14px; margin-bottom: 16px; }
    .agent-icon {
        width: 44px; height: 44px; border-radius: 10px;
        display: flex; align-items: center; justify-content: center; font-size: 1.3rem;
    }
    .icon-blue { background: rgba(59,130,246,0.1); }
    .icon-purple { background: rgba(139,92,246,0.1); }
    .icon-amber { background: rgba(245,158,11,0.1); }
    .icon-emerald { background: linear-gradient(135deg, rgba(16,185,129,0.1), rgba(59,130,246,0.1)); }
    .agent-name { font-size: 0.92rem; font-weight: 700; color: #0f172a !important; }
    .agent-role {
        font-size: 0.68rem; color: #94a3b8 !important;
        text-transform: uppercase; letter-spacing: 0.5px;
    }

    /* Verdict badges */
    .verdict {
        display: inline-flex; align-items: center; gap: 6px;
        padding: 5px 14px; border-radius: 999px;
        font-size: 0.72rem; font-weight: 700;
        text-transform: uppercase; letter-spacing: 0.8px;
    }
    .v-safe, .v-manageable_risk, .v-high_impact {
        background: rgba(16,185,129,0.1); color: #059669;
        border: 1px solid rgba(16,185,129,0.2);
    }
    .v-caution, .v-moderate, .v-proceed_with_caution {
        background: rgba(245,158,11,0.1); color: #d97706;
        border: 1px solid rgba(245,158,11,0.2);
    }
    .v-risky, .v-too_risky, .v-low_impact {
        background: rgba(239,68,68,0.08); color: #dc2626;
        border: 1px solid rgba(239,68,68,0.18);
    }
    .v-go_now {
        background: rgba(16,185,129,0.1); color: #059669;
        border: 1px solid rgba(16,185,129,0.25);
        font-size: 0.82rem; padding: 7px 18px;
    }
    .v-delay_and_prepare {
        background: rgba(245,158,11,0.1); color: #d97706;
        border: 1px solid rgba(245,158,11,0.25);
        font-size: 0.82rem; padding: 7px 18px;
    }
    .v-decline {
        background: rgba(239,68,68,0.08); color: #dc2626;
        border: 1px solid rgba(239,68,68,0.25);
        font-size: 0.82rem; padding: 7px 18px;
    }
    .verdict .vdot {
        width: 6px; height: 6px; border-radius: 50%; background: currentColor;
    }

    /* Key number box */
    .kn-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin: 12px 0; }
    .kn-box {
        padding: 8px 12px; background: #f8fafc;
        border-radius: 8px; border: 1px solid #e2e8f0;
    }
    .kn-label {
        font-size: 0.62rem; color: #94a3b8 !important;
        text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 2px;
    }
    .kn-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.08rem; font-weight: 700; color: #0f172a !important;
    }
    .kn-value.danger { color: #dc2626 !important; }
    .kn-value.warning { color: #d97706 !important; }
    .kn-value.safe { color: #059669 !important; }

    /* Analysis text */
    .analysis {
        font-size: 0.84rem; color: #475569 !important;
        line-height: 1.65; padding-top: 12px;
        border-top: 1px solid #e2e8f0;
    }

    /* Goal tag */
    .goal-tag {
        display: inline-block; padding: 2px 8px; border-radius: 999px;
        font-size: 0.62rem; font-weight: 700; text-transform: uppercase;
    }
    .gt-helps { background: rgba(16,185,129,0.1); color: #059669; }
    .gt-delays { background: rgba(239,68,68,0.08); color: #dc2626; }
    .gt-neutral { background: #f1f5f9; color: #94a3b8; }

    /* Risk item */
    .risk-item {
        font-size: 0.82rem; color: #475569 !important;
        padding: 6px 0; display: flex; gap: 8px;
    }

    /* Coordinator recommendation */
    .rec-box {
        font-size: 1rem; font-weight: 500; color: #0f172a !important;
        line-height: 1.6; padding: 14px 18px; margin: 14px 0;
        background: #f0fdf4;
        border-left: 3px solid #059669;
        border-radius: 0 8px 8px 0;
    }

    /* Synthesis bullets */
    .synth-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin: 14px 0; }
    .synth-box {
        padding: 14px; border-radius: 10px;
        background: #f8fafc; border: 1px solid #e2e8f0;
    }
    .synth-label {
        font-size: 0.68rem; font-weight: 700;
        text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px;
    }
    .synth-label.agrees { color: #059669 !important; }
    .synth-label.tradeoff { color: #d97706 !important; }
    .synth-text { font-size: 0.84rem; color: #475569 !important; line-height: 1.55; }

    /* Next step */
    .step-box {
        display: flex; align-items: flex-start; gap: 14px;
        padding: 12px 14px; margin: 8px 0; border-radius: 10px;
        background: #f8fafc; border: 1px solid #e2e8f0;
    }
    .step-badge {
        flex-shrink: 0; padding: 4px 10px; border-radius: 999px;
        background: rgba(59,130,246,0.08); color: #2563eb;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.68rem; font-weight: 700; white-space: nowrap;
    }
    .step-text { font-size: 0.84rem; color: #475569 !important; line-height: 1.5; }

    /* ML badge */
    .ml-badge {
        display: inline-flex; align-items: center; gap: 8px;
        padding: 8px 16px; border-radius: 999px;
        background: rgba(139,92,246,0.06); border: 1px solid rgba(139,92,246,0.15);
        font-size: 0.75rem; color: #7c3aed; margin-top: 16px;
    }

    /* Thinking animation */
    @keyframes thinking-pulse {
        0%,100% { opacity: 0.4; }
        50% { opacity: 1; }
    }
    .thinking-text {
        color: #94a3b8 !important; font-size: 0.85rem;
        animation: thinking-pulse 1.5s ease-in-out infinite;
    }

    /* Footer */
    .footer {
        text-align: center; padding: 32px 0; color: #94a3b8 !important;
        font-size: 0.72rem; border-top: 1px solid #e2e8f0;
        margin-top: 32px;
    }

    /* Hide streamlit branding */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header[data-testid="stHeader"] { background: transparent; }

    /* Responsive columns */
    @media (max-width: 768px) {
        .kn-grid, .synth-grid { grid-template-columns: 1fr; }
    }

    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');
    * { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# Helper functions
# ═══════════════════════════════════════════════════════════════════

def _verdict_class(verdict: str) -> str:
    return f"v-{verdict.lower()}"


def _color_class(value: float, warn: float, danger: float) -> str:
    if value >= danger:
        return "danger"
    if value >= warn:
        return "warning"
    return "safe"


def _render_verdict(verdict: str) -> str:
    label = verdict.replace("_", " ").title()
    return f'<span class="verdict {_verdict_class(verdict)}"><span class="vdot"></span>{label}</span>'


def _render_kn(label: str, value: str, cls: str = "") -> str:
    return (
        f'<div class="kn-box">'
        f'<div class="kn-label">{label}</div>'
        f'<div class="kn-value {cls}">{value}</div>'
        f'</div>'
    )


def compute_emi(principal: float, rate: float = 12, months: int = 12) -> int:
    """Auto-compute EMI from principal."""
    if principal <= 0:
        return 0
    r = rate / 12 / 100
    if r == 0:
        return round(principal / months)
    emi = (principal * r * (1 + r) ** months) / ((1 + r) ** months - 1)
    return round(emi)


# ═══════════════════════════════════════════════════════════════════
# Rendering functions for each agent
# ═══════════════════════════════════════════════════════════════════

def render_budgeter(data: dict):
    kn = data.get("key_numbers", {})
    st.markdown(f"""
    <div class="agent-card">
        <div class="top-bar blue"></div>
        <div class="agent-header">
            <div class="agent-icon icon-blue">📊</div>
            <div><div class="agent-name">Budget Analyst</div><div class="agent-role">Numbers-First</div></div>
        </div>
        {_render_verdict(data["verdict"])}
        <div class="kn-grid">
            {_render_kn("DTI Ratio", f'{kn["debt_to_income_pct"]}%', _color_class(kn["debt_to_income_pct"], 30, 40))}
            {_render_kn("EMI % Income", f'{kn["proposed_emi_pct"]}%', _color_class(kn["proposed_emi_pct"], 20, 30))}
            {_render_kn("Savings Cover", f'{kn["savings_months_coverage"]} mo', _color_class(2 - kn["savings_months_coverage"], 0.5, 1.5))}
            {_render_kn("Net Surplus", f'₹{kn["net_monthly_surplus"]}', "danger" if kn["net_monthly_surplus"] < 0 else "warning" if kn["net_monthly_surplus"] < 1500 else "safe")}
        </div>
        <div class="analysis">{data["analysis"]}</div>
    </div>
    """, unsafe_allow_html=True)


def render_planner(data: dict):
    goals_html = ""
    for g in data.get("goal_impacts", []):
        tag_cls = f"gt-{g['impact']}"
        goals_html += (
            f'<div style="padding:6px 0;border-bottom:1px solid #e2e8f0;">'
            f'<span class="goal-tag {tag_cls}">{g["impact"]}</span> '
            f'<span style="color:#475569;font-size:0.82rem;"><strong style="color:#0f172a">{g["goal_name"]}</strong> — {g["notes"]}</span>'
            f'</div>'
        )
    roi = data.get("roi_months_estimate", "?")
    roi_cls = "safe" if roi <= 12 else "warning" if roi <= 18 else "danger"

    st.markdown(f"""
    <div class="agent-card">
        <div class="top-bar purple"></div>
        <div class="agent-header">
            <div class="agent-icon icon-purple">🎯</div>
            <div><div class="agent-name">Long-Term Planner</div><div class="agent-role">Goal-Focused</div></div>
        </div>
        {_render_verdict(data["verdict"])}
        <div class="kn-grid">
            {_render_kn("ROI Breakeven", f'{roi} mo', roi_cls)}
            {_render_kn("Goals Tracked", str(len(data.get("goal_impacts", []))))}
        </div>
        {goals_html}
        <div class="analysis">{data["analysis"]}</div>
    </div>
    """, unsafe_allow_html=True)


def render_realist(data: dict):
    risks_html = ""
    for r in data.get("key_risks", []):
        risks_html += f'<div class="risk-item">⚠ {r}</div>'

    ef = data.get("emergency_fund_months", 0)
    wc = data.get("worst_case_months_coverage", 0)

    st.markdown(f"""
    <div class="agent-card">
        <div class="top-bar amber"></div>
        <div class="agent-header">
            <div class="agent-icon icon-amber">🛡️</div>
            <div><div class="agent-name">Risk Assessor</div><div class="agent-role">Pragmatic</div></div>
        </div>
        {_render_verdict(data["verdict"])}
        <div class="kn-grid">
            {_render_kn("Emergency Fund", f'{ef} mo', _color_class(2 - ef, 0.5, 1.5))}
            {_render_kn("Worst-Case Cover", f'{wc} mo', "danger" if wc < 1 else "warning" if wc < 2 else "safe")}
        </div>
        {risks_html}
        <div class="analysis">{data["analysis"]}</div>
    </div>
    """, unsafe_allow_html=True)


def render_coordinator(data: dict):
    cv = data.get("combined_verdict", "unknown")
    steps_html = ""
    for s in data.get("next_steps", []):
        steps_html += (
            f'<div class="step-box">'
            f'<span class="step-badge">{s["timeframe_days"]}d</span>'
            f'<span class="step-text">{s["action"]}</span>'
            f'</div>'
        )

    st.markdown(f"""
    <div class="agent-card" style="max-width:900px;margin:0 auto;">
        <div class="top-bar rainbow"></div>
        <div class="agent-header">
            <div class="agent-icon icon-emerald" style="width:52px;height:52px;font-size:1.5rem;">🏛️</div>
            <div><div class="agent-name" style="font-size:1.1rem;">Coordinator</div><div class="agent-role">Synthesized Recommendation</div></div>
        </div>
        {_render_verdict(cv)}
        <div class="rec-box">{data.get("coordinator_recommendation", "")}</div>
        <div class="synth-grid">
            <div class="synth-box">
                <div class="synth-label agrees">✓ Agreement</div>
                <div class="synth-text">{data.get("agrees", "")}</div>
            </div>
            <div class="synth-box">
                <div class="synth-label tradeoff">⚖ Key Tradeoff</div>
                <div class="synth-text">{data.get("tradeoff", "")}</div>
            </div>
        </div>
        <div style="margin-top:14px;">
            <div style="font-size:0.78rem;font-weight:700;color:#94a3b8;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;">Action Plan</div>
            {steps_html}
        </div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# Main App
# ═══════════════════════════════════════════════════════════════════

def main():
    # ── Hero Header ──────────────────────────────────────────────
    st.markdown("""
    <div style="text-align:center;padding-top:24px;margin-bottom:48px;">
        <div class="hero-badge"><span class="dot"></span>Multi-Agent System</div>
        <div class="hero-title">Financial Boardroom</div>
        <div class="hero-sub">Four specialist agents analyze your financial decision and deliver one clear, actionable recommendation.</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Input Form ───────────────────────────────────────────────
    with st.container():
        st.markdown("### 📋 Your Financial Profile")
        st.caption("Enter your details below. All amounts are in ₹ (monthly).")

        question = st.text_area(
            "Your Question",
            value="Should I take ₹50,000 education loan?",
            height=68,
            key="user_question",
        )

        st.markdown("**Income & Expenses**")
        c1, c2, c3, c4 = st.columns(4)
        income = c1.number_input("Monthly Income (₹)", value=15000, min_value=0, step=500, key="income")
        expenses = c2.number_input("Monthly Expenses (₹)", value=9000, min_value=0, step=500, key="expenses")
        savings = c3.number_input("Total Savings (₹)", value=5000, min_value=0, step=500, key="savings")
        emergency = c4.number_input("Emergency Fund (₹)", value=5000, min_value=0, step=500, key="emergency")

        st.markdown("**Debt & Loan Details**")
        c5, c6, c7, c8 = st.columns(4)
        existing_emi = c5.number_input("Existing Debt EMI (₹)", value=0, min_value=0, step=100, key="existing_emi")
        loan_amount = c6.number_input("Loan Amount (₹)", value=50000, min_value=0, step=1000, key="loan_amt")
        proposed_emi = c7.number_input("Proposed EMI (₹)", value=3500, min_value=0, step=100, key="proposed_emi")
        other_outflows = c8.number_input("Other Outflows (₹)", value=0, min_value=0, step=100, key="other_out")

        st.markdown("**Goals & Growth**")
        goals_text = st.text_area(
            "Goals (name, target date, amount — one per line)",
            value="Placement prep, 2026-12, 20000\nEmergency buffer, 2026-06, 18000",
            height=90,
            key="goals_text",
        )
        c9, c10 = st.columns(2)
        uplift = c9.number_input("Expected Earning Uplift %", value=40, min_value=0, max_value=200, step=5, key="uplift")
        course_months = c10.number_input("Course Length (months)", value=3, min_value=1, max_value=48, step=1, key="course_mo")

    # ── Parse goals ──────────────────────────────────────────────
    goals = []
    for line in goals_text.strip().split("\n"):
        parts = [p.strip() for p in line.split(",")]
        if len(parts) >= 1 and parts[0]:
            goals.append({
                "name": parts[0],
                "target_date": parts[1] if len(parts) > 1 else "2026-12-31",
                "required_amount": float(parts[2]) if len(parts) > 2 else 0,
            })

    # ── Compute EMI if not provided ──────────────────────────────
    emi_val = proposed_emi
    if emi_val == 0 and loan_amount > 0:
        emi_val = compute_emi(loan_amount)

    # ── Build profile ────────────────────────────────────────────
    profile = {
        "income_monthly": income,
        "monthly_expenses": expenses,
        "savings": savings,
        "existing_debt_monthly_EMI": existing_emi,
        "emergency_fund_amount": emergency,
        "requested_loan_amount": loan_amount,
        "proposed_EMI": emi_val,
        "other_known_outflows": other_outflows,
        "goals": goals,
        "expected_skill_earning_uplift_pct": uplift,
        "course_length_months": course_months,
        "expense_volatility": "medium",
        "credit_history": "limited",
        "seasonality_flags": {},
    }

    # ── ML prediction ────────────────────────────────────────────
    ml_available = is_model_available()
    if ml_available:
        now = datetime.now()
        next_month = (now.month % 12) + 1
        is_exam = 1 if next_month in (3, 4, 11) else 0
        is_festival = 1 if next_month in (1, 10, 12) else 0
        predicted = predict_spend(next_month, is_exam, is_festival, expenses)
        profile["predicted_next_month_spend"] = predicted

    # ── Run button ───────────────────────────────────────────────
    st.markdown("---")
    run_btn = st.button("🏛️  Convene Boardroom", type="primary", use_container_width=True)

    if run_btn:
        # ── Specialist thinking animation ────────────────────────
        st.markdown("---")
        st.markdown('<div style="text-align:center;margin-bottom:24px;">'
                    '<span style="font-size:1rem;font-weight:700;color:#94a3b8;'
                    'text-transform:uppercase;letter-spacing:1.5px;">Specialist Analysis</span></div>',
                    unsafe_allow_html=True)

        col_b, col_p, col_r = st.columns(3)

        # Show thinking state
        with col_b:
            thinking_b = st.empty()
            thinking_b.markdown('<div class="agent-card"><div class="top-bar blue"></div>'
                                '<div class="agent-header"><div class="agent-icon icon-blue">📊</div>'
                                '<div><div class="agent-name">Budget Analyst</div>'
                                '<div class="agent-role">Numbers-First</div></div></div>'
                                '<div class="thinking-text">⏳ Crunching numbers…</div></div>',
                                unsafe_allow_html=True)
        with col_p:
            thinking_p = st.empty()
            thinking_p.markdown('<div class="agent-card"><div class="top-bar purple"></div>'
                                '<div class="agent-header"><div class="agent-icon icon-purple">🎯</div>'
                                '<div><div class="agent-name">Long-Term Planner</div>'
                                '<div class="agent-role">Goal-Focused</div></div></div>'
                                '<div class="thinking-text">⏳ Evaluating goals…</div></div>',
                                unsafe_allow_html=True)
        with col_r:
            thinking_r = st.empty()
            thinking_r.markdown('<div class="agent-card"><div class="top-bar amber"></div>'
                                '<div class="agent-header"><div class="agent-icon icon-amber">🛡️</div>'
                                '<div><div class="agent-name">Risk Assessor</div>'
                                '<div class="agent-role">Pragmatic</div></div></div>'
                                '<div class="thinking-text">⏳ Assessing risks…</div></div>',
                                unsafe_allow_html=True)

        # Run agents in parallel
        with ThreadPoolExecutor(max_workers=3) as pool:
            f_b = pool.submit(budget_analyst.run, profile)
            f_p = pool.submit(long_term_planner.run, profile)
            f_r = pool.submit(risk_assessor.run, profile)

            budgeter_result = f_b.result()
            planner_result = f_p.result()
            realist_result = f_r.result()

        # Staggered reveal — Budget Analyst
        time.sleep(0.5)
        with col_b:
            thinking_b.empty()
            render_budgeter(budgeter_result)

        # Planner
        time.sleep(0.4)
        with col_p:
            thinking_p.empty()
            render_planner(planner_result)

        # Realist
        time.sleep(0.4)
        with col_r:
            thinking_r.empty()
            render_realist(realist_result)

        # ── Coordinator ──────────────────────────────────────────
        st.markdown('<div style="text-align:center;margin:32px 0 20px;">'
                    '<span style="font-size:1rem;font-weight:700;color:#94a3b8;'
                    'text-transform:uppercase;letter-spacing:1.5px;">Final Recommendation</span></div>',
                    unsafe_allow_html=True)

        coord_placeholder = st.empty()
        coord_placeholder.markdown(
            '<div class="agent-card" style="max-width:900px;margin:0 auto;">'
            '<div class="top-bar rainbow"></div>'
            '<div class="agent-header"><div class="agent-icon icon-emerald" style="width:52px;height:52px;font-size:1.5rem;">🏛️</div>'
            '<div><div class="agent-name" style="font-size:1.1rem;">Coordinator</div>'
            '<div class="agent-role">Synthesized Recommendation</div></div></div>'
            '<div class="thinking-text">⏳ Synthesizing insights…</div></div>',
            unsafe_allow_html=True,
        )

        profile_summary = {
            "income_monthly": income,
            "monthly_expenses": expenses,
            "savings": savings,
            "proposed_EMI": emi_val,
        }

        time.sleep(0.7)
        coord_result = coordinator.run(
            budgeter_result, planner_result, realist_result, question, profile_summary
        )

        coord_placeholder.empty()
        render_coordinator(coord_result)

        # ML badge
        if ml_available:
            st.markdown(
                '<div style="text-align:center;">'
                '<span class="ml-badge">🧠 ML spending prediction enhanced the Budget Analyst\'s analysis '
                f'(predicted next month: ₹{profile.get("predicted_next_month_spend", "N/A")})</span></div>',
                unsafe_allow_html=True,
            )

        # ── Raw JSON expander ────────────────────────────────────
        with st.expander("📄 View Raw JSON Output"):
            full_output = {
                "budgeter": budgeter_result,
                "planner": planner_result,
                "realist": realist_result,
                "coordinator": coord_result,
                "meta": {
                    "ml_prediction_available": ml_available,
                    "predicted_next_month_spend": profile.get("predicted_next_month_spend"),
                    "computed_emi": emi_val,
                },
            }
            st.json(full_output)

    # ── Footer ───────────────────────────────────────────────────
    st.markdown(
        '<div class="footer">Financial Boardroom · Multi-Agent Decision Engine · Built for students</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
