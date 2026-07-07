import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).parent
db_path = BASE_DIR / "spotify.db"

def get_schema():
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute("PRAGMA table_info(tracks)")
    rows = cursor.fetchall()

    columns = []
    for row in rows:
        columns.append(f"{row[1]} {row[2]}")
    schema = "tracks(" + ", ".join(columns) + ")"

    connection.close()
    return schema

def run_query(sql_query, limit=200):
    if not sql_query.strip().lower().startswith("select"):
        raise ValueError("Only SELECT queries are allowed.")
    connection = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    cursor = connection.cursor()

    try:
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        column_names = [col[0] for col in cursor.description]
        total_count = len(rows)
        limit = min(limit, 1000)  # enforce a maximum limit of 1000 rows
        rows = rows[:limit]
    except sqlite3.Error as e:
        raise ValueError(f"SQL error: {e}")
    finally:
        connection.close()
        
    return rows, total_count, column_names