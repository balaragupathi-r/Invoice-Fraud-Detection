from app.services.ocr_service import extract_text
from app.services.invoice_extractor import extract_invoice_data


image_path = "uploads/sample_invoice.png"

# Step 1: OCR
text = extract_text(image_path)

# Step 2: Extract invoice fields
invoice_data = extract_invoice_data(text)

print("\n===== RAW OCR TEXT =====")
print(text)

print("\n===== EXTRACTED INVOICE DATA =====")

for key, value in invoice_data.items():
    print(f"{key}: {value}")

print("==============================")