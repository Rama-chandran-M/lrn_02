import type { Result } from "../types/types";

interface Props {
  result: Result | null;
  onReset: () => void;
}

const statusConfig: Record<string, { label: string; color: string; bg: string }> = {
  correct: { label: "Correct", color: "#166534", bg: "#dcfce7" },
  partial: { label: "Partial", color: "#92400e", bg: "#fef3c7" },
  incorrect: { label: "Incorrect", color: "#991b1b", bg: "#fee2e2" },
  not_attempted: { label: "Not Attempted", color: "#6b7280", bg: "#f3f4f6" },
};

const Results = ({ result, onReset }: Props) => {
  if (!result) {
    return <div style={{ padding: 20 }}>No result available</div>;
  }

  const summary = result?.summary;

  // 🔥 FIX 1: SAFE evaluation array
  const evaluation = Array.isArray(result?.evaluation)
    ? result.evaluation
    : [];

  if (!summary) {
    return <div style={{ padding: 20 }}>Preparing final report...</div>;
  }

  const pct = summary.percentage ?? 0;

  const scoreColor =
    pct >= 80 ? "#166534" : pct >= 50 ? "#92400e" : "#991b1b";

  const scoreBg =
    pct >= 80 ? "#dcfce7" : pct >= 50 ? "#fef3c7" : "#fee2e2";

  return (
    <div style={styles.root}>
      {/* Header */}
      <div style={styles.pageHeader}>
        <div>
          <h1 style={styles.h1}>Evaluation Report</h1>
          <p style={styles.headerSub}>
            {evaluation.length} question{evaluation.length !== 1 ? "s" : ""} evaluated
          </p>
        </div>
      </div>

      {/* Summary */}
      <div style={styles.summaryGrid}>
        <div style={styles.scoreCard}>
          <span style={styles.metricLabel}>Total Score</span>
          <span
            style={{
              ...styles.scorePill,
              color: scoreColor,
              backgroundColor: scoreBg,
            }}
          >
            {summary.total_score ?? 0} / {summary.max_score ?? 0}
          </span>
        </div>

        <div style={styles.scoreCard}>
          <span style={styles.metricLabel}>Percentage</span>
          <span style={styles.bigNumber}>{pct}%</span>
        </div>
      </div>

      {/* Insights */}
      <div style={styles.insightGrid}>
        <div style={styles.insightCard}>
          <div style={styles.insightHeader}>
            <span style={styles.insightTitle}>Strengths</span>
          </div>
          <p style={styles.insightBody}>
            {summary.strengths || "—"}
          </p>
        </div>

        <div style={styles.insightCard}>
          <div style={styles.insightHeader}>
            <span style={styles.insightTitle}>Areas for Improvement</span>
          </div>
          <p style={styles.insightBody}>
            {summary.weaknesses || "—"}
          </p>
        </div>
      </div>

      {/* Question Breakdown */}
      <div style={styles.section}>
        <h2 style={styles.sectionTitle}>Question Breakdown</h2>

        <div style={styles.questionList}>
          {evaluation.map((q, i) => {
            let mappedStatus = "not_attempted";

            if (q.status === "missing") {
              mappedStatus = "not_attempted";
            } else if (q.status === "attempted") {
              // 🔥 FIX 2: safer answer check
              if (!q.student_answer?.trim()) {
                mappedStatus = "not_attempted";
              }
              // 🔥 FIX 3: float-safe comparison
              else if ((q.score ?? 0) >= (q.marks ?? 0)) {
                mappedStatus = "correct";
              }
              else if ((q.score ?? 0) > 0) {
                mappedStatus = "partial";
              }
              else {
                mappedStatus = "incorrect";
              }
            }

            const cfg = statusConfig[mappedStatus];

            return (
              <div key={i} style={styles.qCard}>
                <div style={styles.qHeader}>
                  <span style={styles.qNumber}>
                    Q{q.question_number ?? i + 1}
                  </span>

                  <span
                    style={{
                      ...styles.statusBadge,
                      color: cfg.color,
                      backgroundColor: cfg.bg,
                    }}
                  >
                    {cfg.label}
                  </span>
                </div>

                <div style={styles.qBlock}>
                  <span style={styles.label}>Question</span>
                  <p style={styles.text}>{q.question_title || "—"}</p>
                </div>

                <div style={styles.qBlock}>
                  <span style={styles.label}>Your Answer</span>
                  <p style={styles.answerText}>
                    {/* 🔥 FIX 4: empty string handling */}
                    {q.student_answer?.trim()
                      ? q.student_answer
                      : "Not answered"}
                  </p>
                </div>

                <div style={styles.qBlock}>
                  <span style={styles.label}>Correct Answer</span>
                  <p style={styles.correctAnswer}>
                    {q.correct_answer || "—"}
                  </p>
                </div>

                <div style={styles.qFooter}>
                  <span style={styles.score}>
                    Score: {q.score ?? 0} / {q.marks ?? 0}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  root: { display: "flex", flexDirection: "column", gap: 28 },
  pageHeader: { display: "flex", justifyContent: "space-between", alignItems: "center" },
  h1: { fontSize: 24, fontWeight: 600 },
  headerSub: { fontSize: 13, color: "#888" },
  summaryGrid: { display: "grid", gridTemplateColumns: "repeat(2,1fr)", gap: 14 },
  scoreCard: { background: "#fff", border: "1px solid #eee", borderRadius: 12, padding: "20px" },
  metricLabel: { fontSize: 12, color: "#888" },
  bigNumber: { fontSize: 30, fontWeight: 600 },
  scorePill: { fontSize: 22, padding: "6px 14px", borderRadius: 10 },
  insightGrid: { display: "grid", gridTemplateColumns: "repeat(2,1fr)", gap: 14 },
  insightCard: { background: "#fff", border: "1px solid #eee", borderRadius: 12, padding: "18px" },
  insightHeader: { marginBottom: 6 },
  insightTitle: { fontSize: 14, fontWeight: 600 },
  insightBody: { fontSize: 13, color: "#555", lineHeight: 1.6 },
  section: { display: "flex", flexDirection: "column", gap: 12 },
  sectionTitle: { fontSize: 18, fontWeight: 600 },
  questionList: { display: "flex", flexDirection: "column", gap: 16 },
  qCard: { border: "1px solid #eee", borderRadius: 12, padding: 18, background: "#fff", display: "flex", flexDirection: "column", gap: 12 },
  qHeader: { display: "flex", justifyContent: "space-between", alignItems: "center" },
  qNumber: { fontSize: 14, fontWeight: 600, color: "#444" },
  qBlock: { display: "flex", flexDirection: "column", gap: 4 },
  label: { fontSize: 12, color: "#888" },
  text: { fontSize: 14, color: "#222", lineHeight: 1.5 },
  answerText: { fontSize: 14, color: "#555", lineHeight: 1.5 },
  correctAnswer: { fontSize: 14, color: "#1f2937", lineHeight: 1.5 },
  qFooter: { display: "flex", justifyContent: "flex-end" },
  score: { fontSize: 13, fontWeight: 500, color: "#333" },
  statusBadge: { fontSize: 11, borderRadius: 6, padding: "4px 8px" },
};

export default Results;