"""Chunking strategy for invoices - chunk by service block."""

from typing import List, Dict, Any


def create_chunks_from_invoice(invoice: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Create chunks from an invoice, one per service block.

    Each chunk includes context: invoice ID, date, customer, vehicle info
    plus the service block details (complaint, cause, correction, parts, labor).
    """
    chunks = []

    if not invoice.get("service_blocks"):
        return chunks

    invoice_id = invoice.get("invoice_id", "UNKNOWN")
    date = invoice.get("date", "UNKNOWN")
    customer_name = invoice.get("customer_name", "UNKNOWN")
    vehicle = invoice.get("vehicle", {})
    year = vehicle.get("year", "UNKNOWN")
    make = vehicle.get("make", "UNKNOWN")
    model = vehicle.get("model", "UNKNOWN")
    vin = vehicle.get("vin", "UNKNOWN")
    mileage = vehicle.get("mileage", "UNKNOWN")

    for service_block in invoice["service_blocks"]:
        chunk_text = format_chunk(
            invoice_id=invoice_id,
            date=date,
            customer_name=customer_name,
            year=year,
            make=make,
            model=model,
            vin=vin,
            mileage=mileage,
            complaint=service_block.get("complaint", ""),
            cause=service_block.get("cause", ""),
            correction=service_block.get("correction", ""),
            parts=service_block.get("parts", []),
            labor_hours=service_block.get("labor_hours"),
        )

        metadata = {
            "invoice_id": str(invoice_id) if invoice_id else "UNKNOWN",
            "date": str(date) if date else "UNKNOWN",
            "customer_name": str(customer_name) if customer_name else "UNKNOWN",
            "vehicle_year": str(year) if year else "UNKNOWN",
            "vehicle_make": str(make) if make else "UNKNOWN",
            "vehicle_model": str(model) if model else "UNKNOWN",
            "vin": str(vin) if vin else "UNKNOWN",
            "mileage": str(mileage) if mileage else "UNKNOWN",
        }

        chunks.append({
            "text": chunk_text,
            "metadata": metadata,
        })

    return chunks


def format_chunk(
    invoice_id: str,
    date: str,
    customer_name: str,
    year: str,
    make: str,
    model: str,
    vin: str,
    mileage: str,
    complaint: str,
    cause: str,
    correction: str,
    parts: List[str],
    labor_hours: float = None,
) -> str:
    """Format a service block into a chunk with context."""
    parts_str = ", ".join(parts) if parts else "None listed"
    labor_str = f"{labor_hours} hours" if labor_hours else "Not specified"

    chunk = f"""Invoice: {invoice_id}
Date: {date}
Customer: {customer_name}
Vehicle: {year} {make} {model}
VIN: {vin}
Mileage: {mileage}

Complaint: {complaint}
Cause: {cause}
Correction: {correction}
Parts Used: {parts_str}
Labor: {labor_str}"""

    return chunk
