import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report


# -----------------------------------------
# 1. Load dataset
# -----------------------------------------

data = pd.read_csv(
    "ml/data/invoice_fraud_dataset.csv"
)

print("Dataset loaded successfully")
print("Dataset shape:", data.shape)


# -----------------------------------------
# 2. Separate features and target
# -----------------------------------------

X = data[
    [
        "subtotal",
        "gst",
        "tax",
        "total_amount",
        "amount_difference",
        "duplicate",
        "missing_fields"
    ]
]

y = data["fraud"]


# -----------------------------------------
# 3. Split dataset
# -----------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


print()
print("Training samples:", len(X_train))
print("Testing samples:", len(X_test))


# -----------------------------------------
# 4. Create Random Forest model
# -----------------------------------------

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)


# -----------------------------------------
# 5. Train model
# -----------------------------------------

model.fit(
    X_train,
    y_train
)

print()
print("Model training completed")


# -----------------------------------------
# 6. Make predictions
# -----------------------------------------

y_pred = model.predict(X_test)


# -----------------------------------------
# 7. Evaluate model
# -----------------------------------------

accuracy = accuracy_score(
    y_test,
    y_pred
)

print()
print("===== MODEL RESULTS =====")
print("Accuracy:", accuracy)

print()
print("Confusion Matrix:")
print(
    confusion_matrix(
        y_test,
        y_pred
    )
)

print()
print("Classification Report:")
print(
    classification_report(
        y_test,
        y_pred
    )
)


# -----------------------------------------
# 8. Save trained model
# -----------------------------------------

joblib.dump(
    model,
    "ml/models/invoice_fraud_model.pkl"
)

print()
print("Model saved successfully")
print(
    "Location: ml/models/invoice_fraud_model.pkl"
)