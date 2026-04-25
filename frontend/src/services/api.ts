import axios from "axios";
import type { Result } from "../types/types";

export const evaluateAPI = async (
  studentFile: File,
  answerKeyFile: File
): Promise<Result> => {
  const formData = new FormData();
  formData.append("student_file", studentFile);
  formData.append("answer_key_file", answerKeyFile);

  const response = await axios.post<Result>(
    "http://127.0.0.1:8000/evaluate",
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }
  );

  return response.data;
};