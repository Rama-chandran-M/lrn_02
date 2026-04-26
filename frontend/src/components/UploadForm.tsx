import { useState, useRef } from "react";

interface Props {
  onSubmit: (students: File[], key: File) => void;
  loading: boolean;
}

const MAX_SIZE = 10 * 1024 * 1024; // 5MB

const UploadForm = ({ onSubmit, loading }: Props) => {
  const inputRef = useRef<HTMLInputElement>(null);
  const keyInputRef = useRef<HTMLInputElement>(null);

  const [dragging, setDragging] = useState(false);
  const [draggingKey, setDraggingKey] = useState(false);

  const [studentFiles, setStudentFiles] = useState<File[]>([]);
  const [answerKeyFile, setAnswerKeyFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);

  // 🔹 VALIDATION
  const validateFile = (file: File) => {
    if (!file.name.toLowerCase().endsWith(".pdf")) {
      return "Only PDF files are allowed";
    }
    if (file.size > MAX_SIZE) {
      return "File size must be less than 10MB";
    }
    return null;
  };

  const handleStudentDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    setError(null);

    const files = Array.from(e.dataTransfer.files);

    for (let file of files) {
      const err = validateFile(file);
      if (err) {
        setError(err);
        return;
      }
    }

    setStudentFiles(files);
  };

  const handleStudentChange = (files: FileList | null) => {
    if (!files) return;
    setError(null);

    const arr = Array.from(files);

    for (let file of arr) {
      const err = validateFile(file);
      if (err) {
        setError(err);
        return;
      }
    }

    setStudentFiles(arr);
  };

  const handleKeyDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDraggingKey(false);
    setError(null);

    const file = e.dataTransfer.files[0];
    if (!file) return;

    const err = validateFile(file);
    if (err) {
      setError(err);
      return;
    }

    setAnswerKeyFile(file);
  };

  const handleKeyChange = (file: File | null) => {
    if (!file) return;
    setError(null);

    const err = validateFile(file);
    if (err) {
      setError(err);
      return;
    }

    setAnswerKeyFile(file);
  };

  const removeStudent = (index: number) => {
    setStudentFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const canSubmit =
    studentFiles.length > 0 && !!answerKeyFile && !loading && !error;

  return (
    <div style={styles.form}>
      {/* 🔹 ERROR MESSAGE */}
      {error && <div style={styles.error}>{error}</div>}

      {/* 🔹 STUDENT FILES */}
      <div style={styles.slotWrapper}>
        <label style={styles.slotLabel}>
          Student Answer Sheets (PDF, max 10MB each)
        </label>

        <div
          style={{
            ...styles.dropZone,
            ...(dragging ? styles.dropZoneActive : {}),
            ...(studentFiles.length ? styles.dropZoneFilled : {}),
          }}
          onClick={() => inputRef.current?.click()}
          onDragOver={(e) => {
            e.preventDefault();
            setDragging(true);
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={handleStudentDrop}
        >
          <input
            ref={inputRef}
            type="file"
            multiple
            style={{ display: "none" }}
            onChange={(e) => handleStudentChange(e.target.files)}
          />

          {studentFiles.length > 0 ? (
            <div style={styles.fileList}>
              {studentFiles.map((file, i) => (
                <div key={i} style={styles.fileItem}>
                  <span>{file.name}</span>
                  <button
                    style={styles.removeBtn}
                    onClick={(e) => {
                      e.stopPropagation();
                      removeStudent(i);
                    }}
                  >
                    ✕
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <div style={styles.emptyState}>
              <p style={styles.emptyText}>
                <span style={styles.clickText}>
                  Upload multiple student sheets
                </span>
              </p>
              <p style={styles.emptyDesc}>Drag & drop or click</p>
            </div>
          )}
        </div>
      </div>

      {/* 🔹 ANSWER KEY */}
      <div style={styles.slotWrapper}>
        <label style={styles.slotLabel}>
          Answer Key (PDF, max 5MB)
        </label>

        <div
          style={{
            ...styles.dropZone,
            ...(draggingKey ? styles.dropZoneActive : {}),
            ...(answerKeyFile ? styles.dropZoneFilled : {}),
          }}
          onClick={() => keyInputRef.current?.click()}
          onDragOver={(e) => {
            e.preventDefault();
            setDraggingKey(true);
          }}
          onDragLeave={() => setDraggingKey(false)}
          onDrop={handleKeyDrop}
        >
          <input
            ref={keyInputRef}
            type="file"
            style={{ display: "none" }}
            onChange={(e) =>
              handleKeyChange(e.target.files?.[0] || null)
            }
          />

          {answerKeyFile ? (
            <div style={styles.fileItem}>
              <span>{answerKeyFile.name}</span>
            </div>
          ) : (
            <div style={styles.emptyState}>
              <p style={styles.emptyText}>
                <span style={styles.clickText}>Upload answer key</span>
              </p>
              <p style={styles.emptyDesc}>Drag & drop or click</p>
            </div>
          )}
        </div>
      </div>

      {/* 🔹 SUBMIT */}
      <button
        style={{
          ...styles.submitBtn,
          ...(canSubmit ? {} : styles.submitBtnDisabled),
        }}
        onClick={() => canSubmit && onSubmit(studentFiles, answerKeyFile!)}
        disabled={!canSubmit}
      >
        {loading ? "Processing..." : "Run Evaluation"}
      </button>
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  form: { display: "flex", flexDirection: "column", gap: 18 },
  slotWrapper: { display: "flex", flexDirection: "column", gap: 6 },
  slotLabel: { fontSize: 13, fontWeight: 500, color: "#333" },
  dropZone: {
    border: "1px dashed #d6d6d2",
    borderRadius: 12,
    backgroundColor: "#fff",
    padding: "20px",
    cursor: "pointer",
  },
  dropZoneActive: { backgroundColor: "#f5f5f3" },
  dropZoneFilled: { border: "1px solid #ddd" },
  emptyState: { textAlign: "center" },
  emptyText: { fontSize: 13, color: "#555" },
  clickText: { fontWeight: 500, color: "#111" },
  emptyDesc: { fontSize: 12, color: "#999" },
  fileList: { display: "flex", flexDirection: "column", gap: 6 },
  fileItem: {
    display: "flex",
    justifyContent: "space-between",
    fontSize: 13,
    background: "#f9f9f9",
    padding: "6px 10px",
    borderRadius: 6,
  },
  removeBtn: { background: "none", border: "none", cursor: "pointer" },
  submitBtn: {
    marginTop: 10,
    padding: "12px",
    fontSize: 14,
    fontWeight: 500,
    color: "#fff",
    backgroundColor: "#111",
    borderRadius: 10,
    cursor: "pointer",
  },
  submitBtnDisabled: { backgroundColor: "#ccc", cursor: "not-allowed" },
  error: {
    backgroundColor: "#ffecec",
    color: "#d8000c",
    padding: "10px",
    borderRadius: 8,
    fontSize: 13,
  },
};

export default UploadForm;