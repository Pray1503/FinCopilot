"""
FinPilot — FastAPI Backend
━━━━━━━━━━━━━━━━━━━━━━━━━━
REST API wrapper for all FinPilot Python modules.
Run: uvicorn api.main:app --reload --port 8000
"""

import sys
from pathlib import Path

# ── Ensure parent dir is on PYTHONPATH so we can import existing modules ─────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import traceback
import json
import io

# ── App setup ────────────────────────────────────────────────────────────────
app = FastAPI(title="FinPilot API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Pydantic Request / Response Models
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class ChatRequest(BaseModel):
    query: str
    profile: Optional[dict] = None


class BoardroomRequest(BaseModel):
    scenario: dict = Field(default_factory=lambda: {
        "income_monthly": 15000,
        "monthly_expenses": 9000,
        "savings": 20000,
        "existing_debt_monthly_EMI": 0,
        "requested_loan_amount": 50000,
        "proposed_EMI": 2500,
        "expected_skill_earning_uplift_pct": 20,
        "emergency_fund_amount": 10000,
        "course_length_months": 6,
    })
    question: str = "Should I take this loan for a coding bootcamp?"


class SimulatorRequest(BaseModel):
    income: float = 15000
    current_savings: float = 20000
    base_expenses: float = 9000
    item_name: str = "Laptop"
    cost: float = 45000
    goal_name: str = "Savings Goal"
    goal_target: float = 100000
    goal_current: float = 20000
    goal_alloc: float = 3000


class MLPredictRequest(BaseModel):
    month_idx: int = 6
    is_exam: int = 0
    is_fest: int = 0
    prev_expense: float = 9000


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Health
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "FinPilot API", "version": "2.0.0"}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. Copilot Chat
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.post("/api/copilot/chat")
def copilot_chat(req: ChatRequest):
    """Send a query, get AI response with intent detection and feature execution."""
    try:
        from services.feature_executor import execute_query
        result = execute_query(req.query, req.profile)
        # feature_data may contain non-serializable items — sanitize
        feature_data = result.get("feature_data")
        if feature_data:
            # Convert any pandas objects or numpy types
            feature_data = _sanitize(feature_data)
        return {
            "intent": result.get("intent", "general"),
            "confidence": result.get("confidence", 0.0),
            "response": result.get("response", ""),
            "feature_html": result.get("feature_html", ""),
            "feature_data": feature_data,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. AI Boardroom (LLM-powered)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.post("/api/boardroom/run")
def boardroom_run(req: BoardroomRequest):
    """Run the 5-agent AI boardroom debate."""
    try:
        from services.boardroom_service import run_boardroom
        result = run_boardroom(req.scenario, req.question)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. Smart Boardroom (Pure Python)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.post("/api/boardroom/smart")
def boardroom_smart(req: BoardroomRequest):
    """Run the pure-Python boardroom analysis (no LLM needed)."""
    try:
        from agents.budget_analyst import run as run_budget
        from agents.risk_assessor import run as run_risk
        from agents.long_term_planner import run as run_planner
        from agents.coordinator import run as run_coordinator

        budget = run_budget(req.scenario)
        risk = run_risk(req.scenario)
        planner = run_planner(req.scenario)
        coord = run_coordinator(budget, planner, risk, req.question, req.scenario)

        return {
            "verdict": coord.get("combined_verdict", "unknown"),
            "budget": _sanitize(budget),
            "risk": _sanitize(risk),
            "planner": _sanitize(planner),
            "coordinator": _sanitize(coord),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. Cash Flow
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.get("/api/cashflow/data")
def cashflow_data():
    """Get historical + forecast cash flow data."""
    try:
        from cashflow.engine import generate_cash_flow_data
        hist, forecast = generate_cash_flow_data()
        return {
            "historical": hist.to_dict(orient="records"),
            "forecast": forecast.to_dict(orient="records"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/cashflow/transactions")
def cashflow_transactions():
    """Get synthetic transaction data."""
    try:
        from cashflow.engine import generate_transactions
        txns = generate_transactions()
        return {"transactions": txns.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/cashflow/health")
def cashflow_health():
    """Get financial health score and metrics."""
    try:
        from cashflow.engine import generate_cash_flow_data
        hist, forecast = generate_cash_flow_data()

        balance = float(hist["balance"].iloc[-1])
        inflow_30 = float(hist.tail(30)["inflow"].sum())
        outflow_30 = float(hist.tail(30)["outflow"].sum())
        net_30 = inflow_30 - outflow_30
        predicted = float(forecast.tail(30)["balance"].iloc[-1])

        # Simple health score
        ratio = inflow_30 / max(outflow_30, 1)
        if ratio >= 1.3:
            score = 90
        elif ratio >= 1.15:
            score = 75
        elif ratio >= 1.0:
            score = 55
        else:
            score = 30

        return {
            "score": score,
            "balance": round(balance),
            "inflow_30d": round(inflow_30),
            "outflow_30d": round(outflow_30),
            "net_30d": round(net_30),
            "predicted_balance": round(predicted),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 5. Decision Simulator
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.post("/api/simulator/run")
def simulator_run(req: SimulatorRequest):
    """Run the purchase decision simulation."""
    try:
        from simulator.decision_engine import simulate_purchase
        result = simulate_purchase(
            income=req.income,
            current_savings=req.current_savings,
            base_expenses=req.base_expenses,
            item_name=req.item_name,
            cost=req.cost,
            goal_name=req.goal_name,
            goal_target=req.goal_target,
            goal_current=req.goal_current,
            goal_alloc=req.goal_alloc,
        )
        return _sanitize(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6. Spending Analysis
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.get("/api/spending/summary")
def spending_summary():
    """Get spending analysis and prediction."""
    try:
        csv_path = PROJECT_ROOT / "data" / "student_spending.csv"
        if not csv_path.exists():
            raise HTTPException(status_code=404, detail="Spending data not found")
        from ml.spending_predictor import SpendingPredictor
        pred = SpendingPredictor(str(csv_path))
        return pred.get_summary()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/spending/predict")
def spending_predict(req: MLPredictRequest):
    """Run ML spending prediction."""
    try:
        from ml.predict import predict_spend, is_model_available
        if not is_model_available():
            raise HTTPException(status_code=404, detail="ML model not available")
        result = predict_spend(req.month_idx, req.is_exam, req.is_fest, req.prev_expense)
        if result is None:
            raise HTTPException(status_code=500, detail="Prediction failed")
        return {"predicted_spend": result, "month": req.month_idx}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 7. Bill Scanner (OCR)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Global PaddleOCR reader (lazy singleton, avoids Streamlit dependency)
_ocr_reader = None


def _get_ocr_reader():
    """Get or create the PaddleOCR reader (replaces the Streamlit-cached version)."""
    global _ocr_reader
    if _ocr_reader is not None:
        return _ocr_reader

    import os
    os.environ["FLAGS_enable_pir_api"] = "0"
    os.environ["FLAGS_enable_pir_in_executor"] = "0"
    os.environ["FLAGS_use_mkldnn"] = "0"
    os.environ["FLAGS_enable_onednn_optims"] = "0"
    os.environ["MKLDNN_CACHE_CAPACITY"] = "0"
    os.environ.setdefault("PADDLE_LOG_LEVEL", "3")

    from contextlib import redirect_stdout, redirect_stderr
    from paddleocr import PaddleOCR

    configs = [
        {"use_angle_cls": True, "lang": "en", "enable_mkldnn": False},
        {"lang": "en", "enable_mkldnn": False},
        {"lang": "en"},
        {},
    ]
    for config in configs:
        try:
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                _ocr_reader = PaddleOCR(**config)
                return _ocr_reader
        except TypeError:
            continue
    raise RuntimeError("Could not initialise PaddleOCR")


@app.post("/api/bills/scan")
async def scan_bill(file: UploadFile = File(...)):
    """Upload and scan a bill/receipt image using PaddleOCR."""
    try:
        import numpy as np
        from PIL import Image, ImageOps
        from contextlib import redirect_stdout, redirect_stderr

        # Read uploaded file
        content = await file.read()
        ext = (file.filename or "").rsplit(".", 1)[-1].lower()

        # Convert to images
        images = []
        if ext in ("jpg", "jpeg", "png"):
            img = Image.open(io.BytesIO(content))
            img = ImageOps.exif_transpose(img)
            images = [img.convert("RGB")]
        elif ext == "pdf":
            try:
                import pypdfium2 as pdfium
                pdf = pdfium.PdfDocument(content)
                for i in range(len(pdf)):
                    bmp = pdf[i].render(scale=2.0).to_pil()
                    images.append(bmp.convert("RGB"))
            except ImportError:
                raise HTTPException(status_code=400, detail="PDF support requires pypdfium2")
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

        if not images:
            raise HTTPException(status_code=400, detail="No readable pages in file")

        # Run OCR
        reader = _get_ocr_reader()
        all_lines = []
        confidences = []
        all_items = []

        for page_num, img in enumerate(images, 1):
            gray = ImageOps.grayscale(img)
            processed = ImageOps.autocontrast(gray).convert("RGB")
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                result = reader.ocr(np.array(processed))

            page_result = result[0] if result and isinstance(result, list) else []
            if isinstance(result, dict):
                texts = result.get("rec_texts", [])
                scores = result.get("rec_scores", [])
                for i, text in enumerate(texts):
                    s = scores[i] if i < len(scores) else 0
                    all_lines.append(str(text).strip())
                    confidences.append(float(s))
                continue

            if not page_result:
                continue

            for line in page_result:
                bbox, (text, conf) = line
                text = str(text).strip()
                if not text:
                    continue
                all_lines.append(text)
                confidences.append(float(conf))
                all_items.append({
                    "page": page_num,
                    "text": text,
                    "confidence": round(float(conf), 4),
                })

        raw_text = "\n".join(all_lines)
        avg_conf = round((sum(confidences) / len(confidences)) * 100, 2) if confidences else 0.0

        if not raw_text.strip():
            raise HTTPException(status_code=422, detail="OCR could not detect readable text")

        # Extract structured data
        from ocr.data_extractor import extract_bill_data
        from ocr.categorizer import categorize_expense

        bill = extract_bill_data(raw_text)
        category, scores = categorize_expense(bill.vendor, raw_text)

        # Save to database
        from ocr.database import add_bill

        bill_id = add_bill(
            vendor=bill.vendor,
            amount=bill.amount,
            tax=bill.tax,
            date=bill.date,
            category=category,
            invoice_number=bill.invoice_number,
            image_path=file.filename or "unknown",
            raw_text=raw_text,
            ocr_confidence=avg_conf,
            payment_method=bill.payment_method,
            extraction_json=json.dumps(bill.to_dict()),
        )

        return {
            "bill_id": bill_id,
            "vendor": bill.vendor,
            "amount": bill.amount,
            "tax": bill.tax,
            "date": bill.date,
            "category": category,
            "invoice_number": bill.invoice_number,
            "payment_method": bill.payment_method,
            "ocr_confidence": avg_conf,
            "raw_text": raw_text,
            "line_count": len(all_lines),
            "warnings": bill.validation_warnings,
        }
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/bills/list")
def list_bills(search: str = "", category: str = ""):
    """Get all scanned bills from the database."""
    try:
        from ocr.database import get_bills
        cat = category if category and category != "All" else None
        df = get_bills(search=search, category=cat)
        records = df.to_dict(orient="records") if not df.empty else []
        return {"bills": records, "total": len(records)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/bills/metrics")
def bill_metrics():
    """Get bill scanning dashboard metrics."""
    try:
        from ocr.database import get_bills
        from ocr.dashboard import dashboard_metrics, spending_pattern_analysis, financial_health_score
        df = get_bills()
        metrics = dashboard_metrics(df)
        patterns = spending_pattern_analysis(df)
        score, insights = financial_health_score(df)
        return {
            "metrics": metrics,
            "patterns": _sanitize(patterns),
            "health_score": score,
            "insights": insights,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/bills/{bill_id}")
def delete_bill_endpoint(bill_id: int):
    """Delete a scanned bill."""
    try:
        from ocr.database import delete_bill
        delete_bill(bill_id)
        return {"deleted": bill_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Utility
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _sanitize(obj):
    """Convert non-JSON-serializable types (numpy, pandas, etc.) to native Python."""
    import numpy as np
    import pandas as pd

    if isinstance(obj, dict):
        return {k: _sanitize(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_sanitize(v) for v in obj]
    elif isinstance(obj, (np.integer,)):
        return int(obj)
    elif isinstance(obj, (np.floating,)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.DataFrame):
        return obj.to_dict(orient="records")
    elif isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    elif isinstance(obj, (pd.Series,)):
        return obj.tolist()
    return obj
