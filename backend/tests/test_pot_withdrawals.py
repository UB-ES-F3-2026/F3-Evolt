"""Tests de T19.2: retirar diners d'una guardiola al compte principal (docs/api.md §11.2 a §11.5).

Proves RE-01 a RE-21 de docs/proves-estalvi.md. A la RE-01, el `percentage` i el
`goalStatus` del `pot` són de la T20.1 (US-20): es comproven quan les dues històries
es trobin a `develop` (prova O-04). El `401` sense sessió és a test_session_auth.py.

Executar des de backend/:  python -m pytest tests/test_pot_withdrawals.py
"""

import threading
import time
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from app.data.seed import DEMO_USER_ID, EMPTY_USER_ID, SeedData, build_seed
from app.main import create_app
from app.models import KIND_OTHER, MADRID_TZ
from app.repositories import AccountRepository, MovementRepository, PotRepository
from app.services.errors import INSUFFICIENT_POT_BALANCE, ApiError
from app.services.pot_service import withdraw

EMPTY_USER = {"X-User-Id": str(EMPTY_USER_ID)}
POT_NOT_FOUND_BODY = {"code": "POT_NOT_FOUND", "message": "No s'ha trobat la guardiola."}
INSUFFICIENT_POT_BALANCE_BODY = {
    "code": "INSUFFICIENT_POT_BALANCE",
    "message": "La guardiola no té prou saldo per aquesta retirada.",
}
# Seed (docs/proves-estalvi.md, «Dades de partida»).
SEED_BALANCE = 379521
VACANCES = 15000
# T0 de docs/proves-estalvi.md.
NOW = datetime(2026, 11, 3, 10, 0, 0, tzinfo=MADRID_TZ)


def _seed(client: TestClient) -> SeedData:
    return client.app.state.seed


def _pot_balance(client: TestClient, pot_id: str) -> int:
    # Per l'API i no pel seed: així també funciona amb TEST_STORAGE=firestore, on
    # `app.state.seed` no existeix (com la CU-20 a la #216).
    return next(pot["balance"] for pot in client.get("/api/pots").json()["items"] if pot["id"] == pot_id)


def _withdraw(client: TestClient, pot_id: str, amount, headers: dict[str, str] | None = None):
    return client.post(f"/api/pots/{pot_id}/withdrawals", json={"amount": amount}, headers=headers)


def _state(seed: SeedData):
    """Estat que una retirada fallida no pot canviar, comptadors inclosos."""
    return (
        {user_id: account.balance for user_id, account in seed.accounts.items()},
        {pot.id: pot.balance for pot in seed.pots},
        [movement.id for movement in seed.movements],
        [entry.id for entry in seed.pot_movements],
        seed.next_movement_number,
        seed.next_movement_seq,
        seed.next_pot_movement_number,
    )


# --- Retirada correcta (§11.2) ----------------------------------------------------------


def test_withdrawal_moves_money_from_the_pot_to_the_account(client: TestClient) -> None:
    # RE-01: 30 € de «Vacances» (150 €) la deixen a 120 €, i el saldo puja 30 €.
    response = _withdraw(client, "pot-01", 3000)

    assert response.status_code == 201
    body = response.json()
    assert set(body) == {"balance", "pot", "movement"}
    assert body["balance"] == 382521
    pot = body["pot"]
    assert (pot["id"], pot["name"], pot["balance"], pot["target"], pot["color"]) == (
        "pot-01",
        "Vacances",
        12000,
        100000,
        "blue",
    )


@pytest.mark.memory_only
def test_withdrawal_creates_an_income_movement_in_the_account(client: TestClient) -> None:
    # RE-01: el moviment del compte principal, «Retirada de Vacances».
    movement = _withdraw(client, "pot-01", 3000).json()["movement"]

    assert movement["id"] == "mov-31"
    assert movement["amount"] == 3000
    assert movement["concept"] == "Retirada de Vacances"
    assert movement["type"] == "income"
    assert movement["icon"] == "savings"
    assert (movement["counterparty"], movement["status"]) == (None, "completed")
    assert movement["reference"] == "EVT-000031"
    # Intern: és un ingrés, però no una recàrrega (no compta per al límit diari).
    assert _seed(client).movements[-1].kind == KIND_OTHER


def test_withdrawal_uses_the_given_moment() -> None:
    # RE-01: el moviment i l'entrada de l'historial porten la data de la retirada (T0).
    seed = build_seed(now=NOW)
    pots = PotRepository(seed)

    result = withdraw(
        DEMO_USER_ID,
        "pot-01",
        3000,
        AccountRepository(seed),
        pots,
        MovementRepository(seed),
        now=NOW,
    )

    assert result.movement.date == NOW
    assert pots.list_movements("pot-01")[0].date == NOW


def test_response_keeps_the_balance_of_this_withdrawal() -> None:
    # La guardiola del resultat és una còpia: una altra retirada no la canvia.
    seed = build_seed(now=NOW)
    repositories = (AccountRepository(seed), PotRepository(seed), MovementRepository(seed))

    first = withdraw(DEMO_USER_ID, "pot-01", 100, *repositories, now=NOW)
    withdraw(DEMO_USER_ID, "pot-01", 100, *repositories, now=NOW)

    assert first.pot.balance == 14900


def test_withdrawing_the_whole_pot_leaves_it_at_zero(client: TestClient) -> None:
    # RE-06: retirar exactament tot el saldo es pot fer.
    response = _withdraw(client, "pot-01", VACANCES)

    assert response.status_code == 201
    assert response.json()["balance"] == 394521
    assert response.json()["pot"]["balance"] == 0


# --- Efecte sobre altres rutes (§11.4) --------------------------------------------------


def test_home_balance_goes_up_as_total_saved_goes_down(client: TestClient) -> None:
    # RE-02: `balance + totalSaved` no canvia amb una retirada.
    _withdraw(client, "pot-01", 3000)

    home = client.get("/api/home").json()
    assert (home["balance"], home["totalSaved"]) == (382521, 27000)
    assert home["balance"] + home["totalSaved"] == 409521


def test_movement_is_the_first_one_at_home_and_in_the_lists(client: TestClient) -> None:
    # RE-03: també amb el filtre d'ingressos.
    movement_id = _withdraw(client, "pot-01", 3000).json()["movement"]["id"]

    assert client.get("/api/home").json()["lastMovements"][0]["id"] == movement_id
    assert client.get("/api/movements").json()["items"][0]["id"] == movement_id
    assert client.get("/api/movements?type=income").json()["items"][0]["id"] == movement_id


def test_withdrawal_movement_has_a_detail(client: TestClient) -> None:
    # RE-05
    movement_id = _withdraw(client, "pot-01", 3000).json()["movement"]["id"]

    response = client.get(f"/api/movements/{movement_id}")

    assert response.status_code == 200
    detail = response.json()
    assert (detail["concept"], detail["type"], detail["status"]) == ("Retirada de Vacances", "income", "completed")


@pytest.mark.memory_only
def test_balance_is_still_the_sum_of_the_movements(client: TestClient) -> None:
    # RE-18
    _withdraw(client, "pot-01", 3000)

    seed = _seed(client)
    movements = [m for m in seed.movements if m.account_id == seed.accounts[DEMO_USER_ID].id]
    assert sum(m.signed_amount for m in movements) == 382521


def test_withdrawal_does_not_count_for_the_daily_topup_limit(client: TestClient) -> None:
    # RE-19: dues recàrregues de 500 € arriben al límit de 1.000 € del dia.
    _withdraw(client, "pot-01", 3000)

    assert client.post("/api/topups", json={"amount": 50000}).status_code == 201
    assert client.post("/api/topups", json={"amount": 50000}).status_code == 201


@pytest.mark.memory_only
def test_withdrawal_gives_no_xp(client: TestClient) -> None:
    # RE-20: en aquest sprint, retirar no dona ni treu XP.
    before = {user_id: user.xp for user_id, user in _seed(client).users.items()}

    _withdraw(client, "pot-01", 3000)

    assert {user_id: user.xp for user_id, user in _seed(client).users.items()} == before


@pytest.mark.memory_only
def test_reset_restores_the_pot_and_its_history(client: TestClient) -> None:
    # RE-21
    before = _state(_seed(client))
    _withdraw(client, "pot-01", 3000)

    client.post("/api/dev/reset")

    assert _state(_seed(client)) == before
    pot = next(pot for pot in client.get("/api/pots").json()["items"] if pot["id"] == "pot-01")
    assert pot["balance"] == VACANCES
    assert len(client.get("/api/pots/pot-01/movements").json()["items"]) == 1


# --- Historial (§11.3) ------------------------------------------------------------------


def test_withdrawal_is_the_first_entry_of_the_history(client: TestClient) -> None:
    # RE-04: una sortida per a la guardiola (expense) amb el concepte «Retirada».
    _withdraw(client, "pot-01", 3000)

    items = client.get("/api/pots/pot-01/movements").json()["items"]

    assert len(items) == 2
    assert (items[0]["amount"], items[0]["concept"], items[0]["type"]) == (3000, "Retirada", "expense")
    assert (items[1]["amount"], items[1]["concept"], items[1]["type"]) == (VACANCES, "Saldo inicial", "income")


def test_pot_balance_is_the_signed_sum_of_its_history(client: TestClient) -> None:
    # §11.3: les entrades income sumen i les expense resten.
    _withdraw(client, "pot-01", 3000)
    client.post("/api/pots/pot-01/contributions", json={"amount": 1000})

    items = client.get("/api/pots/pot-01/movements").json()["items"]
    signed = sum(item["amount"] if item["type"] == "income" else -item["amount"] for item in items)

    assert signed == _pot_balance(client, "pot-01") == 13000


# --- Errors de negoci (§11.5) -----------------------------------------------------------


@pytest.mark.memory_only
def test_one_cent_more_than_the_pot_changes_nothing(client: TestClient) -> None:
    # RE-07
    before = _state(_seed(client))

    response = _withdraw(client, "pot-01", VACANCES + 1)

    assert response.status_code == 422
    assert response.json() == INSUFFICIENT_POT_BALANCE_BODY
    assert _state(_seed(client)) == before


def test_an_empty_pot_has_nothing_to_withdraw(client: TestClient) -> None:
    # RE-08: després de buidar-la (RE-06), qualsevol import positiu.
    _withdraw(client, "pot-01", VACANCES)

    response = _withdraw(client, "pot-01", 100)

    assert response.status_code == 422
    assert response.json() == INSUFFICIENT_POT_BALANCE_BODY


@pytest.mark.memory_only
@pytest.mark.parametrize("amount", [0, -100])
def test_zero_or_negative_amount_changes_nothing(client: TestClient, amount: int) -> None:
    # RE-09
    before = _state(_seed(client))

    response = _withdraw(client, "pot-01", amount)

    assert response.status_code == 422
    assert response.json()["code"] == "INVALID_AMOUNT"
    assert _state(_seed(client)) == before


@pytest.mark.parametrize("body", [{"amount": "30"}, {"amount": 30.0}, {"amount": True}, {}])
def test_badly_formed_body_is_a_validation_error(client: TestClient, body: dict[str, object]) -> None:
    # RE-10
    response = client.post("/api/pots/pot-01/withdrawals", json=body)

    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"
    assert _pot_balance(client, "pot-01") == VACANCES


@pytest.mark.parametrize("pot_id", ["pot-99", "vacances", "1"])
def test_unknown_pot_is_not_found(client: TestClient, pot_id: str) -> None:
    # RE-11: també un id amb un format qualsevol.
    response = _withdraw(client, pot_id, 3000)

    assert response.status_code == 404
    assert response.json() == POT_NOT_FOUND_BODY


def test_pot_of_another_user_looks_like_an_unknown_one(client: TestClient) -> None:
    # RE-12: el mateix cos que RE-11, i la guardiola de l'usuari 1 no canvia.
    response = _withdraw(client, "pot-01", 3000, headers=EMPTY_USER)

    assert response.status_code == 404
    assert response.json() == POT_NOT_FOUND_BODY
    assert _pot_balance(client, "pot-01") == VACANCES


def test_pot_is_checked_before_the_amount(client: TestClient) -> None:
    # RE-13
    assert _withdraw(client, "pot-99", 0).json()["code"] == "POT_NOT_FOUND"


def test_amount_is_checked_before_the_pot_balance(client: TestClient) -> None:
    # RE-14: una guardiola nova de l'usuari 2 té saldo 0.
    pot_id = client.post("/api/pots", json={"name": "Primera"}, headers=EMPTY_USER).json()["id"]

    assert _withdraw(client, pot_id, 0, headers=EMPTY_USER).json()["code"] == "INVALID_AMOUNT"
    assert _withdraw(client, pot_id, 100, headers=EMPTY_USER).json()["code"] == "INSUFFICIENT_POT_BALANCE"


# --- Tot o res --------------------------------------------------------------------------


@pytest.mark.memory_only
def test_simulated_error_changes_nothing(monkeypatch: pytest.MonkeyPatch) -> None:
    # RE-15: la simulació de T08.2 falla abans d'arribar a la ruta.
    monkeypatch.setenv("SIMULATE_ERROR_RATE", "100")

    with TestClient(create_app()) as client:
        before = _state(_seed(client))

        response = _withdraw(client, "pot-01", 3000)

        assert response.status_code == 500
        assert response.json()["code"] == "INTERNAL_ERROR"
        assert _state(_seed(client)) == before


@pytest.mark.memory_only
@pytest.mark.parametrize(
    "repository, write",
    [
        (MovementRepository, "add"),
        (PotRepository, "add_movement"),
        (AccountRepository, "set_balance"),
        (PotRepository, "set_balance"),
    ],
)
def test_error_halfway_changes_nothing(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, repository: type, write: str
) -> None:
    # RE-16: cadascuna de les quatre escriptures, de la primera a l'última.
    def fail(*args: object, **kwargs: object) -> None:
        raise RuntimeError("escriptura fallida")

    before = _state(_seed(client))
    monkeypatch.setattr(repository, write, fail)

    response = _withdraw(client, "pot-01", 3000)

    assert response.status_code == 500
    assert response.json()["code"] == "INTERNAL_ERROR"
    assert _state(_seed(client)) == before

    # Quan torna a funcionar, l'error no ha gastat cap id.
    monkeypatch.undo()
    retried = _withdraw(client, "pot-01", 3000)
    assert retried.status_code == 201
    assert retried.json()["movement"]["id"] == "mov-31"
    assert client.get("/api/pots/pot-01/movements").json()["items"][0]["id"] == "pmov-04"


def _at_once(operations: list, seed: SeedData, monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """Executa les operacions alhora, amb una espera dins de la primera escriptura.

    L'espera obre la finestra entre comprovar el saldo i escriure'l: sense el pany,
    totes passarien la comprovació.
    """
    original_add = MovementRepository.add

    def slow_add(self: MovementRepository, **kwargs: object):
        time.sleep(0.1)
        return original_add(self, **kwargs)

    monkeypatch.setattr(MovementRepository, "add", slow_add)
    repositories = (AccountRepository(seed), PotRepository(seed), MovementRepository(seed))
    barrier = threading.Barrier(len(operations))
    outcomes: list[str] = []

    def run(operation) -> None:
        barrier.wait()
        try:
            operation(DEMO_USER_ID, "pot-01", *repositories)
            outcomes.append("ok")
        except ApiError as error:
            outcomes.append(error.code)

    threads = [threading.Thread(target=run, args=(operation,)) for operation in operations]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    return outcomes


def test_two_withdrawals_at_once_never_leave_the_pot_negative(monkeypatch: pytest.MonkeyPatch) -> None:
    # RE-17: dues retirades de 100 € de Vacances (150 €) alhora.
    seed = build_seed(now=NOW)

    def withdraw_100(user_id, pot_id, accounts, pots, movements) -> None:
        withdraw(user_id, pot_id, 10000, accounts, pots, movements, now=NOW)

    outcomes = _at_once([withdraw_100, withdraw_100], seed, monkeypatch)

    assert sorted(outcomes) == sorted(["ok", INSUFFICIENT_POT_BALANCE])
    assert seed.pots[0].balance == 5000
    assert seed.accounts[DEMO_USER_ID].balance == SEED_BALANCE + 10000
