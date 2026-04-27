import threading

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import shutil
import json

from agents.pipeline_agent import (
    run_full_pipeline,
    prepare_answer_key,
    process_student
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
#  VALIDATION
# =========================
def validate_pdf(file: UploadFile):
    if not file:
        raise HTTPException(status_code=400, detail="File not provided")

    if file.filename == "":
        raise HTTPException(status_code=400, detail="Empty file uploaded")

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Invalid PDF format. Please upload a valid file."
        )
    file.file.seek(0, 2)  # move to end
    size = file.file.tell()
    file.file.seek(0)

    if size > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 10MB)")


@app.get("/")
def home():
    return {"message": "API is running"}


# =========================
#  SINGLE STUDENT (STREAMING)
# =========================
from fastapi.responses import StreamingResponse

@app.post("/evaluate")
async def evaluate(
    student_file: UploadFile = File(...),
    answer_key_file: UploadFile = File(...)
):
    validate_pdf(student_file)
    validate_pdf(answer_key_file)

    async def event_stream():
        try:
            from queue import Queue

            step_queue = Queue()
            result_holder = {"result": None, "error": None}

            def update_step(msg, prog):
                step_queue.put({
                    "type": "step",
                    "message": msg,
                    "progress": prog
                })

            def task():
                try:
                    with tempfile.NamedTemporaryFile(delete=False) as s_temp:
                        shutil.copyfileobj(student_file.file, s_temp)
                        s_path = s_temp.name

                    with tempfile.NamedTemporaryFile(delete=False) as k_temp:
                        shutil.copyfileobj(answer_key_file.file, k_temp)
                        k_path = k_temp.name

                    with open(s_path, "rb") as sf, open(k_path, "rb") as kf:
                        res, err = run_full_pipeline(sf, kf, update_step)

                    result_holder["result"] = res
                    result_holder["error"] = err

                except Exception as e:
                    result_holder["error"] = str(e)

                finally:
                    step_queue.put("DONE")

            threading.Thread(target=task).start()

            #  STREAM STEPS
            while True:
                item = step_queue.get()
                if item == "DONE":
                    break

                yield json.dumps(item) + "\n"

            #  FINAL RESPONSE HANDLING
            if result_holder["error"]:
                msg = result_holder["error"]
                msg_upper = msg.upper()

                if "OCR_ERROR" in msg_upper:
                    msg = "OCR failed to process the document"

                elif "PARSE_ERROR" in msg_upper or "PARSE" in msg_upper:
                    msg = "Error processing evaluation result"

                elif "API_ERROR" in msg_upper:
                    msg = "Evaluation service temporarily unavailable"

                elif "TIMEOUT" in msg_upper:
                    msg = "Request timed out. Please try again."

                else:
                    msg = "Something went wrong during evaluation"

                yield json.dumps({"type": "error", "message": msg}) + "\n"

            else:
                #  PRINT RESULT
                print("\n===== FINAL RESULT SENT TO FRONTEND =====")
                print(json.dumps(result_holder["result"], indent=2))
                print("=========================================\n")

                #  SEND RESULT TO FRONTEND (CRITICAL FIX)
                yield json.dumps({
                    "type": "result",
                    "data": result_holder["result"]
                }) + "\n"

        except Exception:
            yield json.dumps({
                "type": "error",
                "message": "Unexpected server error"
            }) + "\n"

    return StreamingResponse(event_stream(), media_type="text/plain")
# =========================
# 🔹 MULTIPLE STUDENTS
# =========================
from concurrent.futures import ThreadPoolExecutor
from queue import Queue

@app.post("/evaluate-multiple")
async def evaluate_multiple(
    student_files: list[UploadFile] = File(...),
    answer_key_file: UploadFile = File(...)
):
    validate_pdf(answer_key_file)
    for student in student_files:
        validate_pdf(student)

    async def event_stream():
        try:
            step_queue = Queue()
            results = []

            # Save answer key
            with tempfile.NamedTemporaryFile(delete=False) as key_temp:
                shutil.copyfileobj(answer_key_file.file, key_temp)
                key_path = key_temp.name

            with open(key_path, "rb") as kf:
                key_json, err = prepare_answer_key(kf)

            if err:
                yield json.dumps({
                    "type": "error",
                    "message": "Failed to process answer key"
                }) + "\n"
                return

            def process_single_student(student):
                try:
                    student_name = student.filename

                    with tempfile.NamedTemporaryFile(delete=False) as s_temp:
                        shutil.copyfileobj(student.file, s_temp)
                        s_path = s_temp.name

                    def update_step(msg, prog):
                        step_queue.put({
                            "type": "step",
                            "student": student_name,
                            "message": msg,
                            "progress": prog
                        })

                    with open(s_path, "rb") as sf:
                        result, err = process_student(sf, key_json, update_step)

                        if isinstance(result, list) and len(result) > 0:
                            try:
                                result = json.loads(result[0]["text"])
                            except Exception:
                                err = "parse_error"

                    step_queue.put({
                        "type": "done_student",
                        "student": student_name,
                        "result": result,
                        "error": err
                    })

                except Exception:
                    step_queue.put({
                        "type": "done_student",
                        "student": student.filename,
                        "error": "Processing failed"
                    })

            executor = ThreadPoolExecutor(max_workers=3)

            for student in student_files:
                executor.submit(process_single_student, student)

            completed = 0
            total = len(student_files)

            while completed < total:
                item = step_queue.get()

                if item["type"] == "done_student":
                    completed += 1
                    results.append(item)

                yield json.dumps(item) + "\n"
            
            yield json.dumps({
                "type": "final",
                "results": results
            }) + "\n"

        except Exception:
            yield json.dumps({
                "type": "error",
                "message": "Unexpected server error"
            }) + "\n"

    return StreamingResponse(event_stream(), media_type="text/plain")