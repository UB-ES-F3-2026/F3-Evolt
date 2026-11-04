"""Tests de T02.1: verificació i reenviament del codi (docs/api.md §8.6 i §8.7).

Proves V-01 a V-17 de docs/proves-acces.md. Les que depenen del temps fixen el
rellotge al servei (T0 = 2026-11-03 10:00 a Madrid); la resta van per l'API.

Executar des de backend/:  python -m pytest tests/test_verification.py
"""

from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from app.data.seed import DEMO_IDENTIFIER, MADRID_TZ, build_seed
from app.repositories import (
    AccountRepository,
    OutboxRepository,
    SessionRepository,
    UserRepository,
    VerificationCodeRepository,
)
from app.services.errors import CODE_EXPIRED, INVALID_CODE, ApiError
from app.services.registration_service import register
from app.services.verification_service import resend, verify

T0 = datetime(2026, 11, 3, 10, 0, 0, tzinfo=MADRID_TZ)
IDENTIFIER = "ana@x.com"


def _at(minutes: int, seconds: int = 0) -> datetime:
    return T0 + timedelta(minutes=minutes, seconds=seconds)


def _wrong(code: str) -> str:
    """Un codi de 6 xifres diferent del correcte."""
    return f"{(int(code) + 1) % 1_000_000:06d}"


# --- Servei, amb el rellotge fixat --------------------------------------------------


@pytest.fixture
def seed():
    seed = build_seed(now=T0)
    register(
        IDENTIFIER,
        "Platja2026",
        True,
        UserRepository(seed),
        AccountRepository(seed),
        VerificationCodeRepository(seed),
        OutboxRepository(seed),
        now=T0,
    )
    return seed


def _code(seed) -> str:
    return seed.outbox[-1].code


def _verify(seed, code: str, now: datetime) -> str:
    return verify(
        IDENTIFIER, code, UserRepository(seed), VerificationCodeRepository(seed), SessionRepository(seed), now=now
    )


def _resend(seed, now: datetime) -> None:
    resend(IDENTIFIER, UserRepository(seed), VerificationCodeRepository(seed), OutboxRepository(seed), now=now)


def _error(seed, code: str, now: datetime) -> str:
    with pytest.raises(ApiError) as error:
        _verify(seed, code, now)
    return error.value.code


def test_code_is_valid_until_9_59(seed):
    # V-04
    token = _verify(seed, _code(seed), _at(9, 59))
    assert seed.sessions[token].user_id == 3


def test_code_expires_at_minute_10(seed):
    # V-05
    assert _error(seed, _code(seed), _at(10)) == CODE_EXPIRED
    assert UserRepository(seed).find_by_identifier(IDENTIFIER).status == "pending"


def test_resent_code_replaces_the_old_one(seed, monkeypatch):
    # V-11 i V-12
    old = _code(seed)
    # El codi és aleatori: es fixa el nou perquè no pugui coincidir amb el vell per atzar.
    monkeypatch.setattr("app.services.verification_service.secrets.randbelow", lambda _: int(_wrong(old)))
    _resend(seed, _at(2))
    new = _code(seed)

    assert new == _wrong(old)
    assert _error(seed, old, _at(3)) == INVALID_CODE
    # Els 10 minuts tornen a comptar des del reenviament (T0 + 2:00).
    assert _verify(seed, new, _at(11))


def test_expired_code_does_not_count_as_an_attempt(seed):
    # V-16
    code = _code(seed)
    for _ in range(4):
        assert _error(seed, _wrong(code), _at(5)) == INVALID_CODE

    assert _error(seed, code, _at(10)) == CODE_EXPIRED
    assert _error(seed, _wrong(code), _at(10)) == CODE_EXPIRED


def test_verified_session_records_the_moment(seed):
    token = _verify(seed, _code(seed), _at(1))
    assert seed.sessions[token].last_activity == _at(1)


# --- API ----------------------------------------------------------------------------


def _register_api(client: TestClient, identifier: str = IDENTIFIER) -> str:
    client.post(
        "/api/auth/register",
        json={"identifier": identifier, "password": "Platja2026", "acceptedTerms": True},
    )
    return _last_code(client, identifier)


def _last_code(client: TestClient, identifier: str = IDENTIFIER) -> str:
    return client.get("/api/dev/outbox", params={"to": identifier}).json()["messages"][0]["code"]


def _verify_api(client: TestClient, code: str, identifier: str = IDENTIFIER):
    return client.post("/api/auth/verify", json={"identifier": identifier, "code": code})


def test_right_code_activates_the_account_and_returns_a_token(client: TestClient) -> None:
    # V-01
    code = _register_api(client)

    response = _verify_api(client, code)

    assert response.status_code == 200
    assert set(response.json()) == {"token"}
    user = next(u for u in client.app.state.seed.users.values() if u.identifier == IDENTIFIER)
    assert user.status == "active"


def test_token_from_verify_opens_the_home(client: TestClient) -> None:
    # V-02: compte nou, saldo 0 i sense moviments.
    token = _verify_api(client, _register_api(client)).json()["token"]

    home = client.get("/api/home", headers={"Authorization": f"Bearer {token}"})

    assert home.status_code == 200
    assert home.json()["balance"] == 0
    assert home.json()["lastMovements"] == []


def test_verified_account_can_log_in(client: TestClient) -> None:
    _verify_api(client, _register_api(client))

    login = client.post("/api/auth/login", json={"identifier": IDENTIFIER, "password": "Platja2026"})

    assert login.status_code == 200


def test_used_code_does_not_work_again(client: TestClient) -> None:
    # V-03
    code = _register_api(client)
    _verify_api(client, code)

    assert _verify_api(client, code).json()["code"] == "INVALID_CODE"


def test_wrong_code(client: TestClient) -> None:
    # V-06
    code = _register_api(client)

    response = _verify_api(client, _wrong(code))

    assert response.status_code == 422
    assert response.json() == {"code": "INVALID_CODE", "message": "El codi no és correcte o ha caducat."}


def test_four_wrong_codes_then_the_right_one(client: TestClient) -> None:
    # V-07
    code = _register_api(client)
    for _ in range(4):
        assert _verify_api(client, _wrong(code)).json()["code"] == "INVALID_CODE"

    assert _verify_api(client, code).status_code == 200


def test_fifth_wrong_code_blocks_the_code(client: TestClient) -> None:
    # V-08 i V-09
    code = _register_api(client)
    answers = [_verify_api(client, _wrong(code)) for _ in range(5)]

    assert [a.json()["code"] for a in answers] == ["INVALID_CODE"] * 4 + ["TOO_MANY_ATTEMPTS"]
    assert answers[-1].status_code == 429
    assert answers[-1].json()["message"] == "Has fet massa intents. Demana un codi nou."
    # Ara ni el codi correcte serveix.
    assert _verify_api(client, code).json()["code"] == "TOO_MANY_ATTEMPTS"


def test_new_code_after_blocking(client: TestClient) -> None:
    # V-10 i V-17: el reenviament desbloqueja i torna el comptador a zero.
    code = _register_api(client)
    for _ in range(5):
        _verify_api(client, _wrong(code))

    assert client.post("/api/auth/resend-code", json={"identifier": IDENTIFIER}).json() == {"status": "ok"}
    new = _last_code(client)
    for _ in range(4):
        assert _verify_api(client, _wrong(new)).json()["code"] == "INVALID_CODE"
    assert _verify_api(client, new).status_code == 200


def test_resend_sends_a_new_message(client: TestClient) -> None:
    _register_api(client)

    client.post("/api/auth/resend-code", json={"identifier": " ANA@x.com "})

    assert len(client.get("/api/dev/outbox", params={"to": IDENTIFIER}).json()["messages"]) == 2


@pytest.mark.parametrize("identifier", ["ningu@x.com", DEMO_IDENTIFIER])
def test_resend_to_unknown_or_active_account_does_nothing(client: TestClient, identifier: str) -> None:
    # V-13
    response = client.post("/api/auth/resend-code", json={"identifier": identifier})

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert client.get("/api/dev/outbox").json() == {"messages": []}


def test_verify_unknown_account_does_not_reveal_it(client: TestClient) -> None:
    # V-14
    assert _verify_api(client, "123456", "ningu@x.com").json()["code"] == "INVALID_CODE"


def test_verify_active_account_is_invalid_code(client: TestClient) -> None:
    assert _verify_api(client, "123456", DEMO_IDENTIFIER).json()["code"] == "INVALID_CODE"


@pytest.mark.parametrize(
    "body",
    [
        {"identifier": IDENTIFIER, "code": "12345"},  # V-15
        {"identifier": IDENTIFIER, "code": "12a456"},
        {"identifier": IDENTIFIER, "code": "1234567"},
        {"identifier": IDENTIFIER, "code": "١٢٣٤٥٦"},  # xifres d'un altre alfabet
        {"identifier": IDENTIFIER, "code": 123456},  # número i no string
        {"identifier": "ana@", "code": "123456"},
        {"identifier": IDENTIFIER},
    ],
)
def test_malformed_verify_is_a_validation_error_and_does_not_count(client: TestClient, body) -> None:
    code = _register_api(client)

    response = client.post("/api/auth/verify", json=body)

    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"
    # No ha comptat com a intent: encara en queden 5.
    for _ in range(4):
        _verify_api(client, _wrong(code))
    assert _verify_api(client, code).status_code == 200


def test_resend_with_a_malformed_identifier(client: TestClient) -> None:
    response = client.post("/api/auth/resend-code", json={"identifier": "12ab"})
    assert response.json()["code"] == "VALIDATION_ERROR"
