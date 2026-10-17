"""Tests de la resolució de l'usuari actual (T07.2, docs/api.md §2).

Executar des de backend/:  python -m pytest tests/test_current_user.py
"""

from fastapi.testclient import TestClient
from httpx import Response

from app.data.seed import DEMO_USER_ID

VALIDATION_MESSAGE = "Les dades de la petició no són vàlides."


def _assert_validation_error(response: Response) -> None:
    """Tots els valors no vàlids de X-User-Id comparteixen el mateix cos (D1)."""
    body = response.json()
    assert response.status_code == 422
    assert body["code"] == "VALIDATION_ERROR"
    assert body["message"] == VALIDATION_MESSAGE
    assert "details" not in body
    assert "detail" not in body


def test_missing_header_resolves_to_user_1(client: TestClient) -> None:
    """Sense capçalera es fa servir l'usuari demo (docs/api.md §2)."""
    response = client.get("/api/probe/user")

    assert response.status_code == 200
    assert response.json() == {"userId": DEMO_USER_ID}


def test_header_two_resolves_to_user_two(client: TestClient) -> None:
    """X-User-Id: 2 resol l'usuari 2, el compte buit de proves."""
    response = client.get("/api/probe/user", headers={"X-User-Id": "2"})

    assert response.status_code == 200
    assert response.json() == {"userId": 2}


def test_non_numeric_header_returns_validation_error(client: TestClient) -> None:
    """Un valor no numèric (abc) és un 422 VALIDATION_ERROR sense details."""
    response = client.get("/api/probe/user", headers={"X-User-Id": "abc"})

    _assert_validation_error(response)


def test_unknown_user_header_returns_validation_error(client: TestClient) -> None:
    """Un usuari inexistent (99) és un 422 VALIDATION_ERROR sense details."""
    response = client.get("/api/probe/user", headers={"X-User-Id": "99"})

    _assert_validation_error(response)


def test_empty_header_returns_validation_error(client: TestClient) -> None:
    """Una capçalera buida és un 422 VALIDATION_ERROR sense details."""
    response = client.get("/api/probe/user", headers={"X-User-Id": ""})

    _assert_validation_error(response)
