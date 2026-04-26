import json
import re
from agents.ocr_agent import extract_text
from services.langchain_service import run_chain
from prompts.structuring_prompt import STRUCTURING_PROMPT
from prompts.answer_key_prompt import ANSWER_KEY_PROMPT
from prompts.evaluation_prompt import EVALUATION_PROMPT


# =========================
# ✅ SAFE JSON PARSER
# =========================
def safe_json_parse(text):
    if isinstance(text, (dict, list)):
        return text, None

    if not isinstance(text, str):
        return None, f"Unexpected type: {type(text)}"

    if text.strip() == "":
        return None, "Empty response from model"

    try:
        cleaned = re.sub(r"```json|```", "", text).strip()

        try:
            return json.loads(cleaned), None
        except:
            pass

        start = cleaned.find("{")
        end = cleaned.rfind("}")

        if start != -1 and end != -1:
            return json.loads(cleaned[start:end+1]), None

        return None, f"No JSON found.\n{text}"

    except Exception as e:
        return None, f"JSON parse failed: {str(e)}"


# =========================
# 🔹 STEP 1: PREPARE ANSWER KEY (ONCE)
# =========================
def prepare_answer_key(answer_key_file, update_step=None):
    if update_step:
        update_step("📘 Processing answer key...", 10)

    key_text, err = extract_text(answer_key_file)
    if err:
        return None, err

    key_struct, err = run_chain(
        ANSWER_KEY_PROMPT,
        {"ocr_text": key_text}
    )
    if err:
        return None, err

    key_json, parse_err = safe_json_parse(key_struct)
    if parse_err:
        return None, parse_err

    return key_json, None


# =========================
# 🔹 STEP 2: PROCESS ONE STUDENT
# =========================
def process_student(student_file, key_json, update_step=None):
    if update_step:
        update_step("📄 Extracting student text...", 30)

    student_text, err = extract_text(student_file)
    if err:
        return None, err

    if update_step:
        update_step("🧠 Structuring student answers...", 50)

    student_struct, err = run_chain(
        STRUCTURING_PROMPT,
        {"ocr_text": student_text}
    )
    if err:
        return None, err

    student_json, parse_err = safe_json_parse(student_struct)
    if parse_err:
        return None, parse_err

    if update_step:
        update_step("📝 Evaluating answers...", 80)

    evaluation_result, err = run_chain(
        EVALUATION_PROMPT,
        {
            "student_json": json.dumps(student_json, indent=2),
            "answer_key_json": json.dumps(key_json, indent=2)
        }
    )
    if err:
        return None, err

    final_json, parse_err = safe_json_parse(evaluation_result)
    if parse_err:
        return None, parse_err

    if update_step:
        update_step("✅ Done", 100)

    return final_json, None


# =========================
# 🔹 OLD SINGLE PIPELINE (keep for compatibility)
# =========================
def run_full_pipeline(student_file, answer_key_file, update_step=None):
    key_json, err = prepare_answer_key(answer_key_file, update_step)
    if err:
        return None, err

    return process_student(student_file, key_json, update_step)