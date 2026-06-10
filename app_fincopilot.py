"""
fincopilot/app.py
-----------------
Streamlit UI for FinCopilot – AI Wealth Coach for Students.

Run with:
    streamlit run fincopilot/app.py

Imports:
    - copilot_service.py  → get_copilot_response()
    - intents.py          → INTENT_LABELS (for sidebar display)
    - feature_map.py      → FEATURE_MAP (for sidebar display)
"""

import streamlit as st
from copilot_service import get_copilot_response
from intents import INTENT_LABELS
from feature_map import get_all_features

# ──────────────────────────────────────────────
# Page Config
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="FinCopilot – AI Wealth Coach",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# Custom CSS
# ──────────────────────────────────────────────
st.markdown(
    """
<style>
    /* ── Base ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ── Hide Streamlit default chrome ── */
    #MainMenu, footer, header { visibility: hidden; }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: #0f1117;
        border-right: 1px solid #1e2130;
    }
    [data-testid="stSidebar"] * {
        color: #c9d1e0 !important;
    }

    /* ── Chat bubble – user ── */
    .user-bubble {
        background: #1a1f2e;
        border: 1px solid #2a3050;
        border-radius: 16px 16px 4px 16px;
        padding: 14px 18px;
        margin: 8px 0 8px 60px;
        color: #e2e8f0;
        font-size: 0.95rem;
        line-height: 1.6;
    }

    /* ── Chat bubble – assistant ── */
    .assistant-bubble {
        background: #0d1b2a;
        border: 1px solid #1b3a5c;
        border-radius: 16px 16px 16px 4px;
        padding: 16px 20px;
        margin: 8px 60px 8px 0;
        color: #cbd5e1;
        font-size: 0.95rem;
        line-height: 1.7;
    }

    /* ── Intent badge ── */
    .intent-badge {
        display: inline-block;
        background: #0e3460;
        color: #60a5fa;
        border: 1px solid #1e4d8c;
        border-radius: 20px;
        padding: 3px 12px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 10px;
    }

    /* ── Feature recommendation card ── */
    .feature-card {
        background: linear-gradient(135deg, #0a1628 0%, #0d2137 100%);
        border: 1px solid #1e4d8c;
        border-left: 3px solid #3b82f6;
        border-radius: 10px;
        padding: 12px 16px;
        margin: 10px 0 6px 0;
    }
    .feature-card-title {
        color: #93c5fd;
        font-weight: 600;
        font-size: 0.85rem;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    .feature-card-name {
        color: #e2e8f0;
        font-weight: 700;
        font-size: 1rem;
        margin-bottom: 4px;
    }
    .feature-card-reason {
        color: #94a3b8;
        font-size: 0.85rem;
        line-height: 1.5;
    }

    /* ── Send button ── */
    .stButton > button {
        background: #2563eb;
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 28px;
        font-weight: 600;
        font-size: 0.9rem;
        transition: background 0.2s;
        width: 100%;
    }
    .stButton > button:hover {
        background: #1d4ed8;
        border: none;
    }

    /* ── Input box ── */
    .stTextInput > div > div > input {
        background: #1a1f2e;
        color: #e2e8f0;
        border: 1px solid #2a3050;
        border-radius: 10px;
        padding: 12px 16px;
        font-size: 0.95rem;
    }
    .stTextInput > div > div > input:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 2px rgba(59,130,246,0.2);
    }

    /* ── Divider ── */
    hr { border-color: #1e2130; }

    /* ── Quick prompt chip ── */
    .stButton.chip > button {
        background: #1a1f2e;
        color: #93c5fd;
        border: 1px solid #2a3050;
        border-radius: 20px;
        padding: 6px 14px;
        font-size: 0.8rem;
        font-weight: 500;
        width: auto;
    }
    .stButton.chip > button:hover {
        background: #0e3460;
        border-color: #3b82f6;
    }
</style>
""",
    unsafe_allow_html=True,
)


# ──────────────────────────────────────────────
# Session State Init
# ──────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = ""


# ──────────────────────────────────────────────
# Sidebar
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 💰 FinCopilot")
    st.markdown("*AI Wealth Coach for Students*")
    st.markdown("---")

    st.markdown("### 🧭 Supported Intents")
    for label in INTENT_LABELS.values():
        #     feature_info = FEATURE_MAP.get(intent_key, {})
        #     feature_name = feature_info.get("feature", "—")
        st.markdown(f"**{label}**")
    # st.caption(f"→ {feature_name}")

    st.markdown("---")

    st.markdown("### 🛠 Active Modules")
    modules = [
        ("✅", "Financial Boardroom"),
        ("✅", "Decision Simulator"),
        ("✅", "Cash Flow Engine"),
        ("✅", "Spending Predictor"),
        ("✅", "OCR Bill Pipeline"),
        ("🔄", "Monthly Report"),
        ("🔄", "Rewards System"),
    ]
    for icon, name in modules:
        st.markdown(f"{icon} {name}")

    st.markdown("---")

    if st.button("🗑 Clear Chat"):
        st.session_state.messages = []
        st.rerun()


# ──────────────────────────────────────────────
# Header
# ──────────────────────────────────────────────
st.markdown("## 💬 FinCopilot Chat")
st.markdown(
    "Ask me anything about your finances — I'll detect your intent and guide you to the right tool."
)
st.markdown("---")


# ──────────────────────────────────────────────
# Quick Prompt Chips
# ──────────────────────────────────────────────
QUICK_PROMPTS = [
    "Can I afford a new laptop?",
    "Why am I overspending?",
    "Predict my cash flow next month",
    "Scan my electricity bill",
    "I need a second opinion on a big purchase",
    "What is a SIP?",
]

st.markdown("**⚡ Quick questions:**")
chip_cols = st.columns(len(QUICK_PROMPTS))
for i, prompt in enumerate(QUICK_PROMPTS):
    with chip_cols[i]:
        if st.button(prompt, key=f"chip_{i}"):
            st.session_state.pending_prompt = prompt
            st.rerun()

st.markdown("---")


# ──────────────────────────────────────────────
# Chat History Display
# ──────────────────────────────────────────────
chat_container = st.container()

with chat_container:
    for msg in st.session_state.messages:
        role = msg["role"]

        if role == "user":
            st.markdown(
                f'<div class="user-bubble">🧑 {msg["content"]}</div>',
                unsafe_allow_html=True,
            )

        elif role == "assistant":
            intent = msg.get("intent", "")
            feature = msg.get("feature", "")
            reason = msg.get("reason", "")
            response = msg.get("content", "")
            intent_label = INTENT_LABELS.get(intent, intent.replace("_", " ").title())

            assistant_html = f"""
            <div class="assistant-bubble">
                <div class="intent-badge">🎯 {intent_label}</div>
            """

            if feature:
                assistant_html += f"""
                <div class="feature-card">
                    <div class="feature-card-title">Recommended Feature</div>
                    <div class="feature-card-name">🔧 {feature}</div>
                    <div class="feature-card-reason">{reason}</div>
                </div>
                """

            assistant_html += f"""
                <div style="margin-top: 12px;">{response}</div>
            </div>
            """

            st.markdown(assistant_html, unsafe_allow_html=True)


# ──────────────────────────────────────────────
# Input Area
# ──────────────────────────────────────────────
st.markdown("---")

input_col, btn_col = st.columns([5, 1])

with input_col:
    user_input = st.text_input(
        label="user_input",
        label_visibility="collapsed",
        placeholder="Ask about your finances… e.g. 'Can I buy a new phone?'",
        value=st.session_state.pending_prompt,
        key="chat_input",
    )

with btn_col:
    send_clicked = st.button("Send ➤", key="send_btn")


# ──────────────────────────────────────────────
# Handle Send
# ──────────────────────────────────────────────
if (send_clicked or st.session_state.pending_prompt) and user_input.strip():

    # Clear the pending prompt so chips don't re-fire
    st.session_state.pending_prompt = ""

    # Append user message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input.strip(),
        }
    )

    # Call FinCopilot service
    with st.spinner("FinCopilot is thinking…"):
        result = get_copilot_response(user_input.strip())

    # DEBUG
    st.write("DEBUG RESULT:")
    st.write(result)
    st.session_state.messages.append(
        {
            "role": "assistant",
            "intent": result.get("intent", "general_finance"),
            "feature": result.get("feature", ""),
            "reason": result.get("reason", ""),
            "content": result.get(
                "response", "I couldn't process that. Please try again."
            ),
        }
    )

    st.rerun()
