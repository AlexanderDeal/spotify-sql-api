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
  const [columns, setColumns] = useState<string[]>([]);
  const [conversation, setConversation] = useState<{question: string, sql: string}[]>([]);
  const exampleQuestions = [
    "What are the 10 most popular tracks?",
    "Show me the newest song by Taylor Swift.",
    "What's the average track duration?",
  ];

  const handleClick = async () => {
    if (!question.trim()) {
      setError("Please enter a question.");
      return;
    }
    const apiUrl = import.meta.env.VITE_API_URL;
    setIsLoading(true);

    try {
      const response = await fetch(`${apiUrl}/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: question, limit: limit, history: conversation }),
      });
      const data = await response.json();

      if (!response.ok) {
        setError(data.detail);
        setResults([]);
        setColumns([]);
        return;
      }

      setError("");
      setSql(data.sql);
      setColumns(data.column_names);
      setResults(data.results);
      setTotalCount(data.total_count);
      const updatedConversation = [...conversation, { question: question, sql: data.sql }];
      setConversation(updatedConversation.slice(-10)); // Keep only the last 10 items in the conversation history

    } catch (err) {
      setError("Could not reach the server");
      setResults([]);
      setColumns([]);

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
        onKeyDown={(e) => {
          if (e.key === "Enter") {
            handleClick();
          }
        }}
      />

      <button onClick={handleClick} disabled={isLoading} className="submit-button">
        {isLoading ? "Loading..." : "Submit"}
      </button>

      <div className="examples">
        {exampleQuestions.map((q, i) => (
          <button key={i} onClick={() => setQuestion(q)} className="example-chip">
            {q}
          </button>
        ))}
      </div>

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

      <div className="table-wrapper">
        <table className="results-table">
          <thead>
            <tr>
              {columns.map((col, i) => <th key={i}>{col}</th>)}
              </tr>
          </thead>
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

    </div>
  );
}

export default App;