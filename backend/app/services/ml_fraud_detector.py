import pandas as pd
import joblib
import os


# -----------------------------------------
# Load trained ML model
# -----------------------------------------

MODEL_PATH = "ml/models/invoice_fraud_model.pkl"

model = joblib.load(MODEL_PATH)


# -----------------------------------------
# ML fraud prediction
# -----------------------------------------

def predict_fraud(invoice_data, duplicate=False):

    subtotal = invoice_data.get("subtotal") or 0
    gst = invoice_data.get("gst") or 0
    tax = invoice_data.get("tax") or 0
    total_amount = invoice_data.get("total_amount") or 0

    # Calculate expected total
    expected_total = subtotal + gst + tax

    # Difference between expected and actual total
    amount_difference = abs(
        expected_total - total_amount
    )

    # Count missing fields
    missing_fields = 0

    if invoice_data.get("subtotal") is None:
        missing_fields += 1

    if invoice_data.get("gst") is None:
        missing_fields += 1

    if invoice_data.get("tax") is None:
        missing_fields += 1

    if invoice_data.get("total_amount") is None:
        missing_fields += 1

    # -----------------------------------------
    # Create ML input
    # -----------------------------------------

    features = pd.DataFrame([
        {
            "subtotal": subtotal,
            "gst": gst,
            "tax": tax,
            "total_amount": total_amount,
            "amount_difference": amount_difference,
            "duplicate": int(duplicate),
            "missing_fields": missing_fields
        }
    ])

    # -----------------------------------------
    # Prediction
    # -----------------------------------------

    prediction = model.predict(features)[0]

    probabilities = model.predict_proba(features)[0]

    fraud_probability = probabilities[1]

    # -----------------------------------------
    # Return result
    # -----------------------------------------

    return {
        "prediction": int(prediction),
        "fraud_probability": round(
            float(fraud_probability),
            2
        )
    }