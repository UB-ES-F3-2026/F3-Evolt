"""Tests de T18.1: aportacions i historial de les guardioles (docs/api.md §9.4–§9.6).

Proves A-01 a A-22 de docs/proves-estalvi.md, més el model `PotMovement` i els
mètodes nous dels repositoris.

Executar des de backend/:  python -m pytest tests/test_pot_contributions.py
"""

import threading
import time
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from app.data.seed import DEMO_USER_ID, EMPTY_USER_ID, SeedData, build_seed
from app.main import create_app
from app.models import KIND_OTHER, MADRID_TZ, TYPE_INCOME, PotMovement
from app.repositories import AccountRepository, MovementRepository, PotRepository
from app.services.errors import INSUFFICIENT_BALANCE, ApiError
from app.services.pot_service import contribute

EMPTY_USER = {"X-User-Id": str(EMPTY_USER_ID)}
POT_KEYS = {"id", "name", "balance", "target", "color"}
ENTRY_KEYS = {"id", "amount", "concept", "date", "type"}
POT_NOT_FOUND_BODY = {"code": "POT_NOT_FOUND", "message": "No s'ha trobat la guardiola."}
# T0 de docs/proves-estalvi.md.
NOW = datetime(2026, 11, 3, 10, 0, 0, tzinfo=MADRID_TZ)


def _seed(client: TestClient) -> SeedData:
    return client.app.state.seed


def _balance(client: TestClient, user_id: int = DEMO_USER_ID) -> int:
    return _seed(client).accounts[user_id].balance


def _pot_balance(client: TestClient, pot_id: str) -> int:
    return next(pot.balance for pot in _seed(client).pots if pot.id == pot_id)


def _contribute(client: TestClient, pot_id: str, amount, headers: dict[str, str] | None = None):
    return client.post(f"/api/pots/{pot_id}/contributions", json={"amount": amount}, headers=headers)


def _state(seed: SeedData):
    """Estat que una aportació fallida no pot canviar, comptadors inclosos."""
    return (
        {user_id: account.balance for user_id, account in seed.accounts.items()},
        {pot.id: pot.balance for pot in seed.pots},
        [movement.id for movement in seed.movements],
        [entry.id for entry in seed.pot_movements],
        seed.next_movement_number,
        seed.next_movement_seq,
        seed.next_pot_movement_number,
    )


# --- Aportació correcta (§9.4) ----------------------------------------------------------


@pytest.mark.memory_only
def test_contribution_moves_money_from_the_account_to_the_pot(client: TestClient) -> None:
    # A-01: 30 € a «Vacances» (150 €) la deixen a 180 €, i el saldo baixa 30 €.
    before = _balance(client)

    response = _contribute(client, "pot-01", 3000)

    assert response.status_code == 201
    body = response.json()
    assert set(body) == {"balance", "pot", "movement"}
    assert body["balance"] == before - 3000
    assert body["pot"] == {
        "id": "pot-01",
        "name": "Vacances",
        "balance": 18000,
        "target": 100000,
        "color": "blue",
    }
    assert _balance(client) == before - 3000
    assert _pot_balance(client, "pot-01") == 18000


@pytest.mark.memory_only
def test_contribution_creates_the_main_account_movement(client: TestClient) -> None:
    # A-01: el moviment del compte principal (P29).
    movement = _contribute(client, "pot-01", 3000).json()["movement"]

    assert movement["id"] == "mov-31"
    assert movement["amount"] == 3000
    assert movement["concept"] == "Aportació a Vacances"
    assert movement["type"] == "expense"
    assert movement["icon"] == "savings"
    # Ni `kind`, ni `seq`, ni `account_id` surten a l'API (§3, §6).
    assert {"kind", "seq", "account_id"}.isdisjoint(movement)
    # Intern: no compta per al límit diari de recàrrega.
    assert _seed(client).movements[-1].kind == KIND_OTHER


def test_contribution_uses_the_given_moment() -> None:
    # A-01: el moviment i l'entrada de l'historial porten la data de l'aportació.
    seed = build_seed(now=NOW)
    pots = PotRepository(seed)

    result = contribute(
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


def test_response_keeps_the_balance_of_this_contribution() -> None:
    # La guardiola del resultat és una còpia: una altra aportació no la canvia.
    seed = build_seed(now=NOW)
    repositories = (AccountRepository(seed), PotRepository(seed), MovementRepository(seed))

    first = contribute(DEMO_USER_ID, "pot-01", 100, *repositories, now=NOW)
    contribute(DEMO_USER_ID, "pot-01", 100, *repositories, now=NOW)

    assert first.pot.balance == 15100


@pytest.mark.memory_only
def test_contributing_the_whole_balance_leaves_the_account_at_zero(client: TestClient) -> None:
    # A-06
    before = _balance(client)

    response = _contribute(client, "pot-01", before)

    assert response.status_code == 201
    assert response.json()["balance"] == 0
    assert response.json()["pot"]["balance"] == 15000 + before


def test_a_pot_can_go_over_its_target(client: TestClient) -> None:
    # A-15: l'objectiu és una meta, no un límit.
    pot_id = client.post("/api/pots", json={"name": "Viatge", "target": 30000}).json()["id"]

    assert _contribute(client, pot_id, 30000).status_code == 201
    response = _contribute(client, pot_id, 1000)

    assert response.status_code == 201
    assert response.json()["pot"]["balance"] == 31000


# --- Efecte sobre altres rutes (§9.6) ---------------------------------------------------


def test_home_total_saved_goes_up_as_the_balance_goes_down(client: TestClient) -> None:
    # A-02
    before = client.get("/api/home").json()

    _contribute(client, "pot-01", 3000)

    after = client.get("/api/home").json()
    assert after["balance"] == before["balance"] - 3000
    assert after["totalSaved"] == before["totalSaved"] + 3000
    assert after["balance"] + after["totalSaved"] == before["balance"] + before["totalSaved"]


def test_movement_is_the_first_one_at_home_and_in_the_list(client: TestClient) -> None:
    # A-03
    movement = _contribute(client, "pot-01", 3000).json()["movement"]

    assert client.get("/api/home").json()["lastMovements"][0] == movement
    assert client.get("/api/movements").json()["items"][0] == movement


@pytest.mark.memory_only
def test_balance_is_still_the_sum_of_the_movements(client: TestClient) -> None:
    # A-19
    _contribute(client, "pot-01", 3000)

    seed = _seed(client)
    movements = [m for m in seed.movements if m.account_id == seed.accounts[DEMO_USER_ID].id]
    assert sum(m.signed_amount for m in movements) == _balance(client)


@pytest.mark.memory_only
def test_contribution_gives_no_xp(client: TestClient) -> None:
    # A-20
    before = {user_id: user.xp for user_id, user in _seed(client).users.items()}

    _contribute(client, "pot-01", 3000)

    assert {user_id: user.xp for user_id, user in _seed(client).users.items()} == before


def test_contribution_does_not_count_for_the_daily_topup_limit(client: TestClient) -> None:
    # A-21: dues recàrregues arriben al límit de 1.000 € del dia.
    _contribute(client, "pot-01", 3000)

    assert client.post("/api/topups", json={"amount": 50000}).status_code == 201
    assert client.post("/api/topups", json={"amount": 50000}).status_code == 201


@pytest.mark.memory_only
def test_reset_restores_pots_history_and_counters(client: TestClient) -> None:
    # A-22
    before = _state(_seed(client))
    _contribute(client, "pot-01", 3000)

    client.post("/api/dev/reset")

    assert _state(_seed(client)) == before
    assert len(client.get("/api/pots/pot-01/movements").json()["items"]) == 1
    assert _contribute(client, "pot-01", 3000).json()["movement"]["id"] == "mov-31"


# --- Historial (§9.5) -------------------------------------------------------------------


@pytest.mark.memory_only
def test_contribution_is_the_first_entry_of_the_history(client: TestClient) -> None:
    # A-04
    _contribute(client, "pot-01", 3000)

    response = client.get("/api/pots/pot-01/movements")

    assert response.status_code == 200
    items = response.json()["items"]
    assert [set(item) for item in items] == [ENTRY_KEYS, ENTRY_KEYS]
    assert items[0]["id"] == "pmov-04"
    assert (items[0]["amount"], items[0]["concept"], items[0]["type"]) == (3000, "Aportació", "income")
    assert (items[1]["amount"], items[1]["concept"], items[1]["type"]) == (15000, "Saldo inicial", "income")
    assert sum(item["amount"] for item in items) == _pot_balance(client, "pot-01")


def test_seed_pot_has_only_its_initial_entry(client: TestClient) -> None:
    # A-05
    items = client.get("/api/pots/pot-02/movements").json()["items"]

    assert len(items) == 1
    assert (items[0]["id"], items[0]["concept"], items[0]["amount"]) == ("pmov-02", "Saldo inicial", 10000)


def test_new_pot_has_an_empty_history(client: TestClient) -> None:
    pot_id = client.post("/api/pots", json={"name": "Viatge"}).json()["id"]

    assert client.get(f"/api/pots/{pot_id}/movements").json() == {"items": []}


def test_history_date_follows_the_contract(client: TestClient) -> None:
    _contribute(client, "pot-01", 3000)

    for item in client.get("/api/pots/pot-01/movements").json()["items"]:
        # 2026-11-03T10:00:00+01:00: desplaçament de Madrid i precisió de segons (P7).
        assert item["date"][-6:] in {"+02:00", "+01:00"}
        assert len(item["date"]) == len("2026-11-03T10:00:00+01:00")


def test_entries_with_the_same_date_show_the_latest_first() -> None:
    # Desempat de la P4: dues aportacions al mateix segon.
    seed = build_seed(now=NOW)
    pots = PotRepository(seed)
    repositories = (AccountRepository(seed), pots, MovementRepository(seed))

    contribute(DEMO_USER_ID, "pot-01", 100, *repositories, now=NOW)
    contribute(DEMO_USER_ID, "pot-01", 200, *repositories, now=NOW)

    assert [entry.amount for entry in pots.list_movements("pot-01")] == [200, 100, 15000]


def test_seed_pot_balance_is_the_sum_of_its_history() -> None:
    # §9.8: les entrades inicials tenen una data anterior a avui.
    seed = build_seed(now=NOW)
    pots = PotRepository(seed)

    for pot in seed.pots:
        entries = pots.list_movements(pot.id)
        assert sum(entry.amount for entry in entries) == pot.balance
        assert all(entry.date.date() < NOW.date() for entry in entries)
    assert seed.next_pot_movement_number == len(seed.pot_movements) + 1


# --- Errors de negoci (§9.7) ------------------------------------------------------------


@pytest.mark.memory_only
def test_more_than_the_balance_changes_nothing(client: TestClient) -> None:
    # A-07
    before = _state(_seed(client))

    response = _contribute(client, "pot-01", _balance(client) + 1)

    assert response.status_code == 422
    assert response.json() == {
        "code": "INSUFFICIENT_BALANCE",
        "message": "No tens prou saldo per fer aquesta aportació.",
    }
    assert _state(_seed(client)) == before


@pytest.mark.memory_only
@pytest.mark.parametrize("amount", [0, -100])
def test_zero_or_negative_amount_changes_nothing(client: TestClient, amount: int) -> None:
    # A-08
    before = _state(_seed(client))

    response = _contribute(client, "pot-01", amount)

    assert response.status_code == 422
    assert response.json() == {
        "code": "INVALID_AMOUNT",
        "message": "L'import ha de ser més gran que 0.",
    }
    assert _state(_seed(client)) == before


@pytest.mark.memory_only
@pytest.mark.parametrize(
    "body",
    [{"amount": "30"}, {"amount": 30.0}, {"amount": 30.5}, {"amount": True}, {"amount": None}, {}],
)
def test_badly_formed_body_is_a_validation_error(client: TestClient, body: dict[str, object]) -> None:
    # A-09
    before = _state(_seed(client))

    response = client.post("/api/pots/pot-01/contributions", json=body)

    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"
    assert _state(_seed(client)) == before


def test_format_is_checked_before_the_pot(client: TestClient) -> None:
    # Ordre del §9.4: el format va primer.
    response = _contribute(client, "pot-99", "30")

    assert response.json()["code"] == "VALIDATION_ERROR"


@pytest.mark.memory_only
@pytest.mark.parametrize("pot_id", ["pot-99", "abc"])
def test_unknown_pot_is_not_found(client: TestClient, pot_id: str) -> None:
    # A-10: també un id amb un format qualsevol.
    before = _state(_seed(client))

    response = _contribute(client, pot_id, 3000)

    assert response.status_code == 404
    assert response.json() == POT_NOT_FOUND_BODY
    assert _state(_seed(client)) == before


@pytest.mark.memory_only
def test_pot_of_another_user_looks_like_an_unknown_one(client: TestClient) -> None:
    # A-11: el mateix cos que A-10, i la guardiola no canvia.
    before = _state(_seed(client))

    response = _contribute(client, "pot-01", 3000, headers=EMPTY_USER)

    assert response.status_code == 404
    assert response.json() == POT_NOT_FOUND_BODY
    assert _state(_seed(client)) == before


@pytest.mark.parametrize(
    "pot_id, headers",
    [("pot-01", EMPTY_USER), ("pot-99", None)],
)
def test_history_of_a_pot_that_is_not_yours_is_not_found(
    client: TestClient, pot_id: str, headers: dict[str, str] | None
) -> None:
    # A-12
    response = client.get(f"/api/pots/{pot_id}/movements", headers=headers)

    assert response.status_code == 404
    assert response.json() == POT_NOT_FOUND_BODY


def test_pot_is_checked_before_the_amount(client: TestClient) -> None:
    # A-13
    assert _contribute(client, "pot-99", 0).json()["code"] == "POT_NOT_FOUND"


def test_amount_is_checked_before_the_balance(client: TestClient) -> None:
    # A-14: el compte de l'usuari 2 és a 0.
    pot_id = client.post("/api/pots", json={"name": "Primera"}, headers=EMPTY_USER).json()["id"]

    assert _contribute(client, pot_id, 0, headers=EMPTY_USER).json()["code"] == "INVALID_AMOUNT"
    assert _contribute(client, pot_id, 100, headers=EMPTY_USER).json()["code"] == "INSUFFICIENT_BALANCE"


# --- Tot o res --------------------------------------------------------------------------


@pytest.mark.memory_only
def test_simulated_error_changes_nothing(monkeypatch: pytest.MonkeyPatch) -> None:
    # A-16: la simulació de T08.2 falla abans d'arribar a la ruta.
    monkeypatch.setenv("SIMULATE_ERROR_RATE", "100")

    with TestClient(create_app()) as client:
        before = _state(_seed(client))

        response = _contribute(client, "pot-01", 3000)

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
    # A-17: cadascuna de les quatre escriptures, de la primera a l'última.
    def fail(*args: object, **kwargs: object) -> None:
        raise RuntimeError("escriptura fallida")

    before = _state(_seed(client))
    monkeypatch.setattr(repository, write, fail)

    response = _contribute(client, "pot-01", 3000)

    assert response.status_code == 500
    assert response.json()["code"] == "INTERNAL_ERROR"
    assert _state(_seed(client)) == before

    # Quan torna a funcionar, l'error no ha gastat cap id.
    monkeypatch.undo()
    retried = _contribute(client, "pot-01", 3000)
    assert retried.status_code == 201
    assert retried.json()["movement"]["id"] == "mov-31"
    assert client.get("/api/pots/pot-01/movements").json()["items"][0]["id"] == "pmov-04"


def test_two_contributions_at_once_do_not_overdraw(monkeypatch: pytest.MonkeyPatch) -> None:
    # A-18. L'espera dins de la primera escriptura obre la finestra entre comprovar el
    # saldo i escriure'l: sense el pany, totes dues passarien la comprovació.
    seed = build_seed(now=NOW)
    initial_balance = seed.accounts[DEMO_USER_ID].balance
    amount = initial_balance // 2 + 1
    original_add = MovementRepository.add

    def slow_add(self: MovementRepository, **kwargs: object):
        time.sleep(0.1)
        return original_add(self, **kwargs)

    monkeypatch.setattr(MovementRepository, "add", slow_add)

    barrier = threading.Barrier(2)
    outcomes: list[str] = []

    def contribute_at_once() -> None:
        barrier.wait()
        try:
            contribute(
                DEMO_USER_ID,
                "pot-01",
                amount,
                AccountRepository(seed),
                PotRepository(seed),
                MovementRepository(seed),
                now=NOW,
            )
            outcomes.append("ok")
        except ApiError as error:
            outcomes.append(error.code)

    threads = [threading.Thread(target=contribute_at_once) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert sorted(outcomes) == sorted(["ok", INSUFFICIENT_BALANCE])
    assert seed.accounts[DEMO_USER_ID].balance == initial_balance - amount
    assert seed.pots[0].balance == 15000 + amount
    assert len(seed.movements) == 31


# --- Model i repositoris ----------------------------------------------------------------


def _entry_kwargs(**overrides):
    """Arguments per defecte d'una entrada vàlida."""
    kwargs = {
        "id": "pmov-99",
        "pot_id": "pot-01",
        "amount": 100,
        "concept": "Aportació",
        "date": NOW,
        "type": TYPE_INCOME,
        "seq": 99,
    }
    kwargs.update(overrides)
    return kwargs


@pytest.mark.parametrize(
    "overrides, error",
    [
        ({"id": ""}, TypeError),
        ({"amount": 0}, ValueError),
        ({"amount": 1.5}, TypeError),
        ({"amount": True}, TypeError),
        ({"type": "other"}, ValueError),
        ({"date": datetime(2026, 11, 3, 10, 0, 0)}, ValueError),
        ({"date": NOW.replace(microsecond=1)}, ValueError),
    ],
)
def test_pot_movement_model_rejects_invalid_values(overrides, error) -> None:
    with pytest.raises(error):
        PotMovement(**_entry_kwargs(**overrides))


def test_get_by_user_only_finds_your_own_pots() -> None:
    repository = PotRepository(build_seed(now=NOW))

    assert repository.get_by_user(DEMO_USER_ID, "pot-01").name == "Vacances"
    assert repository.get_by_user(EMPTY_USER_ID, "pot-01") is None
    assert repository.get_by_user(DEMO_USER_ID, "pot-99") is None


@pytest.mark.parametrize(
    "pot_id, balance, error",
    [("pot-01", "100", TypeError), ("pot-01", True, TypeError), ("pot-01", -1, ValueError), ("pot-99", 100, KeyError)],
)
def test_set_balance_rejects_invalid_values(pot_id: str, balance, error) -> None:
    seed = build_seed(now=NOW)

    with pytest.raises(error):
        PotRepository(seed).set_balance(pot_id, balance)

    assert seed.pots[0].balance == 15000


def test_add_movement_with_invalid_values_stores_nothing() -> None:
    seed = build_seed(now=NOW)

    with pytest.raises(ValueError):
        PotRepository(seed).add_movement(pot_id="pot-01", amount=0, concept="Aportació", date=NOW, type=TYPE_INCOME)

    assert len(seed.pot_movements) == 3
    assert seed.next_pot_movement_number == 4


def test_removing_an_old_movement_keeps_the_counters() -> None:
    # Si no és l'últim creat, tirar enrere els comptadors repetiria un id.
    seed = build_seed(now=NOW)
    before = (seed.next_movement_number, seed.next_movement_seq)

    MovementRepository(seed).remove(seed.movements[0])

    assert (seed.next_movement_number, seed.next_movement_seq) == before
    assert len(seed.movements) == 29


def test_removing_an_old_entry_keeps_the_counter() -> None:
    seed = build_seed(now=NOW)

    PotRepository(seed).remove_movement(seed.pot_movements[0])

    assert seed.next_pot_movement_number == 4
    assert len(seed.pot_movements) == 2
