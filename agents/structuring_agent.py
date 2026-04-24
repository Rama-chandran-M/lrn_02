from services.gemini_service import call_gemini
from prompts.structuring_prompt import STRUCTURING_PROMPT
from prompts.answer_key_prompt import ANSWER_KEY_PROMPT

def structure_text(text, mode="student"):
    if mode == "student":
        prompt = STRUCTURING_PROMPT
    elif mode == "answer_key":
        prompt = ANSWER_KEY_PROMPT
    else:
        raise ValueError("Invalid mode")

    final_prompt = prompt.replace("{ocr_text}", text)

    response, error = call_gemini(final_prompt)

    if error:
        return None, error

    return response, None