# Spotify Talk-to-Your-Data

Ask questions about a Spotify track dataset in plain English and get real answers — powered by the Claude API translating natural language into SQL, executed against a local database.

**Example:** *"What are the 10 most popular tracks?"* → generates and runs `SELECT track_name, artist_name, track_popularity FROM tracks ORDER BY track_popularity DESC LIMIT 10;` → returns a live results table, the SQL that ran, and a total row count.

## Stack

- **Backend:** FastAPI (Python), SQLite
- **Frontend:** React + TypeScript (Vite)
- **LLM:** Anthropic Claude API (NL → SQL translation)

## How it works

1. User types a question in the frontend
2. Backend sends the database schema + the question to Claude, asking it to generate a SQL query
3. Claude's response is cleaned (stripped of markdown formatting it sometimes adds despite instructions not to) and validated
4. The query runs against a local SQLite database of Spotify track data
5. Results, the executed SQL, and a total row count are returned to the frontend and rendered as a table

## Security considerations

Since an LLM is generating SQL from untrusted user input before it touches a real database, this project treats that output as untrusted and layers multiple independent defenses rather than relying on prompt instructions alone:

- **Query allowlisting:** only strings starting with `SELECT` are permitted — Claude cannot generate `DROP`, `DELETE`, `UPDATE`, `INSERT`, etc.
- **Read-only database connection:** the connection used to run generated SQL is opened in SQLite's URI read-only mode (`file:...?mode=ro`), so even a bypass of the check above still can't write to the database.
- **Statement-stacking protection:** verified that Python's `sqlite3.execute()` refuses to run multiple semicolon-separated statements in one call, closing off a classic SQL injection technique (`SELECT 1; DROP TABLE tracks;`).
- **Graceful failure:** SQL/database errors are caught and returned as clean, generic 400 responses rather than leaking internal error details or crashing the server.
- **Result capping:** the number of rows returned is capped server-side (max 1000) regardless of what a client requests, preventing unbounded queries from returning excessive data.

**Known limitation:** validation is string-based (checks the query starts with `SELECT`), not a full SQL parser — a sufficiently obscure query could theoretically evade the prefix check. Defense-in-depth (read-only connection, no multi-statement execution) is what actually prevents damage even in that case, and this is intentionally documented here as a known trade-off rather than over-engineering a project of this scope with a full SQL parser.

## Running locally

**Backend:**
```
cd backend
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
Create a `.env` file in `backend/` with:
```
ANTHROPIC_API_KEY=your_key_here
```
Then run:
```
uvicorn main:app --reload
```

**Frontend:**
```
cd frontend
npm install
```
Create a `.env` file in `frontend/` with:
```
VITE_API_URL=http://127.0.0.1:8000
```
Then run:
```
npm run dev
```

Visit `http://localhost:5173`.

## Dataset

`spotify.db` (SQLite) — a single `tracks` table with metadata for each track: name, popularity, duration, explicit flag, artist details, and album details.
