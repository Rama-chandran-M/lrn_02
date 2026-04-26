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


from fastapi.responses import StreamingResponse
import json

@app.post("/evaluate")
async def evaluate(
    student_file: UploadFile = File(...),
    answer_key_file: UploadFile = File(...)
):
    async def event_stream():
        try:
            # Save files
            with tempfile.NamedTemporaryFile(delete=False) as student_temp:
                shutil.copyfileobj(student_file.file, student_temp)
                student_path = student_temp.name

            with tempfile.NamedTemporaryFile(delete=False) as key_temp:
                shutil.copyfileobj(answer_key_file.file, key_temp)
                key_path = key_temp.name

            # 🔥 queue to send steps immediately
            from queue import Queue
            step_queue = Queue()

            def update_step(message, progress):
                step_queue.put({
                    "type": "step",
                    "message": message,
                    "progress": progress
                })

            # 🔥 run pipeline in background
            import threading

            result_holder = {"result": None, "error": None}

            def run_pipeline_task():
                with open(student_path, "rb") as sf, open(key_path, "rb") as kf:
                    result, err = run_full_pipeline(sf, kf, update_step=update_step)
                    result_holder["result"] = result
                    result_holder["error"] = err
                step_queue.put("DONE")

            threading.Thread(target=run_pipeline_task).start()

            # 🔥 stream steps LIVE
            while True:
                item = step_queue.get()

                if item == "DONE":
                    break

                yield json.dumps(item) + "\n"

            # send final result
            if result_holder["error"]:
                yield json.dumps({
                    "type": "error",
                    "message": result_holder["error"]
                }) + "\n"
            else:
                yield json.dumps({
                    "type": "result",
                    "data": result_holder["result"]
                }) + "\n"

        except Exception as e:
            yield json.dumps({"type": "error", "message": str(e)}) + "\n"

    return StreamingResponse(event_stream(), media_type="text/plain")