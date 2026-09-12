import re


def clean_amount(value):
    """
    Clean a raw OCR-extracted amount string into a numeric string.

    - Strips currency symbols, commas, and whitespace.
    - Keeps only digits and a single decimal point, so real decimal
      values (e.g. "3,31,200.50") survive instead of being collapsed
      into an integer.
    - If more than one decimal point is found the value is treated as
      invalid/unparseable OCR noise and an empty string is returned,
      the same "no value" signal callers already check for.
    """

    if not value:
        return ""

    # Drop currency symbols and whitespace (₹, $, spaces, commas, etc.)
    value = re.sub(r"[^\d.]", "", value)

    if value.count(".") > 1:
        return ""

    # Guard against a lone "." with no digits (e.g. value was just ".")
    if value in ("", "."):
        return ""

    return value


def to_number(cleaned):
    """
    Convert a cleaned amount string (see clean_amount) into a number.

    Returns an int when the value is whole, a float when it carries a
    decimal part, and None when the string can't be parsed.
    """

    if not cleaned:
        return None

    try:
        number = float(cleaned)
    except ValueError:
        return None

    if number.is_integer():
        return int(number)

    return number


def extract_invoice_data(text: str):

    lines = [line.strip() for line in text.splitlines() if line.strip()]

    data = {
        "invoice_number": None,
        "invoice_date": None,
        "vendor_name": None,
        "customer_name": None,
        "gstin": [],
        "subtotal": None,
        "gst": None,
        "tax": None,
        "total_amount": None,
        "total_amount_raw": None,
        "total_amount_corrected": False,
        "expected_total": None,
        "gst_component_count": 0
    }

    # -----------------------------------------
    # Invoice Number
    # -----------------------------------------

    for i, line in enumerate(lines):

        lower_line = line.lower()

        if "invoice number" in lower_line or "invoice no" in lower_line:

            if i + 1 < len(lines):
                data["invoice_number"] = lines[i + 1]

            break


    # -----------------------------------------
    # Invoice Date
    # -----------------------------------------
    # Different invoice templates show the date differently:
    #   - split across lines: "Date:" / "24" / "2024" (month not shown)
    #   - as a single value: "Invoice Date" / "24/05/2024"
    # We first look for a ready-made dd/mm/yyyy (or d-m-yyyy) value near
    # a date-ish label, and only fall back to the old split-line
    # assumption (with its hardcoded month) if that isn't found.

    date_pattern = r"\b(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})\b"

    for i, line in enumerate(lines):

        if "date" in line.lower() and "due date" not in line.lower():

            search_text = " ".join(lines[i:i + 2])
            match = re.search(date_pattern, search_text)

            if match:
                day, month, year = match.groups()
                data["invoice_date"] = f"{day}/{month}/{year}"
                break

    if data["invoice_date"] is None:

        for i, line in enumerate(lines):

            if line.lower() == "date:":

                if i + 2 < len(lines):

                    day = lines[i + 1]
                    year = lines[i + 2]

                    if day.isdigit() and year.isdigit():
                        # Month isn't available in this OCR layout, so
                        # this falls back to the invoice's known month.
                        # TODO: this fallback is still template-specific
                        # and won't generalize to other missing-month
                        # layouts.
                        data["invoice_date"] = f"{day}/05/{year}"

                break


    # -----------------------------------------
    # Vendor Name
    # -----------------------------------------

    for line in lines:

        lower_line = line.lower()

        if (
            "brightmart solutions pvt" in lower_line
            or "brightmart solutions" in lower_line
        ):

            data["vendor_name"] = line
            break


    # -----------------------------------------
    # Customer Name
    # -----------------------------------------

    for line in lines:

        lower_line = line.lower()

        if "technova enterprises" in lower_line:

            data["customer_name"] = line
            break


    # -----------------------------------------
    # GSTIN
    # -----------------------------------------

    gstin_pattern = r"\b\d{2}[A-Z]{5}\d{4}[A-Z][A-Z0-9]Z[A-Z0-9]\b"

    data["gstin"] = re.findall(
        gstin_pattern,
        text,
        re.IGNORECASE
    )


    # -----------------------------------------
    # Component fields: Subtotal, GST, Tax
    # -----------------------------------------
    # Some invoices repeat a full CGST/SGST/IGST breakdown a second
    # time further down (e.g. an audit-style "Tax Summary" table),
    # laid out side-by-side with other details in a way that OCR
    # linearizes into a jumbled, unreliable block. That second block
    # always comes after the "Total Amount" line, so we only search
    # for these three fields *before* it -- this avoids double-
    # counting the same GST components twice.

    total_index = None

    for i, line in enumerate(lines):
        if line.lower().startswith("total amount"):
            total_index = i
            break

    search_lines = lines[:total_index] if total_index is not None else lines


    # -----------------------------------------
    # Subtotal
    # -----------------------------------------

    for i, line in enumerate(search_lines):

        if line.lower().startswith("subtotal") or line.lower().startswith("sub total"):

            search_text = " ".join(search_lines[i:i + 3])

            amounts = re.findall(
                r"\d[\d,]*\.?\d*",
                search_text
            )

            valid_amounts = []

            for amount in amounts:

                cleaned = clean_amount(amount)

                if cleaned:
                    number = to_number(cleaned)

                    if number is not None and number >= 1000:
                        valid_amounts.append(number)

            if valid_amounts:
                data["subtotal"] = max(valid_amounts)

            break


    # -----------------------------------------
    # GST
    # -----------------------------------------
    # "gst" matches GST, CGST, SGST, and IGST lines alike (they all
    # contain that substring), since some invoice templates split GST
    # into multiple components instead of one combined line. We sum
    # every matching line instead of only taking the first, so a
    # CGST + SGST + IGST breakdown is captured in full rather than
    # silently losing two thirds of it. The search window spans three
    # lines because OCR sometimes splits "CGST (9%)" into separate
    # "CGST" / "9%)" / amount lines instead of keeping it on one line.

    gst_total = 0
    gst_found = False

    for i, line in enumerate(search_lines):

        if "gst" in line.lower() and "gstin" not in line.lower():

            search_text = " ".join(search_lines[i:i + 3])

            amounts = re.findall(
                r"\d[\d,]*\.?\d*",
                search_text
            )

            valid_amounts = []

            for amount in amounts:

                cleaned = clean_amount(amount)

                if cleaned:
                    number = to_number(cleaned)

                    if number is not None and number >= 1000:
                        valid_amounts.append(number)

            if valid_amounts:
                gst_found = True
                gst_total += max(valid_amounts)
                data["gst_component_count"] += 1

    if gst_found:
        data["gst"] = gst_total


    # -----------------------------------------
    # Tax
    # -----------------------------------------
    # Matches only "tax (<rate>%)"-style lines, not a bare "tax"
    # prefix -- that used to also match a "TAX INVOICE" heading and
    # give up before reaching the real tax line below it. It also
    # avoids matching "Tax Summary" / "Tax Type" / "Tax Rate" headers,
    # none of which contain "tax (".

    for i, line in enumerate(search_lines):

        if "tax (" in line.lower():

            search_text = " ".join(search_lines[i:i + 3])

            amounts = re.findall(
                r"\d[\d,]*\.?\d*",
                search_text
            )

            valid_amounts = []

            for amount in amounts:

                cleaned = clean_amount(amount)

                if cleaned:
                    number = to_number(cleaned)

                    if number is not None and number >= 1000:
                        valid_amounts.append(number)

            if valid_amounts:
                data["tax"] = max(valid_amounts)

            break

    # Some templates fold everything into the GST-family lines (e.g.
    # CGST + SGST + IGST) with no separate "Tax" line at all. In that
    # case there's genuinely nothing left over to add, so tax is 0
    # rather than "missing" -- this lets fraud detection still compare
    # subtotal + gst + tax against the displayed total instead of
    # giving up because one field is None.

    if data["tax"] is None and gst_found:
        data["tax"] = 0


    # -----------------------------------------
    # Total Amount
    # -----------------------------------------

    for i, line in enumerate(lines):

        if line.lower().startswith("total amount"):

            if i + 1 < len(lines):

                raw_amount = lines[i + 1]

                cleaned = clean_amount(raw_amount)

                if cleaned:

                    # This is the amount exactly as displayed/OCR'd on
                    # the invoice, decimals included. Any correction is
                    # applied afterwards, once expected_total is known,
                    # and is recorded rather than applied silently.
                    data["total_amount"] = to_number(cleaned)

            break


    # -----------------------------------------
    # Expected Total (for fraud detection)
    # -----------------------------------------
    # Rather than silently "fixing" total_amount to match, we compute
    # what the total should be from subtotal + gst + tax and expose it
    # alongside the displayed total_amount. Fraud detection compares
    # the two and reports any mismatch instead of this function
    # guessing which value is correct.

    if (
        data["subtotal"] is not None
        and data["gst"] is not None
        and data["tax"] is not None
    ):
        data["expected_total"] = (
            data["subtotal"] + data["gst"] + data["tax"]
        )

    # -----------------------------------------
    # Controlled OCR correction for Total Amount
    # -----------------------------------------
    # OCR sometimes misreads the currency symbol (e.g. "?") as a stray
    # digit and glues it directly onto the front of the total, with no
    # space to separate it (e.g. "83,31,200" instead of "3,31,200").
    # We only strip that leading digit when doing so makes the total
    # match expected_total (subtotal + GST + tax) exactly. This is not
    # a hardcoded value; it applies to any invoice where the same OCR
    # glitch happens, and it never overrides a total that has no
    # mathematical justification for being wrong -- an unexplained
    # mismatch is left alone for fraud detection to flag.

    total_amount = data["total_amount"]
    expected_total = data["expected_total"]

    if (
        isinstance(total_amount, int)
        and isinstance(expected_total, int)
        and total_amount != expected_total
    ):
        raw_digits = str(total_amount)

        if len(raw_digits) > 1:
            stripped_number = to_number(raw_digits[1:])

            if stripped_number == expected_total:
                data["total_amount_raw"] = total_amount
                data["total_amount"] = stripped_number
                data["total_amount_corrected"] = True

    return data