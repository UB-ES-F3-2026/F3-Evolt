"""Tests de T01.2: POST /api/auth/register (docs/api.md §8.5).

Proves R-01 a R-17 de docs/proves-acces.md. R-03 (el codi a la bústia) i el
canal `sms` de R-12 són de la T02.1.

Executar des de backend/:  python -m pytest tests/test_register.py
"""

import logging

import pytest
from fastapi.testclient import TestClient

from app.data.seed import DEMO_IDENTIFIER, SeedData
from app.services.password_hashing import verify_password

PASSWORD = "Platja2026"


def _seed(client: TestClient) -> SeedData:
    return client.app.state.seed


def _register(client: TestClient, identifier: str, password: str = PASSWORD, **extra):
    body = {"identifier": identifier, "password": password, "acceptedTerms": True}
    body.update(extra)
    return client.post("/api/auth/register", json=body)


def _state(client: TestClient):
    """Estat que un registre fallit no pot canviar."""
    seed = _seed(client)
    return (sorted(seed.users), sorted(seed.accounts), seed.next_user_id)


def _user_by_identifier(client: TestClient, identifier: str):
    return next(u for u in _seed(client).users.values() if u.identifier == identifier)


# --- Registre correcte --------------------------------------------------------------


def test_register_creates_a_pending_user(client: TestClient) -> None:
    # R-01
    response = _register(client, "ana@x.com")

    assert response.status_code == 201
    assert response.json() == {"identifier": "ana@x.com", "status": "pending"}
    user = _user_by_identifier(client, "ana@x.com")
    assert user.status == "pending"
    assert user.identifier_type == "email"


def test_register_creates_the_main_account_with_zero_balance(client: TestClient) -> None:
    # R-01 i P19: compte principal a 0, sense moviments ni guardioles.
    _register(client, "ana@x.com")

    seed = _seed(client)
    user = _user_by_identifier(client, "ana@x.com")
    account = seed.accounts[user.id]
    assert account.balance == 0
    assert [m for m in seed.movements if m.account_id == account.id] == []
    assert [p for p in seed.pots if p.user_id == user.id] == []
    assert user.xp == 0


def test_register_does_not_open_a_session(client: TestClient) -> None:
    # R-02: no hi ha token ni cap altra clau.
    assert set(_register(client, "ana@x.com").json()) == {"identifier", "status"}


def test_each_new_user_gets_a_new_id(client: TestClient) -> None:
    _register(client, "ana@x.com")
    _register(client, "pau@x.com")

    ana = _user_by_identifier(client, "ana@x.com")
    pau = _user_by_identifier(client, "pau@x.com")
    assert {ana.id, pau.id}.isdisjoint({1, 2})
    assert ana.id != pau.id


def test_response_returns_the_normalized_identifier(client: TestClient) -> None:
    # Exemple del contracte (§8.5): "Ana@X.com" → "ana@x.com".
    assert _register(client, " Ana@X.com ").json()["identifier"] == "ana@x.com"


def test_register_with_a_phone(client: TestClient) -> None:
    # R-12
    response = _register(client, "612 34 56 78")

    assert response.status_code == 201
    assert response.json()["identifier"] == "+34612345678"
    assert _user_by_identifier(client, "+34612345678").identifier_type == "phone"


def test_accented_uppercase_counts(client: TestClient) -> None:
    # R-09
    assert _register(client, "ana@x.com", password="Àlgebra26").status_code == 201


def test_password_is_stored_only_as_a_hash(client: TestClient, caplog) -> None:
    # R-17
    with caplog.at_level(logging.DEBUG):
        _register(client, "ana@x.com")

    user = _user_by_identifier(client, "ana@x.com")
    assert PASSWORD not in user.password_hash
    assert verify_password(PASSWORD, user.password_hash)
    assert PASSWORD not in caplog.text


def test_password_is_not_logged_when_the_body_is_invalid(client: TestClient, caplog) -> None:
    # R-17: el handler de VALIDATION_ERROR registra quin camp falla, però no el valor.
    with caplog.at_level(logging.DEBUG):
        response = client.post(
            "/api/auth/register",
            json={"identifier": "ana@x.com", "password": [PASSWORD], "acceptedTerms": True},
        )

    assert response.status_code == 422
    assert PASSWORD not in caplog.text


# --- Duplicats ----------------------------------------------------------------------


@pytest.mark.parametrize("duplicate", ["ana@x.com", "ANA@x.com", "  ana@X.COM "])
def test_same_email_is_already_registered(client: TestClient, duplicate: str) -> None:
    # R-04 i R-05: també amb el compte encara pendent i una altra contrasenya.
    _register(client, "ana@x.com")
    before = _state(client)

    response = _register(client, duplicate, password="Altra2026")

    assert response.status_code == 409
    assert response.json() == {
        "code": "ALREADY_REGISTERED",
        "message": "Aquest email o telèfon ja té un compte.",
    }
    assert _state(client) == before


def test_same_phone_in_another_format_is_already_registered(client: TestClient) -> None:
    # R-13
    _register(client, "612 34 56 78")

    response = _register(client, "0034612345678")

    assert response.status_code == 409
    assert response.json()["code"] == "ALREADY_REGISTERED"


def test_seed_user_is_already_registered(client: TestClient) -> None:
    # R-14
    assert _register(client, DEMO_IDENTIFIER).json()["code"] == "ALREADY_REGISTERED"


# --- Contrasenya feble --------------------------------------------------------------


@pytest.mark.parametrize("password", ["curta1A", "platja2026", "PlatjaNova"])
def test_weak_password_is_rejected(client: TestClient, password: str) -> None:
    # R-06, R-07 i R-08
    before = _state(client)

    response = _register(client, "ana@x.com", password=password)

    assert response.status_code == 422
    assert response.json() == {
        "code": "WEAK_PASSWORD",
        "message": "La contrasenya ha de tenir 8 caràcters, una majúscula i un número.",
    }
    assert _state(client) == before


# --- Format del cos -----------------------------------------------------------------


@pytest.mark.parametrize(
    "body",
    [
        {"identifier": "ana@x.com", "password": PASSWORD, "acceptedTerms": False},  # R-10
        {"identifier": "ana@x.com", "password": PASSWORD},  # R-10: sense el camp
        {"identifier": "ana@x.com", "password": PASSWORD, "acceptedTerms": "true"},
        {"identifier": "ana@x.com", "password": PASSWORD, "acceptedTerms": 1},
        {"identifier": "ana@", "password": PASSWORD, "acceptedTerms": True},  # R-11
        {"identifier": "12ab", "password": PASSWORD, "acceptedTerms": True},  # R-11
        {"identifier": 612345678, "password": PASSWORD, "acceptedTerms": True},
        {"password": PASSWORD, "acceptedTerms": True},
        {"identifier": "ana@x.com", "acceptedTerms": True},
        {"identifier": "ana@x.com", "password": 20262026, "acceptedTerms": True},
        [PASSWORD],
    ],
)
def test_malformed_body_is_a_validation_error(client: TestClient, body) -> None:
    before = _state(client)

    response = client.post("/api/auth/register", json=body)

    assert response.status_code == 422
    assert response.json() == {
        "code": "VALIDATION_ERROR",
        "message": "Les dades de la petició no són vàlides.",
    }
    assert _state(client) == before


def test_password_longer_than_72_bytes_is_a_validation_error(client: TestClient) -> None:
    # P16: bcrypt no faria servir la resta.
    response = _register(client, "ana@x.com", password="Platja2026" + "a" * 63)

    assert response.json()["code"] == "VALIDATION_ERROR"


# --- Ordre de les validacions -------------------------------------------------------


def test_format_is_checked_before_the_password_policy(client: TestClient) -> None:
    # R-15
    response = _register(client, "ana@x.com", password="WEAK", acceptedTerms=False)
    assert response.json()["code"] == "VALIDATION_ERROR"


def test_password_policy_is_checked_before_duplicates(client: TestClient) -> None:
    # R-16
    response = _register(client, DEMO_IDENTIFIER, password="curta")
    assert response.json()["code"] == "WEAK_PASSWORD"


# --- Reinici ------------------------------------------------------------------------


def test_dev_reset_removes_registered_users(client: TestClient) -> None:
    _register(client, "ana@x.com")

    client.post("/api/dev/reset")

    assert _register(client, "ana@x.com").status_code == 201


# --- Codi de verificació (T02.1) ----------------------------------------------------


def test_register_leaves_a_6_digit_code_in_the_outbox(client: TestClient) -> None:
    # R-03
    _register(client, "ana@x.com")

    messages = client.get("/api/dev/outbox", params={"to": "ana@x.com"}).json()["messages"]

    assert len(messages) == 1
    assert messages[0]["channel"] == "email"
    assert messages[0]["type"] == "verification_code"
    assert len(messages[0]["code"]) == 6
    assert messages[0]["code"].isdigit()
    assert messages[0]["code"] in messages[0]["text"]


def test_register_with_a_phone_sends_an_sms(client: TestClient) -> None:
    # R-12
    _register(client, "612 34 56 78")

    messages = client.get("/api/dev/outbox", params={"to": "+34612345678"}).json()["messages"]

    assert [m["channel"] for m in messages] == ["sms"]


def test_failed_register_sends_nothing(client: TestClient) -> None:
    _register(client, "ana@x.com", password="feble")

    assert client.get("/api/dev/outbox").json() == {"messages": []}
