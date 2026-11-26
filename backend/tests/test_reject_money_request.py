"""Tests de T40.1: rebutjar una sol·licitud rebuda (US-40, docs/api.md §15.4 i §15.6).

Proves RB-01 a RB-10 de docs/proves-pagaments.md. El seed es construeix a T0 i el
rellotge dels serveis es fixa amb `clock`, així les dates no depenen del dia d'avui.

Executar des de backend/:  python -m pytest tests/test_reject_money_request.py
"""

import threading
import time
from collections.abc import Iterator
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from httpx import Response

from app.data.seed import DEMO_USER_ID, EMPTY_USER_ID, SeedData, build_seed
from app.main import create_app
from app.models import MADRID_TZ
from app.repositories import (
    AccountRepository,
    MoneyRequestRepository,
    MovementRepository,
    OutboxRepository,
    UserRepository,
)
from app.routers import transfers as transfers_router
from app.services import money_request_service, transfer_service
from app.services.errors import ApiError
from app.services.money_request_service import pay_request, reject_request

# T0 de docs/proves-pagaments.md.
T0 = datetime(2026, 11, 15, 21, 15, 0, tzinfo=MADRID_TZ)
ALICIA = {"X-User-Id": "3"}
EMPTY_USER = {"X-User-Id": str(EMPTY_USER_ID)}


class Clock:
    now = T0


@pytest.fixture
def clock(monkeypatch: pytest.MonkeyPatch) -> Clock:
    clock = Clock()
    monkeypatch.setattr(money_request_service, "now_madrid", lambda: clock.now)
    monkeypatch.setattr(transfer_service, "now_madrid", lambda: clock.now)
    monkeypatch.setattr(transfers_router, "now_madrid", lambda: clock.now)
    return clock


@pytest.fixture
def seed(client: TestClient, clock: Clock) -> SeedData:
    """Seed a T0: l'usuari 1 ha rebut `req-06` d'Alicia, 25,00 €, pendent (§15.8)."""
    fixed = build_seed(now=T0)
    client.app.state.seed = fixed
    return fixed


def _reject(client: TestClient, request_id: str, headers: dict[str, str] | None = None) -> Response:
    return client.post(f"/api/money-requests/{request_id}/reject", headers=headers)


def _status_of(client: TestClient, request_id: str, path: str, headers: dict[str, str] | None = None) -> str:
    items = client.get(path, headers=headers).json()["items"]
    return next(item["status"] for item in items if item["id"] == request_id)


def _state(seed: SeedData) -> tuple:
    """Saldos, moviments, bústia i estats: el que un rebuig fallit no pot canviar."""
    return (
        {user_id: account.balance for user_id, account in seed.accounts.items()},
        len(seed.movements),
        len(seed.outbox),
        {request.id: request.status for request in seed.money_requests},
    )


def test_rejecting_a_pending_request(client: TestClient, seed: SeedData) -> None:
    # RB-01
    response = _reject(client, "req-06")

    assert response.status_code == 200
    assert response.json() == {
        "request": {
            "id": "req-06",
            "from": {"id": "usr-03", "name": "Alicia", "username": "aliciaa415"},
            "amount": 2500,
            "concept": "El sopar de divendres",
            "status": "rejected",
            "createdAt": "2026-11-13T19:30:00+01:00",
            "expiresAt": "2026-11-20T00:00:00+01:00",
        }
    }


def test_the_request_is_rejected_on_both_sides(client: TestClient, seed: SeedData) -> None:
    # RB-02
    _reject(client, "req-06")

    assert _status_of(client, "req-06", "/api/money-requests/received") == "rejected"
    assert _status_of(client, "req-06", "/api/money-requests", ALICIA) == "rejected"


def test_the_requester_gets_a_notice(client: TestClient, seed: SeedData) -> None:
    # RB-03
    _reject(client, "req-06")

    message = client.get("/api/dev/outbox", params={"to": "alicia@evolt.test"}).json()["messages"][0]

    assert message == {
        "to": "alicia@evolt.test",
        "channel": "email",
        "type": "money_request_rejected",
        "text": "Usuari demo ha rebutjat la teva sol·licitud.",
        "date": "2026-11-15T21:15:00+01:00",
    }


def test_rejecting_moves_no_money(client: TestClient, seed: SeedData) -> None:
    # RB-04
    def snapshot(headers=None):
        paths = ("/api/home", "/api/movements", "/api/transfers/limit")
        return [client.get(path, headers=headers).json() for path in paths]

    before = (snapshot(), snapshot(ALICIA))

    _reject(client, "req-06")

    assert (snapshot(), snapshot(ALICIA)) == before


@pytest.mark.parametrize(
    ("method", "headers"),
    [("reject", None), ("pay", None), ("cancel", ALICIA)],
)
def test_a_rejected_request_cannot_be_reopened(
    client: TestClient, seed: SeedData, method: str, headers: dict[str, str] | None
) -> None:
    # RB-05: rebutjar-la, pagar-la o que Alicia la cancel·li.
    _reject(client, "req-06")

    response = client.post(f"/api/money-requests/req-06/{method}", headers=headers)

    assert response.status_code == 422
    assert response.json()["code"] == "REQUEST_NOT_PENDING"


@pytest.mark.parametrize("request_id", ["req-03", "req-04", "req-05"])
def test_expired_rejected_or_paid_requests_cannot_be_rejected(
    client: TestClient, seed: SeedData, request_id: str
) -> None:
    # RB-06
    response = _reject(client, request_id)

    assert response.status_code == 422
    assert response.json() == {"code": "REQUEST_NOT_PENDING", "message": "Aquesta sol·licitud ja no està pendent."}


@pytest.mark.parametrize(
    ("request_id", "headers"),
    [("req-02", None), ("req-06", EMPTY_USER), ("req-99", None)],
)
def test_only_your_received_requests_can_be_rejected(
    client: TestClient, seed: SeedData, request_id: str, headers: dict[str, str] | None
) -> None:
    # RB-07
    before = _state(seed)

    response = _reject(client, request_id, headers)

    assert response.status_code == 404
    assert response.json()["code"] == "REQUEST_NOT_FOUND"
    assert _state(seed) == before


def test_paying_and_rejecting_at_once_only_one_wins(monkeypatch: pytest.MonkeyPatch) -> None:
    # RB-08: amb una espera dins de l'enviament, sense el pany passarien totes dues.
    seed = build_seed(now=T0)
    original_add = MovementRepository.add

    def slow_add(self: MovementRepository, **kwargs: object):
        time.sleep(0.1)
        return original_add(self, **kwargs)

    monkeypatch.setattr(MovementRepository, "add", slow_add)
    users, accounts, movements = UserRepository(seed), AccountRepository(seed), MovementRepository(seed)
    requests, outbox = MoneyRequestRepository(seed), OutboxRepository(seed)
    operations = [
        lambda: pay_request(DEMO_USER_ID, "req-06", users, accounts, movements, requests, outbox, now=T0),
        lambda: reject_request(DEMO_USER_ID, "req-06", users, requests, outbox, now=T0),
    ]
    barrier = threading.Barrier(len(operations))
    outcomes: list[str] = []

    def run(operation) -> None:
        barrier.wait()
        try:
            operation()
            outcomes.append("ok")
        except ApiError as error:
            outcomes.append(error.code)

    threads = [threading.Thread(target=run, args=(operation,)) for operation in operations]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert sorted(outcomes) == sorted(["ok", "REQUEST_NOT_PENDING"])
    final = requests.get("req-06").status
    paid = seed.accounts[DEMO_USER_ID].balance == 379521 - 2500
    assert (final, paid) in {("paid", True), ("rejected", False)}


@pytest.mark.memory_only
def test_a_failed_notice_keeps_the_request_pending(
    client: TestClient, seed: SeedData, monkeypatch: pytest.MonkeyPatch
) -> None:
    # RB-09
    def fail(*args: object, **kwargs: object) -> None:
        raise RuntimeError("bústia fallida")

    before = _state(seed)
    monkeypatch.setattr(OutboxRepository, "add", fail)

    response = _reject(client, "req-06")

    assert response.status_code == 500
    assert response.json()["code"] == "INTERNAL_ERROR"
    assert _state(seed) == before


@pytest.fixture
def strict_client(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    """App amb ALLOW_X_USER_ID=0, com al desplegament."""
    monkeypatch.setenv("ALLOW_X_USER_ID", "0")
    with TestClient(create_app()) as strict:
        yield strict


def test_rejecting_needs_a_session(strict_client: TestClient) -> None:
    # RB-10
    response = strict_client.post("/api/money-requests/req-06/reject")

    assert response.status_code == 401
    assert response.json()["code"] == "UNAUTHENTICATED"
