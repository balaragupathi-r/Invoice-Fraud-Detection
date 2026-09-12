from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(
        String,
        nullable=False
    )

    email = Column(
        String,
        unique=True,
        nullable=False
    )

    password = Column(
        String,
        nullable=False
    )


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    filename = Column(
        String,
        nullable=False
    )

    filepath = Column(
        String,
        nullable=False
    )

    uploaded_by = Column(
        Integer,
        ForeignKey("users.id")
    )

    # =========================================
    # OCR DATA
    # =========================================

    extracted_text = Column(String)

    # =========================================
    # EXTRACTED INVOICE DATA
    # =========================================

    invoice_number = Column(String)

    invoice_date = Column(String)

    vendor_name = Column(String)

    customer_name = Column(String)

    gstin = Column(String)

    subtotal = Column(Integer)

    gst = Column(Integer)

    tax = Column(Integer)

    total_amount = Column(Integer)

    # =========================================
    # RULE-BASED FRAUD DETECTION
    # =========================================

    fraud_detected = Column(String)

    risk_score = Column(Integer)

    risk_level = Column(String)

    # =========================================
    # MACHINE LEARNING RESULTS
    # =========================================

    ml_prediction = Column(Integer)

    ml_fraud_probability = Column(String)