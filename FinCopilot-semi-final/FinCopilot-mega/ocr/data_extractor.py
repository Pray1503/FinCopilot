from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any

# ADDED: Support for hyphens and slashes in text-based dates
DATE_PATTERNS = [
    r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b",
    r"\b(\d{4}[/-]\d{1,2}[/-]\d{1,2})\b",
    r"\b(\d{1,2}[ \-\/]+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*[ \-\/]+\d{2,4})\b",
    r"\b((?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*[ \-\/]+\d{1,2},?[ \-\/]+\d{2,4})\b",
]

AMOUNT_PATTERN = r"(?:rs\.?|inr|₹|\$|usd)?\s*(?<![a-zA-Z0-9\-])([0-9]{1,3}(?:[, ]?[0-9]{3})*(?:\.\d{1,2})?|[0-9]+(?:\.\d{1,2})?)(?![a-zA-Z0-9\-])"

TOTAL_KEYWORDS = ["grand total", "net amount", "amount due", "total amount", "total", "balance due", "subtotal"]
TAX_KEYWORDS = ["gst", "tax", "cgst", "sgst", "igst", "vat"]

# ADDED: A floating ID catcher that handles spaces if Tesseract misreads hyphens
INVOICE_PATTERNS = [
    r"(?:invoice|inv|bill|receipt|order)\s*(?:no|number|#|id)?\s*[:\-]?\s*([A-Z0-9\-\/]*\d[A-Z0-9\-\/]*)",
    r"(?:^|\s)(?:no|#)\s*[:\-]?\s*([A-Z0-9\-\/]*\d[A-Z0-9\-\/]{2,})\b",
    r"\b([A-Z]{2,5}[ \-\/]+\d{4}[ \-\/]+\d{3,8})\b" 
]

PAYMENT_KEYWORDS = {
    "Cash": ["cash"],
    "Credit Card": ["credit card", "visa", "mastercard", "amex"],
    "Debit Card": ["debit card"],
    "UPI": ["upi", "gpay", "google pay", "phonepe", "paytm", "bhim"],
    "Net Banking": ["net banking", "bank transfer", "imps", "neft"],
}

VENDOR_STOPWORDS = {
    "tax invoice", "invoice", "receipt", "bill", "cash memo", "duplicate", "customer copy", "original"
}

@dataclass
class ExtractedBill:
    vendor: str = "Unknown"
    amount: float = 0.0
    tax: float = 0.0
    date: str | None = None
    invoice_number: str | None = None
    payment_method: str | None = None
    validation_warnings: list[str] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def _clean_text(text: str) -> str:
    return re.sub(r"[ \t]+", " ", text or "").strip()

def _parse_amount(value: str | None) -> float | None:
    if not value:
        return None
    normalized = value.replace(",", "").replace(" ", "")
    try:
        amount = float(normalized)
        return amount if amount >= 0 else None
    except ValueError:
        return None

def _parse_date(value: str | None) -> str | None:
    if not value:
        return None
    value = value.strip()
    formats = [
        "%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y", "%m-%d-%Y", "%Y/%m/%d", "%Y-%m-%d",
        "%d/%m/%y", "%d-%m-%y", "%m/%d/%y", "%m-%d-%y", "%d %b %Y", "%d %B %Y",
        "%b %d %Y", "%B %d %Y", "%b %d, %Y", "%B %d, %Y",
        "%d-%b-%Y", "%d-%B-%Y" # Added hyphenated formats
    ]
    for fmt in formats:
        try:
            return datetime.strptime(value.title().replace(",", ""), fmt.replace(",", "")).date().isoformat()
        except ValueError:
            continue
    return None

def extract_vendor(lines: list[str]) -> str:
    candidates = []
    for line in lines[:8]:
        clean = re.sub(r"[^A-Za-z0-9 &'.-]", "", line).strip()
        lowered = clean.lower()
        if len(clean) < 3 or lowered in VENDOR_STOPWORDS:
            continue
        if any(word in lowered for word in ["date", "invoice no", "gstin", "phone", "mobile", "email"]):
            continue
        alpha_ratio = sum(ch.isalpha() for ch in clean) / max(len(clean), 1)
        if alpha_ratio > 0.45:
            # FIX: If the parser accidentally grabs the floating ID on the right, chop it off
            return clean.split(" CN")[0][:80]
    return candidates[0][:80] if candidates else "Unknown"

def extract_date(text: str) -> str | None:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for i, line in enumerate(lines):
        if any(k in line.lower() for k in ["date", "dt"]):
            lookahead_block = " ".join(lines[i:i+3])
            for pattern in DATE_PATTERNS:
                match = re.search(pattern, lookahead_block, flags=re.IGNORECASE)
                if match:
                    parsed = _parse_date(match.group(1))
                    if parsed: return parsed

    for pattern in DATE_PATTERNS:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            parsed = _parse_date(match.group(1))
            if parsed: return parsed
    return None

def extract_amount_by_keywords(text: str, keywords: list[str]) -> float | None:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    candidates: list[float] = []
    for i, line in enumerate(lines):
        lowered = line.lower()
        if "tax invoice" in lowered: continue
        if any(keyword in lowered for keyword in keywords):
            combined_context = " ".join(lines[i:i+3])
            matches = re.findall(AMOUNT_PATTERN, combined_context, flags=re.IGNORECASE)
            for match in matches:
                amount = _parse_amount(match)
                if amount is not None: candidates.append(amount)
    return max(candidates) if candidates else None

def extract_total_amount(text: str) -> float:
    total = extract_amount_by_keywords(text, TOTAL_KEYWORDS)
    if total is not None: return total
    amounts = [_parse_amount(match) for match in re.findall(AMOUNT_PATTERN, text, flags=re.IGNORECASE)]
    numeric = [amount for amount in amounts if amount is not None and amount > 0]
    return max(numeric) if numeric else 0.0

def extract_tax_amount(text: str, amount: float) -> float:
    # UPGRADE: Add together all distinct taxes found (like CGST + SGST)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    taxes = []
    for i, line in enumerate(lines):
        lowered = line.lower()
        if "tax invoice" in lowered: continue
        if any(keyword in lowered for keyword in TAX_KEYWORDS):
            matches = re.findall(AMOUNT_PATTERN, line, flags=re.IGNORECASE)
            for match in matches:
                val = _parse_amount(match)
                # Avoid adding the grand total if it happens to be on the same line
                if val and val < amount: 
                    taxes.append(val)
    
    # If we found multiple taxes (e.g. CGST 4473 and SGST 4473), sum them
    total_tax = sum(taxes) if taxes else 0.0
    return total_tax if total_tax <= amount else 0.0

def extract_invoice_number(text: str) -> str | None:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for i, line in enumerate(lines):
        if any(k in line.lower() for k in ["invoice", "inv", "bill", "receipt", "order", "#"]):
            combined_context = " ".join(lines[i:i+3])
            for pattern in INVOICE_PATTERNS:
                match = re.search(pattern, combined_context, flags=re.IGNORECASE)
                if match: return match.group(1).strip()[:40]
    
    for pattern in INVOICE_PATTERNS:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match: return match.group(1).strip()[:40]
    return None

def extract_payment_method(text: str) -> str | None:
    lowered = text.lower()
    for method, keywords in PAYMENT_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords): return method
    return None

def extract_bill_data(raw_text: str) -> ExtractedBill:
    clean_text = _clean_text(raw_text)
    lines = [line.strip() for line in clean_text.splitlines() if line.strip()]
    amount = extract_total_amount(clean_text)
    tax = extract_tax_amount(clean_text, amount)
    
    extracted = ExtractedBill(
        vendor=extract_vendor(lines),
        amount=round(amount, 2),
        tax=round(tax, 2),
        date=extract_date(clean_text),
        invoice_number=extract_invoice_number(clean_text),
        payment_method=extract_payment_method(clean_text),
        validation_warnings=[],
    )
    extracted.validation_warnings = validate_extraction(extracted)
    return extracted

def validate_extraction(data: ExtractedBill) -> list[str]:
    warnings = []
    if data.vendor == "Unknown": warnings.append("Vendor could not be identified.")
    if data.amount <= 0: warnings.append("Total amount could not be detected.")
    if data.tax and data.tax > data.amount: warnings.append("Tax amount is higher than total amount.")
    if not data.date: warnings.append("Bill date is missing or invalid.")
    if not data.invoice_number: warnings.append("Invoice number was not found.")
    return warnings