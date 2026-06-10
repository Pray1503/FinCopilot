"""
Page 1 — Copilot Chat
━━━━━━━━━━━━━━━━━━━━━
Smart AI chat with intent detection. Ask any financial question.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
from shared.theme import inject_global_css, render_brand_sidebar

st.set_page_config(page_title="Copilot Chat • FinPilot", page_icon="💬", layout="wide")
st.markdown(inject_global_css(), unsafe_allow_html=True)
render_brand_sidebar(st)

# ── Header ────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div style="padding:1.5rem 0 0.5rem;">
        <h1 style="font-size:2.2rem;font-weight:800;margin:0;
            background:linear-gradient(135deg,#60a5fa,#a78bfa);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
            💬 Copilot Chat
        </h1>
        <p style="color:#9ca3af;font-size:0.95rem;margin-top:6px;">
            Ask any financial question — the AI detects your intent and routes to the right expert.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Chat State ────────────────────────────────────────────────────────────
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

# ── Display History ───────────────────────────────────────────────────────
for msg in st.session_state.chat_messages:
    if msg["role"] == "user":
        st.markdown(f"<div class='user-bubble'>{msg['content']}</div>", unsafe_allow_html=True)
    else:
        intent_html = ""
        if msg.get("intent"):
            intent_html = f"<div class='intent-badge'>🎯 {msg['intent']} — {int(msg.get('confidence', 0) * 100)}% match</div>"
        st.markdown(
            f"<div class='assistant-bubble'>{intent_html}{msg['content']}</div>",
            unsafe_allow_html=True,
        )

# ── Input ─────────────────────────────────────────────────────────────────
query = st.chat_input("Ask me anything about your finances...")

if query:
    st.session_state.chat_messages.append({"role": "user", "content": query})
    st.markdown(f"<div class='user-bubble'>{query}</div>", unsafe_allow_html=True)

    with st.spinner(""):
        st.markdown("<div class='thinking-text'>🧠 Analyzing your question...</div>", unsafe_allow_html=True)
        try:
            from services.copilot_service import process_query
            result = process_query(query)
            response = result["response"]
            intent = result["intent"]
            confidence = result["confidence"]
        except Exception as e:
            response = f"Sorry, I encountered an error: {e}"
            intent = "error"
            confidence = 0.0

    st.session_state.chat_messages.append({
        "role": "assistant",
        "content": response,
        "intent": intent,
        "confidence": confidence,
    })
    st.rerun()

# ── Quick Prompts ─────────────────────────────────────────────────────────
if not st.session_state.chat_messages:
    st.markdown("### 💡 Try asking...")
    cols = st.columns(3)
    prompts = [
        "Should I take a ₹50,000 education loan?",
        "How should I budget my ₹20,000 monthly income?",
        "What's a good SIP to start with ₹500/month?",
        "Can I afford to buy AirPods if I earn ₹15,000?",
        "How do I build an emergency fund?",
        "What are the risks of taking a personal loan?",
    ]
    for idx, prompt in enumerate(prompts):
        with cols[idx % 3]:
            st.markdown(
                f"""
                <div class="mega-card" style="min-height:auto;padding:16px;cursor:pointer;">
                    <div style="font-size:0.88rem;color:#cbd5e1;">{prompt}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
