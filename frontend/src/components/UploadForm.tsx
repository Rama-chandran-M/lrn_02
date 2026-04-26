import { useState, useRef } from "react";

interface Props {
  onSubmit: (student: File, key: File) => void;
  loading: boolean;
}

interface FileSlotProps {
  label: string;
  description: string;
  file: File | null;
  onChange: (file: File | null) => void;
}

const FileSlot = ({ label, description, file, onChange }: FileSlotProps) => {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const dropped = e.dataTransfer.files[0];
    if (dropped) onChange(dropped);
  };

  return (
    <div style={styles.slotWrapper}>
      <label style={styles.slotLabel}>{label}</label>
      <div
        style={{
          ...styles.dropZone,
          ...(dragging ? styles.dropZoneActive : {}),
          ...(file ? styles.dropZoneFilled : {}),
        }}
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
      >
        <input
          ref={inputRef}
          type="file"
          style={{ display: "none" }}
          onChange={(e) => onChange(e.target.files?.[0] || null)}
        />
        {file ? (
          <div style={styles.fileInfo}>
            <span style={styles.fileIcon}>
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M9 1H3a1 1 0 00-1 1v12a1 1 0 001 1h10a1 1 0 001-1V6L9 1z" stroke="#444" strokeWidth="1.2" fill="none"/>
                <path d="M9 1v5h5" stroke="#444" strokeWidth="1.2" fill="none"/>
              </svg>
            </span>
            <div>
              <p style={styles.fileName}>{file.name}</p>
              <p style={styles.fileSize}>{(file.size / 1024).toFixed(1)} KB</p>
            </div>
            <button
              style={styles.removeBtn}
              onClick={(e) => { e.stopPropagation(); onChange(null); }}
            >
              ✕
            </button>
          </div>
        ) : (
          <div style={styles.emptyState}>
            <span style={styles.uploadIconWrap}>
              <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                <path d="M9 12V4M9 4L6 7M9 4l3 3" stroke="#999" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M3 13v1a1 1 0 001 1h10a1 1 0 001-1v-1" stroke="#999" strokeWidth="1.4" strokeLinecap="round"/>
              </svg>
            </span>
            <p style={styles.emptyText}>
              <span style={styles.clickText}>Click to upload</span> or drag & drop
            </p>
            <p style={styles.emptyDesc}>{description}</p>
          </div>
        )}
      </div>
    </div>
  );
};

const UploadForm = ({ onSubmit, loading }: Props) => {
  const [studentFile, setStudentFile] = useState<File | null>(null);
  const [answerKeyFile, setAnswerKeyFile] = useState<File | null>(null);

  const canSubmit = !!studentFile && !!answerKeyFile && !loading;

  return (
    <div style={styles.form}>
      <FileSlot
        label="Student Answer Sheet"
        description="PDF or image of the student's answers"
        file={studentFile}
        onChange={setStudentFile}
      />
      <FileSlot
        label="Answer Key"
        description="PDF or image of the correct answers"
        file={answerKeyFile}
        onChange={setAnswerKeyFile}
      />

      <button
        style={{
          ...styles.submitBtn,
          ...(canSubmit ? {} : styles.submitBtnDisabled),
        }}
        onClick={() => canSubmit && onSubmit(studentFile!, answerKeyFile!)}
        disabled={!canSubmit}
      >
        {loading ? (
          <span style={styles.btnContent}>
            <span style={styles.spinner} /> Processing…
          </span>
        ) : (
          "Run Evaluation"
        )}
      </button>
    </div>
  );
};

// only styles updated — logic untouched

const styles: Record<string, React.CSSProperties> = {
  form: {
    display: "flex",
    flexDirection: "column",
    gap: 18,
  },
  slotWrapper: {
    display: "flex",
    flexDirection: "column",
    gap: 6,
  },
  slotLabel: {
    fontSize: 13,
    fontWeight: 500,
    color: "#333",
  },
  dropZone: {
    border: "1px dashed #d6d6d2",
    borderRadius: 12,
    backgroundColor: "#fff",
    padding: "22px",
    cursor: "pointer",
    transition: "all 0.15s ease",
  },
  dropZoneActive: {
    borderColor: "#aaa",
    backgroundColor: "#f5f5f3",
  },
  dropZoneFilled: {
    border: "1px solid #ddd",
  },
  emptyState: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: 6,
  },
  uploadIconWrap: {
    width: 40,
    height: 40,
    borderRadius: 10,
    backgroundColor: "#f3f3f1",
  },
  emptyText: {
    fontSize: 13,
    color: "#555",
  },
  clickText: {
    fontWeight: 500,
    color: "#111",
  },
  emptyDesc: {
    fontSize: 12,
    color: "#999",
  },
  fileInfo: {
    display: "flex",
    alignItems: "center",
    gap: 12,
  },
  fileName: {
    fontSize: 13,
    fontWeight: 500,
  },
  fileSize: {
    fontSize: 12,
    color: "#888",
  },
  removeBtn: {
    marginLeft: "auto",
    background: "#f3f3f1",
    border: "none",
    borderRadius: 6,
    padding: "4px 6px",
    cursor: "pointer",
  },
  submitBtn: {
    marginTop: 10,
    padding: "12px",
    fontSize: 14,
    fontWeight: 500,
    color: "#fff",
    backgroundColor: "#111",
    borderRadius: 10,
    cursor: "pointer",
    transition: "opacity 0.2s",
  },
  submitBtnDisabled: {
    backgroundColor: "#ccc",
    cursor: "not-allowed",
  },
  btnContent: {
    display: "flex",
    justifyContent: "center",
    gap: 8,
  },
  spinner: {
    width: 14,
    height: 14,
    border: "2px solid rgba(255,255,255,0.3)",
    borderTopColor: "#fff",
    borderRadius: "50%",
    animation: "spin 0.7s linear infinite",
  },
};

export default UploadForm;
