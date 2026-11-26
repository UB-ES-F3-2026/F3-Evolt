"""Tests de T31.1: seguiment d'una despesa dividida (US-31, docs/api.md §17.3, §17.4, §17.5 i §17.7).

Proves SG-01 a SG-15 de docs/proves-despeses.md. Pagar i rebutjar una part són la US-39 i
la US-40, que no són en aquesta branca: el test canvia l'estat de la sol·licitud al
repositori, com diu el document de proves.

Executar des de backend/:  python -m pytest tests/test_split_expense_tracking.py
"""

import threading
import time
from collections.abc import Iterator
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from httpx import Response

from app.data.seed import SeedData, build_seed
from app.main import create_app
from app.models import MADRID_TZ
from app.repositories import MoneyRequestRepository, OutboxRepository, SplitExpenseRepository, UserRepository
from app.services import money_request_service, split_expense_service
from app.services.errors import ApiError
from app.services.split_expense_service import resend_part

T0 = datetime(2026, 11, 15, 21, 15, 0, tzinfo=MADRID_TZ)
IZAN, ALICIA, MARTI = "usr-05", "usr-03", "usr-08"
D0 = {
    "concept": "Sopar d'aniversari",
    "total": 6000,
    "myShare": 1500,
    "parts": [{"toUserId": IZAN, "amount": 1500}, {"toUserId": ALICIA, "amount": 1500}, {"toUserId": MARTI, "amount": 1500}],
}


class Clock:
    now = T0


@pytest.fixture
def clock(monkeypatch: pytest.MonkeyPatch) -> Clock:
    clock = Clock()
    monkeypatch.setattr(split_expense_service, "now_madrid", lambda: clock.now)
    monkeypatch.setattr(money_request_service, "now_madrid", lambda: clock.now)
    return clock


@pytest.fixture
def seed(client: TestClient, clock: Clock) -> SeedData:
    fixed = build_seed(now=T0)
    client.app.state.seed = fixed
    return fixed


@pytest.fixture
def d0(client: TestClient, seed: SeedData) -> dict:
    """La despesa de l'exemple, ja dividida (DD-01)."""
    response = client.post("/api/split-expenses", json=D0)
    assert response.status_code == 201
    return response.json()


def _detail(client: TestClient, split_id: str = "split-01", headers: dict[str, str] | None = None) -> Response:
    return client.get(f"/api/split-expenses/{split_id}", headers=headers)


def _resend(client: TestClient, user: str, split_id: str = "split-01") -> Response:
    return client.post(f"/api/split-expenses/{split_id}/parts/{user}/resend")


def _set(seed: SeedData, request_id: str, status: str) -> None:
    """Pagar o rebutjar una part (US-39 i US-40): aquí, canviant l'estat desat directament."""
    next(r for r in seed.money_requests if r.id == request_id).status = status


def _part(view: dict, user: str) -> dict:
    return next(part for part in view["parts"] if part["to"]["id"] == user)


def _summary(view: dict) -> tuple:
    return (view["paidCount"], view["pendingAmount"], view["status"])


# --- Llista i detall (§17.3 i §17.4) -------------------------------------------------------


def test_the_list_has_the_split(client: TestClient, d0: dict) -> None:
    # SG-01
    assert client.get("/api/split-expenses").json() == {"items": [d0]}


def test_the_newest_split_comes_first(client: TestClient, d0: dict, clock: Clock) -> None:
    # SG-02
    clock.now = datetime(2026, 11, 16, 10, 0, tzinfo=MADRID_TZ)
    client.post("/api/split-expenses", json={**D0, "concept": "Entrades"})

    items = client.get("/api/split-expenses").json()["items"]

    assert [item["id"] for item in items] == ["split-02", "split-01"]


def test_the_detail_is_the_same_split(client: TestClient, d0: dict) -> None:
    # SG-03
    assert _detail(client).json() == d0


# --- Estats (§17.7): l'exemple de la US-31 --------------------------------------------------


def test_the_us31_example_step_by_step(client: TestClient, seed: SeedData, d0: dict) -> None:
    # SG-04 a SG-08
    ids = {part["to"]["id"]: part["requestId"] for part in d0["parts"]}

    _set(seed, ids[IZAN], "paid")
    view = _detail(client).json()
    assert _summary(view) == (1, 3000, "pending")
    assert _part(view, IZAN)["status"] == "paid"

    _set(seed, ids[MARTI], "rejected")
    view = _detail(client).json()
    assert _summary(view) == (1, 1500, "pending")
    assert _part(view, MARTI)["status"] == "rejected"

    _set(seed, ids[ALICIA], "paid")
    assert _summary(_detail(client).json()) == (2, 0, "closed")

    response = _resend(client, MARTI)
    assert response.status_code == 201
    view = response.json()
    new_id = _part(view, MARTI)["requestId"]
    assert new_id != ids[MARTI]
    assert _part(view, MARTI)["status"] == "pending"
    assert _summary(view) == (2, 1500, "pending")
    assert next(r for r in seed.money_requests if r.id == ids[MARTI]).status == "rejected"
    message = client.get("/api/dev/outbox", params={"to": "marti@evolt.test"}).json()["messages"]
    assert [m["type"] for m in message[:2]] == ["money_request", "money_request"]

    _set(seed, new_id, "paid")
    assert _summary(_detail(client).json()) == (3, 0, "completed")


def test_expired_parts_close_the_split_and_can_be_resent(client: TestClient, d0: dict, clock: Clock) -> None:
    # SG-09: D0 és del 15/11 i les parts caduquen el 22/11 a les 00:00.
    clock.now = datetime(2026, 11, 22, 0, 0, tzinfo=MADRID_TZ)

    view = _detail(client).json()

    assert [part["status"] for part in view["parts"]] == ["expired"] * 3
    assert _summary(view) == (0, 0, "closed")
    assert _resend(client, IZAN).status_code == 201


# --- Tornar a enviar (§17.5) ---------------------------------------------------------------


def test_only_rejected_or_expired_parts_can_be_resent(client: TestClient, seed: SeedData, d0: dict) -> None:
    # SG-10: la de Martí és pendent i la d'Izan, pagada.
    _set(seed, _part(d0, IZAN)["requestId"], "paid")

    for user in (MARTI, IZAN):
        response = _resend(client, user)
        assert response.status_code == 422
        assert response.json()["code"] == "PART_NOT_RESENDABLE"


def test_unknown_part_or_split_is_not_found(client: TestClient, d0: dict) -> None:
    # SG-11
    assert _resend(client, "usr-02").json()["code"] == "PART_NOT_FOUND"
    assert _detail(client, "split-99").json()["code"] == "SPLIT_NOT_FOUND"
    assert _resend(client, MARTI, "split-99").json()["code"] == "SPLIT_NOT_FOUND"


def test_another_users_split_is_not_found(client: TestClient, d0: dict) -> None:
    # SG-12
    alicia = {"X-User-Id": "3"}

    assert _detail(client, headers=alicia).status_code == 404
    assert client.get("/api/split-expenses", headers=alicia).json() == {"items": []}


def test_two_resends_at_once_create_one_request(seed: SeedData, monkeypatch: pytest.MonkeyPatch) -> None:
    # SG-13: amb una espera dins de la creació, sense el pany passarien totes dues.
    fixed = build_seed(now=T0)
    users, splits, requests, outbox = (
        UserRepository(fixed),
        SplitExpenseRepository(fixed),
        MoneyRequestRepository(fixed),
        OutboxRepository(fixed),
    )
    view = split_expense_service.create_split(
        1, "Sopar", 3000, 1500, [(MARTI, 1500)], users, splits, requests, outbox, now=T0
    )
    _set(fixed, view.parts[0].request_id, "rejected")
    original_add = MoneyRequestRepository.add

    def slow_add(self: MoneyRequestRepository, **kwargs: object):
        time.sleep(0.1)
        return original_add(self, **kwargs)

    monkeypatch.setattr(MoneyRequestRepository, "add", slow_add)
    barrier = threading.Barrier(2)
    outcomes: list[str] = []

    def resend() -> None:
        barrier.wait()
        try:
            resend_part(1, view.split.id, MARTI, users, splits, requests, outbox, now=T0)
            outcomes.append("ok")
        except ApiError as error:
            outcomes.append(error.code)

    threads = [threading.Thread(target=resend) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert sorted(outcomes) == sorted(["ok", "PART_NOT_RESENDABLE"])
    assert len(requests.list_by_split(view.split.id)) == 2


@pytest.mark.memory_only
def test_a_failed_notice_creates_no_request(
    client: TestClient, seed: SeedData, d0: dict, monkeypatch: pytest.MonkeyPatch
) -> None:
    # SG-14
    _set(seed, _part(d0, MARTI)["requestId"], "rejected")
    before = ([r.id for r in seed.money_requests], seed.next_money_request_number, len(seed.outbox))

    def fail(*args: object, **kwargs: object) -> None:
        raise RuntimeError("bústia fallida")

    monkeypatch.setattr(OutboxRepository, "add", fail)

    response = _resend(client, MARTI)

    assert response.status_code == 500
    assert ([r.id for r in seed.money_requests], seed.next_money_request_number, len(seed.outbox)) == before
    assert _part(_detail(client).json(), MARTI)["status"] == "rejected"


@pytest.fixture
def strict_client(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    """App amb ALLOW_X_USER_ID=0, com al desplegament."""
    monkeypatch.setenv("ALLOW_X_USER_ID", "0")
    with TestClient(create_app()) as strict:
        yield strict


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("GET", "/api/split-expenses"),
        ("GET", "/api/split-expenses/split-01"),
        ("POST", "/api/split-expenses/split-01/parts/usr-08/resend"),
    ],
)
def test_every_route_needs_a_session(strict_client: TestClient, method: str, path: str) -> None:
    # SG-15
    response = strict_client.request(method, path)

    assert response.status_code == 401
    assert response.json()["code"] == "UNAUTHENTICATED"
