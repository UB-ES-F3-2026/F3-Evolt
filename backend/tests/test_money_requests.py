"""Tests de T15.2: sol·licituds de diners (docs/api.md §14).

Proves SO-01 a SO-25 de docs/proves-pagaments.md. El seed es construeix a T0 i el
rellotge del servei es fixa amb `clock`, així les dates no depenen del dia d'avui.

Executar des de backend/:  python -m pytest tests/test_money_requests.py
"""

from collections.abc import Iterator
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from app.data.seed import EMPTY_USER_ID, SeedData, build_seed
from app.main import create_app
from app.models import MADRID_TZ
from app.repositories import MoneyRequestRepository, OutboxRepository
from app.services import money_request_service
from app.services.money_request_service import current_status, expires_at

# T0 de docs/proves-pagaments.md.
T0 = datetime(2026, 11, 15, 21, 15, 0, tzinfo=MADRID_TZ)
ALICIA = {"X-User-Id": "3"}
EMPTY_USER = {"X-User-Id": str(EMPTY_USER_ID)}
REQUEST_KEYS = {"id", "to", "amount", "concept", "status", "createdAt", "expiresAt"}
DINNER = {"toUserId": "usr-03", "amount": 2500, "concept": "El sopar de divendres"}
NOT_FOUND_BODY = {"code": "REQUEST_NOT_FOUND", "message": "Aquesta sol·licitud ja no existeix."}


class Clock:
    now = T0


@pytest.fixture
def clock(monkeypatch: pytest.MonkeyPatch) -> Clock:
    clock = Clock()
    monkeypatch.setattr(money_request_service, "now_madrid", lambda: clock.now)
    return clock


@pytest.fixture
def seed(client: TestClient, clock: Clock) -> SeedData:
    """Seed a T0: enviades `req-01` (6/11, caducada) i `req-02` (14/11 a les 19:30, pendent), i les rebudes `req-03` a `req-06` (§15.8)."""
    fixed = build_seed(now=T0)
    client.app.state.seed = fixed
    return fixed


def _create(client: TestClient, body: dict, headers: dict[str, str] | None = None):
    return client.post("/api/money-requests", json=body, headers=headers)


def _list(client: TestClient, headers: dict[str, str] | None = None) -> list[dict]:
    response = client.get("/api/money-requests", headers=headers)
    assert response.status_code == 200
    return response.json()["items"]


def _cancel(client: TestClient, request_id: str, headers: dict[str, str] | None = None):
    return client.post(f"/api/money-requests/{request_id}/cancel", headers=headers)


def _state(seed: SeedData):
    """El que una sol·licitud rebutjada no pot canviar: sol·licituds, comptador i bústia."""
    return ([r.id for r in seed.money_requests], seed.next_money_request_number, len(seed.outbox))


# --- Crear (§14.2) -------------------------------------------------------------------------


def test_create_a_request(client: TestClient, seed: SeedData) -> None:
    # SO-01
    response = _create(client, DINNER)

    assert response.status_code == 201
    assert response.json() == {
        "id": "req-07",
        "to": {"id": "usr-03", "name": "Alicia", "username": "aliciaa415"},
        "amount": 2500,
        "concept": "El sopar de divendres",
        "status": "pending",
        "createdAt": "2026-11-15T21:15:00+01:00",
        "expiresAt": "2026-11-22T00:00:00+01:00",
    }


def test_sent_requests_newest_first_with_their_state(client: TestClient, seed: SeedData) -> None:
    # SO-02: la caducada del seed continua a la llista.
    _create(client, DINNER)

    items = _list(client)

    assert [(item["id"], item["status"]) for item in items] == [
        ("req-07", "pending"),
        ("req-02", "pending"),
        ("req-01", "expired"),
    ]


def test_each_request_has_the_contract_keys(client: TestClient, seed: SeedData) -> None:
    # SO-03: el destinatari, sense email, telèfon ni saldo.
    _create(client, DINNER)

    for item in _list(client):
        assert set(item) == REQUEST_KEYS
        assert set(item["to"]) == {"id", "name", "username"}


def test_a_request_moves_no_money(client: TestClient, seed: SeedData) -> None:
    # SO-04
    def snapshot(headers=None):
        return [client.get(path, headers=headers).json() for path in ("/api/home", "/api/movements", "/api/pots")]

    before = (snapshot(), snapshot(ALICIA))

    _create(client, DINNER)

    assert (snapshot(), snapshot(ALICIA)) == before


def test_the_recipient_gets_a_notice(client: TestClient, seed: SeedData) -> None:
    # SO-05
    _create(client, DINNER)

    message = client.get("/api/dev/outbox", params={"to": "alicia@evolt.test"}).json()["messages"][0]

    assert message == {
        "to": "alicia@evolt.test",
        "channel": "email",
        "type": "money_request",
        "text": "Usuari demo et demana 25,00 €: El sopar de divendres.",
        "date": "2026-11-15T21:15:00+01:00",
    }


def test_a_user_without_requests_has_an_empty_list(client: TestClient, seed: SeedData) -> None:
    # SO-06
    assert _list(client, EMPTY_USER) == []


def test_asking_yourself_is_rejected(client: TestClient, seed: SeedData) -> None:
    # SO-07
    before = _state(seed)

    response = _create(client, {**DINNER, "toUserId": "usr-01"})

    assert response.status_code == 422
    assert response.json() == {"code": "SELF_REQUEST", "message": "No et pots demanar diners a tu mateix."}
    assert _state(seed) == before


def test_unknown_or_pending_recipient_is_not_found(client: TestClient, seed: SeedData) -> None:
    # SO-08
    client.post("/api/auth/register", json={"identifier": "anna@x.com", "password": "Platja2026", "acceptedTerms": True})
    pending_id = "usr-09"

    for to in ("usr-99", "3", pending_id):
        response = _create(client, {**DINNER, "toUserId": to})
        assert response.status_code == 404
        assert response.json()["code"] == "RECIPIENT_NOT_FOUND"


@pytest.mark.parametrize("amount", [0, -100])
def test_zero_or_negative_amount(client: TestClient, seed: SeedData, amount: int) -> None:
    # SO-09
    response = _create(client, {**DINNER, "amount": amount})

    assert response.status_code == 422
    assert response.json()["code"] == "INVALID_AMOUNT"


def test_at_most_one_million_euros(client: TestClient, seed: SeedData) -> None:
    # SO-10
    assert _create(client, {**DINNER, "amount": 100_000_000}).status_code == 201

    response = _create(client, {**DINNER, "amount": 100_000_001})

    assert response.status_code == 422
    assert response.json() == {"code": "AMOUNT_OVER_LIMIT", "message": "L'import màxim és d'1.000.000,00 €."}


@pytest.mark.parametrize("concept", ["", "   ", "x" * 141])
def test_concept_must_have_1_to_140_characters(client: TestClient, seed: SeedData, concept: str) -> None:
    # SO-11
    response = _create(client, {**DINNER, "concept": concept})

    assert response.status_code == 422
    assert response.json()["code"] == "INVALID_CONCEPT"


def test_concept_is_trimmed_and_140_characters_fit(client: TestClient, seed: SeedData) -> None:
    # SO-11
    assert _create(client, {**DINNER, "concept": "x" * 140}).status_code == 201
    assert _create(client, {**DINNER, "concept": "  Sopar  "}).json()["concept"] == "Sopar"


@pytest.mark.parametrize(
    "body",
    [
        {"toUserId": "usr-03", "amount": 2500},
        {**DINNER, "amount": "2500"},
        {**DINNER, "toUserId": 3},
        {"amount": 2500, "concept": "Sopar"},
    ],
)
def test_badly_formed_body_is_a_validation_error(client: TestClient, seed: SeedData, body: dict) -> None:
    # SO-12
    response = _create(client, body)

    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"


def test_validation_order(client: TestClient, seed: SeedData) -> None:
    # SO-13: el destinatari es comprova abans que l'import.
    assert _create(client, {**DINNER, "toUserId": "usr-01", "amount": 0}).json()["code"] == "SELF_REQUEST"
    assert _create(client, {**DINNER, "toUserId": "usr-99", "amount": 0}).json()["code"] == "RECIPIENT_NOT_FOUND"


# --- Caducitat (§14.5) ---------------------------------------------------------------------


def test_expires_at_midnight_seven_days_later(client: TestClient, seed: SeedData, clock: Clock) -> None:
    # SO-14: `req-02` és del 14/11 a les 19:30.
    clock.now = datetime(2026, 11, 20, 23, 59, 59, tzinfo=MADRID_TZ)
    before_midnight = next(item for item in _list(client) if item["id"] == "req-02")
    clock.now = datetime(2026, 11, 21, 0, 0, 0, tzinfo=MADRID_TZ)
    at_midnight = next(item for item in _list(client) if item["id"] == "req-02")

    assert before_midnight["status"] == "pending"
    assert at_midnight["status"] == "expired"
    assert before_midnight["expiresAt"] == at_midnight["expiresAt"] == "2026-11-21T00:00:00+01:00"


def test_expired_is_never_stored(client: TestClient, seed: SeedData, clock: Clock) -> None:
    # SO-15
    clock.now = datetime(2026, 11, 21, 0, 0, 0, tzinfo=MADRID_TZ)
    _list(client)

    # La `req-03` (rebuda, §15.8) també es veu caducada i continua desada com a pendent.
    assert {request.id: request.status for request in seed.money_requests} == {
        "req-01": "pending",
        "req-02": "pending",
        "req-03": "pending",
        "req-04": "rejected",
        "req-05": "paid",
        "req-06": "pending",
    }


def test_a_request_made_at_midnight_also_lasts_seven_calendar_days() -> None:
    # §14.5: a qualsevol hora del dia 14, caduca a les 00:00 del 21.
    created = datetime(2026, 11, 14, 0, 0, 0, tzinfo=MADRID_TZ)

    assert expires_at(created) == datetime(2026, 11, 21, 0, 0, 0, tzinfo=MADRID_TZ)


def test_expiry_keeps_madrid_midnight_across_a_time_change() -> None:
    # §14.5: el 25/10 canvia l'hora; la del 22/10 caduca a les 00:00 del 29, amb +01:00.
    created = datetime(2026, 10, 22, 12, 0, 0, tzinfo=MADRID_TZ)

    assert expires_at(created).isoformat() == "2026-10-29T00:00:00+01:00"


def test_only_pending_requests_can_expire() -> None:
    # §14.5: amb la US-16, una pagada continua pagada encara que passin els 7 dies.
    request = build_seed(now=T0).money_requests[0]
    request.status = "paid"

    assert current_status(request, T0 + timedelta(days=30)) == "paid"


# --- Cancel·lar (§14.4) --------------------------------------------------------------------


def test_cancel_deletes_a_pending_request(client: TestClient, seed: SeedData) -> None:
    # SO-16
    response = _cancel(client, "req-02")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert [item["id"] for item in _list(client)] == ["req-01"]


def test_cancelling_twice_is_not_found(client: TestClient, seed: SeedData) -> None:
    # SO-17
    _cancel(client, "req-02")

    response = _cancel(client, "req-02")

    assert response.status_code == 404
    assert response.json() == NOT_FOUND_BODY


def test_an_expired_request_cannot_be_cancelled(client: TestClient, seed: SeedData) -> None:
    # SO-18
    response = _cancel(client, "req-01")

    assert response.status_code == 422
    assert response.json() == {
        "code": "REQUEST_NOT_PENDING",
        "message": "Només es poden cancel·lar les sol·licituds pendents.",
    }
    assert "req-01" in [item["id"] for item in _list(client)]


def test_the_recipient_cannot_cancel_it(client: TestClient, seed: SeedData) -> None:
    # SO-19: el mateix cos que una que no existeix.
    response = _cancel(client, "req-02", headers=ALICIA)

    assert response.status_code == 404
    assert response.json() == NOT_FOUND_BODY
    assert next(item for item in _list(client) if item["id"] == "req-02")["status"] == "pending"


@pytest.mark.parametrize("request_id", ["req-99", "abc", "__x"])
def test_unknown_request_is_not_found(client: TestClient, seed: SeedData, request_id: str) -> None:
    # SO-20
    assert _cancel(client, request_id).json() == NOT_FOUND_BODY


def test_state_is_checked_at_the_moment_of_cancelling(client: TestClient, seed: SeedData, clock: Clock) -> None:
    # SO-21: a les 00:00 del dia que caduca, ja no és pendent.
    clock.now = datetime(2026, 11, 21, 0, 0, 0, tzinfo=MADRID_TZ)

    assert _cancel(client, "req-02").json()["code"] == "REQUEST_NOT_PENDING"


def test_the_id_of_a_cancelled_request_is_not_reused(client: TestClient, seed: SeedData) -> None:
    # SO-22: `req-02` cancel·lada, la nova és `req-07` (les rebudes del seed són `req-03` a `req-06`, §15.8).
    _cancel(client, "req-02")

    assert _create(client, DINNER).json()["id"] == "req-07"


# --- Tot o res, reinici -------------------------------------------------------------------


@pytest.mark.memory_only
def test_a_failed_notice_saves_no_request(
    client: TestClient, seed: SeedData, monkeypatch: pytest.MonkeyPatch
) -> None:
    # SO-23
    def fail(*args: object, **kwargs: object) -> None:
        raise RuntimeError("bústia fallida")

    before = _state(seed)
    monkeypatch.setattr(OutboxRepository, "add", fail)

    response = _create(client, DINNER)

    assert response.status_code == 500
    assert response.json()["code"] == "INTERNAL_ERROR"
    assert _state(seed) == before


@pytest.mark.memory_only
def test_reset_brings_back_the_seed_requests(client: TestClient) -> None:
    # SO-24
    _create(client, DINNER)

    client.post("/api/dev/reset")

    assert [item["id"] for item in _list(client)] == ["req-02", "req-01"]


@pytest.fixture
def strict_client(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    """App amb ALLOW_X_USER_ID=0, com al desplegament."""
    monkeypatch.setenv("ALLOW_X_USER_ID", "0")
    with TestClient(create_app()) as strict:
        yield strict


@pytest.mark.parametrize(
    ("method", "path"),
    [("GET", "/api/money-requests"), ("POST", "/api/money-requests"), ("POST", "/api/money-requests/req-02/cancel")],
)
def test_every_route_needs_a_session(strict_client: TestClient, method: str, path: str) -> None:
    # SO-25
    response = strict_client.request(method, path, json=DINNER if path == "/api/money-requests" else None)

    assert response.status_code == 401
    assert response.json()["code"] == "UNAUTHENTICATED"


def test_repository_orders_by_date_then_creation() -> None:
    # P4: dues del mateix moment, primer la creada més tard.
    seed = build_seed(now=T0)
    requests = MoneyRequestRepository(seed)
    first = requests.add(requester_id=2, recipient_id=3, amount=100, concept="A", created_at=T0)
    second = requests.add(requester_id=2, recipient_id=3, amount=100, concept="B", created_at=T0)

    assert [request.id for request in requests.list_by_requester(2)] == [second.id, first.id]
