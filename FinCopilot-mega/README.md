# FinPilot 🚀

> **Your unified AI-powered financial intelligence platform.**
> 7 powerful modules. One seamless experience.

## Modules

| # | Module | Type | Description |
|---|--------|------|-------------|
| 1 | 💬 **Copilot Chat** | AI | Ask any financial question — intent detection routes to the right expert |
| 2 | 🏛️ **AI Boardroom** | AI | 5-agent LLM debate (Budget-Bot, Risk-Radar, Planner, Chairman, Devil) |
| 3 | 📊 **Smart Boardroom** | Live | Pure-Python multi-agent analysis — no API key needed |
| 4 | 💰 **Cash Flow** | Live | Dashboard with forecasting, budgets, and scenario analysis |
| 5 | 💸 **Decision Simulator** | ML | Should you buy it? 12-month ML projection with seasonal patterns |
| 6 | 📄 **Bill Scanner** | AI | OCR-powered receipt scanning with SQLite storage |
| 7 | 📈 **Spending Predictor** | ML | Analyse habits, identify weekend burns, predict next week's budget |

## Quick Start

```bash
# 1. Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Mac/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up API key (for AI modules)
copy .env.example .env
# Edit .env and add your GROQ_API_KEY

# 4. Launch
streamlit run app.py
```

## API Keys

| Key | Required For | Get It At |
|-----|-------------|-----------|
| `GROQ_API_KEY` | Copilot Chat, AI Boardroom | [console.groq.com](https://console.groq.com) |

**Smart Boardroom, Cash Flow, Decision Simulator, and Spending Predictor work without any API key.**

## Optional: Bill Scanner

The Bill Scanner requires PaddleOCR which has heavy dependencies (~2GB):

```bash
pip install paddlepaddle paddleocr pypdfium2
```

## Architecture

```
FinCopilot-mega/
├── app.py                 # Hub landing page
├── pages/                 # 7 Streamlit pages
├── agents/                # All AI agents (LLM + pure-Python)
├── services/              # Groq client, copilot pipeline, boardroom orchestrator
├── simulator/             # Financial + decision simulation engines
├── copilot/               # Intent detection + feature routing
├── cashflow/              # Cash-flow data + chart builders
├── ocr/                   # OCR engine, data extraction, database
├── ml/                    # ML training, prediction, spending analysis
├── shared/                # Theme, CSS, utility functions
└── data/                  # Auto-generated data files
```

## Currency

All amounts are displayed in **₹ (Indian Rupees)**.
