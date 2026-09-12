from app.services.ml_fraud_detector import predict_fraud


# -----------------------------------------
# Genuine invoice
# -----------------------------------------

genuine_invoice = {
    "subtotal": 276000,
    "gst": 49680,
    "tax": 5520,
    "total_amount": 331200
}


result = predict_fraud(
    genuine_invoice,
    duplicate=False
)


print()
print("===== ML GENUINE INVOICE =====")
print("Prediction:", result["prediction"])
print("Fraud probability:", result["fraud_probability"])


# -----------------------------------------
# Fraudulent invoice
# -----------------------------------------

fraud_invoice = {
    "subtotal": 276000,
    "gst": 49680,
    "tax": 5520,
    "total_amount": 400000
}


result = predict_fraud(
    fraud_invoice,
    duplicate=False
)


print()
print("===== ML FRAUDULENT INVOICE =====")
print("Prediction:", result["prediction"])
print("Fraud probability:", result["fraud_probability"])