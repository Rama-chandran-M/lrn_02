from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import shutil

from agents.pipeline_agent import run_full_pipeline

app = FastAPI()

# ✅ Allow React frontend to call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # later restrict to localhost:5173
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"message": "API is running"}


@app.post("/evaluate")
async def evaluate(
    student_file: UploadFile = File(...),
    answer_key_file: UploadFile = File(...)
):
    try:
        # =========================
        # Save uploaded files temporarily
        # =========================
        with tempfile.NamedTemporaryFile(delete=False) as student_temp:
            shutil.copyfileobj(student_file.file, student_temp)
            student_path = student_temp.name

        with tempfile.NamedTemporaryFile(delete=False) as key_temp:
            shutil.copyfileobj(answer_key_file.file, key_temp)
            key_path = key_temp.name

        # =========================
        # Run your existing pipeline (NO CHANGE)
        # =========================
        # reopen files in binary mode
        # =========================
        with open(student_path, "rb") as sf, open(key_path, "rb") as kf:
            result, err = run_full_pipeline(sf, kf)

        if err:
            return {"error": err}

        return result  # already JSON

    except Exception as e:
        return {"error": str(e)}