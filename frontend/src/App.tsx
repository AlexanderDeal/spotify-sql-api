import { useState } from "react";

function App() {
  const [question, setQuestion] = useState("");
  const handleClick = async () => {
    const apiUrl = import.meta.env.VITE_API_URL;

    const response = await fetch(`${apiUrl}/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: question }),
    });
    const data = await response.json();
    console.log(data);
  };

  return (
    <>
    <input
      value={question}
      onChange={(e) => setQuestion(e.target.value)}
    />
    <button onClick={handleClick}>Submit</button>
    </>
  );
}

export default App;