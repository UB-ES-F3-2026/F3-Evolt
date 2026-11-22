"""Tests de T14.1: enviar diners a un altre usuari (US-14, docs/api.md §13.4, §13.5 i §13.9).

Cada test porta l'id de la prova de docs/proves-pagaments.md (EN-xx). Els imports
esperats surten del seed escrits tal qual: l'usuari 1 té `379521` i l'usuari 2, `0`.

Executar des de backend/:  python -m pytest tests/test_transfers.py
"""

import threading
import time
from collections.abc import Iterator
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from httpx import Response

from app.data.seed import (
    DEMO_IDENTIFIER,
    DEMO_USER_ID,
    EMPTY_IDENTIFIER,
    EMPTY_USER_ID,
    SEED_PASSWORD,
    SeedData,
    build_seed,
)
from app.main import create_app
from app.models import MADRID_TZ
from app.repositories import AccountRepository, MovementRepository, OutboxRepository, UserRepository
from app.services.errors import ApiError
from app.services.transfer_service import remaining_today, send_money

T0 = datetime(2026, 11, 15, 21, 15, tzinfo=MADRID_TZ)
DEMO = {"X-User-Id": str(DEMO_USER_ID)}
EMPTY = {"X-User-Id": str(EMPTY_USER_ID)}


def _seed(client: TestClient) -> SeedData:
    return client.app.state.seed


def _send(client: TestClient, body: dict[str, object], headers: dict[str, str] = DEMO) -> Response:
    return client.post("/api/transfers", json=body, headers=headers)


def _send_to(client: TestClient, to: str, amount: int, headers: dict[str, str] = DEMO) -> Response:
    return _send(client, {"toUserId": to, "amount": amount}, headers)


def _balance(client: TestClient, headers: dict[str, str]) -> int:
    return client.get("/api/home", headers=headers).json()["balance"]


def _state(seed: SeedData) -> tuple:
    """Saldos, moviments i bústia: el que un enviament rebutjat no pot canviar (EN-26)."""
    return (
        {user_id: account.balance for user_id, account in seed.accounts.items()},
        len(seed.movements),
        len(seed.outbox),
        seed.next_movement_number,
    )


def _service(seed: SeedData, sender_id: int, to: str, amount: int, now: datetime, concept: str | None = None):
    return send_money(
        sender_id,
        to,
        amount,
        concept,
        UserRepository(seed),
        AccountRepository(seed),
        MovementRepository(seed),
        OutboxRepository(seed),
        now=now,
    )


# --- Èxit (EN-01 a EN-08) -----------------------------------------------------------------


def test_en01_transfer_returns_balance_movement_and_recipient() -> None:
    seed = build_seed(now=T0)

    result = _service(seed, DEMO_USER_ID, "usr-02", 2000, T0, concept="El sopar de divendres")

    assert result.balance == 377521
    movement = result.movement
    assert (movement.amount, movement.concept, movement.date) == (2000, "El sopar de divendres", T0)
    assert (movement.type, movement.icon, movement.counterparty, movement.status) == (
        "expense",
        "transfer",
        "Usuari nou",
        "completed",
    )
    assert (result.recipient.name, result.recipient.username) == ("Usuari nou", "buit")


def test_en01_api_response_follows_the_contract(client: TestClient) -> None:
    response = _send(client, {"toUserId": "usr-02", "amount": 2000, "concept": "El sopar de divendres"})

    body = response.json()
    assert response.status_code == 201
    assert body["balance"] == 377521
    assert body["recipient"] == {"id": "usr-02", "name": "Usuari nou", "username": "buit"}
    assert {key: body["movement"][key] for key in ("amount", "concept", "type", "icon", "counterparty", "status")} == {
        "amount": 2000,
        "concept": "El sopar de divendres",
        "type": "expense",
        "icon": "transfer",
        "counterparty": "Usuari nou",
        "status": "completed",
    }


def test_en02_en03_home_of_both_users(client: TestClient) -> None:
    sent = _send(client, {"toUserId": "usr-02", "amount": 2000, "concept": "El sopar de divendres"}).json()

    demo_home = client.get("/api/home", headers=DEMO).json()
    empty_home = client.get("/api/home", headers=EMPTY).json()

    assert demo_home["balance"] == 377521
    assert demo_home["lastMovements"][0]["id"] == sent["movement"]["id"]
    assert empty_home["balance"] == 2000
    first = empty_home["lastMovements"][0]
    assert (first["concept"], first["amount"], first["type"], first["icon"], first["counterparty"]) == (
        "El sopar de divendres",
        2000,
        "income",
        "transfer",
        "Usuari demo",
    )


@pytest.mark.parametrize("body", [{}, {"concept": "   "}, {"concept": None}])
def test_en04_without_concept_movements_say_sent_and_received(client: TestClient, body: dict) -> None:
    response = _send(client, {"toUserId": "usr-02", "amount": 2000, **body})

    assert response.status_code == 201
    assert response.json()["movement"]["concept"] == "Transferència enviada"
    received = client.get("/api/home", headers=EMPTY).json()["lastMovements"][0]
    assert received["concept"] == "Transferència rebuda"


def test_en05_both_users_get_a_notice(client: TestClient) -> None:
    _send(client, {"toUserId": "usr-02", "amount": 2000, "concept": "El sopar de divendres"})

    [sent] = client.get("/api/dev/outbox", params={"to": DEMO_IDENTIFIER}).json()["messages"]
    [received] = client.get("/api/dev/outbox", params={"to": EMPTY_IDENTIFIER}).json()["messages"]

    assert (sent["type"], sent["text"], sent["channel"]) == (
        "transfer_sent",
        "Has enviat 20,00 € a Usuari nou.",
        "email",
    )
    assert (received["type"], received["text"], received["channel"]) == (
        "transfer_received",
        "Usuari demo t'ha enviat 20,00 €: El sopar de divendres.",
        "email",
    )
    assert "code" not in sent and "link" not in sent


def test_en06_en07_movements_list_filters_and_detail(client: TestClient) -> None:
    sent_id = _send(client, {"toUserId": "usr-02", "amount": 2000}).json()["movement"]["id"]
    received = client.get("/api/home", headers=EMPTY).json()["lastMovements"][0]

    expenses = client.get("/api/movements", params={"type": "expense"}, headers=DEMO).json()["items"]
    incomes = client.get("/api/movements", params={"type": "income"}, headers=EMPTY).json()["items"]
    by_name = client.get("/api/movements", params={"q": "usuari nou"}, headers=DEMO).json()["items"]

    assert expenses[0]["id"] == sent_id
    assert incomes[0]["id"] == received["id"]
    assert by_name[0]["id"] == sent_id
    sent_detail = client.get(f"/api/movements/{sent_id}", headers=DEMO).json()
    received_detail = client.get(f"/api/movements/{received['id']}", headers=EMPTY).json()
    assert sent_detail["status"] == received_detail["status"] == "completed"
    assert sent_detail["reference"] != received_detail["reference"]


@pytest.mark.memory_only
def test_en08_each_balance_is_still_the_sum_of_its_movements(client: TestClient) -> None:
    _send(client, {"toUserId": "usr-02", "amount": 2000})
    seed = _seed(client)

    for user_id, expected in ((DEMO_USER_ID, 377521), (EMPTY_USER_ID, 2000)):
        account = seed.accounts[user_id]
        total = sum(m.signed_amount for m in seed.movements if m.account_id == account.id)
        assert account.balance == total == expected


def test_en10_sending_the_whole_balance_leaves_zero(client: TestClient) -> None:
    assert _send_to(client, "usr-02", 5000).status_code == 201

    response = _send_to(client, "usr-01", 5000, headers=EMPTY)

    assert response.status_code == 201
    assert response.json()["balance"] == 0
    assert _balance(client, EMPTY) == 0


def test_en30_transfers_give_no_xp(client: TestClient) -> None:
    seed = _seed(client)
    xp_before = (seed.users[DEMO_USER_ID].xp, seed.users[EMPTY_USER_ID].xp)

    _send_to(client, "usr-02", 2000)

    assert (seed.users[DEMO_USER_ID].xp, seed.users[EMPTY_USER_ID].xp) == xp_before


def test_en31_reset_restores_balances_movements_and_outbox(client: TestClient) -> None:
    _send_to(client, "usr-02", 2000)

    assert client.post("/api/dev/reset").status_code in (200, 204)

    assert _balance(client, DEMO) == 379521
    assert _balance(client, EMPTY) == 0
    assert client.get("/api/dev/outbox").json() == {"messages": []}


# --- Límit diari (EN-09, EN-12 a EN-18) ----------------------------------------------------


def test_en09_limit_is_checked_even_with_enough_balance(client: TestClient) -> None:
    response = _send_to(client, "usr-02", 379521)

    assert response.status_code == 422
    assert response.json() == {
        "code": "TRANSFER_LIMIT_EXCEEDED",
        "message": "Has superat el límit diari d'enviament.",
        "details": {"remainingToday": 100000},
    }


def test_en12_reaching_exactly_1000_euros_is_allowed(client: TestClient) -> None:
    assert _send_to(client, "usr-02", 2000).status_code == 201
    assert _send_to(client, "usr-02", 98000).status_code == 201


def test_en13_one_cent_over_the_limit_is_rejected(client: TestClient) -> None:
    _send_to(client, "usr-02", 2000)
    _send_to(client, "usr-02", 98000)

    response = _send_to(client, "usr-03", 1)

    assert response.status_code == 422
    assert response.json()["details"] == {"remainingToday": 0}


@pytest.mark.memory_only
def test_en14_rejection_says_what_is_left_and_changes_nothing(client: TestClient) -> None:
    _send_to(client, "usr-02", 2000)
    before = _state(_seed(client))

    response = _send_to(client, "usr-02", 98001)

    assert response.status_code == 422
    assert response.json()["code"] == "TRANSFER_LIMIT_EXCEEDED"
    assert response.json()["details"] == {"remainingToday": 98000}
    assert _state(_seed(client)) == before


def test_en15_limit_is_per_madrid_calendar_day() -> None:
    seed = build_seed(now=T0)
    yesterday = T0 - timedelta(days=1)
    _service(seed, DEMO_USER_ID, "usr-02", 100000, yesterday)

    result = _service(seed, DEMO_USER_ID, "usr-02", 2000, T0)

    assert result.balance == 277521


def test_en16_en17_topup_and_transfer_limits_are_independent(client: TestClient) -> None:
    assert client.post("/api/topups", json={"amount": 50000}, headers=DEMO).status_code == 201
    assert client.post("/api/topups", json={"amount": 50000}, headers=DEMO).status_code == 201
    assert _send_to(client, "usr-02", 100000).status_code == 201

    other = client.post("/api/topups", json={"amount": 50000}, headers=EMPTY)

    assert other.status_code == 201  # enviar no gasta límit de recàrrega (EN-17)


def test_en18_received_money_does_not_count_for_the_limit(client: TestClient) -> None:
    assert _send_to(client, "usr-02", 100000).status_code == 201

    assert _send_to(client, "usr-03", 50000, headers=EMPTY).status_code == 201


# --- Errors (EN-11, EN-19 a EN-26) ---------------------------------------------------------


@pytest.mark.memory_only
def test_en11_more_than_the_balance_changes_nothing(client: TestClient) -> None:
    before = _state(_seed(client))

    response = _send_to(client, "usr-01", 100, headers=EMPTY)

    assert response.status_code == 422
    assert response.json() == {"code": "INSUFFICIENT_BALANCE", "message": "No tens prou saldo."}
    assert _state(_seed(client)) == before


@pytest.mark.memory_only
def test_en19_sending_to_myself_changes_nothing(client: TestClient) -> None:
    before = _state(_seed(client))

    response = _send_to(client, "usr-01", 2000)

    assert response.status_code == 422
    assert response.json() == {"code": "SELF_TRANSFER", "message": "No et pots enviar diners a tu mateix."}
    assert _state(_seed(client)) == before


@pytest.mark.parametrize("to", ["usr-99", "4", "huabin"])
def test_en20_unknown_recipient_is_not_found(client: TestClient, to: str) -> None:
    response = _send_to(client, to, 2000)

    assert response.status_code == 404
    assert response.json() == {"code": "RECIPIENT_NOT_FOUND", "message": "No hem trobat aquest destinatari."}


@pytest.mark.memory_only
def test_en21_pending_user_is_not_found(client: TestClient) -> None:
    response = client.post(
        "/api/auth/register",
        json={"identifier": "anna@x.com", "password": "Contrasenya1", "acceptedTerms": True},
    )
    assert response.status_code == 201
    pending = next(user for user in _seed(client).users.values() if user.identifier == "anna@x.com")

    assert _send_to(client, f"usr-{pending.id:02d}", 2000).json()["code"] == "RECIPIENT_NOT_FOUND"


@pytest.mark.parametrize("amount", [0, -100])
def test_en22_zero_or_negative_amount_is_invalid(client: TestClient, amount: int) -> None:
    response = _send_to(client, "usr-02", amount)

    assert response.status_code == 422
    assert response.json()["code"] == "INVALID_AMOUNT"


@pytest.mark.parametrize(
    "body",
    [
        {"toUserId": "usr-02", "amount": "2000"},
        {"toUserId": "usr-02", "amount": 20.0},
        {"toUserId": "usr-02"},
        {"amount": 2000},
        {"toUserId": 2, "amount": 2000},
        {"toUserId": "usr-02", "amount": 2000, "concept": "x" * 141},
    ],
)
def test_en23_badly_formed_body_is_a_validation_error(client: TestClient, body: dict) -> None:
    response = _send(client, body)

    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"


def test_en23_concept_of_140_characters_is_allowed(client: TestClient) -> None:
    response = _send(client, {"toUserId": "usr-02", "amount": 2000, "concept": "x" * 140})

    assert response.status_code == 201


@pytest.mark.parametrize(
    "to, amount, code",
    [("usr-99", 0, "RECIPIENT_NOT_FOUND"), ("usr-01", 0, "SELF_TRANSFER"), ("usr-01", 500000, "SELF_TRANSFER")],
)
def test_en24_validations_follow_the_contract_order(client: TestClient, to: str, amount: int, code: str) -> None:
    assert _send_to(client, to, amount).json()["code"] == code


def test_en25_amount_is_checked_before_the_balance(client: TestClient) -> None:
    assert _send_to(client, "usr-01", 0, headers=EMPTY).json()["code"] == "INVALID_AMOUNT"


# --- Tot o res i concurrència (EN-27 a EN-29) ----------------------------------------------


@pytest.mark.memory_only
@pytest.mark.parametrize(
    "repository, write, calls_before_failing",
    [
        (MovementRepository, "add", 1),  # el moviment de qui rep
        (AccountRepository, "set_balance", 0),  # el saldo de qui envia
        (AccountRepository, "set_balance", 1),  # el saldo de qui rep
        (OutboxRepository, "add", 0),  # l'avís a qui envia
        (OutboxRepository, "add", 1),  # l'avís a qui rep: el de qui envia també es treu
    ],
)
def test_en27_error_halfway_changes_nothing(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    repository: type,
    write: str,
    calls_before_failing: int,
) -> None:
    original = getattr(repository, write)
    calls = {"n": 0}

    def fail_after(self, *args: object, **kwargs: object):
        # Només falla una crida: les de desfer, que venen després, han de funcionar.
        calls["n"] += 1
        if calls["n"] == calls_before_failing + 1:
            raise RuntimeError("escriptura fallida")
        return original(self, *args, **kwargs)

    before = _state(_seed(client))
    monkeypatch.setattr(repository, write, fail_after)

    response = _send_to(client, "usr-02", 2000)

    assert response.status_code == 500
    assert response.json()["code"] == "INTERNAL_ERROR"
    assert _state(_seed(client)) == before


@pytest.mark.memory_only
def test_en28_simulated_error_changes_nothing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SIMULATE_ERROR_RATE", "100")

    with TestClient(create_app()) as client:
        before = _state(_seed(client))

        response = _send_to(client, "usr-02", 2000)

        assert response.status_code == 500
        assert _state(_seed(client)) == before


def test_en29_two_transfers_at_once_do_not_pass_the_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    # L'espera dins de la primera escriptura obre la finestra entre comprovar el límit i
    # escriure: sense el pany, tots dos enviaments passarien la comprovació.
    seed = build_seed(now=T0)
    _service(seed, DEMO_USER_ID, "usr-02", 60000, T0)
    original_add = MovementRepository.add

    def slow_add(self: MovementRepository, **kwargs: object):
        time.sleep(0.1)
        return original_add(self, **kwargs)

    monkeypatch.setattr(MovementRepository, "add", slow_add)
    barrier = threading.Barrier(2)
    outcomes: list[str] = []

    def send_at_once() -> None:
        barrier.wait()
        try:
            _service(seed, DEMO_USER_ID, "usr-02", 30000, T0)
            outcomes.append("ok")
        except ApiError as error:
            outcomes.append(error.code)

    threads = [threading.Thread(target=send_at_once) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert sorted(outcomes) == ["TRANSFER_LIMIT_EXCEEDED", "ok"]
    assert seed.accounts[DEMO_USER_ID].balance == 289521
    assert seed.accounts[EMPTY_USER_ID].balance == 90000


def test_en29_two_transfers_at_once_never_overdraw(monkeypatch: pytest.MonkeyPatch) -> None:
    seed = build_seed(now=T0)
    _service(seed, DEMO_USER_ID, "usr-02", 5000, T0)
    original_add = MovementRepository.add

    def slow_add(self: MovementRepository, **kwargs: object):
        time.sleep(0.1)
        return original_add(self, **kwargs)

    monkeypatch.setattr(MovementRepository, "add", slow_add)
    barrier = threading.Barrier(2)
    outcomes: list[str] = []

    def send_at_once() -> None:
        barrier.wait()
        try:
            _service(seed, EMPTY_USER_ID, "usr-03", 3000, T0)
            outcomes.append("ok")
        except ApiError as error:
            outcomes.append(error.code)

    threads = [threading.Thread(target=send_at_once) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert sorted(outcomes) == ["INSUFFICIENT_BALANCE", "ok"]
    assert seed.accounts[EMPTY_USER_ID].balance == 2000


# --- Límit que queda avui (EN-33 a EN-35) --------------------------------------------------


def test_en33_limit_of_the_seed(client: TestClient) -> None:
    response = client.get("/api/transfers/limit", headers=DEMO)

    assert response.status_code == 200
    assert response.json() == {"dailyLimit": 100000, "remainingToday": 100000}


def test_en34_limit_after_a_transfer_only_counts_what_was_sent(client: TestClient) -> None:
    _send_to(client, "usr-02", 2000)

    assert client.get("/api/transfers/limit", headers=DEMO).json()["remainingToday"] == 98000
    assert client.get("/api/transfers/limit", headers=EMPTY).json()["remainingToday"] == 100000


def test_en35_limit_reached_and_reset_next_day() -> None:
    seed = build_seed(now=T0)
    _service(seed, DEMO_USER_ID, "usr-02", 2000, T0)
    _service(seed, DEMO_USER_ID, "usr-02", 98000, T0)
    accounts, movements = AccountRepository(seed), MovementRepository(seed)
    midnight = datetime(2026, 11, 16, 0, 0, tzinfo=MADRID_TZ)

    assert remaining_today(DEMO_USER_ID, accounts, movements, T0) == 0
    assert remaining_today(DEMO_USER_ID, accounts, movements, midnight) == 100000


# --- Sessió (EN-32 i EN-36) ----------------------------------------------------------------


@pytest.fixture
def strict_client(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    """App amb ALLOW_X_USER_ID=0, com al desplegament des de la T03.5."""
    monkeypatch.setenv("ALLOW_X_USER_ID", "0")
    with TestClient(create_app()) as client:
        yield client


@pytest.mark.parametrize(
    "method, path",
    [("POST", "/api/transfers"), ("GET", "/api/transfers/limit")],
)
def test_en32_en36_routes_need_a_session(strict_client: TestClient, method: str, path: str) -> None:
    response = strict_client.request(method, path, json={"toUserId": "usr-02", "amount": 2000})

    assert response.status_code == 401
    assert response.json() == {"code": "UNAUTHENTICATED", "message": "Cal iniciar sessió."}


def test_en32_transfer_works_with_a_session(strict_client: TestClient) -> None:
    login = strict_client.post("/api/auth/login", json={"identifier": DEMO_IDENTIFIER, "password": SEED_PASSWORD})
    headers = {"Authorization": f"Bearer {login.json()['token']}"}

    response = strict_client.post("/api/transfers", json={"toUserId": "usr-02", "amount": 2000}, headers=headers)

    assert response.status_code == 201
    assert response.json()["balance"] == 377521
