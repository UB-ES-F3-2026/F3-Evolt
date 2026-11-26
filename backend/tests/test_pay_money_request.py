"""Tests de T39.1: pagar una sol·licitud rebuda (US-39, docs/api.md §15.3).

Proves PG-01 a PG-17 de docs/proves-pagaments.md. El seed es construeix a T0 i el
rellotge dels serveis es fixa amb `clock`, així les dates i el límit diari no depenen
del dia d'avui.

Executar des de backend/:  python -m pytest tests/test_pay_money_request.py
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
from app.services.money_request_service import pay_request

# T0 de docs/proves-pagaments.md.
T0 = datetime(2026, 11, 15, 21, 15, 0, tzinfo=MADRID_TZ)
ALICIA = {"X-User-Id": "3"}
EMPTY_USER = {"X-User-Id": str(EMPTY_USER_ID)}
SEED_BALANCE = 379521


class Clock:
    now = T0


@pytest.fixture
def clock(monkeypatch: pytest.MonkeyPatch) -> Clock:
    clock = Clock()
    monkeypatch.setattr(money_request_service, "now_madrid", lambda: clock.now)
    monkeypatch.setattr(transfer_service, "now_madrid", lambda: clock.now)
    # `GET /api/transfers/limit` llegeix l'hora al router.
    monkeypatch.setattr(transfers_router, "now_madrid", lambda: clock.now)
    return clock


@pytest.fixture
def seed(client: TestClient, clock: Clock) -> SeedData:
    """Seed a T0: l'usuari 1 ha rebut `req-06` d'Alicia, 25,00 €, pendent (§15.8)."""
    fixed = build_seed(now=T0)
    client.app.state.seed = fixed
    return fixed


def _pay(client: TestClient, request_id: str, headers: dict[str, str] | None = None) -> Response:
    return client.post(f"/api/money-requests/{request_id}/pay", headers=headers)


def _status_of(client: TestClient, request_id: str, path: str, headers: dict[str, str] | None = None) -> str:
    items = client.get(path, headers=headers).json()["items"]
    return next(item["status"] for item in items if item["id"] == request_id)


def _state(seed: SeedData) -> tuple:
    """Saldos, moviments, bústia i estats: el que un pagament rebutjat no pot canviar."""
    return (
        {user_id: account.balance for user_id, account in seed.accounts.items()},
        len(seed.movements),
        len(seed.outbox),
        {request.id: request.status for request in seed.money_requests},
    )


# --- Pagar (§15.3) -------------------------------------------------------------------------


def test_paying_a_pending_request_sends_the_money(client: TestClient, seed: SeedData) -> None:
    # PG-01
    response = _pay(client, "req-06")

    assert response.status_code == 201
    assert response.json() == {
        "balance": 377021,
        "movement": {
            "id": "mov-31",
            "amount": 2500,
            "concept": "El sopar de divendres",
            "date": "2026-11-15T21:15:00+01:00",
            "type": "expense",
            "icon": "transfer",
            "counterparty": "Alicia",
            "status": "completed",
            "reference": "EVT-000031",
        },
        "request": {
            "id": "req-06",
            "from": {"id": "usr-03", "name": "Alicia", "username": "aliciaa415"},
            "amount": 2500,
            "concept": "El sopar de divendres",
            "status": "paid",
            "createdAt": "2026-11-13T19:30:00+01:00",
            "expiresAt": "2026-11-20T00:00:00+01:00",
        },
    }


def test_both_balances_and_movements_change(client: TestClient, seed: SeedData) -> None:
    # PG-02
    _pay(client, "req-06")

    payer = client.get("/api/home").json()
    requester = client.get("/api/home", headers=ALICIA).json()

    assert payer["balance"] == 377021
    assert (payer["lastMovements"][0]["concept"], payer["lastMovements"][0]["type"]) == (
        "El sopar de divendres",
        "expense",
    )
    assert requester["balance"] == 2500
    received = requester["lastMovements"][0]
    assert (received["concept"], received["type"], received["amount"]) == ("El sopar de divendres", "income", 2500)
    detail = client.get(f"/api/movements/{received['id']}", headers=ALICIA).json()
    assert detail["counterparty"] == "Usuari demo"


def test_the_request_is_paid_on_both_sides(client: TestClient, seed: SeedData) -> None:
    # PG-03
    _pay(client, "req-06")

    assert _status_of(client, "req-06", "/api/money-requests/received") == "paid"
    assert _status_of(client, "req-06", "/api/money-requests", ALICIA) == "paid"


def test_paying_sends_the_us14_notices_and_nothing_else(client: TestClient, seed: SeedData) -> None:
    # PG-04
    before = len(seed.outbox)

    _pay(client, "req-06")

    demo = client.get("/api/dev/outbox", params={"to": "demo@evolt.test"}).json()["messages"][0]
    alicia = client.get("/api/dev/outbox", params={"to": "alicia@evolt.test"}).json()["messages"][0]
    assert (demo["type"], demo["text"]) == ("transfer_sent", "Has enviat 25,00 € a Alicia.")
    assert (alicia["type"], alicia["text"]) == (
        "transfer_received",
        "Usuari demo t'ha enviat 25,00 €: El sopar de divendres.",
    )
    assert len(seed.outbox) == before + 2


def test_paying_counts_for_the_daily_limit(client: TestClient, seed: SeedData) -> None:
    # PG-05
    _pay(client, "req-06")

    assert client.get("/api/transfers/limit").json()["remainingToday"] == 97500


def test_paying_twice_is_not_pending(client: TestClient, seed: SeedData) -> None:
    # PG-06
    _pay(client, "req-06")
    before = _state(seed)

    response = _pay(client, "req-06")

    assert response.status_code == 422
    assert response.json()["code"] == "REQUEST_NOT_PENDING"
    assert _state(seed) == before


@pytest.mark.parametrize("request_id", ["req-03", "req-04", "req-05"])
def test_expired_rejected_or_paid_requests_cannot_be_paid(client: TestClient, seed: SeedData, request_id: str) -> None:
    # PG-07: caducada, rebutjada i pagada.
    response = _pay(client, request_id)

    assert response.status_code == 422
    assert response.json() == {"code": "REQUEST_NOT_PENDING", "message": "Aquesta sol·licitud ja no està pendent."}


@pytest.mark.parametrize(
    ("request_id", "headers"),
    [("req-02", None), ("req-06", EMPTY_USER), ("req-99", None), ("abc", None)],
)
def test_only_your_received_requests_can_be_paid(
    client: TestClient, seed: SeedData, request_id: str, headers: dict[str, str] | None
) -> None:
    # PG-08: la `req-02` l'ha enviada l'usuari 1; la `req-06` no és de l'usuari 2.
    before = _state(seed)

    response = _pay(client, request_id, headers)

    assert response.status_code == 404
    assert response.json() == {"code": "REQUEST_NOT_FOUND", "message": "Aquesta sol·licitud ja no existeix."}
    assert _state(seed) == before


def test_not_enough_balance_keeps_the_request_pending(client: TestClient, seed: SeedData) -> None:
    # PG-09: Alicia demana 4.000,00 € i l'usuari 1 en té 3.795,21.
    created = client.post(
        "/api/money-requests", json={"toUserId": "usr-01", "amount": 400000, "concept": "Lloguer"}, headers=ALICIA
    ).json()
    before = _state(seed)

    response = _pay(client, created["id"])

    assert response.status_code == 422
    assert response.json()["code"] == "INSUFFICIENT_BALANCE"
    assert _state(seed) == before


def test_over_the_daily_limit_keeps_the_request_pending(client: TestClient, seed: SeedData) -> None:
    # PG-10: 980,00 € enviats avui + 25,00 € passen de 1.000,00 €.
    client.post("/api/transfers", json={"toUserId": "usr-02", "amount": 98000})
    before = _state(seed)

    response = _pay(client, "req-06")

    assert response.status_code == 422
    assert response.json()["code"] == "TRANSFER_LIMIT_EXCEEDED"
    assert response.json()["details"] == {"remainingToday": 2000}
    assert _state(seed) == before


def test_reaching_the_daily_limit_exactly_is_allowed(client: TestClient, seed: SeedData) -> None:
    # PG-11
    client.post("/api/transfers", json={"toUserId": "usr-02", "amount": 97500})

    assert _pay(client, "req-06").status_code == 201


def test_not_pending_is_checked_before_the_balance(client: TestClient, seed: SeedData, clock: Clock) -> None:
    # PG-12: una caducada de 50,00 € a l'usuari 2, que té saldo 0.
    created = client.post(
        "/api/money-requests", json={"toUserId": "usr-02", "amount": 5000, "concept": "Pizza"}, headers=ALICIA
    ).json()
    clock.now = datetime(2026, 11, 22, 0, 0, 0, tzinfo=MADRID_TZ)

    assert _pay(client, created["id"], EMPTY_USER).json()["code"] == "REQUEST_NOT_PENDING"


def test_paying_on_the_day_it_expires_is_too_late(client: TestClient, seed: SeedData, clock: Clock) -> None:
    # PG-13: la `req-06` caduca el 20/11 a les 00:00.
    clock.now = datetime(2026, 11, 20, 0, 0, 0, tzinfo=MADRID_TZ)

    assert _pay(client, "req-06").json()["code"] == "REQUEST_NOT_PENDING"


def test_two_payments_at_once_move_the_money_once(monkeypatch: pytest.MonkeyPatch) -> None:
    # PG-14: amb una espera dins de la primera escriptura, sense el pany passarien totes dues.
    seed = build_seed(now=T0)
    original_add = MovementRepository.add

    def slow_add(self: MovementRepository, **kwargs: object):
        time.sleep(0.1)
        return original_add(self, **kwargs)

    monkeypatch.setattr(MovementRepository, "add", slow_add)
    repositories = (
        UserRepository(seed),
        AccountRepository(seed),
        MovementRepository(seed),
        MoneyRequestRepository(seed),
        OutboxRepository(seed),
    )
    barrier = threading.Barrier(2)
    outcomes: list[str] = []

    def pay() -> None:
        barrier.wait()
        try:
            pay_request(DEMO_USER_ID, "req-06", *repositories, now=T0)
            outcomes.append("ok")
        except ApiError as error:
            outcomes.append(error.code)

    threads = [threading.Thread(target=pay) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert sorted(outcomes) == sorted(["ok", "REQUEST_NOT_PENDING"])
    assert seed.accounts[DEMO_USER_ID].balance == SEED_BALANCE - 2500


@pytest.mark.memory_only
def test_a_failed_notice_changes_nothing(client: TestClient, seed: SeedData, monkeypatch: pytest.MonkeyPatch) -> None:
    # PG-15
    def fail(*args: object, **kwargs: object) -> None:
        raise RuntimeError("bústia fallida")

    before = _state(seed)
    monkeypatch.setattr(OutboxRepository, "add", fail)

    response = _pay(client, "req-06")

    assert response.status_code == 500
    assert response.json()["code"] == "INTERNAL_ERROR"
    assert _state(seed) == before


def test_paying_gives_no_xp(client: TestClient, seed: SeedData) -> None:
    # PG-16
    xp_before = (seed.users[DEMO_USER_ID].xp, seed.users[3].xp)

    _pay(client, "req-06")

    assert (seed.users[DEMO_USER_ID].xp, seed.users[3].xp) == xp_before


@pytest.fixture
def strict_client(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    """App amb ALLOW_X_USER_ID=0, com al desplegament."""
    monkeypatch.setenv("ALLOW_X_USER_ID", "0")
    with TestClient(create_app()) as strict:
        yield strict


def test_paying_needs_a_session(strict_client: TestClient) -> None:
    # PG-17
    response = strict_client.post("/api/money-requests/req-06/pay")

    assert response.status_code == 401
    assert response.json()["code"] == "UNAUTHENTICATED"
