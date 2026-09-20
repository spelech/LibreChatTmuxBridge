"""
API endpoint tests: /health, /api/status, /v1/models, /v1/chat/completions.
"""

from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert data["active_sessions"] == 2


def test_system_status(client: TestClient):
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "librechat-tmux-bridge"
    assert "settings" in data
    assert "sessions" in data
    assert "diagnostics" in data


def test_list_models(client: TestClient):
    response = client.get("/v1/models")
    assert response.status_code == 200
    data = response.json()
    assert data["object"] == "list"
    ids = [m["id"] for m in data["data"]]
    assert "tmux:new" in ids
    assert "tmux:agy-work" in ids
    assert "tmux:infra" in ids


def test_get_model(client: TestClient):
    # Found model
    res_ok = client.get("/v1/models/tmux:infra")
    assert res_ok.status_code == 200
    assert res_ok.json()["id"] == "tmux:infra"

    # 'new' pseudo model
    res_new = client.get("/v1/models/tmux:new")
    assert res_new.status_code == 200

    # Non-existent model
    res_404 = client.get("/v1/models/tmux:phantom_sess")
    assert res_404.status_code == 404


def test_chat_completions_non_streaming(client: TestClient):
    payload = {
        "model": "tmux:infra",
        "messages": [
            {"role": "user", "content": "echo 'Testing non streaming'"},
        ],
        "stream": False,
    }
    response = client.post("/v1/chat/completions", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["object"] == "chat.completion"
    assert len(data["choices"]) == 1
    assert (
        "executed echo 'Testing non streaming' successfully"
        in data["choices"][0]["message"]["content"]
    )


def test_chat_completions_streaming(client: TestClient):
    payload = {
        "model": "tmux:infra",
        "messages": [
            {"role": "user", "content": "ls -la"},
        ],
        "stream": True,
    }
    response = client.post("/v1/chat/completions", json=payload)
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]
    text = response.text
    assert "data: " in text
    assert "data: [DONE]" in text
    assert "executed ls -la successfully" in text
