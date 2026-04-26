from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import tempfile
import shutil

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


@app.get("/")
def home():
    return {"message": "API is running"}


# =========================
# 🔹 SINGLE STUDENT (STREAMING)
# =========================
from fastapi.responses import StreamingResponse
import json

@app.post("/evaluate")
async def evaluate(
    student_file: UploadFile = File(...),
    answer_key_file: UploadFile = File(...)
):
    async def event_stream():
        try:
            from queue import Queue
            import threading

            step_queue = Queue()
            result_holder = {"result": None, "error": None}

            def update_step(msg, prog):
                step_queue.put({"type": "step", "message": msg, "progress": prog})

            def task():
                with tempfile.NamedTemporaryFile(delete=False) as s_temp:
                    shutil.copyfileobj(student_file.file, s_temp)
                    s_path = s_temp.name

                with tempfile.NamedTemporaryFile(delete=False) as k_temp:
                    shutil.copyfileobj(answer_key_file.file, k_temp)
                    k_path = k_temp.name

                with open(s_path, "rb") as sf, open(k_path, "rb") as kf:
                    res, err = run_full_pipeline(sf, kf, update_step)

                # 🔥 FIX: parse LLM output if needed
                if isinstance(res, list) and len(res) > 0:
                    try:
                        res = json.loads(res[0]["text"])
                    except Exception as e:
                        print("JSON parse error:", e)

                result_holder["result"] = res
                result_holder["error"] = err
                step_queue.put("DONE")

            threading.Thread(target=task).start()

            while True:
                item = step_queue.get()
                if item == "DONE":
                    break

                print(json.dumps(item, indent=2))  # DEBUG
                yield json.dumps(item) + "\n"

            if result_holder["error"]:
                error_data = {"type": "error", "message": result_holder["error"]}
                print(json.dumps(error_data, indent=2))
                yield json.dumps(error_data) + "\n"
            else:
                # 🔥 FIX: send clean result (no wrapper)
                print(json.dumps(result_holder["result"], indent=2))
                yield json.dumps(result_holder["result"]) + "\n"

        except Exception as e:
            error_data = {"type": "error", "message": str(e)}
            print(json.dumps(error_data, indent=2))
            yield json.dumps(error_data) + "\n"

    return StreamingResponse(event_stream(), media_type="text/plain")


# =========================
# 🔥 MULTIPLE STUDENTS (OPTIMIZED)
# =========================
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
import json

@app.post("/evaluate-multiple")
async def evaluate_multiple(
    student_files: list[UploadFile] = File(...),
    answer_key_file: UploadFile = File(...)
):
    async def event_stream():
        try:
            step_queue = Queue()
            results = []

            # =========================
            # Save answer key
            # =========================
            with tempfile.NamedTemporaryFile(delete=False) as key_temp:
                shutil.copyfileobj(answer_key_file.file, key_temp)
                key_path = key_temp.name

            # =========================
            # Prepare key ONCE
            # =========================
            with open(key_path, "rb") as kf:
                key_json, err = prepare_answer_key(kf)

            if err:
                yield json.dumps({"type": "error", "message": err}) + "\n"
                return

            # =========================
            # Worker function
            # =========================
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

                        # 🔥 FIX: parse LLM output
                        if isinstance(result, list) and len(result) > 0:
                            try:
                                result = json.loads(result[0]["text"])
                            except Exception as e:
                                print("JSON parse error:", e)

                    step_queue.put({
                        "type": "done_student",
                        "student": student_name,
                        "result": result,
                        "error": err
                    })

                except Exception as e:
                    step_queue.put({
                        "type": "done_student",
                        "student": student.filename,
                        "error": str(e)
                    })

            # =========================
            # Run in parallel
            # =========================
            executor = ThreadPoolExecutor(max_workers=3)

            for student in student_files:
                executor.submit(process_single_student, student)

            completed = 0
            total = len(student_files)

            # =========================
            # STREAM LOOP
            # =========================
            while completed < total:
                item = step_queue.get()

                if item["type"] == "done_student":
                    completed += 1
                    results.append(item)

                print(json.dumps(item, indent=2))  # DEBUG
                yield json.dumps(item) + "\n"

            # =========================
            # FINAL OUTPUT
            # =========================
            final_data = {
                "type": "final",
                "results": results
            }

            print(json.dumps(final_data, indent=2))  # ✅ FIXED
            yield json.dumps(final_data) + "\n"

        except Exception as e:
            error_data = {"type": "error", "message": str(e)}
            print(json.dumps(error_data, indent=2))
            yield json.dumps(error_data) + "\n"

    return StreamingResponse(event_stream(), media_type="text/plain")