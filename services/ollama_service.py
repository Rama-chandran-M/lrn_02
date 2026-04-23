import requests
from config.settings import OLLAMA_MODEL, OLLAMA_URL

def call_ollama(prompt):
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=payload)

    if response.status_code != 200:
        return None, response.text

    return response.json().get("response"), None