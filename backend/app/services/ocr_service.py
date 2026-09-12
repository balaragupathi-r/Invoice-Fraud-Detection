import easyocr

print("Loading EasyOCR...")

reader = easyocr.Reader(['en'], gpu=False)

print("EasyOCR loaded successfully.")


def extract_text(image_path: str):
    """
    Extract text from an invoice image.
    """

    print("Reading image:", image_path)

    results = reader.readtext(image_path)

    print("OCR completed.")
    print("Number of text regions:", len(results))

    extracted_text = []

    for result in results:
        text = result[1]
        extracted_text.append(text)

    return "\n".join(extracted_text)