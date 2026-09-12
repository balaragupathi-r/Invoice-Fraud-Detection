from app.services.ocr_service import extract_text
from app.services.invoice_extractor import extract_invoice_data
from app.services.fraud_detector import check_invoice_fraud


image_path = "uploads/fraud_invoice.png"

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

# Step 3: Fraud check
result = check_invoice_fraud(invoice_data)

print("\n===== FRAUD ANALYSIS =====")
print("Fraud detected:", result["fraud_detected"])
print("Risk score:", result["risk_score"])
print("Risk level:", result["risk_level"])
print("Calculation valid:", result["calculation_valid"])
print("Problems:", result["problems"])
print("==========================")