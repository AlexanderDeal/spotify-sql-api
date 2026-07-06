from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database import get_schema, run_query
from dotenv import load_dotenv
import os
import anthropic
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

client = anthropic.Anthropic()

class QueryRequest(BaseModel):
    question: str
    limit: int = 200

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def strip_markdown_fence(sql_query: str) -> str:
    sql_query = sql_query.strip()
    if sql_query.startswith("```") and sql_query.endswith("```"):
        lines = sql_query.split("\n")
        lines = lines[1:-1]  # drop first and last line
        return "\n".join(lines)
    return sql_query

@app.post("/query")
def query(request: QueryRequest):
    schema = get_schema()
    
    prompt = f"""You are a SQL expert. Given this database schema:
    {schema}

    Write a SQL query to answer this question: {request.question}

    Respond with ONLY the SQL query, no explanation, no markdown formatting."""

    message = client.messages.create(
        model="claude-sonnet-5",  # model may need to update in the future
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )

    sql = message.content[0].text    # extract the SQL text from Claude's response
    sql = strip_markdown_fence(sql)  # checks and removes markdown formatting
    
    try:
        results, total_count = run_query(sql, request.limit)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"sql": sql, "results": results, "total_count": total_count}
