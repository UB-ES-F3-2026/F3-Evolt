"""Tests de T04.1: POST /api/auth/forgot-password i /api/auth/reset-password (docs/api.md §8.10 i §8.11).

Proves C-01 a C-13 de docs/proves-acces.md. El rellotge dels serveis es fixa
amb `clock`: T0 = 2026-11-03 10:00 (Madrid).

Executar des de backend/:  python -m pytest tests/test_password_reset.py
"""

import logging
import threading
from datetime import datetime, timedelta
from urllib.parse import parse_qs, urlsplit

import pytest
from fastapi.testclient import TestClient

from app.data.seed import DEMO_IDENTIFIER, DEMO_USER_ID, MADRID_TZ, SEED_PASSWORD, build_seed
from app.main import create_app
from app.repositories import (
    OutboxRepository,
    PasswordResetTokenRepository,
    SessionRepository,
    UserRepository,
)
from app.services import password_reset_service, session_service
from app.services.errors import RESET_LINK_EXPIRED, ApiError
from app.services.password_hashing import verify_password
from app.services.password_reset_service import forgot_password, reset_password

T0 = datetime(2026, 11, 3, 10, 0, 0, tzinfo=MADRID_TZ)
NEW_PASSWORD = "NovaClau2026"
LOCAL_LINK = "http://localhost:5173/nova-contrasenya?token="
EXPIRED_BODY = {"code": "RESET_LINK_EXPIRED", "message": "Aquest enllaç ha caducat."}


class Clock:
    """Hora que veuen els serveis d'accés; els tests la mouen."""

    def __init__(self) -> None:
        self.now = T0

    def set(self, minutes: int = 0, seconds: int = 0) -> None:
        self.now = T0 + timedelta(minutes=minutes, seconds=seconds)


@pytest.fixture
def clock(monkeypatch) -> Clock:
    clock = Clock()
    monkeypatch.setattr(password_reset_service, "now_madrid", lambda: clock.now)
    monkeypatch.setattr(session_service, "now_madrid", lambda: clock.now)
    return clock


def _forgot(client: TestClient, identifier: str = DEMO_IDENTIFIER):
    return client.post("/api/auth/forgot-password", json={"identifier": identifier})


def _reset(client: TestClient, token: str, password: str = NEW_PASSWORD):
    return client.post("/api/auth/reset-password", json={"token": token, "password": password})


def _login(client: TestClient, password: str, identifier: str = DEMO_IDENTIFIER):
    return client.post("/api/auth/login", json={"identifier": identifier, "password": password})


def _resets(client: TestClient, to: str = DEMO_IDENTIFIER) -> list[dict]:
    messages = client.get("/api/dev/outbox", params={"to": to}).json()["messages"]
    return [m for m in messages if m["type"] == "password_reset"]


def _token_from(link: str) -> str:
    return parse_qs(urlsplit(link).query)["token"][0]


def _new_link_token(client: TestClient, identifier: str = DEMO_IDENTIFIER) -> str:
    _forgot(client, identifier)
    return _token_from(_resets(client, identifier)[0]["link"])


# --- forgot-password ----------------------------------------------------------------


def test_forgot_password_sends_a_link(client: TestClient, clock: Clock) -> None:
    # C-01
    response = _forgot(client)

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    [message] = _resets(client)
    assert message["channel"] == "email"
    assert message["link"].startswith(LOCAL_LINK)
    assert message["link"] in message["text"]
    assert "30 minuts" in message["text"]
    assert "code" not in message


def test_unknown_account_gets_the_same_answer_and_no_message(client: TestClient, clock: Clock) -> None:
    # C-02
    known = _forgot(client)
    client.post("/api/dev/reset")

    unknown = _forgot(client, "ningu@x.com")

    assert (unknown.status_code, unknown.json()) == (known.status_code, known.json())
    assert client.get("/api/dev/outbox").json() == {"messages": []}


@pytest.mark.parametrize("body", [{"identifier": "ana@"}, {"identifier": 612345678}, {}])
def test_forgot_password_with_a_malformed_identifier(client: TestClient, body) -> None:
    response = client.post("/api/auth/forgot-password", json=body)

    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"
    assert client.get("/api/dev/outbox").json() == {"messages": []}


def test_phone_account_gets_the_link_by_sms(client: TestClient, clock: Clock) -> None:
    # C-12
    client.post(
        "/api/auth/register",
        json={"identifier": "612 34 56 78", "password": "Platja2026", "acceptedTerms": True},
    )

    assert _forgot(client, "612 34 56 78").status_code == 200

    [message] = _resets(client, "+34612345678")
    assert message["channel"] == "sms"


def test_link_uses_frontend_url(monkeypatch) -> None:
    # C-13
    monkeypatch.setenv("FRONTEND_URL", "https://f3-evolt.onrender.com/")
    with TestClient(create_app()) as client:
        _forgot(client)
        [message] = _resets(client)

    assert message["link"].startswith("https://f3-evolt.onrender.com/nova-contrasenya?token=")


def test_pending_account_also_gets_a_link(client: TestClient, clock: Clock) -> None:
    client.post(
        "/api/auth/register",
        json={"identifier": "ana@x.com", "password": "Platja2026", "acceptedTerms": True},
    )

    _forgot(client, "ana@x.com")

    assert len(_resets(client, "ana@x.com")) == 1


# --- reset-password -----------------------------------------------------------------


def test_reset_changes_the_password(client: TestClient, clock: Clock) -> None:
    # C-03
    token = _new_link_token(client)

    response = _reset(client, token)

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert _login(client, NEW_PASSWORD).status_code == 200
    assert _login(client, SEED_PASSWORD).json()["code"] == "INVALID_CREDENTIALS"


def test_link_works_only_once(client: TestClient, clock: Clock) -> None:
    # C-04
    token = _new_link_token(client)
    _reset(client, token)

    response = _reset(client, token, "AltraClau2026")

    assert response.status_code == 422
    assert response.json() == EXPIRED_BODY
    assert _login(client, NEW_PASSWORD).status_code == 200


def test_link_lasts_30_minutes(client: TestClient, clock: Clock) -> None:
    # C-05 i C-06
    token = _new_link_token(client)

    clock.set(30)
    assert _reset(client, token).json() == EXPIRED_BODY
    clock.set(29, 59)
    assert _reset(client, token).status_code == 200


def test_weak_password_keeps_the_link(client: TestClient, clock: Clock) -> None:
    # C-07
    token = _new_link_token(client)

    weak = _reset(client, token, "novaclau")

    assert weak.status_code == 422
    assert weak.json()["code"] == "WEAK_PASSWORD"
    assert _reset(client, token).status_code == 200


def test_reset_closes_every_session(client: TestClient, clock: Clock) -> None:
    # C-08
    phone = _login(client, SEED_PASSWORD).json()["token"]
    laptop = _login(client, SEED_PASSWORD).json()["token"]
    token = _new_link_token(client)

    assert _reset(client, token).status_code == 200

    for session in (phone, laptop):
        response = client.get("/api/home", headers={"Authorization": f"Bearer {session}"})
        assert response.status_code == 401
        assert response.json()["code"] == "UNAUTHENTICATED"


def test_reset_does_not_close_other_users_sessions(client: TestClient, clock: Clock) -> None:
    other = _login(client, SEED_PASSWORD, "buit@evolt.test").json()["token"]

    _reset(client, _new_link_token(client))

    assert client.get("/api/home", headers={"Authorization": f"Bearer {other}"}).status_code == 200


def test_a_new_link_replaces_the_old_one(client: TestClient, clock: Clock) -> None:
    # C-09
    old = _new_link_token(client)
    clock.set(1)
    new = _new_link_token(client)

    assert _reset(client, old).json() == EXPIRED_BODY
    assert _reset(client, new).status_code == 200


@pytest.mark.parametrize("token", ["inventat", "", "a" * 43])
def test_unknown_token_is_expired(client: TestClient, token: str) -> None:
    # C-10
    response = _reset(client, token)

    assert response.status_code == 422
    assert response.json() == EXPIRED_BODY


def test_reset_unlocks_the_account(client: TestClient, clock: Clock) -> None:
    # C-11 (P15)
    for _ in range(5):
        _login(client, "Equivocada1")
    assert _login(client, SEED_PASSWORD).status_code == 423

    _reset(client, _new_link_token(client))

    assert _login(client, NEW_PASSWORD).status_code == 200


def test_reset_puts_the_failed_logins_to_zero(client: TestClient, clock: Clock) -> None:
    for _ in range(4):
        _login(client, "Equivocada1")

    _reset(client, _new_link_token(client))

    # Si el comptador no s'hagués posat a zero, aquest primer error bloquejaria el compte.
    assert _login(client, "Equivocada1").status_code == 401


def test_reset_does_not_activate_a_pending_account(client: TestClient, clock: Clock) -> None:
    client.post(
        "/api/auth/register",
        json={"identifier": "ana@x.com", "password": "Platja2026", "acceptedTerms": True},
    )

    _reset(client, _new_link_token(client, "ana@x.com"))

    assert _login(client, NEW_PASSWORD, "ana@x.com").json()["code"] == "ACCOUNT_NOT_VERIFIED"


@pytest.mark.parametrize(
    "body",
    [
        {"token": "x", "password": 20262026},
        {"token": 1, "password": NEW_PASSWORD},
        {"password": NEW_PASSWORD},
        {"token": "x"},
        {"token": "x", "password": NEW_PASSWORD + "a" * 61},  # 73 bytes
    ],
)
def test_malformed_body_is_a_validation_error(client: TestClient, body) -> None:
    response = client.post("/api/auth/reset-password", json=body)

    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"


def test_expired_link_is_checked_before_the_password_policy(client: TestClient, clock: Clock) -> None:
    # §8.11: l'ordre és format → enllaç → política.
    assert _reset(client, "inventat", "feble").json()["code"] == "RESET_LINK_EXPIRED"


def test_password_and_token_are_not_logged(client: TestClient, clock: Clock, caplog) -> None:
    with caplog.at_level(logging.DEBUG):
        token = _new_link_token(client)
        _reset(client, token)

    assert NEW_PASSWORD not in caplog.text
    assert token not in caplog.text


def test_dev_reset_removes_the_links(client: TestClient, clock: Clock) -> None:
    token = _new_link_token(client)

    client.post("/api/dev/reset")

    assert _reset(client, token).json() == EXPIRED_BODY


# --- Servei -------------------------------------------------------------------------


@pytest.fixture
def repos():
    seed = build_seed(now=T0)
    return (
        seed,
        UserRepository(seed),
        PasswordResetTokenRepository(seed),
        SessionRepository(seed),
        OutboxRepository(seed),
    )


def test_service_stores_the_new_hash_and_spends_the_token(repos) -> None:
    seed, users, tokens, sessions, outbox = repos
    forgot_password(DEMO_IDENTIFIER, users, tokens, outbox, "http://localhost:5173", now=T0)
    [token] = seed.password_reset_tokens

    reset_password(token, NEW_PASSWORD, users, tokens, sessions, now=T0)

    assert verify_password(NEW_PASSWORD, seed.users[DEMO_USER_ID].password_hash)
    assert seed.password_reset_tokens[token].used


def test_simultaneous_resets_with_the_same_link_change_the_password_once(repos) -> None:
    seed, users, tokens, sessions, outbox = repos
    forgot_password(DEMO_IDENTIFIER, users, tokens, outbox, "http://localhost:5173", now=T0)
    [token] = seed.password_reset_tokens
    threads_count = 6
    barrier = threading.Barrier(threads_count)
    results: list[str] = []

    def attempt(index: int) -> None:
        barrier.wait()
        try:
            reset_password(token, f"NovaClau{index}A", users, tokens, sessions, now=T0)
            results.append("ok")
        except ApiError as error:
            results.append(error.code)

    threads = [threading.Thread(target=attempt, args=(i,)) for i in range(threads_count)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert results.count("ok") == 1
    assert results.count(RESET_LINK_EXPIRED) == threads_count - 1
