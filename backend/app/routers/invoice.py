from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session

import shutil
import os

from app.database import get_db
from app.models import Invoice

from app.services.ocr_service import extract_text

from app.services.invoice_extractor import (
    extract_invoice_data
)

from app.services.fraud_detector import (
    check_invoice_fraud
)

from app.services.duplicate_detector import (
    check_duplicate_invoice
)

from app.services.ml_fraud_detector import (
    predict_fraud
)


router = APIRouter()


# =========================================================
# UPLOAD INVOICE
# =========================================================

@router.post("/upload")
async def upload_invoice(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    # -----------------------------------------
    # 1. Create uploads folder
    # -----------------------------------------

    upload_folder = "uploads"

    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)


    # -----------------------------------------
    # 2. Save uploaded file
    # -----------------------------------------

    file_path = os.path.join(
        upload_folder,
        file.filename
    )

    with open(file_path, "wb") as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )


    # -----------------------------------------
    # 3. Run OCR
    # -----------------------------------------

    extracted_text = extract_text(
        file_path
    )


    # -----------------------------------------
    # 4. Extract invoice information
    # -----------------------------------------

    invoice_data = extract_invoice_data(
        extracted_text
    )


    # -----------------------------------------
    # 5. Rule-based fraud detection
    # -----------------------------------------

    fraud_analysis = check_invoice_fraud(
        invoice_data
    )


    # -----------------------------------------
    # 6. Duplicate invoice detection
    # -----------------------------------------

    duplicate_result = check_duplicate_invoice(
        invoice_data,
        db
    )


    if duplicate_result["duplicate"]:

        fraud_analysis["risk_score"] += 30

        fraud_analysis["problems"].append(
            "Duplicate invoice detected"
        )

        fraud_analysis["duplicate"] = True

        fraud_analysis["existing_invoice_id"] = (
            duplicate_result[
                "existing_invoice_id"
            ]
        )

    else:

        fraud_analysis["duplicate"] = False


    # -----------------------------------------
    # 7. Recalculate risk level
    # -----------------------------------------

    if fraud_analysis["risk_score"] >= 50:

        fraud_analysis["risk_level"] = "HIGH"

    elif fraud_analysis["risk_score"] >= 20:

        fraud_analysis["risk_level"] = "MEDIUM"

    else:

        fraud_analysis["risk_level"] = "LOW"


    # -----------------------------------------
    # 8. Final rule-based fraud decision
    # -----------------------------------------

    fraud_analysis["fraud_detected"] = (
        fraud_analysis["risk_level"] == "HIGH"
    )


    # -----------------------------------------
    # 9. Machine Learning prediction
    # -----------------------------------------

    ml_analysis = predict_fraud(
        invoice_data,
        duplicate=duplicate_result[
            "duplicate"
        ]
    )


    # -----------------------------------------
    # 10. Save everything in database
    # -----------------------------------------

    new_invoice = Invoice(

        filename=file.filename,

        filepath=file_path,

        uploaded_by=1,

        # OCR
        extracted_text=extracted_text,

        # Invoice data
        invoice_number=invoice_data.get(
            "invoice_number"
        ),

        invoice_date=invoice_data.get(
            "invoice_date"
        ),

        vendor_name=invoice_data.get(
            "vendor_name"
        ),

        customer_name=invoice_data.get(
            "customer_name"
        ),

        gstin=",".join(
            invoice_data.get(
                "gstin",
                []
            )
        ),

        subtotal=invoice_data.get(
            "subtotal"
        ),

        gst=invoice_data.get(
            "gst"
        ),

        tax=invoice_data.get(
            "tax"
        ),

        total_amount=invoice_data.get(
            "total_amount"
        ),

        # Rule-based fraud
        fraud_detected=str(
            fraud_analysis.get(
                "fraud_detected"
            )
        ),

        risk_score=fraud_analysis.get(
            "risk_score"
        ),

        risk_level=fraud_analysis.get(
            "risk_level"
        ),

        # ML results
        ml_prediction=ml_analysis.get(
            "prediction"
        ),

        ml_fraud_probability=str(
            ml_analysis.get(
                "fraud_probability"
            )
        )
    )


    # -----------------------------------------
    # 11. Save invoice
    # -----------------------------------------

    db.add(new_invoice)

    db.commit()

    db.refresh(new_invoice)


    # -----------------------------------------
    # 12. Return result
    # -----------------------------------------

    return {

        "message":
            "Invoice uploaded and processed successfully",


        "invoice": {

            "id":
                new_invoice.id,

            "filename":
                new_invoice.filename,

            "filepath":
                new_invoice.filepath,

            "uploaded_by":
                new_invoice.uploaded_by
        },


        "extracted_data":
            invoice_data,


        "fraud_analysis":
            fraud_analysis,


        "ml_analysis":
            ml_analysis
    }


# =========================================================
# GET SINGLE INVOICE
# =========================================================

@router.get("/id/{invoice_id}")
def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db)
):

    invoice = (
        db.query(Invoice)
        .filter(
            Invoice.id == invoice_id
        )
        .first()
    )


    # -----------------------------------------
    # Invoice not found
    # -----------------------------------------

    if not invoice:

        return {
            "message":
                "Invoice not found"
        }


    # -----------------------------------------
    # Return invoice
    # -----------------------------------------

    return {

        "invoice": {

            "id":
                invoice.id,

            "filename":
                invoice.filename,

            "filepath":
                invoice.filepath,

            "uploaded_by":
                invoice.uploaded_by,


            # =================================
            # EXTRACTED DATA
            # =================================

            "extracted_data": {

                "invoice_number":
                    invoice.invoice_number,

                "invoice_date":
                    invoice.invoice_date,

                "vendor_name":
                    invoice.vendor_name,

                "customer_name":
                    invoice.customer_name,

                "gstin":
                    invoice.gstin.split(",")
                    if invoice.gstin
                    else [],

                "subtotal":
                    invoice.subtotal,

                "gst":
                    invoice.gst,

                "tax":
                    invoice.tax,

                "total_amount":
                    invoice.total_amount
            },


            # =================================
            # RULE-BASED FRAUD ANALYSIS
            # =================================

            "fraud_analysis": {

                "fraud_detected":
                    invoice.fraud_detected
                    == "True",

                "risk_score":
                    invoice.risk_score,

                "risk_level":
                    invoice.risk_level
            },


            # =================================
            # MACHINE LEARNING ANALYSIS
            # =================================

            "ml_analysis": {

                "prediction":
                    invoice.ml_prediction,

                "fraud_probability":
                    float(
                        invoice.ml_fraud_probability
                    )
                    if invoice.ml_fraud_probability
                    else None
            }
        }
    }


# =========================================================
# GET ALL INVOICES
# =========================================================

@router.get("/")
def get_all_invoices(
    db: Session = Depends(get_db)
):

    invoices = (
        db.query(Invoice)
        .all()
    )


    return {

        "total_invoices":
            len(invoices),


        "invoices": [

            {

                "id":
                    invoice.id,

                "filename":
                    invoice.filename,

                "invoice_number":
                    invoice.invoice_number,

                "vendor_name":
                    invoice.vendor_name,

                "customer_name":
                    invoice.customer_name,

                "total_amount":
                    invoice.total_amount,


                # Rule-based
                "fraud_detected":
                    invoice.fraud_detected
                    == "True",

                "risk_score":
                    invoice.risk_score,

                "risk_level":
                    invoice.risk_level,


                # ML
                "ml_prediction":
                    invoice.ml_prediction,

                "ml_fraud_probability":
                    float(
                        invoice.ml_fraud_probability
                    )
                    if invoice.ml_fraud_probability
                    else None
            }

            for invoice in invoices
        ]
    }