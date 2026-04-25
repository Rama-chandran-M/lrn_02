from services.langchain_service import run_chain
from prompts.structuring_prompt import STRUCTURING_PROMPT
from prompts.answer_key_prompt import ANSWER_KEY_PROMPT

def structure_text(text, mode="student"):
    if mode == "student":
        prompt = STRUCTURING_PROMPT
    elif mode == "answer_key":
        prompt = ANSWER_KEY_PROMPT
    else:
        raise ValueError("Invalid mode")

    response, error = run_chain(
        prompt_template_str=prompt,
        input_dict={"ocr_text": text}
    )

    if error:
        return None, error

    return response, None