"""Tests del endpoint de salut (T07.2, docs/api.md §2).

Executar des de backend/:  python -m pytest tests/test_health.py
"""

from fastapi.testclient import TestClient


def test_health_returns_200_and_status_ok(client: TestClient) -> None:
    """GET /api/health respon 200 amb el JSON exacte {"status": "ok"}."""
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert response.headers["content-type"].startswith("application/json")


def test_health_ignores_invalid_user_header(client: TestClient) -> None:
    """L'endpoint de salut no resol l'usuari: amb X-User-Id invàlid segueix
    sent 200 (docs/api.md §2)."""
    response = client.get("/api/health", headers={"X-User-Id": "abc"})

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
