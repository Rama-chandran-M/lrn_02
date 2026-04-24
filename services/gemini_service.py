# import requests
# from config.settings import OLLAMA_MODEL, OLLAMA_URL

# def call_ollama(prompt):
#     payload = {
#         "model": OLLAMA_MODEL,
#         "prompt": prompt,
#         "stream": False
#     }

#     response = requests.post(OLLAMA_URL, json=payload)

#     if response.status_code != 200:
#         return None, response.text

#     return response.json().get("response"), None

import google.generativeai as genai
from config.settings import GEMINI_API_KEY, GEMINI_MODEL

# Configure API key
genai.configure(api_key=GEMINI_API_KEY)

def call_gemini(prompt):
    try:
        model = genai.GenerativeModel(GEMINI_MODEL)

        response = model.generate_content(prompt)

        # Extract text safely
        if response and response.text:
            return response.text, None
        else:
            return None, "Empty response from Gemini"

    except Exception as e:
        return None, str(e)