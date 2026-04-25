from services.cloudinary_service import upload_file
from services.mistral_service import call_mistral_ocr

def extract_text(file):
    file_url = upload_file(file)

    if not file_url:
        return None, "Cloudinary upload failed"

    text, error = call_mistral_ocr(file_url)

    if error:
        return None, error

    return text, None