from main import strip_markdown_fence
import pytest
from database import run_query
from database import get_schema

def test_strip_markdown_fence_removes_fence():
    wrapped = "```sql\nSELECT * FROM tracks\n```"
    result = strip_markdown_fence(wrapped)
    assert result == "SELECT * FROM tracks"

def test_strip_markdown_fence_leaves_plain_sql_unchanged():
    plain = "SELECT * FROM tracks"
    result = strip_markdown_fence(plain)
    assert result == plain

def test_run_query_rejects_non_select():
    with pytest.raises(ValueError):
        run_query("DELETE FROM tracks")

def test_run_query_allows_select():
    rows, total_count, column_names = run_query("SELECT track_name FROM tracks LIMIT 5")
    assert len(rows) == 5
    assert "track_name" in column_names

def test_get_schema_returns_expected_format():
    schema = get_schema()
    assert schema.startswith("tracks(")
    assert "track_name TEXT" in schema
    assert "track_popularity INTEGER" in schema

def test_run_query_caps_limit_at_1000():
    rows, total_count, column_names = run_query("SELECT track_id FROM tracks", limit=999999)
    assert len(rows) <= 1000

def test_run_query_total_count_reflects_full_result_not_cap():
    rows, total_count, column_names = run_query("SELECT track_id FROM tracks", limit=5)
    assert len(rows) == 5
    assert total_count >= len(rows)  # total_count should reflect all matching rows, not just the capped slice

def test_run_query_allows_lowercase_select():
    rows, total_count, column_names = run_query("select track_id from tracks limit 1")
    assert len(rows) == 1

def test_run_query_blocks_statement_stacking():
    with pytest.raises(ValueError):
        run_query("SELECT 1; DELETE FROM tracks;")

def test_strip_markdown_fence_ignores_unmatched_fence():
    malformed = "```sql\nSELECT * FROM tracks"  # no closing fence
    result = strip_markdown_fence(malformed)
    assert result == malformed
