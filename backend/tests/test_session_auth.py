"""Tests de T03.1: rutes protegides amb sessió i transició d'X-User-Id (docs/api.md §8.2).

Proves G-01 a G-09 de docs/proves-acces.md.

Executar des de backend/:  python -m pytest tests/test_session_auth.py
"""

from collections.abc import Iterator
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from app.data.seed import DEMO_IDENTIFIER, EMPTY_USER_ID, MADRID_TZ, SEED_PASSWORD, build_seed
from app.main import create_app
from app.repositories import SessionRepository
from app.routers.current_user import bearer_token
from app.services.errors import UNAUTHENTICATED, ApiError
from app.services.session_service import user_id_for_token

FRONTEND_ORIGIN = "http://localhost:5173"
PROTECTED = [
    ("GET", "/api/home"),
    ("GET", "/api/movements"),
    ("POST", "/api/topups"),
]
UNAUTHENTICATED_BODY = {"code": "UNAUTHENTICATED", "message": "Cal iniciar sessió."}


@pytest.fixture
def strict_client(monkeypatch) -> Iterator[TestClient]:
    """App amb ALLOW_X_USER_ID=0, com quedarà després de la T03.5."""
    monkeypatch.setenv("ALLOW_X_USER_ID", "0")
    with TestClient(create_app()) as client:
        yield client


def _token(client: TestClient) -> str:
    response = client.post("/api/auth/login", json={"identifier": DEMO_IDENTIFIER, "password": SEED_PASSWORD})
    return response.json()["token"]


def _call(client: TestClient, method: str, path: str, headers: dict[str, str] | None = None):
    body = {"amount": 1000} if method == "POST" else None
    return client.request(method, path, json=body, headers=headers or {})


# --- Sense X-User-Id (després de la T03.5) -----------------------------------------


@pytest.mark.parametrize("method, path", PROTECTED)
def test_protected_routes_need_a_session(strict_client: TestClient, method: str, path: str) -> None:
    # G-01
    response = _call(strict_client, method, path)

    assert response.status_code == 401
    assert response.json() == UNAUTHENTICATED_BODY


@pytest.mark.parametrize("method, path", PROTECTED)
def test_x_user_id_is_ignored_when_not_allowed(strict_client: TestClient, method: str, path: str) -> None:
    assert _call(strict_client, method, path, {"X-User-Id": "1"}).status_code == 401


@pytest.mark.parametrize("method, path", PROTECTED)
def test_protected_routes_work_with_a_session(strict_client: TestClient, method: str, path: str) -> None:
    token = _token(strict_client)

    response = _call(strict_client, method, path, {"Authorization": f"Bearer {token}"})

    assert response.status_code in (200, 201)


def test_public_routes_do_not_need_a_session(strict_client: TestClient) -> None:
    # G-02
    assert strict_client.get("/api/health").status_code == 200
    assert strict_client.post("/api/auth/logout").status_code == 200


# --- Tokens no vàlids ---------------------------------------------------------------


@pytest.mark.parametrize(
    "authorization",
    [
        "Bearer inventat",  # G-03
        "Bearer ",
        "Bearer",
        "Basic dXN1YXJpOmNsYXU=",
        "inventat",
    ],
)
def test_invalid_authorization_is_unauthenticated(client: TestClient, authorization: str) -> None:
    response = client.get("/api/home", headers={"Authorization": authorization})

    assert response.status_code == 401
    assert response.json() == UNAUTHENTICATED_BODY


def test_scheme_is_case_insensitive(client: TestClient) -> None:
    token = _token(client)
    assert client.get("/api/home", headers={"Authorization": f"bearer {token}"}).status_code == 200


# --- Transició: amb X-User-Id permesa (per defecte fins a la T03.5) -----------------


def test_x_user_id_still_works_without_a_token(client: TestClient) -> None:
    # G-04 i G-08: els tests de l'Sprint 0 continuen passant.
    response = client.get("/api/home", headers={"X-User-Id": str(EMPTY_USER_ID)})

    assert response.status_code == 200
    assert response.json()["lastMovements"] == []


def test_token_wins_over_x_user_id(client: TestClient) -> None:
    # G-05: el token és de l'usuari 1; X-User-Id: 2 s'ignora.
    token = _token(client)

    response = client.get("/api/home", headers={"Authorization": f"Bearer {token}", "X-User-Id": "2"})

    assert response.json()["lastMovements"] != []


def test_invalid_token_does_not_fall_back_to_x_user_id(client: TestClient) -> None:
    # G-06
    response = client.get("/api/home", headers={"Authorization": "Bearer inventat", "X-User-Id": "1"})

    assert response.status_code == 401


# --- CORS i reinici -----------------------------------------------------------------


def test_preflight_allows_the_authorization_header(client: TestClient) -> None:
    # G-07
    response = client.options(
        "/api/home",
        headers={
            "Origin": FRONTEND_ORIGIN,
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "authorization",
        },
    )

    assert response.status_code == 200
    assert "authorization" in response.headers["access-control-allow-headers"].lower()


def test_dev_reset_closes_every_session(client: TestClient) -> None:
    # G-09
    token = _token(client)

    client.post("/api/dev/reset")

    assert client.get("/api/home", headers={"Authorization": f"Bearer {token}"}).status_code == 401


# --- Unitats: capçalera i servei ----------------------------------------------------


@pytest.mark.parametrize(
    "header, expected",
    [
        (None, None),
        ("Bearer abc", "abc"),
        ("bearer abc", "abc"),
        ("  Bearer   abc  ", "abc"),
        ("Bearer", ""),
        ("Basic abc", ""),
    ],
)
def test_bearer_token(header, expected) -> None:
    assert bearer_token(header) == expected


def test_each_request_records_the_last_activity() -> None:
    # La T03.2 farà servir aquesta hora per tancar la sessió als 5 minuts.
    seed = build_seed()
    sessions = SessionRepository(seed)
    opened = datetime(2026, 11, 3, 10, 0, tzinfo=MADRID_TZ)
    later = datetime(2026, 11, 3, 10, 4, tzinfo=MADRID_TZ)
    session = sessions.create(1, opened)

    assert user_id_for_token(session.token, sessions, now=later) == 1
    assert sessions.get(session.token).last_activity == later


def test_unknown_token_raises_unauthenticated() -> None:
    with pytest.raises(ApiError) as error:
        user_id_for_token("inventat", SessionRepository(build_seed()))
    assert error.value.code == UNAUTHENTICATED
