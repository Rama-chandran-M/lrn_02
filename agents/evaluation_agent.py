import json
from services.gemini_service import call_gemini
from prompts.evaluation_prompt import EVALUATION_PROMPT

def evaluate_answers(student_json, answer_key_json):
    prompt = EVALUATION_PROMPT.replace(
        "__STUDENT_JSON__", json.dumps(student_json, indent=2)
    ).replace(
        "__ANSWER_KEY_JSON__", json.dumps(answer_key_json, indent=2)
    )

    response, error = call_gemini(prompt)

    if error:
        return None, error

    return response, None