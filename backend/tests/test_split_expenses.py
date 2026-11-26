"""Tests de T30.2: dividir una despesa (US-30, docs/api.md §17.2, §17.6 i §17.9).

Proves DD-01 a DD-20 de docs/proves-despeses.md. El seed es construeix a T0 i el
rellotge del servei es fixa amb `clock`. Els ids de les sol·licituds no s'escriuen
tal qual: es fan servir els `requestId` de la resposta.

Executar des de backend/:  python -m pytest tests/test_split_expenses.py
"""

from collections.abc import Iterator
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from httpx import Response

from app.data.seed import SeedData, build_seed
from app.main import create_app
from app.models import MADRID_TZ
from app.repositories import OutboxRepository
from app.services import split_expense_service

T0 = datetime(2026, 11, 15, 21, 15, 0, tzinfo=MADRID_TZ)
PASSWORD = "Platja2026"
IZAN, ALICIA, MARTI = "usr-05", "usr-03", "usr-08"
D0 = {
    "concept": "Sopar d'aniversari",
    "total": 6000,
    "myShare": 1500,
    "parts": [{"toUserId": IZAN, "amount": 1500}, {"toUserId": ALICIA, "amount": 1500}, {"toUserId": MARTI, "amount": 1500}],
}
EMAILS = {IZAN: "izan@evolt.test", ALICIA: "alicia@evolt.test", MARTI: "marti@evolt.test"}


@pytest.fixture
def seed(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> SeedData:
    """Seed a T0, sense cap despesa dividida, i el rellotge del servei a T0."""
    monkeypatch.setattr(split_expense_service, "now_madrid", lambda: T0)
    fixed = build_seed(now=T0)
    client.app.state.seed = fixed
    return fixed


def _split(client: TestClient, body: dict, headers: dict[str, str] | None = None) -> Response:
    return client.post("/api/split-expenses", json=body, headers=headers)


def _with(**changes: object) -> dict:
    return {**D0, **changes}


def _state(seed: SeedData) -> tuple:
    """El que una despesa rebutjada no pot canviar: despeses, sol·licituds, comptadors i bústia."""
    return (
        len(seed.split_expenses),
        seed.next_split_expense_number,
        [r.id for r in seed.money_requests],
        seed.next_money_request_number,
        len(seed.outbox),
    )


# --- Dividir (§17.2) ----------------------------------------------------------------------


def test_splitting_creates_one_request_per_participant(client: TestClient, seed: SeedData) -> None:
    # DD-01
    response = _split(client, D0)

    assert response.status_code == 201
    body = response.json()
    parts = body.pop("parts")
    assert body == {
        "id": "split-01",
        "concept": "Sopar d'aniversari",
        "total": 6000,
        "myShare": 1500,
        "createdAt": "2026-11-15T21:15:00+01:00",
        "status": "pending",
        "people": 4,
        "paidCount": 0,
        "pendingAmount": 4500,
    }
    assert [(p["to"]["id"], p["amount"], p["status"]) for p in parts] == [
        (IZAN, 1500, "pending"),
        (ALICIA, 1500, "pending"),
        (MARTI, 1500, "pending"),
    ]
    assert set(parts[0]) == {"requestId", "to", "amount", "status"}


def test_the_requests_are_saved_and_linked_to_the_split(client: TestClient, seed: SeedData) -> None:
    # DD-02
    ids = [p["requestId"] for p in _split(client, D0).json()["parts"]]

    saved = {r.id: r for r in seed.money_requests}
    for request_id, user in zip(ids, (5, 3, 8), strict=True):
        request = saved[request_id]
        assert (request.requester_id, request.recipient_id, request.amount) == (1, user, 1500)
        assert (request.concept, request.created_at, request.status) == ("Sopar d'aniversari", T0, "pending")
        assert request.split_id == "split-01"


def test_every_participant_gets_a_notice(client: TestClient, seed: SeedData) -> None:
    # DD-03
    _split(client, D0)

    for email in EMAILS.values():
        message = client.get("/api/dev/outbox", params={"to": email}).json()["messages"][0]
        assert (message["type"], message["text"]) == (
            "money_request",
            "Usuari demo et demana 15,00 €: Sopar d'aniversari.",
        )


def test_splitting_moves_no_money(client: TestClient, seed: SeedData) -> None:
    # DD-04
    def snapshot() -> list:
        return [
            client.get(path, headers={"X-User-Id": user}).json()
            for user in ("1", "3", "5", "8")
            for path in ("/api/home", "/api/movements")
        ]

    before = snapshot()

    _split(client, D0)

    assert snapshot() == before


def test_split_requests_do_not_appear_alone_in_the_sent_list(client: TestClient, seed: SeedData) -> None:
    # DD-05 (P104)
    _split(client, D0)

    items = client.get("/api/money-requests").json()["items"]

    assert [item["id"] for item in items] == ["req-02", "req-01"]


def test_equal_parts_leave_the_spare_cents_to_me(client: TestClient, seed: SeedData) -> None:
    # DD-06: 100,00 € entre 3 → 33,33 € cada participant i 33,34 € per a mi.
    body = _with(total=10000, myShare=3334, parts=[{"toUserId": IZAN, "amount": 3333}, {"toUserId": ALICIA, "amount": 3333}])

    assert _split(client, body).status_code == 201


@pytest.mark.parametrize("parts", [[], [{"toUserId": f"usr-{n}", "amount": 100} for n in range(11, 21)]])
def test_one_to_nine_participants(client: TestClient, seed: SeedData, parts: list) -> None:
    # DD-07
    response = _split(client, _with(total=1500 + 100 * len(parts), parts=parts))

    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"


def test_a_participant_cannot_be_repeated(client: TestClient, seed: SeedData) -> None:
    # DD-08
    body = _with(total=4500, parts=[{"toUserId": IZAN, "amount": 1500}, {"toUserId": IZAN, "amount": 1500}])

    assert _split(client, body).json()["code"] == "VALIDATION_ERROR"


def test_unknown_or_pending_participant_saves_nothing(client: TestClient, seed: SeedData) -> None:
    # DD-09: usr-99 i un compte pendent de verificar (usr-09).
    client.post("/api/auth/register", json={"identifier": "anna@x.com", "password": PASSWORD, "acceptedTerms": True})
    for unknown in ("usr-99", "usr-09"):
        before = _state(seed)
        body = _with(parts=[{"toUserId": IZAN, "amount": 1500}, {"toUserId": ALICIA, "amount": 1500}, {"toUserId": unknown, "amount": 1500}])

        response = _split(client, body)

        assert response.status_code == 404
        assert response.json()["code"] == "RECIPIENT_NOT_FOUND"
        assert _state(seed) == before


def test_i_cannot_be_a_participant(client: TestClient, seed: SeedData) -> None:
    # DD-10
    body = _with(parts=[{"toUserId": IZAN, "amount": 1500}, {"toUserId": ALICIA, "amount": 1500}, {"toUserId": "usr-01", "amount": 1500}])

    assert _split(client, body).json()["code"] == "SELF_REQUEST"


@pytest.mark.parametrize(
    ("total", "code"),
    [(0, "INVALID_AMOUNT"), (-100, "INVALID_AMOUNT"), (100000001, "AMOUNT_OVER_LIMIT")],
)
def test_total_between_one_cent_and_one_million(client: TestClient, seed: SeedData, total: int, code: str) -> None:
    # DD-11
    assert _split(client, _with(total=total)).json()["code"] == code


def test_one_million_euros_fits(client: TestClient, seed: SeedData) -> None:
    # DD-11
    body = _with(total=100000000, myShare=99995500)

    assert _split(client, body).status_code == 201


@pytest.mark.parametrize("concept", ["", "   ", "x" * 141])
def test_concept_must_have_1_to_140_characters(client: TestClient, seed: SeedData, concept: str) -> None:
    # DD-12
    assert _split(client, _with(concept=concept)).json()["code"] == "INVALID_CONCEPT"


@pytest.mark.parametrize(
    "body",
    [
        _with(total=4500, parts=[{"toUserId": IZAN, "amount": 1500}, {"toUserId": ALICIA, "amount": 1500}, {"toUserId": MARTI, "amount": 0}]),
        _with(total=4500, myShare=0),
    ],
)
def test_every_part_must_be_more_than_zero(client: TestClient, seed: SeedData, body: dict) -> None:
    # DD-13 (P101): també la meva.
    response = _split(client, body)

    assert response.status_code == 422
    assert response.json() == {"code": "INVALID_SHARE", "message": "Cada part ha de ser més gran que 0."}


def test_parts_must_add_up_to_the_total(client: TestClient, seed: SeedData) -> None:
    # DD-14
    body = _with(parts=[{"toUserId": IZAN, "amount": 1500}, {"toUserId": ALICIA, "amount": 1500}, {"toUserId": MARTI, "amount": 1000}])

    response = _split(client, body)

    assert response.json() == {"code": "SHARES_DO_NOT_MATCH", "message": "La suma de les parts ha de ser igual al total."}


def test_validation_order(client: TestClient, seed: SeedData) -> None:
    # DD-15
    body = _with(total=0, parts=[{"toUserId": "usr-01", "amount": 1500}])

    assert _split(client, body).json()["code"] == "SELF_REQUEST"


@pytest.mark.parametrize(
    "body",
    [
        _with(total="6000"),
        {key: value for key, value in D0.items() if key != "myShare"},
        _with(parts={"toUserId": IZAN, "amount": 1500}),
    ],
)
def test_badly_formed_body_is_a_validation_error(client: TestClient, seed: SeedData, body: dict) -> None:
    # DD-16
    assert _split(client, body).json()["code"] == "VALIDATION_ERROR"


@pytest.mark.memory_only
def test_a_failed_notice_saves_nothing(client: TestClient, seed: SeedData, monkeypatch: pytest.MonkeyPatch) -> None:
    # DD-17: falla l'avís del segon participant; el primer ja s'havia desat i es treu.
    original_add = OutboxRepository.add
    calls = []

    def fail_on_second(self: OutboxRepository, message: object) -> None:
        calls.append(message)
        if len(calls) == 2:
            raise RuntimeError("bústia fallida")
        original_add(self, message)

    before = _state(seed)
    monkeypatch.setattr(OutboxRepository, "add", fail_on_second)

    response = _split(client, D0)

    assert response.status_code == 500
    assert response.json()["code"] == "INTERNAL_ERROR"
    assert _state(seed) == before


def test_a_split_request_cannot_be_cancelled(client: TestClient, seed: SeedData) -> None:
    # DD-18 (P105)
    request_id = _split(client, D0).json()["parts"][0]["requestId"]

    response = client.post(f"/api/money-requests/{request_id}/cancel")

    assert response.status_code == 404
    assert response.json()["code"] == "REQUEST_NOT_FOUND"
    assert next(r for r in seed.money_requests if r.id == request_id).status == "pending"


@pytest.mark.memory_only
def test_reset_removes_the_splits(client: TestClient) -> None:
    # DD-19
    _split(client, D0)

    client.post("/api/dev/reset")

    assert client.app.state.seed.split_expenses == []


@pytest.fixture
def strict_client(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    """App amb ALLOW_X_USER_ID=0, com al desplegament."""
    monkeypatch.setenv("ALLOW_X_USER_ID", "0")
    with TestClient(create_app()) as strict:
        yield strict


def test_splitting_needs_a_session(strict_client: TestClient) -> None:
    # DD-20
    response = strict_client.post("/api/split-expenses", json=D0)

    assert response.status_code == 401
    assert response.json()["code"] == "UNAUTHENTICATED"
