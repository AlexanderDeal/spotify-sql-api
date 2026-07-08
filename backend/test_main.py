from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_query_endpoint_returns_results():
    fake_text_block = MagicMock()
    fake_text_block.type = "text"
    fake_text_block.text = "SELECT track_name FROM tracks LIMIT 3"

    fake_message = MagicMock()
    fake_message.content = [fake_text_block]

    with patch("main.client.messages.create", return_value=fake_message):
        response = client.post("/query", json={"question": "test"})

    assert response.status_code == 200
    assert "results" in response.json()

def test_query_endpoint_rejects_non_select():
    fake_text_block = MagicMock()
    fake_text_block.type = "text"
    fake_text_block.text = "DELETE FROM tracks"

    fake_message = MagicMock()
    fake_message.content = [fake_text_block]

    with patch("main.client.messages.create", return_value=fake_message):
        response = client.post("/query", json={"question": "delete everything"})

    assert response.status_code == 400
    assert "Only SELECT queries are allowed" in response.json()["detail"]

def test_query_endpoint_rate_limits_after_too_many_requests():
    fake_text_block = MagicMock()
    fake_text_block.type = "text"
    fake_text_block.text = "SELECT track_name FROM tracks LIMIT 1"

    fake_message = MagicMock()
    fake_message.content = [fake_text_block]

    with patch("main.client.messages.create", return_value=fake_message):
        responses = [client.post("/query", json={"question": "test"}) for _ in range(11)]

    assert responses[-1].status_code == 429