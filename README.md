# Spotify Talk-to-Your-Data

Ask questions about a Spotify track dataset in plain English and get real answers — powered by the Claude API translating natural language into SQL, executed against a live database.

**Live demo:** [spotify-sql-api.netlify.app](https://spotify-sql-api.netlify.app/)
**Backend API:** [spotify-sql-api.onrender.com](https://spotify-sql-api.onrender.com)

**Example:** *"What are the 10 most popular tracks?"* → generates and runs `SELECT track_name, artist_name, track_popularity FROM tracks ORDER BY track_popularity DESC LIMIT 10;` → returns a live results table, the SQL that ran, and a total row count.

## Stack

- **Backend:** FastAPI (Python), SQLite
- **Frontend:** React + TypeScript (Vite)
- **LLM:** Anthropic Claude API (NL → SQL translation)
- **Deployment:** Render (backend), Netlify (frontend)

## Features

- Natural language to SQL translation with schema-aware prompting
- **Multi-turn conversation:** follow-up questions ("who's the artist?" after "what's the most popular song?") work by passing recent question/SQL history back to Claude for context
- Configurable result limit (user-adjustable, server-capped at 1000 rows)
- Example question chips for quick, no-typing demos
- Enter-to-submit, loading states, and clear error messaging for both network and validation failures
- Rate limiting (10 requests/minute per IP) to control API cost exposure on a publicly deployed endpoint

## How it works

1. User types a question in the frontend (or picks an example chip)
2. Backend sends the database schema, the question, and recent conversation history to Claude, asking it to generate a SQL query
3. Claude's response is cleaned (stripped of markdown formatting it sometimes adds despite instructions not to) and validated
4. The query runs against a SQLite database of Spotify track data
5. Results, the executed SQL, column names, and a total row count are returned to the frontend and rendered as a table

## Security considerations

Since an LLM is generating SQL from untrusted user input before it touches a real database, this project treats that output as untrusted and layers multiple independent defenses rather than relying on prompt instructions alone:

- **Query allowlisting:** only strings starting with `SELECT` are permitted — Claude cannot generate `DROP`, `DELETE`, `UPDATE`, `INSERT`, etc.
- **Read-only database connection:** the connection used to run generated SQL is opened in SQLite's URI read-only mode (`file:...?mode=ro`), so even a bypass of the check above still can't write to the database.
- **Statement-stacking protection:** verified that Python's `sqlite3.execute()` refuses to run multiple semicolon-separated statements in one call, closing off a classic SQL injection technique (`SELECT 1; DROP TABLE tracks;`).
- **Graceful failure:** SQL/database errors are caught and returned as clean, generic 400 responses rather than leaking internal error details or crashing the server.
- **Result capping:** the number of rows returned is capped server-side (max 1000) regardless of what a client requests, preventing unbounded queries from returning excessive data.
- **Rate limiting:** capped at 10 requests/minute per IP address, since every request costs real money via the Claude API and the endpoint is publicly reachable.

**Known limitation:** validation is string-based (checks the query starts with `SELECT`), not a full SQL parser — a sufficiently obscure query could theoretically evade the prefix check. Defense-in-depth (read-only connection, no multi-statement execution) is what actually prevents damage even in that case, and this is intentionally documented here as a known trade-off rather than over-engineering a project of this scope with a full SQL parser.

All of the above (except rate limiting, which is timing-dependent) is covered by an automated test suite — see below.

## Testing

Backend tests use `pytest`, including:
- Unit tests for schema formatting, markdown-fence stripping, and SQL validation logic
- Integration tests against the actual `/query` endpoint using FastAPI's `TestClient`, with the Claude API call mocked out (`unittest.mock`) so tests run without network access or real API cost
- Explicit regression tests for the security behaviors above, including the SELECT-only rejection and statement-stacking protection

Run them:
```
cd backend
pytest
```

## Running locally

**Backend:**
```
cd backend
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
Create a `.env` file in `backend/` (see `.env.example`) with:
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
Create a `.env` file in `frontend/` (see `.env.example`) with:
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
