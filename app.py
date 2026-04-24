import streamlit as st
import json
import re

from agents.ocr_agent import extract_text
from agents.structuring_agent import structure_text
from agents.evaluation_agent import evaluate_answers

# =========================
# 🎨 CONFIG
# =========================
st.set_page_config(page_title="AI Evaluator", layout="wide")

# =========================
# 🎨 MODERN MINIMAL CSS
# =========================
st.markdown("""
<style>
.block-container {
    max-width: 1000px;
    padding-top: 2rem;
}
.step {
    display: inline-block;
    padding: 8px 18px;
    border-radius: 20px;
    margin-right: 8px;
    font-size: 14px;
    background-color: #f1f3f5;
}
.active {
    background-color: #111827;
    color: white;
}
.big-btn button {
    height: 50px;
    font-size: 16px;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# 🧠 STATE INIT
# =========================
for key in ["student_json", "answer_key_json", "evaluation", "student_file", "answer_key_file"]:
    if key not in st.session_state:
        st.session_state[key] = None

# =========================
# 🧹 JSON CLEANER
# =========================
def clean_and_parse(response):
    try:
        cleaned = re.sub(r"```json|```", "", response).strip()
        return json.loads(cleaned), None
    except:
        return None, "Parsing error"

# =========================
# 🧠 HEADER
# =========================
st.title("🧠 AI Answer Evaluator")

# =========================
# 🧭 STEP TRACKER
# =========================
step1 = "active" if not st.session_state.student_json else ""
step2 = "active" if st.session_state.student_json and not st.session_state.answer_key_json else ""
step3 = "active" if st.session_state.answer_key_json and not st.session_state.evaluation else ""
step4 = "active" if st.session_state.evaluation else ""

st.markdown(f"""
<div>
<span class="step {step1}">Upload</span>
<span class="step {step2}">Process</span>
<span class="step {step3}">Evaluate</span>
<span class="step {step4}">Done</span>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# =========================
# 📂 UPLOAD (FIXED)
# =========================
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 📄 Student Sheet")
    student_file = st.file_uploader(
        "Upload Student Sheet",
        type=["pdf", "png", "jpg"],
        key="student_uploader"
    )
    if student_file:
        st.session_state.student_file = student_file

with col2:
    st.markdown("#### 📘 Answer Key")
    answer_key_file = st.file_uploader(
        "Upload Answer Key",
        type=["pdf", "png", "jpg"],
        key="answer_key_uploader"
    )
    if answer_key_file:
        st.session_state.answer_key_file = answer_key_file

# =========================
# ⚙️ PROCESS
# =========================
st.markdown("### ⚙️ Processing")

p1, p2 = st.columns(2)

with p1:
    if st.button("Process Student", key="process_student"):
        if st.session_state.student_file:
            with st.spinner("Processing student..."):
                text, err = extract_text(st.session_state.student_file)

                if err:
                    st.error(err)
                else:
                    json_out, err = structure_text(text, mode="student")

                    if err:
                        st.error(err)
                    else:
                        parsed, _ = clean_and_parse(json_out)
                        st.session_state.student_json = parsed
                        st.success("✔ Student processed")
        else:
            st.warning("Upload student file first")

with p2:
    if st.button("Process Answer Key", key="process_key"):
        if st.session_state.answer_key_file:
            with st.spinner("Processing key..."):
                text, err = extract_text(st.session_state.answer_key_file)

                if err:
                    st.error(err)
                else:
                    json_out, err = structure_text(text, mode="answer_key")

                    if err:
                        st.error(err)
                    else:
                        parsed, _ = clean_and_parse(json_out)
                        st.session_state.answer_key_json = parsed
                        st.success("✔ Answer key processed")
        else:
            st.warning("Upload answer key first")

# =========================
# 🚀 EVALUATE
# =========================
st.markdown("### 🚀 Evaluation")

ready = st.session_state.student_json and st.session_state.answer_key_json

st.markdown('<div class="big-btn">', unsafe_allow_html=True)
if st.button("Run Evaluation", disabled=not ready):
    with st.spinner("Evaluating..."):
        result, err = evaluate_answers(
            st.session_state.student_json,
            st.session_state.answer_key_json
        )

        if err:
            st.error(err)
        else:
            parsed, _ = clean_and_parse(result)
            st.session_state.evaluation = parsed
            st.success("🎉 Evaluation complete!")
st.markdown('</div>', unsafe_allow_html=True)

# =========================
# 📊 RESULTS
# =========================
if st.session_state.evaluation:
    st.markdown("### 📊 Results")

    summary = st.session_state.evaluation.get("summary", {})

    c1, c2, c3 = st.columns(3)
    c1.metric("Score", summary.get("total_score", 0))
    c2.metric("Max", summary.get("max_score", 0))
    c3.metric("Percentage", f"{round(summary.get('percentage', 0), 2)}%")

    st.progress(min(summary.get("percentage", 0) / 100, 1.0))

    st.markdown("#### 💪 Strengths")
    st.write(summary.get("strengths", "N/A"))

    st.markdown("#### ⚠️ Weaknesses")
    st.write(summary.get("weaknesses", "N/A"))

# =========================
# 🔍 DATA DRAWER (DROPDOWNS)
# =========================
if any([
    st.session_state.student_json,
    st.session_state.answer_key_json,
    st.session_state.evaluation
]):
    st.markdown("---")
    st.markdown("### 🔍 Data Explorer")

    if st.session_state.student_json:
        with st.expander("📄 Student JSON"):
            st.json(st.session_state.student_json)

    if st.session_state.answer_key_json:
        with st.expander("📘 Answer Key JSON"):
            st.json(st.session_state.answer_key_json)

    if st.session_state.evaluation:
        with st.expander("📊 Evaluation JSON"):
            st.json(st.session_state.evaluation)