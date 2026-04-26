import { useState } from "react";
import UploadForm from "./components/UploadForm";
import Results from "./components/Results";
import { evaluateMultipleStream, evaluateSingle } from "./services/api";
import type { Result } from "./types/types";

function App() {
  const [results, setResults] = useState<
    { student: string; result: Result }[]
  >([]);
  const [progressMap, setProgressMap] = useState<
    Record<string, string[]>
  >({});
  const [expanded, setExpanded] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (students: File[], key: File) => {
    try {
      setLoading(true);
      setResults([]);
      setProgressMap({});
      setExpanded(null);

      // ✅ SINGLE (FIXED → STREAM SUPPORT)
      if (students.length === 1) {
        const studentName = students[0].name;

        const res = await evaluateSingle(
          students[0],
          key,
          (step, progress) => {
            setProgressMap((prev) => ({
              ...prev,
              [studentName]: [
                ...(prev[studentName] || []),
                step,
              ],
            }));
          }
        );

        setResults([
          {
            student: studentName,
            result: res,
          },
        ]);

        setLoading(false);
        return;
      }

      // ✅ MULTIPLE (UNCHANGED)
      await evaluateMultipleStream(
        students,
        key,
        (student, step) => {
          setProgressMap((prev) => ({
            ...prev,
            [student]: [...(prev[student] || []), step],
          }));
        },
        (student, result) => {
          setResults((prev) => [...prev, { student, result }]);
        },
        () => {
          setLoading(false);
        },
        (err) => {
          console.error(err);
          alert("Something went wrong");
          setLoading(false);
        }
      );
    } catch (err) {
      console.error(err);
      alert("Something went wrong");
      setLoading(false);
    }
  };

  return (
    <div style={styles.root}>
      <header style={styles.header}>
        <div style={styles.headerInner}>
          <div style={styles.logo}>
            <span style={styles.logoMark} />
            <span style={styles.logoText}>EvalAI</span>
          </div>
          <span style={styles.badge}>Beta</span>
        </div>
      </header>

      <main style={styles.main}>
        {!results.length ? (
          <div style={styles.uploadSection}>
            <div style={styles.hero}>
              <h1 style={styles.h1}>Answer Sheet Evaluator</h1>
              <p style={styles.subtitle}>
                Upload multiple student sheets and one answer key to get
                structured evaluation reports.
              </p>
            </div>

            <UploadForm onSubmit={handleSubmit} loading={loading} />

            {/* 🔥 NOW WORKS FOR BOTH SINGLE + MULTIPLE */}
            {loading && Object.keys(progressMap).length > 0 && (
              <div style={styles.progressWrap}>
                {Object.entries(progressMap).map(([student, steps]) => (
                  <div key={student} style={styles.studentCard}>
                    <div style={styles.studentHeader}>
                      <span style={styles.studentName}>{student}</span>
                    </div>

                    <div style={styles.steps}>
                      {steps.map((s, i) => (
                        <div key={i} style={styles.step}>
                          ✔ {s}
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        ) : (
          <>
            {/* ✅ GLOBAL RESET BUTTON */}
            <div style={styles.resetWrap}>
              <button
                style={styles.resetBtn}
                onClick={() => {
                  setResults([]);
                  setProgressMap({});
                  setExpanded(null);
                }}
              >
                ← New Evaluation
              </button>
            </div>

            {results.length === 1 ? (
              <Results result={results[0].result} onReset={() => {}} />
            ) : (
              <div style={styles.dropdownList}>
                {results.map((r, i) => (
                  <div key={i} style={styles.dropdownItem}>
                    <div
                      style={styles.dropdownHeader}
                      onClick={() =>
                        setExpanded(
                          expanded === r.student ? null : r.student
                        )
                      }
                    >
                      {expanded === r.student ? "▼" : "▶"} {r.student}
                    </div>

                    {expanded === r.student && (
                      <div style={styles.dropdownContent}>
                        <Results result={r.result} onReset={() => {}} />
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  root: {
    minHeight: "100vh",
    backgroundColor: "#fafaf9",
    fontFamily: "'Inter', sans-serif",
    color: "#111",
  },

  header: {
    borderBottom: "1px solid #ececea",
    backgroundColor: "#fff",
  },

  headerInner: {
    maxWidth: 960,
    margin: "0 auto",
    padding: "0 24px",
    height: 56,
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
  },

  logo: {
    display: "flex",
    gap: 8,
  },

  logoMark: {
    width: 18,
    height: 18,
    backgroundColor: "#111",
    borderRadius: 5,
  },

  logoText: {
    fontSize: 15,
    fontWeight: 600,
  },

  badge: {
    fontSize: 11,
    background: "#f3f3f1",
    padding: "3px 8px",
  },

  main: {
    maxWidth: 960,
    margin: "0 auto",
    padding: "40px 20px",
  },

  uploadSection: {
    maxWidth: 600,
    margin: "0 auto",
  },

  hero: {
    marginBottom: 30,
  },

  h1: {
    fontSize: 28,
    fontWeight: 600,
  },

  subtitle: {
    fontSize: 14,
    color: "#666",
  },

  progressWrap: {
    marginTop: 20,
    display: "flex",
    flexDirection: "column",
    gap: 10,
  },

  studentCard: {
    border: "1px solid #eee",
    padding: 12,
    borderRadius: 10,
    background: "#fff",
  },

  studentHeader: {
    fontWeight: 500,
    marginBottom: 6,
  },

  studentName: {
    fontSize: 14,
  },

  steps: {
    display: "flex",
    flexDirection: "column",
    gap: 4,
  },

  step: {
    fontSize: 13,
    color: "#444",
  },

  dropdownList: {
    display: "flex",
    flexDirection: "column",
    gap: 10,
  },

  dropdownItem: {
    border: "1px solid #eee",
    borderRadius: 10,
    overflow: "hidden",
    background: "#fff",
  },

  dropdownHeader: {
    padding: 12,
    cursor: "pointer",
    fontWeight: 500,
    background: "#fafafa",
  },

  dropdownContent: {
    padding: 12,
  },

  resetWrap: {
    display: "flex",
    justifyContent: "flex-end",
    marginBottom: 20,
  },

  resetBtn: {
    border: "1px solid #ddd",
    borderRadius: 8,
    padding: "8px 14px",
    background: "#fff",
    cursor: "pointer",
  },
};

export default App;