import streamlit as st
import json
import re

from agents.pipeline_agent import run_full_pipeline

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
for key in ["evaluation", "student_file", "answer_key_file"]:
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
step1 = "active" if not st.session_state.evaluation else ""
step2 = "active" if st.session_state.evaluation else ""

st.markdown(f"""
<div>
<span class="step {step1}">Upload & Run</span>
<span class="step {step2}">Results</span>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# =========================
# 📂 UPLOAD
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
# 🚀 RUN FULL PIPELINE
# =========================
st.markdown("### 🚀 Run AI Evaluation")

ready = st.session_state.student_file and st.session_state.answer_key_file

st.markdown('<div class="big-btn">', unsafe_allow_html=True)
if st.button("Run Full Evaluation", disabled=not ready):

    step_placeholder = st.empty()     # 👈 dynamic step text
    progress_bar = st.progress(0)     # 👈 progress bar

    def update_step(text, progress):
        step_placeholder.markdown(f"**{text}**")
        progress_bar.progress(progress)

    with st.spinner("Running full AI pipeline..."):

        update_step("🚀 Starting...", 5)

        result, err = run_full_pipeline(
            st.session_state.student_file,
            st.session_state.answer_key_file,
            update_step=update_step   # 👈 pass callback
        )

        if err:
            st.error(err)
        else:
            parsed, parse_err = clean_and_parse(result)

            if parse_err:
                st.error("Parsing failed")
                st.code(result)
            else:
                update_step("✅ Finalizing results...", 100)
                st.session_state.evaluation = parsed
                st.success("🎉 Evaluation Complete!")

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
# 🔍 DATA EXPLORER
# =========================
if st.session_state.evaluation:
    st.markdown("---")
    st.markdown("### 🔍 Detailed Evaluation")

    with st.expander("📊 Evaluation JSON"):
        st.json(st.session_state.evaluation)