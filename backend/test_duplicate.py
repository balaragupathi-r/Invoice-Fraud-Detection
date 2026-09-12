from app.database import SessionLocal
from app.services.duplicate_detector import check_duplicate_invoice


db = SessionLocal()

invoice_data = {
    "invoice_number": "INV-2024-0789",
    "vendor_name": "BrightMart Solutions",
    "total_amount": 331200
}

result = check_duplicate_invoice(
    invoice_data,
    db
)

print("\n===== DUPLICATE CHECK =====")
print("Duplicate:", result["duplicate"])
print("Message:", result["message"])

if "existing_invoice_id" in result:
    print("Existing Invoice ID:", result["existing_invoice_id"])

print("===========================")

db.close()