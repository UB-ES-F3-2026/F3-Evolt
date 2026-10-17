"""Tests de la conversió d'errors al contracte (T07.2, docs/api.md §5).

Executar des de backend/:  python -m pytest tests/test_errors.py
"""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.services.errors import DAILY_LIMIT_EXCEEDED, INTERNAL_ERROR

INTERNAL_MESSAGE = "S'ha produït un error inesperat. Torna-ho a provar més tard."
VALIDATION_MESSAGE = "Les dades de la petició no són vàlides."


def test_unexpected_error_returns_internal_error_without_leaking(app: FastAPI) -> None:
    """Un error de programador no aboca el text intern ni el traceback al client."""
    # El TestClient re-llança les excepcions que l'aplicació ja ha tractat, i
    # per això cal `raise_server_exceptions=False`: la resposta del handler sí
    # que s'envia, però Starlette torna a llençar l'excepció després.
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/api/probe/crash")

    assert response.status_code == 500
    assert response.json() == {"code": INTERNAL_ERROR, "message": INTERNAL_MESSAGE}
    assert "boom" not in response.text
    assert "Traceback" not in response.text
    assert "details" not in response.json()


def test_malformed_query_param_returns_validation_error(client: TestClient) -> None:
    """Un paràmetre que no es pot convertir és un 422 VALIDATION_ERROR."""
    response = client.get("/api/probe/validation", params={"limit": "abc"})

    body = response.json()
    assert response.status_code == 422
    assert body["code"] == "VALIDATION_ERROR"
    assert body["message"] == VALIDATION_MESSAGE
    assert "details" not in body
    assert "detail" not in body


def test_api_error_with_details_includes_details(client: TestClient) -> None:
    """Un ApiError llençat pels serveis manté els seus details."""
    response = client.get("/api/probe/api-error")

    body = response.json()
    assert response.status_code == 422
    assert body["code"] == DAILY_LIMIT_EXCEEDED
    assert body["details"] == {"remainingToday": 10000}


def test_unexpected_http_exception_becomes_internal_error(client: TestClient) -> None:
    """El contracte no té codi per a 404/405: esdevenen INTERNAL_ERROR a 500."""
    response = client.get("/api/does-not-exist")

    body = response.json()
    assert response.status_code == 500
    assert body["code"] == INTERNAL_ERROR
