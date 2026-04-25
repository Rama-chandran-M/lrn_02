import requests
import os
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

load_dotenv()

# Mistral
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

# Cloudinary config
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)


import io

def upload_to_cloudinary(file):
    try:
        file_bytes = file.read()
        file.seek(0)

        result = cloudinary.uploader.upload(
            io.BytesIO(file_bytes),
            resource_type="raw",
            access_mode="public"   # 🔥 important
        )

        print("UPLOAD SUCCESS:", result)

        return result.get("secure_url")

    except Exception as e:
        print("❌ Cloudinary Upload Error:", str(e))
        return None

def extract_text_from_pdf(file):
    url = "https://api.mistral.ai/v1/ocr"

    # Step 1: upload to Cloudinary
    file_url = upload_to_cloudinary(file)

    if not file_url:
        return "Error: Cloudinary upload failed"

    print("FILE URL:", file_url)

    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mistral-ocr-latest",
        "document": {
            "type": "document_url",
            "document_url": file_url
        }
    }

    response = requests.post(url, headers=headers, json=payload)

    print("STATUS:", response.status_code)
    print("RESPONSE:", response.text)

    try:
        data = response.json()
    except:
        return f"Invalid response: {response.text}"

    if response.status_code != 200:
        return f"Error: {data}"

    try:
        pages = data.get("pages", [])

        text = "\n".join([
            p.get("markdown") or p.get("content", "")
            for p in pages
        ])

        return text if text else "No text extracted"

    except Exception:
        return str(data)