import streamlit as st
import json
import re

from agents.ocr_agent import extract_text
from agents.structuring_agent import structure_text
from agents.evaluation_agent import evaluate_answers

st.set_page_config(page_title="AI Answer Evaluator")

st.title("📄 Handwritten Answer Evaluator")

# =========================
# 📂 File Uploads
# =========================
student_file = st.file_uploader("Upload Student Answer Sheet", type=["pdf", "png", "jpg"])
answer_key_file = st.file_uploader("Upload Answer Key", type=["pdf", "png", "jpg"])

# =========================
# 🧠 Session State
# =========================
for key in ["student_json", "answer_key_json", "evaluation"]:
    if key not in st.session_state:
        st.session_state[key] = None

# =========================
# 🧹 JSON Cleaner + Parser
# =========================
def clean_and_parse(response):
    try:
        cleaned = re.sub(r"```json|```", "", response).strip()
        return json.loads(cleaned), None
    except Exception as e:
        return None, f"JSON Parsing Error: {str(e)}"

# =========================
# 🔘 1. Process Student Sheet
# =========================
if st.button("Process Student Sheet"):
    if not student_file:
        st.warning("Please upload a student answer sheet")
    else:
        with st.spinner("Running OCR + Structuring..."):
            text, error = extract_text(student_file)

            if error:
                st.error(error)
            else:
                json_output, error = structure_text(text, mode="student")

                if error:
                    st.error(error)
                else:
                    parsed, parse_error = clean_and_parse(json_output)

                    if parse_error:
                        st.error(parse_error)
                        st.code(json_output)
                    else:
                        st.session_state.student_json = parsed
                        st.success("✅ Student Sheet Processed")

# =========================
# 📊 Show Student JSON (Expandable)
# =========================
if st.session_state.student_json:
    st.subheader("📊 Student Answers")

    with st.expander("View Student Answers JSON"):
        st.json(st.session_state.student_json)

# =========================
# 🔘 2. Process Answer Key
# =========================
if st.button("Process Answer Key"):
    if not answer_key_file:
        st.warning("Please upload an answer key")
    else:
        with st.spinner("Running OCR + Structuring (Answer Key)..."):
            text, error = extract_text(answer_key_file)

            if error:
                st.error(error)
            else:
                json_output, error = structure_text(text, mode="answer_key")

                if error:
                    st.error(error)
                else:
                    parsed, parse_error = clean_and_parse(json_output)

                    if parse_error:
                        st.error(parse_error)
                        st.code(json_output)
                    else:
                        st.session_state.answer_key_json = parsed
                        st.success("✅ Answer Key Processed")

# =========================
# 📘 Show Answer Key JSON (Expandable)
# =========================
if st.session_state.answer_key_json:
    st.subheader("📘 Answer Key")

    with st.expander("View Answer Key JSON"):
        st.json(st.session_state.answer_key_json)

# =========================
# 🔘 3. Evaluate
# =========================
if st.button("Evaluate Answers"):
    if not st.session_state.student_json:
        st.warning("Process student sheet first")
    elif not st.session_state.answer_key_json:
        st.warning("Process answer key first")
    else:
        with st.spinner("Evaluating answers..."):
            result, error = evaluate_answers(
                st.session_state.student_json,
                st.session_state.answer_key_json
            )

            if error:
                st.error(error)
            else:
                parsed, parse_error = clean_and_parse(result)

                if parse_error:
                    st.error(parse_error)
                    st.code(result)
                else:
                    st.session_state.evaluation = parsed
                    st.success("✅ Evaluation Complete")

# =========================
# 📊 Show Evaluation Summary + Expandable JSON
# =========================
if st.session_state.evaluation and isinstance(st.session_state.evaluation, dict):
    st.subheader("📊 Evaluation Summary")

    summary = st.session_state.evaluation.get("summary")

    if not summary:
        st.warning("Summary not available. Model output may be invalid.")
    else:
        total = summary.get("total_score", 0)
        max_score = summary.get("max_score", 0)
        percentage = round(summary.get("percentage", 0), 2)

        col1, col2 = st.columns(2)

        col1.metric("Score", f"{total} / {max_score}")
        col2.metric("Percentage", f"{percentage}%")

        # Optional progress bar
        st.progress(min(percentage / 100, 1.0))

        st.markdown("### 💪 Strengths")
        st.write(summary.get("strengths", "N/A"))

        st.markdown("### ⚠️ Weaknesses")
        st.write(summary.get("weaknesses", "N/A"))

    # =========================
    # 🔍 Expandable JSON
    # =========================
    st.markdown("---")
    st.subheader("🔍 Detailed Evaluation (JSON)")

    with st.expander("View Full Evaluation JSON"):
        st.json(st.session_state.evaluation)