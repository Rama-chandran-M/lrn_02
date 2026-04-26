import { useState } from "react";
import UploadForm from "./components/UploadForm";
import Results from "./components/Results";
import { evaluateAPIStream } from "./services/api";
import type { Result } from "./types/types";

function App() {
  const [result, setResult] = useState<Result | null>(null);
  const [loading, setLoading] = useState(false);

  // 🔥 NEW
  const [steps, setSteps] = useState<string[]>([]);
  const [progress, setProgress] = useState(0);

  const handleSubmit = async (student: File, key: File) => {
    try {
      setLoading(true);
      setSteps([]);
      setProgress(0);
      setResult(null);

      await evaluateAPIStream(
        student,
        key,
        (step, prog) => {
          setSteps((prev) => [...prev, step]);
          setProgress(prog);
        },
        (data) => {
          setResult(data);
          setLoading(false);
        },
        (err) => {
          console.error(err);
          alert("Something went wrong. Please try again.");
          setLoading(false);
        }
      );
    } catch (err) {
      console.error(err);
      alert("Something went wrong.");
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
        {!result ? (
          <div style={styles.uploadSection}>
            <div style={styles.hero}>
              <h1 style={styles.h1}>Answer Sheet Evaluator</h1>
              <p style={styles.subtitle}>
                Upload a student answer sheet and answer key to get a clean,
                structured evaluation report instantly.
              </p>
            </div>

            <UploadForm onSubmit={handleSubmit} loading={loading} />

            {/* 🔥 PROGRESS UI */}
            {loading && (
              <div style={styles.progressCard}>
                <div style={styles.progressHeader}>
                  <span style={styles.progressTitle}>Processing</span>
                  <span style={styles.progressPercent}>{progress}%</span>
                </div>

                {/* Progress bar */}
                <div style={styles.progressBar}>
                  <div
                    style={{
                      ...styles.progressFill,
                      width: `${progress}%`,
                    }}
                  />
                </div>

                {/* Steps */}
                <div style={styles.steps}>
                  {steps.map((s, i) => (
                    <div key={i} style={styles.step}>
                      ✔ {s}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          <Results result={result} onReset={() => setResult(null)} />
        )}
      </main>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  root: {
    minHeight: "100vh",
    backgroundColor: "#fafaf9",
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
    color: "#111",
  },

  header: {
    borderBottom: "1px solid #ececea",
    backgroundColor: "#fff",
    position: "sticky",
    top: 0,
    zIndex: 10,
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
    alignItems: "center",
    gap: 8,
  },

  logoMark: {
    width: 18,
    height: 18,
    borderRadius: 5,
    backgroundColor: "#111",
  },

  logoText: {
    fontSize: 15,
    fontWeight: 600,
  },

  badge: {
    fontSize: 11,
    backgroundColor: "#f3f3f1",
    color: "#666",
    borderRadius: 5,
    padding: "3px 8px",
  },

  main: {
    maxWidth: 960,
    margin: "0 auto",
    padding: "56px 24px 80px",
  },

  uploadSection: {
    maxWidth: 560,
    margin: "0 auto",
  },

  hero: {
    marginBottom: 40,
  },

  h1: {
    fontSize: 28,
    fontWeight: 600,
    marginBottom: 8,
  },

  subtitle: {
    fontSize: 15,
    color: "#666",
    lineHeight: 1.6,
  },

  /* 🔥 NEW PROGRESS UI */

  progressCard: {
    marginTop: 24,
    border: "1px solid #eee",
    borderRadius: 12,
    padding: 16,
    background: "#fff",
    display: "flex",
    flexDirection: "column",
    gap: 12,
  },

  progressHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
  },

  progressTitle: {
    fontSize: 14,
    fontWeight: 500,
  },

  progressPercent: {
    fontSize: 13,
    color: "#666",
  },

  progressBar: {
    height: 6,
    background: "#f1f1f1",
    borderRadius: 6,
    overflow: "hidden",
  },

  progressFill: {
    height: "100%",
    background: "#111",
    transition: "width 0.3s ease",
  },

  steps: {
    display: "flex",
    flexDirection: "column",
    gap: 6,
  },

  step: {
    fontSize: 13,
    color: "#444",
  },
};

export default App;