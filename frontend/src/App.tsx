import { useState } from "react";

function App() {
  const [question, setQuestion] = useState("");
  const [results, setResults] = useState<any[][]>([]);
  const [error, setError] = useState("");
  const [sql, setSql] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleClick = async () => {
  const apiUrl = import.meta.env.VITE_API_URL;
  setIsLoading(true);

  try {
    const response = await fetch(`${apiUrl}/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: question }),
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