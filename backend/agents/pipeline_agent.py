import json
import re
import logging
import concurrent.futures

from agents.ocr_agent import extract_text
from services.langchain_service import run_chain
from prompts.structuring_prompt import STRUCTURING_PROMPT
from prompts.answer_key_prompt import ANSWER_KEY_PROMPT
from prompts.evaluation_prompt import EVALUATION_PROMPT

# =========================
#  CONFIG
# =========================
TIMEOUT_SECONDS = 240

logging.basicConfig(level=logging.INFO)


# =========================
#  SAFE JSON PARSER
# =========================
def safe_json_parse(text):
    try:
        if isinstance(text, (dict, list)):
            return text, None

        if not isinstance(text, str):
            return None, "Invalid response format from model"

        if text.strip() == "":
            return None, "Empty response from model"

        cleaned = re.sub(r"```json|```", "", text).strip()

        try:
            return json.loads(cleaned), None
        except:
            pass

        #  Improved extraction
        start = cleaned.find("{")
        end = cleaned.rfind("}")

        if start != -1 and end != -1:
            cleaned = cleaned[start:end + 1]
            return json.loads(cleaned), None

        return None, "Model did not return valid JSON"

    except Exception as e:
        logging.error(f"JSON parsing error: {e}")
        return None, "JSON parsing failed"


# =========================
# ⏱ TIMEOUT WRAPPER (FIXED)
# =========================
def run_with_timeout(func, *args, timeout=TIMEOUT_SECONDS):
    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(func, *args)
            result = future.result(timeout=timeout)

            #  CRITICAL FIX: unpack correctly
            if isinstance(result, tuple) and len(result) == 2:
                return result  # (output, error)

            return result, None

    except concurrent.futures.TimeoutError:
        return None, "API_ERROR: Request timed out"

    except Exception as e:
        logging.error(f"Timeout wrapper error: {e}")
        return None, "API_ERROR: Execution failed"


# =========================
#  STEP 1: PREPARE ANSWER KEY
# =========================
def prepare_answer_key(answer_key_file, update_step=None):
    try:
        if update_step:
            update_step("📘 Processing answer key...", 10)

        key_text, err = extract_text(answer_key_file)
        if err:
            return None, "OCR_ERROR: Failed to read answer key"

        if not key_text or key_text.strip() == "":
            return None, "OCR_ERROR: Empty text extracted from answer key"

        key_struct, err = run_with_timeout(
            run_chain,
            ANSWER_KEY_PROMPT,
            {"ocr_text": key_text}
        )

        if err:
            return None, err

        key_json, parse_err = safe_json_parse(key_struct)
        if parse_err:
            return None, f"PARSE_ERROR: {parse_err}"

        return key_json, None

    except Exception as e:
        logging.error(f"Answer key error: {e}")
        return None, "Unexpected error while processing answer key"


# =========================
#  STEP 2: PROCESS STUDENT
# =========================
def process_student(student_file, key_json, update_step=None):
    try:
        if update_step:
            update_step("📄 Extracting student text...", 30)

        student_text, err = extract_text(student_file)
        if err:
            return None, "OCR_ERROR: Failed to read student file"

        if not student_text or student_text.strip() == "":
            return None, "OCR_ERROR: Empty text extracted from student file"

        if update_step:
            update_step("🧠 Structuring student answers...", 50)

        student_struct, err = run_with_timeout(
            run_chain,
            STRUCTURING_PROMPT,
            {"ocr_text": student_text}
        )

        if err:
            return None, err

        student_json, parse_err = safe_json_parse(student_struct)
        if parse_err:
            return None, f"PARSE_ERROR: {parse_err}"

        if update_step:
            update_step("📝 Evaluating answers...", 80)

        evaluation_result, err = run_with_timeout(
            run_chain,
            EVALUATION_PROMPT,
            {
                "student_json": json.dumps(student_json, indent=2),
                "answer_key_json": json.dumps(key_json, indent=2)
            }
        )

        if err:
            return None, err

        #  NEW: unwrap before parsing
        if isinstance(evaluation_result, list) and len(evaluation_result) > 0:
            if isinstance(evaluation_result[0], dict) and "text" in evaluation_result[0]:
                evaluation_result = evaluation_result[0]["text"]

        final_json, parse_err = safe_json_parse(evaluation_result)

        if parse_err:
            return None, f"PARSE_ERROR: {parse_err}"

        if update_step:
            update_step("✅ Done", 100)

        return final_json, None

    except Exception as e:
        logging.error(f"Student processing error: {e}")
        return None, "Unexpected error while processing student file"


# =========================
#  FULL PIPELINE
# =========================
def run_full_pipeline(student_file, answer_key_file, update_step=None):
    try:
        key_json, err = prepare_answer_key(answer_key_file, update_step)
        if err:
            return None, err

        return process_student(student_file, key_json, update_step)

    except Exception as e:
        logging.error(f"Pipeline error: {e}")
        return None, "Pipeline execution failed"