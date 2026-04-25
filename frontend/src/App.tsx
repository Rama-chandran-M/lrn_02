import { useState } from "react";
import UploadForm from "./components/UploadForm";
import Results from "./components/Results";
import { evaluateAPI } from "./services/api";
import type { Result } from "./types/types";

function App() {
  const [result, setResult] = useState<Result | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (student: File, key: File) => {
    try {
      setLoading(true);
      const data = await evaluateAPI(student, key);
      setResult(data);
    } catch (err) {
      console.error(err);
      alert("API error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>AI Answer Evaluator</h1>

      <UploadForm onSubmit={handleSubmit} loading={loading} />

      {result && <Results result={result} />}
    </div>
  );
}

export default App;