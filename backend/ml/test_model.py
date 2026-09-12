import pandas as pd
import joblib


# -----------------------------------------
# 1. Load trained model
# -----------------------------------------

model = joblib.load(
    "ml/models/invoice_fraud_model.pkl"
)

print("ML model loaded successfully")


# -----------------------------------------
# 2. Create a genuine invoice
# -----------------------------------------

genuine_invoice = pd.DataFrame([
    {
        "subtotal": 276000,
        "gst": 49680,
        "tax": 5520,
        "total_amount": 331200,
        "amount_difference": 0,
        "duplicate": 0,
        "missing_fields": 0
    }
])


# -----------------------------------------
# 3. Predict genuine invoice
# -----------------------------------------

prediction = model.predict(
    genuine_invoice
)

probability = model.predict_proba(
    genuine_invoice
)


print()
print("===== GENUINE INVOICE =====")
print("Prediction:", prediction[0])
print("Fraud probability:", probability[0][1])


# -----------------------------------------
# 4. Create suspicious invoice
# -----------------------------------------

fraud_invoice = pd.DataFrame([
    {
        "subtotal": 276000,
        "gst": 49680,
        "tax": 5520,
        "total_amount": 400000,
        "amount_difference": 68800,
        "duplicate": 0,
        "missing_fields": 0
    }
])


# -----------------------------------------
# 5. Predict fraudulent invoice
# -----------------------------------------

prediction = model.predict(
    fraud_invoice
)

probability = model.predict_proba(
    fraud_invoice
)


print()
print("===== FRAUDULENT INVOICE =====")
print("Prediction:", prediction[0])
print("Fraud probability:", probability[0][1])