"""Tests de T03.2: bloqueig als 5 errors i sessió tancada per inactivitat (docs/api.md §8.1).

Proves S-12 a S-22 de docs/proves-acces.md. El rellotge del servei de sessió es
fixa amb `clock`: T0 = 2026-11-03 10:00 (Madrid).

Executar des de backend/:  python -m pytest tests/test_lockout_inactivity.py
"""

import threading
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from app.data.seed import DEMO_IDENTIFIER, DEMO_USER_ID, MADRID_TZ, SEED_PASSWORD, build_seed
from app.repositories import OutboxRepository, SessionRepository, UserRepository
from app.services import session_service
from app.services.errors import (
    ACCOUNT_LOCKED,
    INVALID_CREDENTIALS,
    SESSION_EXPIRED,
    UNAUTHENTICATED,
    ApiError,
)
from app.services.session_service import login, user_id_for_token

T0 = datetime(2026, 11, 3, 10, 0, 0, tzinfo=MADRID_TZ)
WRONG = "Equivocada1"
LOCKED_BODY = {
    "code": "ACCOUNT_LOCKED",
    "message": "Compte bloquejat durant 15 minuts.",
    "details": {"lockedUntil": "2026-11-03T10:15:00+01:00"},
}
EXPIRED_BODY = {"code": "SESSION_EXPIRED", "message": "La sessió s'ha tancat per inactivitat."}


def _at(minutes: int = 0, seconds: int = 0) -> datetime:
    return T0 + timedelta(minutes=minutes, seconds=seconds)


class Clock:
    """Hora que veu el servei de sessió; els tests la mouen."""

    def __init__(self) -> None:
        self.now = T0

    def set(self, minutes: int = 0, seconds: int = 0) -> None:
        self.now = _at(minutes, seconds)


@pytest.fixture
def clock(monkeypatch) -> Clock:
    clock = Clock()
    monkeypatch.setattr(session_service, "now_madrid", lambda: clock.now)
    return clock


def _login(client: TestClient, password: str = SEED_PASSWORD, identifier: str = DEMO_IDENTIFIER):
    return client.post("/api/auth/login", json={"identifier": identifier, "password": password})


def _fail(client: TestClient, times: int, identifier: str = DEMO_IDENTIFIER) -> list[int]:
    return [_login(client, WRONG, identifier).status_code for _ in range(times)]


def _home(client: TestClient, token: str):
    return client.get("/api/home", headers={"Authorization": f"Bearer {token}"})


def _outbox(client: TestClient, to: str = DEMO_IDENTIFIER) -> list[dict]:
    return client.get("/api/dev/outbox", params={"to": to}).json()["messages"]


# --- Bloqueig (API) -----------------------------------------------------------------


def test_fifth_wrong_password_locks_the_account(client: TestClient, clock: Clock) -> None:
    # S-12
    assert _fail(client, 4) == [401] * 4

    response = _login(client, WRONG)

    assert response.status_code == 423
    assert response.json() == LOCKED_BODY


def test_right_password_is_locked_too(client: TestClient, clock: Clock) -> None:
    # S-13
    _fail(client, 5)
    clock.set(1)

    response = _login(client)

    assert response.status_code == 423
    assert response.json() == LOCKED_BODY
    assert client.app.state.seed.sessions == {}


def test_lock_sends_a_notice(client: TestClient, clock: Clock) -> None:
    # S-14
    _fail(client, 5)

    [message] = _outbox(client)
    assert message["channel"] == "email"
    assert message["type"] == "account_locked"
    assert "15 minuts" in message["text"]


def test_lock_lasts_15_minutes(client: TestClient, clock: Clock) -> None:
    # S-15
    _fail(client, 5)

    clock.set(14, 59)
    assert _login(client).status_code == 423
    clock.set(15)
    assert _login(client).status_code == 200


def test_a_right_login_resets_the_counter(client: TestClient, clock: Clock) -> None:
    # S-16
    assert _fail(client, 4) == [401] * 4
    assert _login(client).status_code == 200

    assert _fail(client, 4) == [401] * 4
    assert _login(client).status_code == 200


def test_unknown_identifier_never_locks(client: TestClient, clock: Clock) -> None:
    # S-17
    assert _fail(client, 6, "ningu@x.com") == [401] * 6
    assert client.get("/api/dev/outbox").json() == {"messages": []}


def test_attempts_while_locked_do_not_count(client: TestClient, clock: Clock) -> None:
    # §8.1: durant el bloqueig cap intent compta; en acabar, es torna a començar de zero.
    _fail(client, 5)
    clock.set(5)
    assert _fail(client, 3) == [423] * 3

    clock.set(15)
    assert _fail(client, 4) == [401] * 4
    assert _login(client).status_code == 200
    assert len(_outbox(client)) == 1


def test_lock_after_it_expires_starts_a_new_15_minutes(client: TestClient, clock: Clock) -> None:
    _fail(client, 5)
    clock.set(20)

    assert _fail(client, 4) == [401] * 4
    response = _login(client, WRONG)

    assert response.status_code == 423
    assert response.json()["details"] == {"lockedUntil": "2026-11-03T10:35:00+01:00"}
    assert len(_outbox(client)) == 2


def test_lock_of_a_phone_account_sends_an_sms(client: TestClient, clock: Clock) -> None:
    client.post(
        "/api/auth/register",
        json={"identifier": "612 34 56 78", "password": "Platja2026", "acceptedTerms": True},
    )

    _fail(client, 5, "612345678")

    # La bústia va de més nou a més antic: l'avís de bloqueig i el codi del registre.
    messages = _outbox(client, "+34612345678")
    assert [(m["type"], m["channel"]) for m in messages] == [("account_locked", "sms"), ("verification_code", "sms")]


def test_password_over_72_bytes_counts_as_an_error(client: TestClient, clock: Clock) -> None:
    for _ in range(4):
        _login(client, "Platja2026" + "a" * 63)

    assert _login(client, WRONG).status_code == 423


# --- Bloqueig (servei) --------------------------------------------------------------


@pytest.fixture
def repos():
    seed = build_seed(now=T0)
    return seed, UserRepository(seed), SessionRepository(seed), OutboxRepository(seed)


def test_counter_and_lock_are_stored_on_the_user(repos) -> None:
    seed, users, sessions, outbox = repos
    for expected in range(1, 5):
        with pytest.raises(ApiError):
            login(DEMO_IDENTIFIER, WRONG, users, sessions, outbox, now=T0)
        assert seed.users[DEMO_USER_ID].failed_logins == expected

    with pytest.raises(ApiError) as error:
        login(DEMO_IDENTIFIER, WRONG, users, sessions, outbox, now=T0)

    assert error.value.code == ACCOUNT_LOCKED
    user = seed.users[DEMO_USER_ID]
    assert (user.failed_logins, user.locked_until) == (0, _at(15))


def test_simultaneous_wrong_passwords_are_all_counted(repos) -> None:
    # Sense el pany, dos errors alhora podrien comptar com un de sol.
    seed, users, sessions, outbox = repos
    threads_count = 5
    barrier = threading.Barrier(threads_count)
    codes: list[str] = []

    def attempt():
        barrier.wait()
        try:
            login(DEMO_IDENTIFIER, WRONG, users, sessions, outbox, now=T0)
        except ApiError as error:
            codes.append(error.code)

    threads = [threading.Thread(target=attempt) for _ in range(threads_count)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert sorted(codes) == sorted([INVALID_CREDENTIALS] * 4 + [ACCOUNT_LOCKED])
    assert seed.users[DEMO_USER_ID].locked_until == _at(15)
    assert len(seed.outbox) == 1


# --- Inactivitat (API) --------------------------------------------------------------


def test_activity_before_5_minutes_keeps_the_session(client: TestClient, clock: Clock) -> None:
    # S-18 i S-19
    token = _login(client).json()["token"]

    clock.set(4, 59)
    assert _home(client, token).status_code == 200
    clock.set(9, 58)
    assert _home(client, token).status_code == 200


def test_5_minutes_without_activity_closes_the_session(client: TestClient, clock: Clock) -> None:
    # S-20 i S-21
    token = _login(client).json()["token"]

    clock.set(5, 1)
    response = _home(client, token)
    assert response.status_code == 401
    assert response.json() == EXPIRED_BODY

    again = _home(client, token)
    assert again.status_code == 401
    assert again.json()["code"] == "UNAUTHENTICATED"


def test_a_business_error_counts_as_activity(client: TestClient, clock: Clock) -> None:
    # S-22
    token = _login(client).json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    clock.set(4)
    topup = client.post("/api/topups", json={"amount": 60000}, headers=headers)
    assert topup.status_code == 422
    assert topup.json()["code"] == "AMOUNT_OVER_LIMIT"

    clock.set(8, 30)
    assert _home(client, token).status_code == 200


def test_expiry_only_closes_that_session(client: TestClient, clock: Clock) -> None:
    old = _login(client).json()["token"]
    clock.set(4)
    recent = _login(client).json()["token"]

    clock.set(6)
    assert _home(client, old).status_code == 401
    assert _home(client, recent).status_code == 200


# --- Inactivitat (servei) -----------------------------------------------------------


@pytest.mark.parametrize(
    "elapsed, expected",
    [
        (timedelta(minutes=4, seconds=59), None),
        (timedelta(minutes=5), SESSION_EXPIRED),
        (timedelta(minutes=5, seconds=1), SESSION_EXPIRED),
    ],
)
def test_inactivity_limit_is_5_minutes(elapsed, expected) -> None:
    sessions = SessionRepository(build_seed(now=T0))
    token = sessions.create(DEMO_USER_ID, T0).token

    if expected is None:
        assert user_id_for_token(token, sessions, now=T0 + elapsed) == DEMO_USER_ID
        return
    with pytest.raises(ApiError) as error:
        user_id_for_token(token, sessions, now=T0 + elapsed)
    assert error.value.code == expected
    assert sessions.get(token) is None


def test_expired_check_does_not_renew_the_session() -> None:
    sessions = SessionRepository(build_seed(now=T0))
    token = sessions.create(DEMO_USER_ID, T0).token
    with pytest.raises(ApiError):
        user_id_for_token(token, sessions, now=_at(6))

    with pytest.raises(ApiError) as error:
        user_id_for_token(token, sessions, now=_at(6, 1))

    assert error.value.code == UNAUTHENTICATED
