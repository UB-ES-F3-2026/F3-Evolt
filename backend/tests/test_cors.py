"""Tests del CORS cap al frontend de desenvolupament (T07.2).

Executar des de backend/:  python -m pytest tests/test_cors.py
"""

from fastapi.testclient import TestClient

from app.config import DEFAULT_FRONTEND_ORIGIN as FRONTEND_ORIGIN


def test_preflight_from_frontend_origin_is_allowed(client: TestClient) -> None:
    """El preflight des de l'origen de Vite (5173) rep permís."""
    response = client.options(
        "/api/health",
        headers={
            "Origin": FRONTEND_ORIGIN,
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "content-type,x-user-id",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == FRONTEND_ORIGIN


def test_get_from_frontend_origin_exposes_cors_header(client: TestClient) -> None:
    """Una petició simple des de 5173 també porta el header d'origen."""
    response = client.get("/api/health", headers={"Origin": FRONTEND_ORIGIN})

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == FRONTEND_ORIGIN


def test_other_origin_gets_no_cors_header(client: TestClient) -> None:
    """Un altre origen (3000) no rep cap permís de CORS."""
    response = client.get("/api/health", headers={"Origin": "http://localhost:3000"})

    assert "access-control-allow-origin" not in response.headers


def test_unexpected_error_response_includes_cors_header(client: TestClient) -> None:
    """Una 500 inesperada (p. ex. /api/probe/crash) també porta CORS."""
    response = client.get("/api/probe/crash", headers={"Origin": FRONTEND_ORIGIN})

    assert response.status_code == 500
    assert response.headers["access-control-allow-origin"] == FRONTEND_ORIGIN
