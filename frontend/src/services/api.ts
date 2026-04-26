export const evaluateMultipleStream = async (
  studentFiles: File[],
  answerKeyFile: File,
  onStep: (student: string, step: string, progress: number) => void,
  onStudentDone: (student: string, result: any) => void,
  onFinal: (results: any[]) => void,
  onError: (err: string) => void
) => {
  const formData = new FormData();

  studentFiles.forEach((file) => {
    formData.append("student_files", file);
  });

  formData.append("answer_key_file", answerKeyFile);

  const res = await fetch("http://127.0.0.1:8000/evaluate-multiple", {
    method: "POST",
    body: formData,
  });

  if (!res.body) {
    onError("No response from server");
    return;
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder("utf-8");

  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    for (let line of lines) {
      if (!line.trim()) continue;

      try {
        const data = JSON.parse(line);
        console.log("MULTI STREAM:", data);

        if (data.type === "step") {
          onStep(data.student, data.message, data.progress);
        }

        if (data.type === "done_student") {
          onStudentDone(data.student, data.result);
        }

        if (data.type === "final") {
          onFinal(data.results);
        }

        if (data.type === "error") {
          onError(data.message);
        }
      } catch (err) {
        console.error("Parse error:", err);
      }
    }
  }
};


export const evaluateSingle = async (
  studentFile: File,
  answerKeyFile: File,
  onStep: (step: string, progress: number) => void
) => {
  const formData = new FormData();
  formData.append("student_file", studentFile);
  formData.append("answer_key_file", answerKeyFile);

  const res = await fetch("http://127.0.0.1:8000/evaluate", {
    method: "POST",
    body: formData,
  });

  if (!res.body) throw new Error("No response body");

  const reader = res.body.getReader();
  const decoder = new TextDecoder();

  let buffer = "";
  let finalResult: any = null;

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    for (const line of lines) {
      if (!line.trim()) continue;

      try {
        const data = JSON.parse(line);
        console.log("SINGLE STREAM:", data); // 🔥 DEBUG

        // 🔹 STEP
        if (data.type === "step") {
          onStep(data.message, data.progress);
        }

        // 🔥 FIX: HANDLE RESULT CORRECTLY
        else if (data.type === "result") {
          finalResult = data.data;
        }

        // 🔹 ERROR
        else if (data.type === "error") {
          throw new Error(data.message);
        }
      } catch (err) {
        console.error("Parse error:", err);
      }
    }
  }

  if (!finalResult) {
    throw new Error("No result received from server");
  }

  return finalResult;
};