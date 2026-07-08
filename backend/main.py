from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from database import get_schema, run_query
from dotenv import load_dotenv
import os
import anthropic
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

load_dotenv()

client = anthropic.Anthropic()

class HistoryItem(BaseModel):
    question: str
    sql: str

class QueryRequest(BaseModel):
    question: str
    limit: int = 200
    history: list[HistoryItem] = []

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up rate limiting 
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Define API endpoints
def strip_markdown_fence(sql_query: str) -> str:
    sql_query = sql_query.strip()
    if sql_query.startswith("```") and sql_query.endswith("```"):
        lines = sql_query.split("\n")
        lines = lines[1:-1]  # drop first and last line
        return "\n".join(lines)
    return sql_query

@app.post("/query")
@limiter.limit("10/minute")  # Limit to 10 requests per minute
def query(request: Request, body: QueryRequest):
    schema = get_schema()
    history_text = ""
    for item in body.history:
        history_text += f"Previous question: {item.question}\nPrevious SQL: {item.sql}\n\n"
    
    prompt = f"""You are a SQL expert. Given this database schema:
    {schema}

    You are given the following conversation history:
    {history_text}

    Write a SQL query to answer this question: {body.question}

    Respond with ONLY the SQL query, no explanation, no markdown formatting."""

    message = client.messages.create(
        model="claude-sonnet-5",  # model may need to update in the future
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )

    sql = next(block.text for block in message.content if block.type == "text")    # extract the SQL text from Claude's response
    sql = strip_markdown_fence(sql)  # checks and removes markdown formatting
    
    try:
        results, total_count, column_names = run_query(sql, body.limit)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"sql": sql, "results": results, "total_count": total_count, "column_names": column_names}
