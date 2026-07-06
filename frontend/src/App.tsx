import { useState } from "react";

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
    <>
    <input
      value={question}
      onChange={(e) => setQuestion(e.target.value)}
    />
    <button onClick={handleClick} disabled={isLoading}>
      {isLoading ? "Loading..." : "Submit"}
    </button>

    <input 
      type="number"
      value={limit}
      onChange={(e) => setLimit(Number(e.target.value))}
      min={1}
      max={1000}
    />

    <p>Showing {results.length} of {totalCount} rows</p>

    <table>
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

    {sql && (
      <pre>{sql}</pre>
    )}

    {error && <p style={{ color: "red" }}>{error}</p>}

    </>
  );
}

export default App;