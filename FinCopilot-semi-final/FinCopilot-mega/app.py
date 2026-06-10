"""
FinPilot — Hub Landing Page
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
The unified entry point. Displays all 7 modules with status badges.
Navigate via the sidebar — each module is a separate page.
"""

import streamlit as st
from shared.theme import inject_global_css, render_brand_sidebar

st.set_page_config(
    page_title="FinPilot",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(inject_global_css(), unsafe_allow_html=True)

render_brand_sidebar(st)

# ── Hero Section ─────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="home-brand">
        <h1>FinPilot</h1>
        <p>
            Your unified AI-powered financial intelligence platform.<br>
            7 powerful modules. One seamless experience.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<div class='section-kicker'>Features</div>", unsafe_allow_html=True)

# ── Module Cards ─────────────────────────────────────────────────────────────
modules = [
    {
        "icon": "💬", "title": "Copilot Chat",
        "desc": "Ask any financial question. AI detects intent and routes to the right expert.",
        "badge": "AI", "badge_class": "badge-ai", "page": "1_💬_Copilot_Chat",
    },
    {
        "icon": "🏛️", "title": "AI Boardroom",
        "desc": "5-agent LLM debate: Budget-Bot, Risk-Radar, Planner, Chairman, and Devil's Advocate.",
        "badge": "AI", "badge_class": "badge-ai", "page": "2_🏛️_AI_Boardroom",
    },
    {
        "icon": "📊", "title": "Smart Boardroom",
        "desc": "Pure-Python multi-agent analysis with instant calculations — no API key needed.",
        "badge": "LIVE", "badge_class": "badge-live", "page": "3_📊_Smart_Boardroom",
    },
    {
        "icon": "💰", "title": "Cash Flow",
        "desc": "Interactive dashboard with forecasting, budgets, scenario analysis, and health score.",
        "badge": "LIVE", "badge_class": "badge-live", "page": "4_💰_Cash_Flow",
    },
    {
        "icon": "💸", "title": "Decision Simulator",
        "desc": "Should you buy it? ML-powered 12-month projection with seasonal spending prediction.",
        "badge": "ML", "badge_class": "badge-ml", "page": "5_💸_Decision_Sim",
    },
    {
        "icon": "📄", "title": "Bill Scanner",
        "desc": "Upload receipts and bills. PaddleOCR extracts vendor, amount, date, and category.",
        "badge": "AI", "badge_class": "badge-ai", "page": "6_📄_Bill_Scanner",
    },
    {
        "icon": "📈", "title": "Spending Predictor",
        "desc": "Analyse spending habits, identify weekend burn, and predict next week's budget.",
        "badge": "ML", "badge_class": "badge-ml", "page": "7_📈_Spending_Pred",
    },
]

cols = st.columns(3)
for idx, mod in enumerate(modules):
    with cols[idx % 3]:
        st.markdown(
            f"""
            <div class="module-card">
                <div class="module-icon">{mod["icon"]}</div>
                <div class="module-title">{mod["title"]}</div>
                <div class="module-desc">{mod["desc"]}</div>
                <div class="module-badge {mod["badge_class"]}">{mod["badge"]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    """
    <div style="text-align:center;padding:1rem 0 2rem;">
        <p style="color:#6b7280;font-size:0.85rem;">
            Built with ❤️ using Streamlit • Navigate to any module from the sidebar →
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)
