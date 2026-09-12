from app.services.fraud_detector import check_invoice_fraud


invoice_data = {
    "invoice_number": "INV-2024-0789",
    "invoice_date": "24/05/2024",
    "vendor_name": "BrightMart Solutions",
    "customer_name": "TechNova Enterprises",
    "gstin": [
        "29ABCDE1234F1Z5",
        "33XYZAB5678C1Z9"
    ],
    "subtotal": 276000,
    "gst": 49680,
    "tax": 5520,
    "total_amount": 350000
}


result = check_invoice_fraud(invoice_data)

print("\n===== FRAUD ANALYSIS =====")

print("Fraud detected:", result["fraud_detected"])
print("Risk score:", result["risk_score"])
print("Risk level:", result["risk_level"])
print("Calculation valid:", result["calculation_valid"])
print("Problems:", result["problems"])

print("==========================")