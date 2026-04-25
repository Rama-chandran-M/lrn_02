import type { Result } from "../types/types"

interface Props {
  result: Result;
}

const Results = ({ result }: Props) => {
  return (
    <div>
      <h2>Results</h2>

      <p>Score: {result.summary.total_score}</p>
      <p>Max: {result.summary.max_score}</p>
      <p>Percentage: {result.summary.percentage}%</p>

      <h3>Strengths</h3>
      <p>{result.summary.strengths}</p>

      <h3>Weaknesses</h3>
      <p>{result.summary.weaknesses}</p>

      <h3>Evaluation</h3>

      {result.evaluation.map((q, i) => (
        <div key={i}>
          <p><strong>Q{q.question_number}</strong></p>
          <p>{q.question_title}</p>
          <p>Score: {q.score}/{q.marks}</p>
          <p>Status: {q.status}</p>
          <p>Your Answer: {q.student_answer || "Not Attempted"}</p>
        </div>
      ))}
    </div>
  );
};

export default Results;