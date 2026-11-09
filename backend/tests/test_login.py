"""Tests de T03.1: POST /api/auth/login i /api/auth/logout (docs/api.md §8.8 i §8.9).

Proves S-01 a S-11 de docs/proves-acces.md. El bloqueig (S-12 a S-17) i la
inactivitat (S-18 a S-22) són a test_lockout_inactivity.py (T03.2).

Executar des de backend/:  python -m pytest tests/test_login.py
"""

import pytest
from fastapi.testclient import TestClient

from app.data.seed import DEMO_IDENTIFIER, DEMO_USER_ID, EMPTY_IDENTIFIER, EMPTY_USER_ID, SEED_PASSWORD

INVALID_CREDENTIALS = {
    "code": "INVALID_CREDENTIALS",
    "message": "L'email, el telèfon o la contrasenya no són correctes.",
}


def _login(client: TestClient, identifier: str = DEMO_IDENTIFIER, password: str = SEED_PASSWORD):
    return client.post("/api/auth/login", json={"identifier": identifier, "password": password})


def _token(client: TestClient, identifier: str = DEMO_IDENTIFIER) -> str:
    return _login(client, identifier).json()["token"]


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


# --- Login correcte -----------------------------------------------------------------


def test_login_returns_a_token(client: TestClient) -> None:
    # S-01
    response = _login(client)

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"token"}
    assert isinstance(body["token"], str)
    assert len(body["token"]) >= 32


def test_token_opens_the_home_of_the_user(client: TestClient) -> None:
    # S-02: el token dona les dades de l'usuari 1, sense X-User-Id.
    token = _token(client)
    expected = client.get("/api/home", headers={"X-User-Id": str(DEMO_USER_ID)}).json()

    response = client.get("/api/home", headers=_auth(token))

    assert response.status_code == 200
    assert response.json() == expected


def test_each_user_gets_their_own_data(client: TestClient) -> None:
    token = _token(client, EMPTY_IDENTIFIER)
    expected = client.get("/api/home", headers={"X-User-Id": str(EMPTY_USER_ID)}).json()

    assert client.get("/api/home", headers=_auth(token)).json() == expected


def test_identifier_is_normalized(client: TestClient) -> None:
    # S-03
    assert _login(client, "  DEMO@evolt.test ").status_code == 200


def test_each_login_opens_a_new_session(client: TestClient) -> None:
    assert _token(client) != _token(client)


@pytest.mark.memory_only
def test_registered_phone_account_can_log_in_once_active(client: TestClient) -> None:
    # Login amb telèfon. El compte s'activa a mà: verificar el codi és de la T02.1.
    client.post(
        "/api/auth/register",
        json={"identifier": "612 34 56 78", "password": "Platja2026", "acceptedTerms": True},
    )
    user = next(u for u in client.app.state.seed.users.values() if u.identifier == "+34612345678")
    user.status = "active"

    assert _login(client, "+34 612 345 678", "Platja2026").status_code == 200


# --- Credencials incorrectes: sempre el mateix error --------------------------------


@pytest.mark.memory_only
@pytest.mark.parametrize(
    "identifier, password",
    [
        (DEMO_IDENTIFIER, "Dolent2026"),  # S-04: contrasenya errònia
        ("ningu@x.com", SEED_PASSWORD),  # S-05: compte inexistent
        ("12ab", SEED_PASSWORD),  # S-06: identificador no vàlid
        (DEMO_IDENTIFIER, ""),
        (DEMO_IDENTIFIER, "Evolt2026" + "a" * 70),  # més de 72 bytes
    ],
)
def test_wrong_credentials_give_the_same_generic_error(client: TestClient, identifier, password) -> None:
    sessions_before = dict(client.app.state.seed.sessions)

    response = _login(client, identifier, password)

    assert response.status_code == 401
    assert response.json() == INVALID_CREDENTIALS
    assert client.app.state.seed.sessions == sessions_before


def test_password_policy_is_not_checked_on_login(client: TestClient) -> None:
    # Una contrasenya «feble» no és WEAK_PASSWORD al login: només és incorrecta.
    assert _login(client, password="curta").json() == INVALID_CREDENTIALS


# --- Compte pendent (P8) ------------------------------------------------------------


def _register_pending(client: TestClient) -> None:
    client.post(
        "/api/auth/register",
        json={"identifier": "ana@x.com", "password": "Platja2026", "acceptedTerms": True},
    )


@pytest.mark.memory_only
def test_pending_account_with_the_right_password_is_not_verified(client: TestClient) -> None:
    # S-07
    _register_pending(client)

    response = _login(client, "ana@x.com", "Platja2026")

    assert response.status_code == 403
    assert response.json() == {
        "code": "ACCOUNT_NOT_VERIFIED",
        "message": "Has de verificar el compte abans d'iniciar sessió.",
    }
    assert client.app.state.seed.sessions == {}


def test_pending_account_with_a_wrong_password_gets_the_generic_error(client: TestClient) -> None:
    # S-08: sense la contrasenya bona no es revela que el compte existeix.
    _register_pending(client)

    assert _login(client, "ana@x.com", "Dolent2026").json() == INVALID_CREDENTIALS


# --- Format del cos -----------------------------------------------------------------


@pytest.mark.parametrize(
    "body",
    [
        {"identifier": DEMO_IDENTIFIER},
        {"password": SEED_PASSWORD},
        {"identifier": 612345678, "password": SEED_PASSWORD},
        {"identifier": DEMO_IDENTIFIER, "password": 20262026},
        [DEMO_IDENTIFIER, SEED_PASSWORD],
    ],
)
def test_malformed_body_is_a_validation_error(client: TestClient, body) -> None:
    response = client.post("/api/auth/login", json=body)

    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"


# --- Logout -------------------------------------------------------------------------


def test_logout_closes_the_session(client: TestClient) -> None:
    # S-09
    token = _token(client)

    response = client.post("/api/auth/logout", headers=_auth(token))

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    after = client.get("/api/home", headers=_auth(token))
    assert after.status_code == 401
    assert after.json()["code"] == "UNAUTHENTICATED"


@pytest.mark.parametrize(
    "headers",
    [
        {},  # sense capçalera
        {"Authorization": "Bearer inventat"},
        {"Authorization": "Basic abc"},
    ],
)
def test_logout_always_answers_ok(client: TestClient, headers) -> None:
    # S-10 (P14)
    response = client.post("/api/auth/logout", headers=headers)

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_logout_twice_is_fine(client: TestClient) -> None:
    token = _token(client)
    client.post("/api/auth/logout", headers=_auth(token))

    assert client.post("/api/auth/logout", headers=_auth(token)).status_code == 200


def test_logout_closes_only_its_own_session(client: TestClient) -> None:
    # S-11: dues sessions de l'usuari 1 (dos dispositius).
    first, second = _token(client), _token(client)

    client.post("/api/auth/logout", headers=_auth(first))

    assert client.get("/api/home", headers=_auth(first)).status_code == 401
    assert client.get("/api/home", headers=_auth(second)).status_code == 200
