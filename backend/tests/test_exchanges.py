"""Tests de T27.1: canvi de divisa entre dos comptes de l'usuari (docs/api.md §12.7 i §12.8).

Proves CV-01 a CV-23 de docs/proves-multidivisa.md, més la regla de la comissió i
el repositori. Els valors esperats són els del document, escrits tal qual: el seed
dona `379521` a l'usuari 1.

Executar des de backend/:  python -m pytest tests/test_exchanges.py
"""

import threading
import time
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from app.data.seed import DEMO_IDENTIFIER, DEMO_USER_ID, SEED_PASSWORD, SeedData, build_seed
from app.main import create_app
from app.models import MADRID_TZ, commission, convert, reaches_one_unit
from app.models.currency import minimum_commission
from app.repositories import AccountRepository, MovementRepository, SubaccountRepository
from app.repositories.atomic import MemoryAtomic
from app.services.errors import INSUFFICIENT_BALANCE, ApiError
from app.services.exchange_service import exchange

SAME_CURRENCY = {"code": "SAME_CURRENCY", "message": "Origen i destí no poden ser el mateix subcompte."}
NOT_FOUND = {"code": "SUBACCOUNT_NOT_FOUND", "message": "No s'ha trobat el subcompte."}
INVALID_AMOUNT = {"code": "INVALID_AMOUNT", "message": "L'import ha de ser més gran que 0."}
TOO_SMALL = {"code": "AMOUNT_TOO_SMALL", "message": "L'import és massa petit per canviar."}
NO_BALANCE = {"code": "INSUFFICIENT_BALANCE", "message": "No tens prou saldo."}


def _seed(client: TestClient) -> SeedData:
    return client.app.state.seed


def _create(client: TestClient, currency: str):
    return client.post("/api/subaccounts", json={"currency": currency})


def _exchange(client: TestClient, from_currency, to_currency, amount, headers: dict[str, str] | None = None):
    body = {"fromCurrency": from_currency, "toCurrency": to_currency, "amount": amount}
    return client.post("/api/exchanges", json=body, headers=headers)


def _balances(client: TestClient) -> dict[str, int]:
    return {item["currency"]: item["balance"] for item in client.get("/api/subaccounts").json()["items"]}


def _state(seed: SeedData):
    """Estat que un canvi fallit no pot canviar, comptadors inclosos."""
    return (
        {user_id: account.balance for user_id, account in seed.accounts.items()},
        {sub.id: sub.balance for sub in seed.subaccounts},
        [movement.id for movement in seed.movements],
        [entry.id for entry in seed.subaccount_movements],
        seed.next_movement_number,
        seed.next_movement_seq,
        seed.next_subaccount_movement_number,
    )


# --- Canvi correcte (§12.7) ---------------------------------------------------------------


def test_cv01_euros_to_dollars(client: TestClient) -> None:
    _create(client, "USD")  # DV-03

    response = _exchange(client, "EUR", "USD", 10000)

    assert response.status_code == 201
    assert response.json() == {
        "from": {"id": "main", "currency": "EUR", "balance": 369371, "isMain": True, "rateBps": 10000},
        "to": {"id": "sub-01", "currency": "USD", "balance": 10961, "isMain": False, "rateBps": 9123},
        "amount": 10000,
        "commission": 150,
        "received": 10961,
    }


def test_cv02_the_total_goes_down_by_the_commission(client: TestClient) -> None:
    _create(client, "USD")
    _exchange(client, "EUR", "USD", 10000)  # CV-01

    body = client.get("/api/subaccounts").json()

    assert [(item["id"], item["balance"]) for item in body["items"]] == [("main", 369371), ("sub-01", 10961)]
    assert body["totalInEuros"] == 379371


def test_cv03_the_euro_movement_is_at_home_and_in_the_list(client: TestClient) -> None:
    _create(client, "USD")
    _exchange(client, "EUR", "USD", 10000)  # CV-01

    assert client.get("/api/home").json()["balance"] == 369371
    first = client.get("/api/movements").json()["items"][0]
    assert first["id"] == "mov-31"
    assert first["concept"] == "Canvi EUR → USD"
    assert first["type"] == "expense"
    assert first["amount"] == 10150
    assert first["icon"] == "transfer"
    assert first["counterparty"] is None
    assert first["status"] == "completed"
    assert first["reference"] == "EVT-000031"


def test_cv04_the_dollar_movement_is_in_its_history(client: TestClient) -> None:
    _create(client, "USD")
    _exchange(client, "EUR", "USD", 10000)  # CV-01

    items = client.get("/api/subaccounts/sub-01/movements").json()["items"]

    assert [(e["id"], e["amount"], e["concept"], e["type"]) for e in items] == [
        ("smov-01", 10961, "Canvi EUR → USD", "income")
    ]


def test_cv05_the_minimum_commission(client: TestClient) -> None:
    _create(client, "USD")

    response = _exchange(client, "EUR", "USD", 1000)

    assert response.status_code == 201
    assert response.json()["commission"] == 50
    assert response.json()["received"] == 1096
    assert _balances(client)["EUR"] == 378471


def test_cv06_there_and_back_the_us26_example(client: TestClient) -> None:
    _create(client, "USD")

    there = _exchange(client, "EUR", "USD", 28970).json()
    back = _exchange(client, "USD", "EUR", 31286).json()

    assert (there["commission"], there["received"], there["to"]["balance"]) == (435, 31755, 31755)
    assert (back["commission"], back["received"]) == (469, 28542)
    assert _balances(client) == {"EUR": 378658, "USD": 0}


def test_cv11_one_euro_cent_to_yen(client: TestClient) -> None:
    _create(client, "JPY")  # DV-11

    response = _exchange(client, "EUR", "JPY", 1)

    assert response.status_code == 201
    assert (response.json()["received"], response.json()["commission"]) == (2, 50)
    assert _balances(client)["EUR"] == 379470


def test_cv13_the_whole_balance_with_the_commission(client: TestClient) -> None:
    _create(client, "USD")
    _exchange(client, "EUR", "USD", 10000)  # CV-01

    response = _exchange(client, "USD", "EUR", 10799)

    assert response.status_code == 201
    assert (response.json()["commission"], response.json()["received"]) == (162, 9852)
    assert _balances(client) == {"EUR": 379223, "USD": 0}


def test_cv14_leaves_one_cent(client: TestClient) -> None:
    _create(client, "USD")
    _exchange(client, "EUR", "USD", 10000)  # CV-01

    response = _exchange(client, "USD", "EUR", 10798)

    assert response.status_code == 201
    assert (response.json()["commission"], response.json()["received"]) == (162, 9851)
    assert _balances(client) == {"EUR": 379222, "USD": 1}


def test_cv15_yen_have_no_decimals(client: TestClient) -> None:
    _create(client, "JPY")

    response = _exchange(client, "EUR", "JPY", 1000)

    assert (response.json()["received"], response.json()["commission"]) == (1754, 50)
    body = client.get("/api/subaccounts").json()
    assert [(item["currency"], item["balance"]) for item in body["items"]] == [("EUR", 378471), ("JPY", 1754)]
    assert body["totalInEuros"] == 379471


def test_cv16_the_minimum_commission_in_yen(client: TestClient) -> None:
    _create(client, "JPY")
    _exchange(client, "EUR", "JPY", 1000)  # CV-15

    response = _exchange(client, "JPY", "EUR", 100)

    assert response.status_code == 201
    assert (response.json()["commission"], response.json()["received"]) == (88, 57)
    assert _balances(client) == {"EUR": 378528, "JPY": 1566}


def test_cv21_an_exchange_does_not_count_for_the_topup_limit(client: TestClient) -> None:
    _create(client, "USD")
    _exchange(client, "EUR", "USD", 10000)  # CV-01

    first = client.post("/api/topups", json={"amount": 50000})
    second = client.post("/api/topups", json={"amount": 50000})

    assert (first.status_code, second.status_code) == (201, 201)


def test_cv22_without_the_euro_there_is_no_main_account_movement(client: TestClient) -> None:
    _create(client, "GBP")  # DV-12
    _create(client, "USD")
    _exchange(client, "EUR", "GBP", 10000)

    response = _exchange(client, "GBP", "USD", 1000)

    assert response.status_code == 201
    euro_exchanges = [m["concept"] for m in client.get("/api/movements").json()["items"] if "Canvi" in m["concept"]]
    assert euro_exchanges == ["Canvi EUR → GBP"]
    usd_history = client.get("/api/subaccounts/sub-02/movements").json()["items"]
    assert [(e["concept"], e["type"]) for e in usd_history] == [("Canvi GBP → USD", "income")]


def test_balances_are_still_the_sum_of_their_movements(client: TestClient) -> None:
    # Invariant de §12.11: la comissió va dins del moviment d'origen.
    _create(client, "USD")
    _exchange(client, "EUR", "USD", 28970)
    _exchange(client, "USD", "EUR", 10000)

    usd_history = client.get("/api/subaccounts/sub-01/movements").json()["items"]
    signed = sum(e["amount"] if e["type"] == "income" else -e["amount"] for e in usd_history)
    assert signed == _balances(client)["USD"]
    seed = _seed(client)
    account = seed.accounts[DEMO_USER_ID]
    assert account.balance == sum(m.signed_amount for m in seed.movements if m.account_id == account.id)


# --- Errors (§12.7, ordre de les validacions) ---------------------------------------------


def test_cv07_same_currency(client: TestClient) -> None:
    _create(client, "USD")
    before = _state(_seed(client))

    response = _exchange(client, "EUR", "EUR", 1000)

    assert response.status_code == 422
    assert response.json() == SAME_CURRENCY
    assert _state(_seed(client)) == before


@pytest.mark.parametrize("to_currency", ["USD", "BTC"])
def test_cv08_a_currency_without_an_account(client: TestClient, to_currency: str) -> None:
    response = _exchange(client, "EUR", to_currency, 1000)

    assert response.status_code == 404
    assert response.json() == NOT_FOUND


def test_cv08_another_users_subaccount_is_not_yours(client: TestClient) -> None:
    _create(client, "USD")  # de l'usuari 1

    response = _exchange(client, "EUR", "USD", 1000, headers={"X-User-Id": "2"})

    assert response.status_code == 404
    assert response.json() == NOT_FOUND


@pytest.mark.parametrize("amount", [0, -100])
def test_cv09_zero_or_negative_amount(client: TestClient, amount: int) -> None:
    _create(client, "USD")

    response = _exchange(client, "EUR", "USD", amount)

    assert response.status_code == 422
    assert response.json() == INVALID_AMOUNT


def test_cv10_one_dollar_cent_does_not_reach_one_euro_cent(client: TestClient) -> None:
    _create(client, "USD")
    _exchange(client, "EUR", "USD", 10000)  # CV-01
    before = _state(_seed(client))

    response = _exchange(client, "USD", "EUR", 1)

    assert response.status_code == 422
    assert response.json() == TOO_SMALL
    assert _state(_seed(client)) == before


def test_cv12_the_whole_balance_leaves_no_room_for_the_commission(client: TestClient) -> None:
    _create(client, "USD")
    before = _state(_seed(client))

    response = _exchange(client, "EUR", "USD", 379521)

    assert response.status_code == 422
    assert response.json() == NO_BALANCE
    assert _state(_seed(client)) == before


@pytest.mark.parametrize(
    "body",
    [
        {"fromCurrency": "EUR", "toCurrency": "USD"},
        {"fromCurrency": "EUR", "toCurrency": "USD", "amount": "1000"},
        {"fromCurrency": "EUR", "toCurrency": "USD", "amount": 10.5},
        {"fromCurrency": 978, "toCurrency": "USD", "amount": 1000},
        {"fromCurrency": "EUR", "toCurrency": "USD", "amount": True},
    ],
)
def test_cv17_badly_formed_body(client: TestClient, body: dict[str, object]) -> None:
    _create(client, "USD")

    response = client.post("/api/exchanges", json=body)

    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"


def test_cv18_currencies_are_checked_before_the_amount(client: TestClient) -> None:
    _create(client, "USD")

    response = _exchange(client, "EUR", "EUR", 0)

    assert response.status_code == 422
    assert response.json() == SAME_CURRENCY


def test_account_is_checked_before_the_amount(client: TestClient) -> None:
    response = _exchange(client, "EUR", "USD", 0)  # sense USD

    assert response.status_code == 404
    assert response.json() == NOT_FOUND


def test_too_small_is_checked_before_the_balance(client: TestClient) -> None:
    _create(client, "USD")  # USD a 0: 1 cèntim no hi arriba i tampoc hi ha saldo

    response = _exchange(client, "USD", "EUR", 1)

    assert response.json() == TOO_SMALL


def test_cv23_without_a_session(monkeypatch: pytest.MonkeyPatch) -> None:
    # Amb ALLOW_X_USER_ID=0, com al desplegament des de la T03.5.
    monkeypatch.setenv("ALLOW_X_USER_ID", "0")
    with TestClient(create_app()) as strict_client:
        response = _exchange(strict_client, "EUR", "USD", 1000)

    assert response.status_code == 401
    assert response.json() == {"code": "UNAUTHENTICATED", "message": "Cal iniciar sessió."}


def test_cv23_works_with_a_session(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ALLOW_X_USER_ID", "0")
    with TestClient(create_app()) as strict_client:
        login = strict_client.post("/api/auth/login", json={"identifier": DEMO_IDENTIFIER, "password": SEED_PASSWORD})
        headers = {"Authorization": f"Bearer {login.json()['token']}"}
        strict_client.post("/api/subaccounts", json={"currency": "USD"}, headers=headers)

        response = _exchange(strict_client, "EUR", "USD", 10000, headers=headers)

    assert response.status_code == 201
    assert response.json()["received"] == 10961


# --- Tot o res (§12.7) --------------------------------------------------------------------


@pytest.mark.memory_only
@pytest.mark.parametrize(
    "repository, write",
    [
        (MovementRepository, "add"),
        (SubaccountRepository, "add_movement"),
        (AccountRepository, "set_balance"),
        (SubaccountRepository, "set_balance"),
    ],
)
def test_cv20_error_halfway_changes_nothing(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, repository: type, write: str
) -> None:
    # Cadascuna de les quatre escriptures, de la primera a l'última.
    _create(client, "USD")

    def fail(*args: object, **kwargs: object) -> None:
        raise RuntimeError("escriptura fallida")

    before = _state(_seed(client))
    monkeypatch.setattr(repository, write, fail)

    response = _exchange(client, "EUR", "USD", 10000)

    assert response.status_code == 500
    assert response.json()["code"] == "INTERNAL_ERROR"
    assert _state(_seed(client)) == before

    # Quan torna a funcionar, l'error no ha gastat cap id ni cap referència.
    monkeypatch.undo()
    assert _exchange(client, "EUR", "USD", 10000).status_code == 201
    first = client.get("/api/movements").json()["items"][0]
    assert (first["id"], first["reference"]) == ("mov-31", "EVT-000031")
    assert client.get("/api/subaccounts/sub-01/movements").json()["items"][0]["id"] == "smov-01"


def test_cv19_two_exchanges_at_once_do_not_overdraw(monkeypatch: pytest.MonkeyPatch) -> None:
    # Dos canvis d'USD a EUR de 6000 (6090 amb la comissió) amb 10961 $. L'espera dins
    # de la primera escriptura obre la finestra entre comprovar el saldo i escriure'l:
    # sense l'`atomic` del router, tots dos passarien la comprovació.
    seed = build_seed()
    subaccounts = SubaccountRepository(seed)
    subaccounts.add(user_id=DEMO_USER_ID, currency="USD")
    run = MemoryAtomic()
    run.run(
        lambda: exchange(
            DEMO_USER_ID, "EUR", "USD", 10000, AccountRepository(seed), subaccounts, MovementRepository(seed)
        )
    )  # CV-01
    original_add_movement = SubaccountRepository.add_movement

    def slow_add_movement(self: SubaccountRepository, **kwargs: object):
        time.sleep(0.1)
        return original_add_movement(self, **kwargs)

    monkeypatch.setattr(SubaccountRepository, "add_movement", slow_add_movement)
    barrier = threading.Barrier(2)
    outcomes: list[str] = []

    def exchange_at_once() -> None:
        barrier.wait()
        try:
            run.run(
                lambda: exchange(
                    DEMO_USER_ID,
                    "USD",
                    "EUR",
                    6000,
                    AccountRepository(seed),
                    SubaccountRepository(seed),
                    MovementRepository(seed),
                )
            )
            outcomes.append("ok")
        except ApiError as error:
            outcomes.append(error.code)

    threads = [threading.Thread(target=exchange_at_once) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert sorted(outcomes) == sorted(["ok", INSUFFICIENT_BALANCE])
    assert seed.subaccounts[0].balance == 4871


# --- Regla de la comissió i conversió (D2, §12.7) -----------------------------------------


def test_minimum_commission_in_every_currency() -> None:
    # Taula de §12.7: 0,50 € convertits cap amunt.
    assert {code: minimum_commission(code) for code in ("EUR", "USD", "GBP", "CHF", "JPY")} == {
        "EUR": 50,
        "USD": 55,
        "GBP": 43,
        "CHF": 49,
        "JPY": 88,
    }


@pytest.mark.parametrize(
    "amount, code, expected",
    [(10000, "EUR", 150), (1000, "EUR", 50), (31286, "USD", 469), (100, "JPY", 88), (379521, "EUR", 5693)],
)
def test_commission(amount: int, code: str, expected: int) -> None:
    assert commission(amount, code) == expected


def test_conversion_rounds_half_up() -> None:
    # 100,00 € són 10961,30… $ → 10961; 1 cèntim són 1,75 ¥ → 2.
    assert convert(10000, "EUR", "USD") == 10961
    assert convert(1, "EUR", "JPY") == 2


def test_one_dollar_cent_does_not_reach_one_euro_cent_even_if_it_rounds_to_one() -> None:
    assert convert(1, "USD", "EUR") == 1
    assert not reaches_one_unit(1, "USD", "EUR")
    assert reaches_one_unit(2, "USD", "EUR")


# --- Repositori ---------------------------------------------------------------------------


@pytest.mark.parametrize("balance, error", [(-1, ValueError), (1.5, TypeError), (True, TypeError)])
def test_set_balance_rejects_invalid_values(balance, error) -> None:
    seed = build_seed()
    subaccounts = SubaccountRepository(seed)
    subaccounts.add(user_id=DEMO_USER_ID, currency="USD")

    with pytest.raises(error):
        subaccounts.set_balance("sub-01", balance)
    assert seed.subaccounts[0].balance == 0


def test_set_balance_of_an_unknown_subaccount_is_a_programming_error() -> None:
    with pytest.raises(KeyError):
        SubaccountRepository(build_seed()).set_balance("sub-99", 100)


def test_removing_an_old_entry_keeps_the_counter() -> None:
    seed = build_seed()
    subaccounts = SubaccountRepository(seed)
    subaccounts.add(user_id=DEMO_USER_ID, currency="USD")
    when = datetime(2026, 11, 22, 10, 0, 0, tzinfo=MADRID_TZ)
    first = subaccounts.add_movement(subaccount_id="sub-01", amount=100, concept="x", date=when, type="income")
    subaccounts.add_movement(subaccount_id="sub-01", amount=100, concept="x", date=when, type="income")

    subaccounts.remove_movement(first)

    assert seed.next_subaccount_movement_number == 3
    assert [entry.id for entry in seed.subaccount_movements] == ["smov-02"]
