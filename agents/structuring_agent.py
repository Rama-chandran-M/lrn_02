from services.ollama_service import call_ollama

from services.ollama_service import call_ollama
from prompts.structuring_prompt import STRUCTURING_PROMPT

def structure_text(ocr_text):
    final_prompt = STRUCTURING_PROMPT.replace("{ocr_text}", ocr_text)

    response, error = call_ollama(final_prompt)

    if error:
        return None, error

    return response, None

    return response, None