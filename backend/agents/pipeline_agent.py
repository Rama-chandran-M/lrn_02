import json
import re
from agents.ocr_agent import extract_text
from services.langchain_service import run_chain
from prompts.structuring_prompt import STRUCTURING_PROMPT
from prompts.answer_key_prompt import ANSWER_KEY_PROMPT
from prompts.evaluation_prompt import EVALUATION_PROMPT


# =========================
# ✅ SAFE JSON PARSER (FIXED)
# =========================
def safe_json_parse(text):
    # ✅ Case 1: Already parsed JSON (LLM returned dict/list)
    if isinstance(text, (dict, list)):
        return text, None

    # ❌ Unexpected type
    if not isinstance(text, str):
        return None, f"Unexpected type: {type(text)}"

    # ❌ Empty string
    if text.strip() == "":
        return None, "Empty response from model"

    try:
        # Remove markdown formatting
        cleaned = re.sub(r"```json|```", "", text).strip()

        # =========================
        # ✅ FIXED JSON EXTRACTION
        # =========================

        # Try full parse first
        try:
            return json.loads(cleaned), None
        except:
            pass

        # Extract full JSON safely
        start = cleaned.find("{")
        end = cleaned.rfind("}")

        if start != -1 and end != -1:
            json_text = cleaned[start:end+1]
            return json.loads(json_text), None

        return None, f"No JSON found.\nRaw output:\n{text}"

    except Exception as e:
        return None, f"JSON parse failed: {str(e)}\nRaw:\n{text}"


# =========================
# 🚀 FULL PIPELINE
# =========================
def run_full_pipeline(student_file, answer_key_file, update_step=None):
    try:
        # =========================
        # STEP 1: OCR
        # =========================
        if update_step:
            update_step("📄 Extracting text (OCR)...", 20)

        student_text, err1 = extract_text(student_file)
        if err1:
            return None, err1

        key_text, err2 = extract_text(answer_key_file)
        if err2:
            return None, err2

        # =========================
        # STEP 2: STRUCTURE STUDENT
        # =========================
        if update_step:
            update_step("🧠 Structuring student answers...", 40)

        student_struct, err = run_chain(
            STRUCTURING_PROMPT,
            {"ocr_text": student_text}
        )
        if err:
            return None, err

        student_json, parse_err = safe_json_parse(student_struct)
        if parse_err:
            return None, f"Student JSON error:\n{parse_err}"

        # =========================
        # STEP 3: STRUCTURE KEY
        # =========================
        if update_step:
            update_step("📘 Structuring answer key...", 60)

        key_struct, err = run_chain(
            ANSWER_KEY_PROMPT,
            {"ocr_text": key_text}
        )
        if err:
            return None, err

        key_json, parse_err = safe_json_parse(key_struct)
        if parse_err:
            return None, f"Answer Key JSON error:\n{parse_err}"

        # =========================
        # STEP 4: EVALUATE
        # =========================
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

        # =========================
        # FINAL STEP
        # =========================
        if update_step:
            update_step("✅ Finalizing results...", 100)

        final_json, parse_err = safe_json_parse(evaluation_result)

        if parse_err:
            return None, f"Final JSON error:\n{parse_err}"

        return final_json, None

    except Exception as e:
        return None, str(e)