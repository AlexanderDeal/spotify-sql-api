from fastapi import FastAPI
from pydantic import BaseModel
from database import get_schema, run_query
from dotenv import load_dotenv
import os
import anthropic

load_dotenv()

client = anthropic.Anthropic()

class QueryRequest(BaseModel):
    question: str

app = FastAPI()

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

    sql = message.content[0].text          # extract the SQL text from Claude's response
    results = run_query(sql)               # run it against the database

    return {"sql": sql, "results": results}
