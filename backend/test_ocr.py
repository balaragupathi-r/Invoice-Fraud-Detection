from app.services.ocr_service import extract_text

print("Starting OCR test...")

image_path = "uploads/sample_invoice.png"

text = extract_text(image_path)

print("OCR function returned successfully.")
print("Type:", type(text))
print("Length:", len(text))

print("\n===== EXTRACTED TEXT =====")
print(text)
print("==========================")

print("Test finished.")