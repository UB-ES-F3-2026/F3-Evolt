"""Tests de T12.2: dades del compte i transferència d'un altre banc (US-12, docs/api.md §16).

Proves IB-01 a IB-20 de docs/proves-compte.md. Els imports esperats surten del seed
escrits tal qual: l'usuari 1 té `379521`.

Executar des de backend/:  python -m pytest tests/test_account.py
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
from app.services import account_service
from app.services.account_service import iban_for, user_id_for_iban

T0 = datetime(2026, 11, 15, 21, 15, 0, tzinfo=MADRID_TZ)
PASSWORD = "Platja2026"
DEMO_IBAN = "ES9121000418450200051332"
MARIA = {"iban": "ES91 2100 0418 4502 0005 1332", "amount": 12000, "payer": "Maria Puig"}
# Taula de §16.2.
SEED_IBANS = {
    1: "ES9121000418450200051332",
    2: "ES2121000418410200051333",
    3: "ES0221000418440200051334",
    4: "ES5321000418490200051335",
    5: "ES1021000418430200051336",
    6: "ES6121000418480200051337",
    7: "ES1821000418420200051338",
    8: "ES6921000418470200051339",
}
_CCC_WEIGHTS = (1, 2, 4, 8, 5, 10, 9, 7, 3, 6)


@pytest.fixture
def seed(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> SeedData:
    """Seed a T0, amb el rellotge del servei fixat a T0."""
    monkeypatch.setattr(account_service, "now_madrid", lambda: T0)
    fixed = build_seed(now=T0)
    client.app.state.seed = fixed
    return fixed


def _as(user_id: int) -> dict[str, str]:
    return {"X-User-Id": str(user_id)}


def _account(client: TestClient, user_id: int = 1) -> dict:
    response = client.get("/api/account", headers=_as(user_id))
    assert response.status_code == 200
    return response.json()


def _incoming(client: TestClient, body: dict) -> Response:
    return client.post("/api/dev/incoming-transfers", json=body)


def _register(client: TestClient, identifier: str) -> None:
    response = client.post(
        "/api/auth/register", json={"identifier": identifier, "password": PASSWORD, "acceptedTerms": True}
    )
    assert response.status_code == 201


def _register_and_verify(client: TestClient, identifier: str) -> None:
    _register(client, identifier)
    code = client.get("/api/dev/outbox", params={"to": identifier}).json()["messages"][0]["code"]
    assert client.post("/api/auth/verify", json={"identifier": identifier, "code": code}).status_code == 200


def _state(seed: SeedData) -> tuple:
    return ({user_id: account.balance for user_id, account in seed.accounts.items()}, len(seed.movements), len(seed.outbox))


def _ccc_ok(digits: str, control: str) -> bool:
    rest = 11 - sum(int(digit) * weight for digit, weight in zip(digits, _CCC_WEIGHTS, strict=True)) % 11
    return str({11: 0, 10: 1}.get(rest, rest)) == control


# --- Dades del compte (§16.1 i §16.2) ------------------------------------------------------


def test_the_demo_user_has_the_mockup_iban(client: TestClient, seed: SeedData) -> None:
    # IB-01
    assert _account(client) == {"iban": DEMO_IBAN, "bic": "EVOLESB1XXX", "holder": "Usuari demo"}


def test_the_account_has_only_iban_bic_and_holder(client: TestClient, seed: SeedData) -> None:
    # IB-02
    assert set(_account(client)) == {"iban", "bic", "holder"}


def test_every_seed_user_has_a_different_valid_iban(client: TestClient, seed: SeedData) -> None:
    # IB-03: 24 caràcters, dígits del CCC correctes i residu 1 entre 97.
    ibans = {user_id: _account(client, user_id)["iban"] for user_id in SEED_IBANS}

    assert ibans == SEED_IBANS
    for iban in ibans.values():
        assert len(iban) == 24
        assert _ccc_ok("00" + iban[4:12], iban[12]) and _ccc_ok(iban[14:], iban[13])
        assert int(iban[4:] + "1428" + iban[2:4]) % 97 == 1


def test_the_iban_never_changes(client: TestClient, seed: SeedData) -> None:
    # IB-04
    first = _account(client)["iban"]

    assert _account(client)["iban"] == first
    client.post("/api/dev/reset")
    assert _account(client)["iban"] == first


def test_a_new_user_gets_an_iban_with_the_same_rule(client: TestClient, seed: SeedData) -> None:
    # IB-05 i IB-06: usr-09, sense nom, té de titular l'@usuari.
    _register_and_verify(client, "anna@x.com")

    assert _account(client, 9) == {"iban": "ES9621000418430200051340", "bic": "EVOLESB1XXX", "holder": "@anna"}


@pytest.fixture
def strict_client(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    """App amb ALLOW_X_USER_ID=0, com al desplegament."""
    monkeypatch.setenv("ALLOW_X_USER_ID", "0")
    with TestClient(create_app()) as strict:
        yield strict


def test_the_account_needs_a_session(strict_client: TestClient) -> None:
    # IB-07
    response = strict_client.get("/api/account")

    assert response.status_code == 401
    assert response.json()["code"] == "UNAUTHENTICATED"


def test_iban_rule_round_trip() -> None:
    # §16.5: d'un IBAN es torna al seu usuari, i un IBAN que no quadra no és de ningú.
    assert [user_id_for_iban(iban_for(user_id)) for user_id in range(1, 50)] == list(range(1, 50))
    assert user_id_for_iban("es91 2100 0418 4502 0005 1332") == 1
    assert user_id_for_iban("ES9221000418450200051332") is None
    assert user_id_for_iban("ES0000000000000000000000") is None


# --- Transferència d'un altre banc (§16.3 i §16.4) -----------------------------------------


def test_an_incoming_transfer_adds_to_the_balance(client: TestClient, seed: SeedData) -> None:
    # IB-08
    response = _incoming(client, MARIA)

    assert response.status_code == 201
    assert response.json() == {
        "balance": 391521,
        "movement": {
            "id": "mov-31",
            "amount": 12000,
            "concept": "Transferència rebuda · Maria Puig",
            "date": "2026-11-15T21:15:00+01:00",
            "type": "income",
            "icon": "transfer",
            "counterparty": "Maria Puig",
            "status": "completed",
            "reference": "EVT-000031",
        },
    }


def test_the_transfer_is_first_at_home_and_in_movements(client: TestClient, seed: SeedData) -> None:
    # IB-09
    _incoming(client, MARIA)

    home = client.get("/api/home", headers=_as(1)).json()
    incomes = client.get("/api/movements", params={"type": "income"}, headers=_as(1)).json()["items"]

    assert home["balance"] == 391521
    assert home["lastMovements"][0]["concept"] == "Transferència rebuda · Maria Puig"
    assert incomes[0]["id"] == "mov-31"


def test_the_recipient_gets_a_notice(client: TestClient, seed: SeedData) -> None:
    # IB-10
    _incoming(client, MARIA)

    message = client.get("/api/dev/outbox", params={"to": "demo@evolt.test"}).json()["messages"][0]

    assert message == {
        "to": "demo@evolt.test",
        "channel": "email",
        "type": "incoming_transfer",
        "text": "Has rebut 120,00 € de Maria Puig.",
        "date": "2026-11-15T21:15:00+01:00",
    }


def test_the_iban_can_be_lowercase_without_spaces(client: TestClient, seed: SeedData) -> None:
    # IB-11
    assert _incoming(client, {**MARIA, "iban": DEMO_IBAN.lower()}).status_code == 201


@pytest.mark.parametrize("iban", ["ES9621000418430200051340", "ES0000000000000000000000"])
def test_an_iban_of_nobody_is_not_found(client: TestClient, seed: SeedData, iban: str) -> None:
    # IB-12: el de l'usr-09, que encara no existeix, i un que no és d'Evolt.
    before = _state(seed)

    response = _incoming(client, {**MARIA, "iban": iban})

    assert response.status_code == 404
    assert response.json()["code"] == "RECIPIENT_NOT_FOUND"
    assert _state(seed) == before


def test_a_pending_user_cannot_receive(client: TestClient, seed: SeedData) -> None:
    # IB-13: usr-09 registrat però sense verificar.
    _register(client, "anna@x.com")

    response = _incoming(client, {**MARIA, "iban": iban_for(9)})

    assert response.status_code == 404
    assert response.json()["code"] == "RECIPIENT_NOT_FOUND"


@pytest.mark.parametrize(
    ("amount", "status", "code"),
    [
        (0, 422, "INVALID_AMOUNT"),
        (-100, 422, "INVALID_AMOUNT"),
        (100000000, 201, None),
        (100000001, 422, "AMOUNT_OVER_LIMIT"),
    ],
)
def test_amount_between_one_cent_and_one_million(
    client: TestClient, seed: SeedData, amount: int, status: int, code: str | None
) -> None:
    # IB-14
    response = _incoming(client, {**MARIA, "amount": amount})

    assert response.status_code == status
    if code:
        assert response.json()["code"] == code


@pytest.mark.parametrize("payer", ["", "   ", "x" * 71])
def test_the_payer_must_have_1_to_70_characters(client: TestClient, seed: SeedData, payer: str) -> None:
    # IB-15
    response = _incoming(client, {**MARIA, "payer": payer})

    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"


def test_the_payer_is_trimmed_and_70_characters_fit(client: TestClient, seed: SeedData) -> None:
    # IB-15
    assert _incoming(client, {**MARIA, "payer": "x" * 70}).status_code == 201
    response = _incoming(client, {**MARIA, "payer": "  Maria Puig  "})

    assert response.json()["movement"]["counterparty"] == "Maria Puig"


@pytest.mark.parametrize(
    "body",
    [
        {"amount": 12000, "payer": "Maria Puig"},
        {**MARIA, "amount": "12000"},
        {**MARIA, "amount": 120.5},
    ],
)
def test_badly_formed_body_is_a_validation_error(client: TestClient, seed: SeedData, body: dict) -> None:
    # IB-16
    response = _incoming(client, body)

    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"


def test_receiving_counts_for_no_limit_and_gives_no_xp(client: TestClient, seed: SeedData) -> None:
    # IB-17
    xp_before = seed.users[1].xp

    _incoming(client, MARIA)

    assert client.get("/api/transfers/limit", headers=_as(1)).json()["remainingToday"] == 100000
    assert seed.users[1].xp == xp_before


@pytest.mark.memory_only
def test_a_failed_notice_changes_nothing(client: TestClient, seed: SeedData, monkeypatch: pytest.MonkeyPatch) -> None:
    # IB-18
    def fail(*args: object, **kwargs: object) -> None:
        raise RuntimeError("bústia fallida")

    before = _state(seed)
    monkeypatch.setattr(OutboxRepository, "add", fail)

    response = _incoming(client, MARIA)

    assert response.status_code == 500
    assert _state(seed) == before


def test_without_dev_routes_the_route_does_not_exist(monkeypatch: pytest.MonkeyPatch) -> None:
    # IB-19: GET /api/account continua funcionant.
    monkeypatch.setenv("ENABLE_DEV_ROUTES", "false")
    with TestClient(create_app()) as no_dev:
        missing = no_dev.post("/api/dev/route-that-does-not-exist", json=MARIA)
        response = no_dev.post("/api/dev/incoming-transfers", json=MARIA)
        assert (response.status_code, response.json()) == (missing.status_code, missing.json())
        assert no_dev.get("/api/account", headers=_as(1)).status_code == 200


@pytest.mark.memory_only
def test_reset_removes_the_incoming_transfer(client: TestClient) -> None:
    # IB-20
    _incoming(client, MARIA)

    client.post("/api/dev/reset")

    assert client.get("/api/home", headers=_as(1)).json()["balance"] == 379521
