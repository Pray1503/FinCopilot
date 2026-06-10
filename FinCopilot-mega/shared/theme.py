"""
shared/theme.py
───────────────
Unified design system for FinPilot — BRIGHT EDITION.
Single source of truth for CSS, colours, and typography.
"""

FONTS_URL = "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&display=swap"

# ── Colour tokens ─────────────────────────────────────────────────────────────
BG_PRIMARY = "#f8fafc"
BG_CARD = "#ffffff"
BG_SURFACE = "#f1f5f9"
BORDER = "#e2e8f0"
TEXT_PRIMARY = "#0f172a"
TEXT_SECONDARY = "#475569"
TEXT_MUTED = "#94a3b8"
ACCENT_BLUE = "#2563eb"
ACCENT_PURPLE = "#7c3aed"
ACCENT_GREEN = "#059669"
ACCENT_AMBER = "#d97706"
ACCENT_RED = "#dc2626"
ACCENT_CYAN = "#0891b2"
ACCENT_PINK = "#db2777"

GRADIENT_HERO = "linear-gradient(135deg, #2563eb, #7c3aed, #db2777)"
GRADIENT_BUTTON = "linear-gradient(135deg, #2563eb, #7c3aed)"


def inject_global_css():
    """Return the full CSS block for injection via st.markdown."""
    return f"""
<style>
@import url('{FONTS_URL}');

*, *::before, *::after {{ box-sizing: border-box; }}

html, body, .stApp {{
    background-color: {BG_PRIMARY} !important;
    color: {TEXT_PRIMARY} !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}}

/* ── Sidebar ──────────────────────────────────────────────────── */
[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #eef2ff 0%, #faf5ff 50%, #fff1f2 100%);
    border-right: 1px solid {BORDER};
}}
[data-testid="stSidebar"] * {{
    color: #334155 !important;
}}
.brand-block {{
    padding: 0.4rem 0 1.1rem;
    margin-bottom: 0.7rem;
    border-bottom: 1px solid {BORDER};
}}
.brand-name {{
    font-size: 1.75rem;
    font-weight: 900;
    line-height: 1.05;
    color: {ACCENT_BLUE} !important;
}}
.brand-tagline {{
    color: {TEXT_SECONDARY} !important;
    font-size: 0.78rem;
    font-weight: 600;
    margin-top: 4px;
}}
.home-brand {{
    text-align: center;
    padding: 2.2rem 1rem 1.25rem;
}}
.home-brand h1 {{
    font-size: clamp(2.6rem, 5vw, 4.2rem);
    font-weight: 900;
    margin: 0;
    color: {ACCENT_BLUE} !important;
}}
.home-brand p {{
    color: {TEXT_SECONDARY};
    font-size: 1rem;
    margin: 10px auto 0;
    max-width: 620px;
}}
.section-kicker {{
    color: {TEXT_MUTED};
    font-size: 0.78rem;
    font-weight: 800;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin: 0 0 12px;
}}

/* ── Headings ─────────────────────────────────────────────────── */
h1, h2, h3, h4, h5, h6 {{ color: {TEXT_PRIMARY} !important; font-weight: 700; }}
p, span, div {{ color: {TEXT_PRIMARY}; }}

/* ── Metric values ────────────────────────────────────────────── */
div[data-testid="stMetricValue"] {{
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 1.6rem !important;
    font-weight: 700;
    color: {TEXT_PRIMARY} !important;
}}
div[data-testid="stMetricDelta"] svg {{ display: none; }}

/* ── Dividers ─────────────────────────────────────────────────── */
hr {{ border-color: {BORDER} !important; }}

/* ── Labels ───────────────────────────────────────────────────── */
label {{
    color: {TEXT_SECONDARY} !important;
    font-size: 0.82rem !important;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}}

/* ── Buttons ──────────────────────────────────────────────────── */
.stButton > button {{
    background: {GRADIENT_BUTTON} !important;
    color: #fff !important;
    font-weight: 700 !important;
    letter-spacing: 0.08em !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.75rem 1.5rem !important;
    font-size: 0.95rem !important;
    box-shadow: 0 4px 14px rgba(37,99,235,0.25) !important;
    transition: all 0.25s cubic-bezier(0.16,1,0.3,1);
}}
.stButton > button:hover {{
    box-shadow: 0 6px 20px rgba(37,99,235,0.35) !important;
    transform: translateY(-2px);
}}

/* ── Inputs ───────────────────────────────────────────────────── */
.stNumberInput input, .stTextArea textarea, .stTextInput input {{
    background: {BG_CARD} !important;
    border: 1.5px solid {BORDER} !important;
    color: {TEXT_PRIMARY} !important;
    border-radius: 10px !important;
}}
.stNumberInput input:focus, .stTextArea textarea:focus, .stTextInput input:focus {{
    border-color: {ACCENT_BLUE} !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,0.10) !important;
}}

/* ── Cards ────────────────────────────────────────────────────── */
.mega-card {{
    background: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 16px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.03);
    transition: all 0.3s cubic-bezier(0.16,1,0.3,1);
    position: relative;
    overflow: hidden;
}}
.mega-card:hover {{
    border-color: rgba(37,99,235,0.25);
    box-shadow: 0 8px 30px rgba(37,99,235,0.10);
    transform: translateY(-2px);
}}

/* ── Debate / agent cards ─────────────────────────────────────── */
.debate-card {{
    background: {BG_CARD};
    border-left: 5px solid {BORDER};
    padding: 16px 20px;
    margin-bottom: 10px;
    border-radius: 12px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    animation: slideIn 0.35s ease-out;
}}
@keyframes slideIn {{
    from {{ opacity: 0; transform: translateY(8px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}

/* ── Verdict headers ──────────────────────────────────────────── */
.verdict-header {{
    padding: 18px 24px;
    border-radius: 14px;
    font-weight: 800;
    text-align: center;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-size: 1.15rem;
    margin-bottom: 18px;
}}
.vh-go      {{ background: #ecfdf5; color: {ACCENT_GREEN}; border: 1.5px solid {ACCENT_GREEN}; }}
.vh-delay   {{ background: #fffbeb; color: {ACCENT_AMBER}; border: 1.5px solid {ACCENT_AMBER}; }}
.vh-decline {{ background: #fef2f2; color: {ACCENT_RED}; border: 1.5px solid {ACCENT_RED}; }}

/* ── Explainability cards ─────────────────────────────────────── */
.explain-card {{
    background: {BG_SURFACE};
    border: 1px solid {BORDER};
    padding: 16px;
    border-radius: 12px;
    height: 100%;
}}
.explain-card h4 {{ color: {TEXT_PRIMARY}; margin-bottom: 8px; font-size: 0.9rem; }}
.explain-card p  {{ color: {TEXT_SECONDARY}; font-size: 0.85rem; line-height: 1.55; margin: 0; }}

/* ── Score bar ────────────────────────────────────────────────── */
.score-bar-bg {{
    background: {BORDER};
    border-radius: 999px;
    height: 8px;
    margin-top: 6px;
    overflow: hidden;
}}
.score-bar-fill {{
    height: 8px;
    border-radius: 999px;
    transition: width 0.8s ease;
}}

/* ── Agent timeline ───────────────────────────────────────────── */
.timeline-wrap {{
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
    margin-bottom: 18px;
}}
.tl-node {{
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 5px 12px;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    border: 1px solid {BORDER};
    color: {TEXT_MUTED};
    background: {BG_CARD};
}}
.tl-node.active {{
    color: {ACCENT_BLUE};
    border-color: {ACCENT_BLUE};
    background: #eff6ff;
}}

/* ── Mono text ────────────────────────────────────────────────── */
.mono {{ font-family: 'JetBrains Mono', monospace !important; }}

/* ── Action steps ─────────────────────────────────────────────── */
.action-step {{
    display: flex;
    gap: 12px;
    align-items: flex-start;
    padding: 10px 14px;
    background: {BG_SURFACE};
    border: 1px solid {BORDER};
    border-radius: 10px;
    margin-bottom: 8px;
}}
.action-num {{
    background: {ACCENT_BLUE};
    color: #fff;
    font-weight: 700;
    font-size: 0.75rem;
    min-width: 24px;
    height: 24px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}}
.action-text {{ color: {TEXT_SECONDARY}; font-size: 0.88rem; line-height: 1.5; }}

/* ── Info / warning / error boxes ─────────────────────────────── */
.info-box  {{ background: #eff6ff; border-left: 4px solid {ACCENT_BLUE}; padding: 12px 16px; border-radius: 10px; color: #1e40af; font-size: 0.87rem; line-height: 1.5; }}
.warn-box  {{ background: #fffbeb; border-left: 4px solid {ACCENT_AMBER}; padding: 12px 16px; border-radius: 10px; color: #92400e; font-size: 0.87rem; line-height: 1.5; }}
.error-box {{ background: #fef2f2; border-left: 4px solid {ACCENT_RED}; padding: 12px 16px; border-radius: 10px; color: #991b1b; font-size: 0.87rem; line-height: 1.5; }}

/* ── Module cards (hub page) ──────────────────────────────────── */
.module-card {{
    background: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 18px;
    padding: 28px 24px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04), 0 6px 18px rgba(0,0,0,0.03);
    transition: all 0.35s cubic-bezier(0.16,1,0.3,1);
    cursor: pointer;
    min-height: 200px;
}}
.module-card:hover {{
    border-color: rgba(37,99,235,0.3);
    box-shadow: 0 12px 40px rgba(37,99,235,0.12);
    transform: translateY(-4px);
}}
.module-icon {{
    font-size: 2.4rem;
    margin-bottom: 14px;
}}
.module-title {{
    font-size: 1.1rem;
    font-weight: 700;
    color: {TEXT_PRIMARY};
    margin-bottom: 8px;
}}
.module-desc {{
    font-size: 0.85rem;
    color: {TEXT_SECONDARY};
    line-height: 1.5;
}}
.module-badge {{
    display: inline-block;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 0.7rem;
    font-weight: 700;
    margin-top: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}
.badge-live {{ background: #ecfdf5; color: {ACCENT_GREEN}; }}
.badge-ml   {{ background: #f5f3ff; color: {ACCENT_PURPLE}; }}
.badge-ai   {{ background: #eff6ff; color: {ACCENT_BLUE}; }}

/* ── Chat bubbles ─────────────────────────────────────────────── */
.user-bubble {{
    background: linear-gradient(135deg, #eff6ff, #eef2ff);
    border: 1px solid #c7d2fe;
    border-radius: 18px 18px 4px 18px;
    padding: 14px 18px;
    margin: 8px 0 8px 60px;
    color: {TEXT_PRIMARY};
    font-size: 0.95rem;
    line-height: 1.6;
}}
.assistant-bubble {{
    background: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 18px 18px 18px 4px;
    padding: 16px 20px;
    margin: 8px 60px 8px 0;
    color: {TEXT_PRIMARY};
    font-size: 0.95rem;
    line-height: 1.7;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}}
.intent-badge {{
    display: inline-block;
    background: #eff6ff;
    color: {ACCENT_BLUE};
    border: 1px solid #bfdbfe;
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin-bottom: 10px;
}}
.feature-card {{
    background: linear-gradient(135deg, #f0f9ff, #eff6ff);
    border: 1px solid #bfdbfe;
    border-left: 3px solid {ACCENT_BLUE};
    border-radius: 10px;
    padding: 14px 18px;
    margin: 10px 0 6px 0;
}}
.feature-card h5 {{ color: {ACCENT_BLUE}; margin: 0 0 6px; font-size: 0.85rem; }}
.feature-card p  {{ color: {TEXT_SECONDARY}; margin: 0; font-size: 0.88rem; line-height: 1.55; }}

/* ── Result inline cards (chat) ───────────────────────────────── */
.result-inline {{
    background: linear-gradient(135deg, #f0fdf4, #ecfdf5);
    border: 1px solid #86efac;
    border-radius: 12px;
    padding: 16px 18px;
    margin: 10px 0;
}}
.result-inline.warn {{
    background: linear-gradient(135deg, #fffbeb, #fef3c7);
    border-color: #fcd34d;
}}
.result-inline.danger {{
    background: linear-gradient(135deg, #fef2f2, #fee2e2);
    border-color: #fca5a5;
}}
.result-metric {{
    display: inline-block;
    background: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 10px 16px;
    margin: 4px;
    text-align: center;
    min-width: 120px;
}}
.result-metric .label {{ font-size: 0.72rem; color: {TEXT_MUTED}; text-transform: uppercase; font-weight: 600; letter-spacing: 0.05em; }}
.result-metric .value {{ font-size: 1.15rem; font-weight: 700; color: {TEXT_PRIMARY}; font-family: 'JetBrains Mono', monospace; }}

/* ── Thinking animation ───────────────────────────────────────── */
@keyframes thinking-pulse {{
    0%,100% {{ opacity: 0.4; }}
    50% {{ opacity: 1; }}
}}
.thinking-text {{
    color: {TEXT_MUTED} !important; font-size: 0.85rem;
    animation: thinking-pulse 1.5s ease-in-out infinite;
}}

/* ── Hide streamlit branding ──────────────────────────────────── */
#MainMenu {{ visibility: hidden; }}
footer {{ visibility: hidden; }}
header[data-testid="stHeader"] {{ background: transparent; }}

/* ── Plotly override for bright theme ─────────────────────────── */
.stPlotlyChart {{ background: transparent !important; }}
</style>
"""


def render_brand_sidebar(st):
    """Render the shared FinPilot sidebar brand."""
    with st.sidebar:
        st.markdown(
            """
            <div class="brand-block">
                <div class="brand-name">FinPilot</div>
                <div class="brand-tagline">AI Financial Workspace</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
