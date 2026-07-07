import { useState } from "react";
import "./App.css";

function App() {
  const [question, setQuestion] = useState("");
  const [results, setResults] = useState<any[][]>([]);
  const [error, setError] = useState("");
  const [sql, setSql] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [limit, setLimit] = useState(200);
  const [totalCount, setTotalCount] = useState(0);

  const handleClick = async () => {
    const apiUrl = import.meta.env.VITE_API_URL;
    setIsLoading(true);

    try {
      const response = await fetch(`${apiUrl}/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: question, limit: limit }),
      });
      const data = await response.json();

      if (!response.ok) {
        setError(data.detail);
        setResults([]);
        return;
      }

      setError("");
      setSql(data.sql);
      setResults(data.results);
      setTotalCount(data.total_count);

    } catch (err) {
      setError("Could not reach the server");
      setResults([]);

    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container">
      <input
        className="question-input"
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
      />
      <button onClick={handleClick} disabled={isLoading} className="submit-button">
        {isLoading ? "Loading..." : "Submit"}
      </button>

      <div className="limit-container">
        <label htmlFor="limit-input">Max rows:</label>
        <input
          className="limit-input"
          type="number"
          value={limit}
          onChange={(e) => setLimit(Number(e.target.value))}
          min={1}
          max={1000}
        />
      </div>

      <p>Showing {results.length} of {totalCount} rows</p>

      {sql && (
        <pre className="sql-output">{sql}</pre>
      )}

      <table className="results-table">
        <tbody>
          {results.map((row, index) => (
            <tr key={index}>
              {row.map((cell, i) => (
                <td key={i}>{cell}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>

      {error && <p className="error">
        {error}
      </p>}

    </div>
  );
}

export default App;