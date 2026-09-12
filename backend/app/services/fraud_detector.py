import re


def check_invoice_fraud(invoice_data):

    subtotal = invoice_data.get("subtotal")
    gst = invoice_data.get("gst")
    tax = invoice_data.get("tax")
    total_amount = invoice_data.get("total_amount")

    invoice_number = invoice_data.get("invoice_number")
    invoice_date = invoice_data.get("invoice_date")
    vendor_name = invoice_data.get("vendor_name")
    customer_name = invoice_data.get("customer_name")
    gstins = invoice_data.get("gstin", [])

    problems = []
    risk_score = 0

    # -----------------------------------------
    # 1. Check required fields
    # -----------------------------------------

    if not invoice_number:
        problems.append("Invoice number is missing")
        risk_score += 10

    if not invoice_date:
        problems.append("Invoice date is missing")
        risk_score += 5

    if not vendor_name:
        problems.append("Vendor name is missing")
        risk_score += 10

    if not customer_name:
        problems.append("Customer name is missing")
        risk_score += 10

    # -----------------------------------------
    # 2. Check required amounts
    # -----------------------------------------

    if subtotal is None:
        problems.append("Subtotal is missing")
        risk_score += 10

    if gst is None:
        problems.append("GST is missing")
        risk_score += 10

    if tax is None:
        problems.append("Tax is missing")
        risk_score += 10

    if total_amount is None:
        problems.append("Total amount is missing")
        risk_score += 10

    # -----------------------------------------
    # 3. Check invoice calculation
    # -----------------------------------------

    calculation_valid = False

    if (
        subtotal is not None
        and gst is not None
        and tax is not None
        and total_amount is not None
    ):

        calculated_total = subtotal + gst + tax

        if calculated_total == total_amount:
            calculation_valid = True

        else:
            problems.append(
                "Invoice total does not match subtotal + GST + tax"
            )

            risk_score += 50

    # -----------------------------------------
    # 4. Check GST calculation
    # -----------------------------------------
    # This assumes a flat 18% GST on subtotal, which only holds for
    # invoices that show GST as a single combined line. Invoices that
    # break it into components (CGST + SGST + IGST, etc.) can
    # legitimately use a different combined rate, so this check is
    # skipped when more than one GST-family component was found --
    # there's no single declared rate to validate against in that case.

    gst_component_count = invoice_data.get("gst_component_count", 1)

    if (
        subtotal is not None
        and gst is not None
        and gst_component_count <= 1
    ):

        expected_gst = round(subtotal * 0.18)

        if gst != expected_gst:

            problems.append(
                "GST amount does not match the expected 18% GST"
            )

            risk_score += 15

    # -----------------------------------------
    # 5. Check Tax calculation
    # -----------------------------------------
    # Same caveat as above: this 2% assumption only applies to the
    # single-GST-line template, not a CGST/SGST/IGST breakdown where
    # "tax" is legitimately 0 because everything is already inside gst.

    if (
        subtotal is not None
        and tax is not None
        and gst_component_count <= 1
    ):

        expected_tax = round(subtotal * 0.02)

        if tax != expected_tax:

            problems.append(
                "Tax amount does not match the expected 2% tax"
            )

            risk_score += 10

    # -----------------------------------------
    # 6. Validate GSTIN
    # -----------------------------------------

    gstin_pattern = r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][A-Z0-9]Z[A-Z0-9]$"

    if not gstins:

        problems.append("GSTIN is missing")
        risk_score += 10

    else:

        valid_gstin_found = False

        for gstin in gstins:

            if re.match(
                gstin_pattern,
                gstin.upper()
            ):
                valid_gstin_found = True
                break

        if not valid_gstin_found:

            problems.append("Invalid GSTIN format")
            risk_score += 15

    # -----------------------------------------
    # 7. Check unusually high invoice amount
    # -----------------------------------------

    if total_amount is not None:

        if total_amount > 1000000:

            problems.append(
                "Invoice amount is unusually high"
            )

            risk_score += 10

    # -----------------------------------------
    # 8. Limit risk score to 100
    # -----------------------------------------

    risk_score = min(risk_score, 100)

    # -----------------------------------------
    # 9. Determine risk level
    # -----------------------------------------

    if risk_score >= 50:

        risk_level = "HIGH"

    elif risk_score >= 20:

        risk_level = "MEDIUM"

    else:

        risk_level = "LOW"

    # -----------------------------------------
    # 10. Fraud decision
    # -----------------------------------------

    fraud_detected = risk_level == "HIGH"

    # -----------------------------------------
    # 11. Return result
    # -----------------------------------------

    return {

        "fraud_detected": fraud_detected,

        "risk_score": risk_score,

        "risk_level": risk_level,

        "calculation_valid": calculation_valid,

        "problems": problems
    }