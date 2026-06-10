"""
Page 6 — Bill Scanner
━━━━━━━━━━━━━━━━━━━━━
OCR-powered bill scanning with PaddleOCR.
Upload receipts → extract data → categorize → save to SQLite.
"""

import sys
import json
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import streamlit as st

from shared.theme import inject_global_css, render_brand_sidebar
from shared import money_precise

st.set_page_config(page_title="Bill Scanner • FinPilot", page_icon="📄", layout="wide")
st.markdown(inject_global_css(), unsafe_allow_html=True)
render_brand_sidebar(st)

st.markdown(
    """
    <div style="padding:1.5rem 0 0.5rem;">
        <h1 style="font-size:2.2rem;font-weight:800;margin:0;
            background:linear-gradient(135deg,#06b6d4,#34d399);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
            📄 Bill Scanner
        </h1>
        <p style="color:#9ca3af;font-size:0.95rem;margin-top:6px;">
            Upload bills and receipts — PaddleOCR extracts vendor, amount, date, and category automatically.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Check PaddleOCR availability ──────────────────────────────────────────
try:
    from ocr.ocr_engine import save_uploaded_file, load_uploaded_file_as_images, run_ocr_on_images
    from ocr.data_extractor import extract_bill_data
    from ocr.categorizer import CATEGORIES, categorize_expense
    from ocr.database import init_db, get_bills, add_bill, update_bill, delete_bill
    from ocr.dashboard import (
        dashboard_metrics, category_pie_chart, monthly_trend_chart,
        top_categories_chart, financial_health_score, spending_pattern_analysis,
    )
    from ocr.reports import monthly_expense_report, category_report, to_csv_bytes, to_excel_bytes

    PADDLE_AVAILABLE = True
    PADDLE_IMPORT_ERROR = ""
    init_db()
except ImportError as exc:
    PADDLE_AVAILABLE = False
    PADDLE_IMPORT_ERROR = str(exc)

if not PADDLE_AVAILABLE:
    st.markdown(
        f"""
        <div class='warn-box'>
            ⚠️ <strong>PaddleOCR not installed.</strong> The Bill Scanner requires:
            <code>paddlepaddle</code>, <code>paddleocr</code>, and <code>pypdfium2</code>.<br><br>
            Install them with: <code>pip install paddlepaddle paddleocr pypdfium2</code><br><br>
            Details: <code>{PADDLE_IMPORT_ERROR}</code>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

# ── Navigation ────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "📤 Upload", "📋 History", "📈 Reports"])

# ═══════ Dashboard ═══════════════════════════════════════════════════════
with tab1:
    bills = get_bills()
    metrics = dashboard_metrics(bills)
    health, insights = financial_health_score(bills)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Expenses", money_precise(metrics["total"]))
    c2.metric("Bills Scanned", f"{metrics['count']}")
    c3.metric("Average Bill", money_precise(metrics["average"]))
    c4.metric("Health Score", f"{health}/100")

    left, right = st.columns(2)
    with left:
        st.plotly_chart(category_pie_chart(bills), use_container_width=True)
    with right:
        st.plotly_chart(monthly_trend_chart(bills), use_container_width=True)
    st.plotly_chart(top_categories_chart(bills), use_container_width=True)

    if insights:
        st.markdown("### 💡 Insights")
        for insight in insights:
            st.info(insight)

# ═══════ Upload ══════════════════════════════════════════════════════════
with tab2:
    history = get_bills()
    uploaded_files = st.file_uploader(
        "Upload one or more bills",
        type=["jpg", "jpeg", "png", "pdf"],
        accept_multiple_files=True,
    )
    if not uploaded_files:
        st.markdown(
            "<div class='info-box'>📎 Drop bill images or PDFs here to extract data automatically.</div>",
            unsafe_allow_html=True,
        )
    else:
        for uploaded_file in uploaded_files:
            st.markdown("<div class='mega-card'>", unsafe_allow_html=True)
            st.subheader(uploaded_file.name)
            try:
                saved_path = save_uploaded_file(uploaded_file)
                images = load_uploaded_file_as_images(uploaded_file)
                col_img, col_res = st.columns([0.9, 1.1])
                with col_img:
                    st.image(images[0], use_container_width=True)

                with st.spinner("Reading bill with PaddleOCR..."):
                    ocr_result = run_ocr_on_images(images)

                extracted = extract_bill_data(ocr_result["raw_text"]).to_dict()
                category, scores = categorize_expense(extracted["vendor"], ocr_result["raw_text"], history)

                with col_res:
                    st.markdown(f"**Vendor:** {extracted.get('vendor', 'Unknown')}")
                    st.markdown(f"**Amount:** {money_precise(float(extracted.get('amount', 0)))}")
                    st.markdown(f"**Date:** {extracted.get('date', 'Missing')}")
                    st.markdown(f"**Category:** {category}")
                    st.markdown(f"**OCR Confidence:** {ocr_result['confidence']:.1f}%")
                    with st.expander("Raw OCR text"):
                        st.text(ocr_result["raw_text"])
                    st.markdown("### Save Bill")
                    with st.form(f"save_{saved_path.name}"):
                        vendor = st.text_input("Vendor", value=extracted["vendor"])
                        amount = st.number_input("Amount", value=float(extracted["amount"] or 0), step=1.0)
                        tax = st.number_input("Tax", value=float(extracted["tax"] or 0), step=1.0)
                        bill_date = st.date_input("Date", value=date.today())
                        selected_cat = st.selectbox("Category", CATEGORIES, index=CATEGORIES.index(category) if category in CATEGORIES else len(CATEGORIES) - 1)
                        if st.form_submit_button("💾 Save Bill", type="primary", use_container_width=True):
                            add_bill(
                                vendor=vendor, amount=float(amount), tax=float(tax),
                                date=bill_date.isoformat(), category=selected_cat,
                                invoice_number=extracted.get("invoice_number"),
                                image_path=str(saved_path), raw_text=ocr_result["raw_text"],
                                ocr_confidence=float(ocr_result["confidence"]),
                                payment_method=extracted.get("payment_method"),
                                extraction_json=json.dumps({"extracted": extracted, "scores": scores}),
                            )
                            st.success("Bill saved!")
            except Exception as e:
                st.error(f"Could not process: {e}")
                with st.expander("Technical details"):
                    st.exception(e)
            st.markdown("</div>", unsafe_allow_html=True)

# ═══════ History ═════════════════════════════════════════════════════════
with tab3:
    all_bills = get_bills()
    if all_bills.empty:
        st.info("No bills saved yet. Upload some bills first!")
    else:
        visible = ["id", "date", "vendor", "category", "amount", "tax", "payment_method", "ocr_confidence"]
        st.dataframe(all_bills[[c for c in visible if c in all_bills.columns]], use_container_width=True, hide_index=True)

# ═══════ Reports ═════════════════════════════════════════════════════════
with tab4:
    bills = get_bills()
    if bills.empty:
        st.info("Scan some bills to generate reports.")
    else:
        monthly = monthly_expense_report(bills)
        categories = category_report(bills)
        r1, r2 = st.tabs(["Monthly Report", "Category Report"])
        with r1:
            st.dataframe(monthly, use_container_width=True, hide_index=True)
        with r2:
            st.dataframe(categories, use_container_width=True, hide_index=True)

        st.download_button("📥 Download CSV", data=to_csv_bytes(bills.drop(columns=["raw_text"], errors="ignore")),
                           file_name="finpilot_bills.csv", mime="text/csv")
