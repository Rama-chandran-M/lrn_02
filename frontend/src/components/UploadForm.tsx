import { useState } from "react";

interface Props {
  onSubmit: (student: File, key: File) => void;
  loading: boolean;
}

const UploadForm = ({ onSubmit, loading }: Props) => {
  const [studentFile, setStudentFile] = useState<File | null>(null);
  const [answerKeyFile, setAnswerKeyFile] = useState<File | null>(null);

  const handleClick = () => {
    if (!studentFile || !answerKeyFile) {
      alert("Upload both files");
      return;
    }
    onSubmit(studentFile, answerKeyFile);
  };

  return (
    <div>
      <h2>Upload Files</h2>

      <input
        type="file"
        onChange={(e) => setStudentFile(e.target.files?.[0] || null)}
      />

      <input
        type="file"
        onChange={(e) => setAnswerKeyFile(e.target.files?.[0] || null)}
      />

      <button onClick={handleClick} disabled={loading}>
        {loading ? "Processing..." : "Run Evaluation"}
      </button>
    </div>
  );
};

export default UploadForm;