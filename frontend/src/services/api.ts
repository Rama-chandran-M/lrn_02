export const evaluateAPIStream = async (
  studentFile: File,
  answerKeyFile: File,
  onStep: (step: string, progress: number) => void,
  onResult: (data: any) => void,
  onError: (err: string) => void
) => {
  const formData = new FormData();
  formData.append("student_file", studentFile);
  formData.append("answer_key_file", answerKeyFile);

  const res = await fetch("http://127.0.0.1:8000/evaluate", {
    method: "POST",
    body: formData,
  });

  const reader = res.body?.getReader();
  const decoder = new TextDecoder("utf-8");

  while (true) {
    const { done, value } = await reader!.read();
    if (done) break;

    const chunk = decoder.decode(value);
    const lines = chunk.split("\n").filter(Boolean);

    for (let line of lines) {
      const data = JSON.parse(line);

      if (data.type === "step") {
        onStep(data.message, data.progress);
      }

      if (data.type === "result") {
        onResult(data.data);
      }

      if (data.type === "error") {
        onError(data.message);
      }
    }
  }
};