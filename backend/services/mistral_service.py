import requests
from config.settings import MISTRAL_API_KEY

def call_mistral_ocr(file_url):
    url = "https://api.mistral.ai/v1/ocr"

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

    if response.status_code != 200:
        return None, response.text

    data = response.json()

    pages = data.get("pages", [])
    text = "\n".join([
        p.get("markdown") or p.get("content", "")
        for p in pages
    ])

    return text, None