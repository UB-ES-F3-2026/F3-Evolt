"""Tests de T09.6: POST /api/dev/reset (docs/api.md §4.4).

Executar des de backend/:  python -m pytest tests/test_dev_reset.py
"""

from fastapi.testclient import TestClient


def test_reset_returns_ok(client: TestClient) -> None:
    response = client.post("/api/dev/reset")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_reset_restores_seed_after_topup(client: TestClient) -> None:
    initial_balance = client.get("/api/home").json()["balance"]
    initial_page = client.get("/api/movements", params={"limit": 50}).json()
    initial_count = len(initial_page["items"])

    changed = client.post("/api/topups", json={"amount": 5000})
    assert changed.status_code == 201
    assert changed.json()["balance"] == initial_balance + 5000

    client.post("/api/dev/reset")

    assert client.get("/api/home").json()["balance"] == initial_balance
    restored = client.get("/api/movements", params={"limit": 50}).json()
    assert len(restored["items"]) == initial_count


def test_reset_is_idempotent(client: TestClient) -> None:
    client.post("/api/dev/reset")
    first = client.get("/api/home").json()

    client.post("/api/dev/reset")
    second = client.get("/api/home").json()

    assert second == first
