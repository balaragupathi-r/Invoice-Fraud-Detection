import pandas as pd
import random

data = []

for i in range(500):

    subtotal = random.randint(10000, 500000)

    gst = int(subtotal * 0.18)

    tax = int(subtotal * 0.02)

    correct_total = subtotal + gst + tax

    duplicate = random.choice([0, 0, 0, 0, 1])

    missing_fields = random.choice([0, 0, 0, 1])

    fraud = 0

    amount_difference = 0

    # Create fraudulent invoices
    if random.random() < 0.30:

        fraud = 1

        fraud_type = random.choice([
            "wrong_total",
            "duplicate",
            "missing_data"
        ])

        if fraud_type == "wrong_total":

            wrong_total = correct_total + random.randint(
                5000,
                100000
            )

            total_amount = wrong_total

            amount_difference = abs(
                correct_total - total_amount
            )

        elif fraud_type == "duplicate":

            duplicate = 1
            total_amount = correct_total

        else:

            missing_fields = random.randint(1, 3)
            total_amount = correct_total

    else:

        total_amount = correct_total

    data.append([
        subtotal,
        gst,
        tax,
        total_amount,
        amount_difference,
        duplicate,
        missing_fields,
        fraud
    ])


columns = [
    "subtotal",
    "gst",
    "tax",
    "total_amount",
    "amount_difference",
    "duplicate",
    "missing_fields",
    "fraud"
]


df = pd.DataFrame(
    data,
    columns=columns
)


df.to_csv(
    "ml/data/invoice_fraud_dataset.csv",
    index=False
)


print("Dataset created successfully")
print()
print(df.head())
print()
print("Dataset shape:", df.shape)
print()
print("Fraud distribution:")
print(df["fraud"].value_counts())