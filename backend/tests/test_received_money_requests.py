"""Tests de T16.2: sol·licituds rebudes (docs/api.md §15.2, §15.5 i el seed de §15.8).

Proves SR-01 a SR-12 de docs/proves-pagaments.md. El seed es construeix a T0 i el
rellotge del servei es fixa amb `clock`, així les dates no depenen del dia d'avui.

Executar des de backend/:  python -m pytest tests/test_received_money_requests.py
"""

from collections.abc import Iterator
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from app.data.seed import EMPTY_USER_ID, SeedData, build_seed
from app.main import create_app
from app.models import MADRID_TZ
from app.repositories import MoneyRequestRepository
from app.services import money_request_service

# T0 de docs/proves-pagaments.md.
T0 = datetime(2026, 11, 15, 21, 15, 0, tzinfo=MADRID_TZ)
ALICIA = {"X-User-Id": "3"}
EMPTY_USER = {"X-User-Id": str(EMPTY_USER_ID)}
RECEIVED_KEYS = {"id", "from", "amount", "concept", "status", "createdAt", "expiresAt"}


class Clock:
    now = T0


@pytest.fixture
def clock(monkeypatch: pytest.MonkeyPatch) -> Clock:
    clock = Clock()
    monkeypatch.setattr(money_request_service, "now_madrid", lambda: clock.now)
    return clock


@pytest.fixture
def seed(client: TestClient, clock: Clock) -> SeedData:
    """Seed a T0: l'usuari 1 ha rebut `req-03` a `req-06`, una en cada estat (§15.8)."""
    fixed = build_seed(now=T0)
    client.app.state.seed = fixed
    return fixed


def _received(client: TestClient, headers: dict[str, str] | None = None) -> list[dict]:
    response = client.get("/api/money-requests/received", headers=headers)
    assert response.status_code == 200
    return response.json()["items"]


def _summary(items: list[dict]) -> list[tuple[str, str, str]]:
    return [(item["id"], item["from"]["name"], item["status"]) for item in items]


# --- La llista (§15.2) ---------------------------------------------------------------------


def test_received_requests_newest_first_one_in_each_state(client: TestClient, seed: SeedData) -> None:
    # SR-01: les dades dels mockups de la US-16.
    items = _received(client)

    assert _summary(items) == [
        ("req-06", "Alicia", "pending"),
        ("req-05", "Junhao", "paid"),
        ("req-04", "Izan", "rejected"),
        ("req-03", "Jiajun", "expired"),
    ]
    assert items[0] == {
        "id": "req-06",
        "from": {"id": "usr-03", "name": "Alicia", "username": "aliciaa415"},
        "amount": 2500,
        "concept": "El sopar de divendres",
        "status": "pending",
        "createdAt": "2026-11-13T19:30:00+01:00",
        "expiresAt": "2026-11-20T00:00:00+01:00",
    }


def test_each_received_request_has_the_contract_keys(client: TestClient, seed: SeedData) -> None:
    # SR-02: qui demana, sense email, telèfon ni saldo.
    for item in _received(client):
        assert set(item) == RECEIVED_KEYS
        assert set(item["from"]) == {"id", "name", "username"}


def test_a_user_without_received_requests_has_an_empty_list(client: TestClient, seed: SeedData) -> None:
    # SR-03
    assert _received(client, EMPTY_USER) == []


def test_only_the_requests_received_by_the_user(client: TestClient, seed: SeedData) -> None:
    # SR-04: la `req-06`, que ha enviat Alicia, no surt a les seves rebudes.
    assert _summary(_received(client, ALICIA)) == [("req-02", "Usuari demo", "pending")]


def test_sent_list_does_not_include_received_requests(client: TestClient, seed: SeedData) -> None:
    # SR-05
    items = client.get("/api/money-requests").json()["items"]

    assert [item["id"] for item in items] == ["req-02", "req-01"]


def test_the_sender_sees_the_same_request_in_the_sent_list(client: TestClient, seed: SeedData) -> None:
    # SR-06
    items = client.get("/api/money-requests", headers=ALICIA).json()["items"]

    assert [(item["id"], item["to"]["id"], item["status"]) for item in items] == [("req-06", "usr-01", "pending")]


# --- Estats (§15.5) ------------------------------------------------------------------------


def test_a_pending_received_request_expires_at_madrid_midnight(client: TestClient, seed: SeedData, clock: Clock) -> None:
    # SR-07: la `req-06` és del 13/11 a les 19:30 i caduca el 20/11 a les 00:00.
    clock.now = datetime(2026, 11, 19, 23, 59, 59, tzinfo=MADRID_TZ)
    assert _received(client)[0]["status"] == "pending"

    clock.now = datetime(2026, 11, 20, 0, 0, 0, tzinfo=MADRID_TZ)
    assert _received(client)[0]["status"] == "expired"


def test_paid_and_rejected_requests_never_expire(client: TestClient, seed: SeedData, clock: Clock) -> None:
    # SR-08
    clock.now = T0 + timedelta(days=30)

    statuses = {item["id"]: item["status"] for item in _received(client)}

    assert statuses["req-05"] == "paid"
    assert statuses["req-04"] == "rejected"


def test_a_cancelled_request_also_leaves_the_received_list(client: TestClient, seed: SeedData) -> None:
    # SR-09: l'usuari 1 cancel·la la que va enviar a Alicia.
    assert client.post("/api/money-requests/req-02/cancel").status_code == 200

    assert _received(client, ALICIA) == []


def test_a_new_request_appears_first_in_the_received_list(client: TestClient, seed: SeedData) -> None:
    # SR-10
    created = client.post(
        "/api/money-requests", json={"toUserId": "usr-01", "amount": 1000, "concept": "Cafè"}, headers=ALICIA
    )

    assert created.json()["id"] == "req-07"
    assert _summary(_received(client))[0] == ("req-07", "Alicia", "pending")


# --- Seed i reinici (§15.8) ----------------------------------------------------------------


def test_the_paid_seed_request_does_not_change_the_demo_balance(client: TestClient, seed: SeedData) -> None:
    # P92: la `req-05` surt pagada, però el seed no té els moviments d'aquell pagament.
    assert client.get("/api/home").json()["balance"] == 379521


@pytest.mark.memory_only
def test_reset_brings_back_the_received_requests(client: TestClient) -> None:
    # SR-11
    client.post("/api/money-requests", json={"toUserId": "usr-01", "amount": 1000, "concept": "Cafè"}, headers=ALICIA)

    client.post("/api/dev/reset")

    assert [item["id"] for item in _received(client)] == ["req-06", "req-05", "req-04", "req-03"]


@pytest.fixture
def strict_client(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    """App amb ALLOW_X_USER_ID=0, com al desplegament."""
    monkeypatch.setenv("ALLOW_X_USER_ID", "0")
    with TestClient(create_app()) as strict:
        yield strict


def test_the_received_list_needs_a_session(strict_client: TestClient) -> None:
    # SR-12
    response = strict_client.get("/api/money-requests/received")

    assert response.status_code == 401
    assert response.json()["code"] == "UNAUTHENTICATED"


def test_repository_orders_received_by_date_then_creation() -> None:
    # P4: dues del mateix moment, primer la creada més tard.
    seed = build_seed(now=T0)
    requests = MoneyRequestRepository(seed)
    first = requests.add(requester_id=3, recipient_id=2, amount=100, concept="A", created_at=T0)
    second = requests.add(requester_id=4, recipient_id=2, amount=100, concept="B", created_at=T0)

    assert [request.id for request in requests.list_by_recipient(2)] == [second.id, first.id]
