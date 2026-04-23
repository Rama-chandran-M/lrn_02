import streamlit as st
from agents.ocr_agent import extract_text
from agents.structuring_agent import structure_text

st.set_page_config(page_title="AI Answer Evaluator")

st.title("📄 Handwritten Answer Evaluator")

# Uploads
student_file = st.file_uploader("Upload Student Answer Sheet", type=["pdf", "png", "jpg"])
answer_key = st.file_uploader("Upload Answer Key (Optional)", type=["pdf", "png", "jpg"])

# Session state
if "ocr_text" not in st.session_state:
    st.session_state.ocr_text = None

if "structured_json" not in st.session_state:
    st.session_state.structured_json = None

# 🔘 Extract Text
if st.button("Extract Text"):
    if student_file:
        with st.spinner("Extracting text using OCR..."):
            text, error = extract_text(student_file)

            if error:
                st.error(error)
            else:
                st.session_state.ocr_text = text
                st.success("OCR Extraction Complete")

# Show OCR text
if st.session_state.ocr_text:
    st.subheader("📝 Extracted Text")
    st.text_area("OCR Output", st.session_state.ocr_text, height=300)

# 🔘 Convert to JSON
if st.button("Convert to JSON"):
    if st.session_state.ocr_text:
        with st.spinner("Structuring using LLM..."):
            json_output, error = structure_text(st.session_state.ocr_text)

            if error:
                st.error(error)
            else:
                st.session_state.structured_json = json_output
                st.success("Structuring Complete")

# Show JSON
if st.session_state.structured_json:
    st.subheader("📊 Structured JSON")
    st.code(st.session_state.structured_json, language="json")