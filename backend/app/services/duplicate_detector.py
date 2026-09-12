def check_duplicate_invoice(invoice_data, db):
    from app.models import Invoice

    invoice_number = invoice_data.get("invoice_number")
    vendor_name = invoice_data.get("vendor_name")
    total_amount = invoice_data.get("total_amount")

    if not invoice_number:
        return {
            "duplicate": False,
            "message": "Invoice number is missing"
        }

    existing_invoice = db.query(Invoice).filter(
        Invoice.invoice_number == invoice_number
    ).first()

    if existing_invoice:
        return {
            "duplicate": True,
            "message": "Duplicate invoice detected",
            "existing_invoice_id": existing_invoice.id
        }

    return {
        "duplicate": False,
        "message": "No duplicate invoice found"
    }