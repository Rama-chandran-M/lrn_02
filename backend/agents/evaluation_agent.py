import json
from services.langchain_service import run_chain
from prompts.evaluation_prompt import EVALUATION_PROMPT

def evaluate_answers(student_json, answer_key_json):

    response, error = run_chain(
        prompt_template_str=EVALUATION_PROMPT,
        input_dict={
            "student_json": json.dumps(student_json, indent=2),
            "answer_key_json": json.dumps(answer_key_json, indent=2)
        }
    )

    if error:
        return None, error

    return response, None