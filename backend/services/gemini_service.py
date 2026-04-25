import google.generativeai as genai
import time
from config.settings import GEMINI_API_KEY, GEMINI_MODEL

# Configure API key
genai.configure(api_key=GEMINI_API_KEY)

def call_gemini(prompt, retries=3):
    try:
        model = genai.GenerativeModel(GEMINI_MODEL)

        for attempt in range(retries):
            try:
                response = model.generate_content(prompt)

                # ✅ Safe extraction
                if response and hasattr(response, "text") and response.text:
                    return response.text.strip(), None

                return None, "Empty response from Gemini"

            except Exception as e:
                # 🔁 Handle rate limit (429)
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    wait_time = 10 * (attempt + 1)
                    time.sleep(wait_time)
                else:
                    return None, str(e)

        return None, "Max retries exceeded (rate limit)"

    except Exception as e:
        return None, str(e)