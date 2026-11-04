"""Tests del servei de registre (T01.2, docs/api.md §8.5).

Executar des de backend/:  python -m pytest tests/test_registration_service.py
"""

import threading
from datetime import datetime

import pytest

from app.data.seed import MADRID_TZ, build_seed
from app.repositories import (
    AccountRepository,
    OutboxRepository,
    UserRepository,
    VerificationCodeRepository,
)
from app.services.errors import (
    ALREADY_REGISTERED,
    VALIDATION_ERROR,
    WEAK_PASSWORD,
    ApiError,
)
from app.services.password_hashing import verify_password
from app.services.registration_service import register

NOW = datetime(2026, 11, 3, 10, 0, 0, tzinfo=MADRID_TZ)


@pytest.fixture
def seed():
    return build_seed(now=NOW)


def _register(seed, identifier="ana@x.com", password="Platja2026", accepted_terms=True):
    return register(
        identifier,
        password,
        accepted_terms,
        UserRepository(seed),
        AccountRepository(seed),
        VerificationCodeRepository(seed),
        OutboxRepository(seed),
        now=NOW,
    )


def _snapshot(seed):
    return (sorted(seed.users), sorted(seed.accounts), seed.next_user_id, len(seed.outbox))


def test_register_returns_the_pending_user_with_a_hash(seed):
    user = _register(seed, identifier="Ana@X.com")

    assert user.identifier == "ana@x.com"
    assert user.status == "pending"
    assert verify_password("Platja2026", user.password_hash)
    assert seed.users[user.id] is user
    assert seed.accounts[user.id].balance == 0


@pytest.mark.parametrize(
    "kwargs, code",
    [
        ({"accepted_terms": False}, VALIDATION_ERROR),
        ({"identifier": "ana@"}, VALIDATION_ERROR),
        ({"password": "Platja2026" + "a" * 63}, VALIDATION_ERROR),  # 73 bytes
        ({"password": "platja2026"}, WEAK_PASSWORD),
        ({"identifier": "DEMO@evolt.test"}, ALREADY_REGISTERED),
    ],
)
def test_errors_raise_and_change_nothing(seed, kwargs, code):
    before = _snapshot(seed)

    with pytest.raises(ApiError) as error:
        _register(seed, **kwargs)

    assert error.value.code == code
    assert error.value.details is None
    assert _snapshot(seed) == before


def test_simultaneous_registrations_with_the_same_email_create_one_user(seed):
    # Revisió de la PR: dos registres alhora no poden crear dos usuaris amb el mateix email.
    threads_count = 8
    barrier = threading.Barrier(threads_count)
    results: list[str] = []

    def attempt():
        barrier.wait()  # tots els fils comencen alhora
        try:
            _register(seed)
            results.append("created")
        except ApiError as error:
            results.append(error.code)

    threads = [threading.Thread(target=attempt) for _ in range(threads_count)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert results.count("created") == 1
    assert results.count(ALREADY_REGISTERED) == threads_count - 1
    assert [u.identifier for u in seed.users.values()].count("ana@x.com") == 1
    assert seed.next_user_id == 4


def test_register_sends_a_verification_code(seed):
    # R-03 (T02.1): el codi arriba a la bústia i queda desat com a codi vigent.
    user = _register(seed)

    [message] = seed.outbox
    assert message.to == "ana@x.com"
    assert message.channel == "email"
    assert message.type == "verification_code"
    assert message.date == NOW
    assert seed.verification_codes[user.id].code == message.code
