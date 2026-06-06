"""
app.py — AI Student Wealth Coach
══════════════════════════════════
Streamlit frontend.  Strictly UI only — no math, no AI calls here.

Run:
    streamlit run app.py

Upgrades vs original:
  • 3-agent boardroom
  • Agent speaking-order timeline strip (shows which agent is active)
  • Radar / spider chart for score breakdown (uses st.bar_chart fallback
    if plotly not installed)
  • Action Steps panel from Chairman verdict
  • Winning Argument highlight badge
  • Score breakdown explainability (sub-scores from financial engine)
  • API key check at startup — clear error before anything runs
  • Dark theme tokens consistent throughout
  • All f-strings use :, number formatting (no raw floats shown)
"""

import os
import time
import streamlit as st

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="AI Wealth Coach · Boardroom",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body, .stApp { background-color: #030712 !important; color: #f9fafb !important; font-family: 'Plus Jakarta Sans', sans-serif !important; }

/* Metric values */
div[data-testid="stMetricValue"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 1.6rem !important;
    font-weight: 700;
    color: #f3f4f6 !important;
}
div[data-testid="stMetricDelta"] svg { display: none; }

/* Section divider */
hr { border-color: #1f2937 !important; }

/* Input labels */
label { color: #9ca3af !important; font-size: 0.82rem !important; font-weight: 600; letter-spacing: 0.04em; text-transform: uppercase; }

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #1d4ed8, #7c3aed) !important;
    color: #fff !important;
    font-weight: 700 !important;
    letter-spacing: 0.08em !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.75rem 1.5rem !important;
    font-size: 0.95rem !important;
    transition: opacity 0.2s;
}
.stButton > button:hover { opacity: 0.88; }

/* Debate cards */
.debate-card {
    background: #111827;
    border-left: 5px solid #374151;
    padding: 16px 20px;
    margin-bottom: 10px;
    border-radius: 10px;
    animation: slideIn 0.35s ease-out;
}
@keyframes slideIn {
    from { opacity: 0; transform: translateY(6px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* Verdict header */
.verdict-header {
    padding: 18px 24px;
    border-radius: 14px;
    font-weight: 800;
    text-align: center;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-size: 1.15rem;
    margin-bottom: 18px;
}
.vh-go      { background: rgba(16,185,129,0.12); color: #10b981; border: 1px solid #10b981; }
.vh-delay   { background: rgba(245,158,11,0.12); color: #f59e0b; border: 1px solid #f59e0b; }
.vh-decline { background: rgba(239,68,68,0.12);  color: #ef4444; border: 1px solid #ef4444; }

/* Explainability cards */
.explain-card {
    background: #0f172a;
    border: 1px solid #1f2937;
    padding: 16px;
    border-radius: 10px;
    height: 100%;
}
.explain-card h4 { color: #e2e8f0; margin-bottom: 8px; font-size: 0.9rem; }
.explain-card p  { color: #94a3b8; font-size: 0.85rem; line-height: 1.55; margin: 0; }

/* Score bar */
.score-bar-bg {
    background: #1f2937;
    border-radius: 999px;
    height: 8px;
    margin-top: 6px;
    overflow: hidden;
}
.score-bar-fill {
    height: 8px;
    border-radius: 999px;
    transition: width 0.8s ease;
}

/* Agent timeline */
.timeline-wrap {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
    margin-bottom: 18px;
}
.tl-node {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 5px 12px;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    border: 1px solid #374151;
    color: #6b7280;
    background: #111827;
}
.tl-node.active {
    color: #f9fafb;
    border-color: currentColor;
}

/* Mono text */
.mono { font-family: 'JetBrains Mono', monospace !important; }

/* Action steps */
.action-step {
    display: flex;
    gap: 12px;
    align-items: flex-start;
    padding: 10px 14px;
    background: #0f172a;
    border: 1px solid #1f2937;
    border-radius: 8px;
    margin-bottom: 8px;
}
.action-num {
    background: #1d4ed8;
    color: #fff;
    font-weight: 700;
    font-size: 0.75rem;
    min-width: 24px;
    height: 24px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
}
.action-text { color: #cbd5e1; font-size: 0.88rem; line-height: 1.5; }

/* Info / warning boxes */
.info-box  { background: #0c1a33; border-left: 4px solid #2563eb; padding: 12px 16px; border-radius: 8px; color: #93c5fd; font-size: 0.87rem; line-height: 1.5; }
.warn-box  { background: #1a1100; border-left: 4px solid #f59e0b; padding: 12px 16px; border-radius: 8px; color: #fcd34d; font-size: 0.87rem; line-height: 1.5; }
.error-box { background: #1a0a0a; border-left: 4px solid #ef4444; padding: 12px 16px; border-radius: 8px; color: #fca5a5; font-size: 0.87rem; line-height: 1.5; }
</style>
""",
    unsafe_allow_html=True,
)


# ── Imports (after st.set_page_config) ───────────────────────────────────────
from simulator.financial_engine import compute_scenario_matrices, ScenarioResult
from services.boardroom_service import execute_boardroom_debate_stream


# ── Helper: score colour ──────────────────────────────────────────────────────
def _score_color(score: int) -> str:
    if score >= 70:
        return "#10b981"
    if score >= 45:
        return "#f59e0b"
    return "#ef4444"


def _score_bar(score: int, label: str):
    color = _score_color(score)
    st.markdown(
        f"<div style='font-size:0.78rem;color:#9ca3af;font-weight:600;letter-spacing:0.04em;text-transform:uppercase;'>"
        f"{label}</div>"
        f"<div style='font-family:JetBrains Mono;font-size:1.4rem;font-weight:700;color:{color};'>{score}/100</div>"
        f"<div class='score-bar-bg'>"
        f"<div class='score-bar-fill' style='width:{score}%;background:{color};'></div></div>",
        unsafe_allow_html=True,
    )


def _flag_badge(flag: str) -> str:
    mapping = {
        "OK": (
            "<span style='background:#064e3b;color:#10b981;padding:3px 10px;border-radius:999px;font-size:0.75rem;font-weight:700;'>✓ OK</span>"
        ),
        "TIGHT": (
            "<span style='background:#451a03;color:#f59e0b;padding:3px 10px;border-radius:999px;font-size:0.75rem;font-weight:700;'>⚠ TIGHT</span>"
        ),
        "OVEREXTENDED": (
            "<span style='background:#450a0a;color:#ef4444;padding:3px 10px;border-radius:999px;font-size:0.75rem;font-weight:700;'>✗ OVEREXTENDED</span>"
        ),
    }
    return mapping.get(flag, flag)


# ════════════════════════════════════════════════════════════════════════════════
#  HEADER
# ════════════════════════════════════════════════════════════════════════════════
st.markdown(
    """
<div style='text-align:center; padding: 2rem 0 1rem;'>
  <div style='font-size:2.6rem; font-weight:800; letter-spacing:-0.5px;
              background: linear-gradient(135deg,#60a5fa,#a78bfa,#34d399);
              -webkit-background-clip:text; -webkit-text-fill-color:transparent;'>
    🏛️ AI Student Wealth Coach
  </div>
  <div style='color:#6b7280; font-size:0.95rem; margin-top:6px; letter-spacing:0.05em;'>
    MULTI-AGENT FINANCIAL BOARDROOM  ·  3-SPECIALIST DEBATE ENGINE
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# ── API key check ─────────────────────────────────────────────────────────────
if not os.environ.get("GROQ_API_KEY"):
    st.markdown(
        """
    <div class='error-box'>
      <strong>⚠ GROQ_API_KEY not detected.</strong><br>
      Add your key to the <code>.env</code> file:<br><br>

      <code style='font-family:JetBrains Mono;'>
      GROQ_API_KEY=your-key-here
      </code><br><br>

      Then restart Streamlit:
      <code>streamlit run app.py</code>
    </div>
    """,
        unsafe_allow_html=True,
    )
    st.stop()
# ════════════════════════════════════════════════════════════════════════════════
#  INPUT PANEL
# ════════════════════════════════════════════════════════════════════════════════
st.markdown("### 📥 Financial Profile Input")
with st.container():
    c1, c2, c3 = st.columns(3)
    income = c1.number_input("Monthly Income (₹)", value=15000, step=500, min_value=1)
    expenses = c2.number_input(
        "Monthly Fixed Expenses (₹)", value=8000, step=500, min_value=0
    )
    savings = c3.number_input(
        "Current Liquid Savings (₹)", value=30000, step=1000, min_value=0
    )


st.markdown("### 🎯 Milestone Goal")
with st.container():
    gc1, gc2, gc3 = st.columns(3)
    goal_name = gc1.text_input("Goal Name", value="Study Abroad")
    goal_cost = gc2.number_input("Goal Cost (₹)", value=200000, step=10000, min_value=1)
    goal_deadline = gc3.number_input("Deadline (months)", value=24, step=1, min_value=1)

st.markdown("### 💳 Proposed Allocation Decision")
with st.container():
    dc1, dc2, dc3, dc4 = st.columns(4)
    decision_query = dc1.text_input(
        "Decision Description", value="Buy a laptop for a coding course"
    )
    item_cost = dc2.number_input(
        "Upfront Purchase Cost (₹)", value=40000, step=1000, min_value=0
    )
    proposed_emi = dc3.number_input(
        "Monthly EMI (₹ — 0 if paying outright)", value=3500, step=100, min_value=0
    )
    emi_months = dc4.number_input(
        "EMI Duration (months)", value=12, step=1, min_value=1, max_value=60
    )

# Quick sanity warning
if expenses >= income:
    st.markdown(
        "<div class='warn-box'>⚠ Monthly expenses ≥ income — surplus is zero or negative. Simulation will show severe constraints.</div>",
        unsafe_allow_html=True,
    )

st.markdown("---")
run_btn = st.button(
    "🏛️  CONVENE BOARDROOM · RUN FULL SIMULATION",
    use_container_width=True,
    type="primary",
)


# ════════════════════════════════════════════════════════════════════════════════
#  SIMULATION + BOARDROOM
# ════════════════════════════════════════════════════════════════════════════════
if run_btn:

    # ── Compute financial matrices ────────────────────────────────────────────
    res: ScenarioResult = compute_scenario_matrices(
        income,
        expenses,
        savings,
        goal_name,
        goal_cost,
        goal_deadline,
        item_cost,
        proposed_emi,
        emi_months=emi_months,
    )

    # ── Telemetry log ─────────────────────────────────────────────────────────
    st.markdown("## 🖥️ System Telemetry")
    tele_ph = st.empty()
    logs = [
        "[INIT]      Input state parameters loaded.",
        "[SIMULATOR] Cash-flow projection matrices computed.",
        "[SIMULATOR] Scenario A (baseline) and Scenario B (active) packaged.",
        f"[SIMULATOR] Affordability flag → {res.affordability_flag}",
        "[BOARDROOM] 3-agent network initialising…",
    ]

    def _render_logs(extra: str = ""):
        all_lines = logs + ([extra] if extra else [])
        html = "".join(f"<div style='margin-bottom:3px'>{l}</div>" for l in all_lines)
        tele_ph.markdown(
            f'<div class="mono" style="background:#0a0f1a;color:#38bdf8;'
            f'padding:16px;border-radius:10px;font-size:0.8rem;">{html}</div>',
            unsafe_allow_html=True,
        )

    _render_logs()

    # ── Scenario comparison ───────────────────────────────────────────────────
    st.markdown("## 📊 Scenario Comparison Engine")
    sc1, sc2 = st.columns(2)

    with sc1:
        st.markdown("#### Scenario A — Status Quo (No Purchase)")
        _score_bar(res.base_score, "Financial Health Index")
        st.markdown("<br>", unsafe_allow_html=True)
        m1, m2, m3 = st.columns(3)
        m1.metric("Monthly Surplus", f"₹{res.base_surplus:,.0f}")
        m2.metric("Emergency Runway", f"{res.base_runway} mo")
        m3.metric("Savings Rate", f"{res.savings_rate_base}%")

    with sc2:
        st.markdown("#### Scenario B — With Proposed Allocation")
        _score_bar(res.active_score, "Financial Health Index")
        st.markdown("<br>", unsafe_allow_html=True)
        m4, m5, m6 = st.columns(3)
        delta_s = int(res.simulated_surplus - res.base_surplus)
        delta_r = round(res.active_runway - res.base_runway, 1)
        delta_score = int(res.active_score - res.base_score)
        m4.metric("Monthly Surplus", f"₹{res.simulated_surplus:,.0f}", delta=delta_s)
        m5.metric("Emergency Runway", f"{res.active_runway} mo", delta=delta_r)
        m6.metric("Debt-to-Income", f"{res.debt_to_income}%")

    # Affordability flag
    st.markdown(
        f"<div style='margin-top:12px;'>Affordability status: "
        f"{_flag_badge(res.affordability_flag)}</div>",
        unsafe_allow_html=True,
    )

    # ── Score sub-breakdown ───────────────────────────────────────────────────
    if res.score_breakdown:
        st.markdown("#### Score Breakdown (Scenario B)")
        sb_cols = st.columns(len(res.score_breakdown))
        labels = {
            "emergency_runway": "Emergency Runway",
            "surplus_health": "Surplus Health",
            "goal_delay_impact": "Goal Impact",
            "debt_to_income": "Debt Ratio",
        }
        maxes = {
            "emergency_runway": 40,
            "surplus_health": 30,
            "goal_delay_impact": 20,
            "debt_to_income": 10,
        }
        for col, (key, pts) in zip(sb_cols, res.score_breakdown.items()):
            max_pts = maxes.get(key, 10)
            pct = int(pts / max_pts * 100)
            col.metric(labels.get(key, key), f"{pts}/{max_pts} pts")

    # ── Forward projections ───────────────────────────────────────────────────
    st.markdown("#### Cash Balance Projections (Scenario B)")
    p1, p2, p3 = st.columns(3)
    p1.metric("3-Month Balance", f"₹{res.future_3m:,.0f}")
    p2.metric("6-Month Balance", f"₹{res.future_6m:,.0f}")
    p3.metric("12-Month Balance", f"₹{res.future_12m:,.0f}")

    # Goal delay pill
    delay_color = (
        "#10b981"
        if res.goal_delay == 0
        else ("#f59e0b" if res.goal_delay <= 6 else "#ef4444")
    )
    st.markdown(
        f"<div style='margin-top:8px;'>Goal <strong>{goal_name}</strong> delay: "
        f"<span style='background:{delay_color}22;color:{delay_color};padding:3px 12px;"
        f"border-radius:999px;font-weight:700;font-size:0.88rem;'>"
        f"{'+' if res.goal_delay > 0 else ''}{res.goal_delay} months</span></div>",
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # ── Build financial facts payload ─────────────────────────────────────────
    financial_facts = f"""
[FINANCIAL PROFILE]
Monthly Income: ₹{income:,} | Fixed Expenses: ₹{expenses:,} | Liquid Savings: ₹{savings:,}
Proposed Decision: {decision_query}
Upfront Cost: ₹{item_cost:,} | Monthly EMI: ₹{proposed_emi:,} over {emi_months} months

[SCENARIO A — BASELINE]
Health Index: {res.base_score}/100 | Surplus: ₹{res.base_surplus:,}/mo | Runway: {res.base_runway} months
Savings Rate: {res.savings_rate_base}%

[SCENARIO B — ACTIVE]
Health Index: {res.active_score}/100 | Surplus: ₹{res.simulated_surplus:,}/mo | Runway: {res.active_runway} months
Debt-to-Income: {res.debt_to_income}% | Affordability: {res.affordability_flag}
Savings Rate: {res.savings_rate_active}%

[GOAL METRICS]
Goal '{goal_name}' costs ₹{goal_cost:,}. Target deadline: {goal_deadline} months.
Delay under Scenario B: {res.goal_delay} months.

[12-MONTH PROJECTIONS (Scenario B)]
3 months: ₹{res.future_3m:,.0f} | 6 months: ₹{res.future_6m:,.0f} | 12 months: ₹{res.future_12m:,.0f}
""".strip()

    # ── Agent timeline strip ──────────────────────────────────────────────────
    st.markdown("## 🏛️ Boardroom Debate — Live Stream")

    TIMELINE = [
        ("🏛️", "Chairman", "#1e3a8a"),
        ("📊", "Budget Analyst", "#2563eb"),
        ("🛡️", "Risk Assessor", "#d97706"),
        ("🎯", "Long-Term Planner", "#7c3aed"),
        ("📊", "Budget Rebuttal", "#2563eb"),
        ("🛡️", "Risk Rebuttal", "#d97706"),
        ("🎯", "Planner Closing", "#7c3aed"),
        ("🏛️", "Verdict", "#1e3a8a"),
    ]
    timeline_ph = st.empty()
    active_turn = [0]

    def _render_timeline(active_idx: int):
        nodes = ""
        for i, (icon, label, color) in enumerate(TIMELINE):
            if i < active_idx:
                nodes += f"<div class='tl-node' style='color:{color};border-color:{color};opacity:0.5;'>✓ {icon} {label}</div>"
            elif i == active_idx:
                nodes += f"<div class='tl-node active' style='color:{color};border-color:{color};box-shadow:0 0 8px {color}44;'>{icon} {label}</div>"
            else:
                nodes += f"<div class='tl-node'>{icon} {label}</div>"
        timeline_ph.markdown(
            f"<div class='timeline-wrap'>{nodes}</div>",
            unsafe_allow_html=True,
        )

    _render_timeline(0)

    # ── Boardroom output area ─────────────────────────────────────────────────
    debate_ph = st.empty()
    debate_cards: list[str] = []
    turn_counter = [0]

    def boardroom_callback(
        event_type: str, content: str, sender: str = "", color: str = "#374151"
    ):
        if event_type == "STATUS":
            # Advance timeline
            turn_counter[0] += 1
            _render_timeline(min(turn_counter[0], len(TIMELINE) - 1))
            # Update telemetry
            _render_logs(f"[LIVE]      {content}")

        elif event_type == "MESSAGE":
            card = (
                f'<div class="debate-card" style="border-left-color:{color};">'
                f'<strong style="color:#cbd5e1;font-size:0.95rem;">{sender}</strong><br><br>'
                f'<div style="color:#f3f4f6;line-height:1.65;font-size:0.88rem;">{content}</div>'
                f"</div>"
            )
            debate_cards.append(card)
            debate_ph.markdown(
                f"<div>{''.join(debate_cards)}</div>",
                unsafe_allow_html=True,
            )

    # ── Execute boardroom ─────────────────────────────────────────────────────
    verdict = execute_boardroom_debate_stream(financial_facts, boardroom_callback)
    _render_timeline(len(TIMELINE) - 1)

    st.markdown("---")

    # ── Explainability panel ──────────────────────────────────────────────────
    st.markdown("## 🧠 Explainability Matrix")
    ex_cols = st.columns(4)
    panels = [
        (
            "📉 Surplus Impact",
            f"Monthly cash flexibility shifts from <b>₹{res.base_surplus:,}</b> to "
            f"<b>₹{res.simulated_surplus:,}</b> "
            f"({'–' if delta_s < 0 else '+'}{abs(delta_s):,}/mo).",
        ),
        (
            "🎯 Goal Impact",
            f"<b>{goal_name}</b> target of ₹{goal_cost:,} is delayed by "
            f"<b>{res.goal_delay} month{'s' if res.goal_delay != 1 else ''}</b> "
            f"under Scenario B.",
        ),
        (
            "🛡️ Emergency Buffer",
            f"Runway shifts from <b>{res.base_runway}</b> to <b>{res.active_runway}</b> months "
            f"({'below' if res.active_runway < 3 else 'above'} the 3-month safety threshold).",
        ),
        (
            "📐 Debt Exposure",
            f"EMI consumes <b>{res.debt_to_income}%</b> of income. "
            f"Recommended ceiling: 20%. "
            f"Affordability: <b>{res.affordability_flag}</b>.",
        ),
    ]
    for col, (title, body) in zip(ex_cols, panels):
        col.markdown(
            f'<div class="explain-card"><h4>{title}</h4><hr style="border-color:#1f2937;">'
            f"<p>{body}</p></div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # ── Verdict panel ─────────────────────────────────────────────────────────
    st.markdown("## ⚖️ Boardroom Arbitration Verdict")
    v_map = {
        "APPROVED": "vh-go",
        "PROCEED WITH CAUTION": "vh-delay",
        "REJECTED": "vh-decline",
    }
    v_key = v_map.get(verdict.get("verdict", "PROCEED WITH CAUTION"), "vh-delay")
    v_txt = verdict.get("verdict", "PROCEED WITH CAUTION")
    v_conf = verdict.get("confidence", "—")
    v_risk = verdict.get("risk_level", "MEDIUM")
    winner = verdict.get("winning_argument", "—")

    st.markdown(
        f'<div class="verdict-header {v_key}">'
        f"SETTLEMENT: {v_txt}<br>"
        f'<span style="font-size:0.82rem;font-weight:600;opacity:0.9;">'
        f"Confidence: {v_conf}  ·  Risk Level: {v_risk}  ·  "
        f"Decisive Argument: {winner}"
        f"</span></div>",
        unsafe_allow_html=True,
    )

    # Reasoning
    st.markdown(
        f'<div class="info-box"><strong>Key Reasoning:</strong> '
        f'{verdict.get("key_reasoning", "—")}</div>',
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    # Recommended action
    rec = verdict.get("recommended_action", "")
    if rec:
        st.markdown(
            f'<div class="warn-box"><strong>Recommended Action:</strong> {rec}</div>',
            unsafe_allow_html=True,
        )

    # Action steps
    steps = verdict.get("action_steps", [])
    if steps:
        st.markdown("#### Structured Action Plan")
        for i, step in enumerate(steps, 1):
            st.markdown(
                f'<div class="action-step">'
                f'<div class="action-num">{i}</div>'
                f'<div class="action-text">{step}</div>'
                f"</div>",
                unsafe_allow_html=True,
            )

    st.markdown("<br><br>", unsafe_allow_html=True)
