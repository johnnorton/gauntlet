"""PDF extraction and parsing for truck service invoices."""

import re
from pathlib import Path
from typing import Optional, Dict, Any, List
import pdfplumber


def extract_invoice_text(pdf_path: str) -> Optional[str]:
    """Extract all text from a PDF file."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
            return text
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return None


def parse_invoice(text: str, pdf_filename: str) -> Optional[Dict[str, Any]]:
    """Parse invoice text into structured data."""
    if not text:
        return None

    invoice = {
        "filename": pdf_filename,
        "invoice_id": None,
        "date": None,
        "customer_name": None,
        "customer_email": None,
        "vehicle": {
            "year": None,
            "make": None,
            "model": None,
            "vin": None,
            "mileage": None,
        },
        "service_blocks": [],
    }

    # Extract Invoice ID
    invoice_match = re.search(r"Invoice[:\s]+([A-Z0-9]+)", text)
    if invoice_match:
        invoice["invoice_id"] = invoice_match.group(1)

    # Extract Date
    date_match = re.search(r"Date[:\s]+(\d{1,2}/\d{1,2}/\d{4})", text)
    if date_match:
        invoice["date"] = date_match.group(1)

    # Extract Customer Name and Email
    customer_match = re.search(r"Customer[:\s]+([^\n]+)", text)
    if customer_match:
        customer_info = customer_match.group(1).strip()
        # Try to split name and email
        if "@" in customer_info:
            parts = customer_info.split("@")
            invoice["customer_name"] = parts[0].strip()
            invoice["customer_email"] = customer_info.strip()
        else:
            invoice["customer_name"] = customer_info

    # Extract Vehicle Info
    vehicle_match = re.search(
        r"Vehicle[:\s]+(\d{4})\s+([A-Za-z ]+?)\s+([A-Za-z0-9 ]+?)(?:\n|$)",
        text
    )
    if vehicle_match:
        invoice["vehicle"]["year"] = vehicle_match.group(1)
        invoice["vehicle"]["make"] = vehicle_match.group(2).strip()
        invoice["vehicle"]["model"] = vehicle_match.group(3).strip()

    # Extract VIN
    vin_match = re.search(r"VIN[:\s]+([A-Z0-9]+)", text)
    if vin_match:
        invoice["vehicle"]["vin"] = vin_match.group(1)

    # Extract Mileage
    mileage_match = re.search(r"Mileage[:\s]+([0-9,]+)", text)
    if mileage_match:
        invoice["vehicle"]["mileage"] = mileage_match.group(1)

    # Extract Service Blocks
    # Split by "Service Block" or "Complaint:" pattern
    service_blocks = re.split(r"(?:Service Block \d+[:\s]*|(?=Complaint:))", text)

    for block_text in service_blocks[1:]:  # Skip header before first block
        service_block = parse_service_block(block_text)
        if service_block:
            invoice["service_blocks"].append(service_block)

    return invoice if invoice["invoice_id"] else None


def parse_service_block(text: str) -> Optional[Dict[str, Any]]:
    """Parse a single service block from invoice text."""
    block = {
        "complaint": None,
        "cause": None,
        "correction": None,
        "labor_hours": None,
        "labor_rate": None,
        "parts": [],
    }

    # Extract Complaint
    complaint_match = re.search(r"Complaint[:\s]+([^\n]+(?:\n(?!Cause|Correction|Labor|Parts)[^\n]*)*)", text, re.IGNORECASE)
    if complaint_match:
        block["complaint"] = complaint_match.group(1).strip()

    # Extract Cause
    cause_match = re.search(r"Cause[:\s]+([^\n]+(?:\n(?!Correction|Labor|Parts|Complaint)[^\n]*)*)", text, re.IGNORECASE)
    if cause_match:
        block["cause"] = cause_match.group(1).strip()

    # Extract Correction
    correction_match = re.search(r"Correction[:\s]+([^\n]+(?:\n(?!Labor|Parts|Complaint|Cause)[^\n]*)*)", text, re.IGNORECASE)
    if correction_match:
        block["correction"] = correction_match.group(1).strip()

    # Extract Labor
    labor_match = re.search(r"Labor[:\s]+([0-9.]+)\s*hrs?\s*@?\s*\$?([0-9.]+)?", text, re.IGNORECASE)
    if labor_match:
        block["labor_hours"] = float(labor_match.group(1))
        if labor_match.group(2):
            block["labor_rate"] = float(labor_match.group(2))

    # Extract Parts
    parts_match = re.search(r"Parts[:\s]+([^\n]+(?:\n(?!Labor|Complaint|Cause|Correction)[^\n]*)*)", text, re.IGNORECASE)
    if parts_match:
        parts_text = parts_match.group(1).strip()
        # Split by newline or comma to get individual parts
        parts_list = re.split(r"[,\n]", parts_text)
        block["parts"] = [p.strip() for p in parts_list if p.strip()]

    # Only return if we have at least complaint/cause/correction
    if block["complaint"] or block["cause"] or block["correction"]:
        return block

    return None


def extract_and_parse_invoice(pdf_path: str) -> Optional[Dict[str, Any]]:
    """Extract and parse a single invoice PDF."""
    text = extract_invoice_text(pdf_path)
    if not text:
        return None

    pdf_filename = Path(pdf_path).name
    return parse_invoice(text, pdf_filename)
