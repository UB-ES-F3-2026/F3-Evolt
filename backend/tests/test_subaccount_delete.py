"""Tests de T26.1: eliminar un subcompte i veure'n l'historial (docs/api.md §12.5 i §12.6).

Proves EL-01 a EL-11 de docs/proves-multidivisa.md, més l'ordre de l'historial,
dues eliminacions alhora, el model `SubaccountMovement` i el repositori.

Sense «Aportar» (#189) i sense el canvi (T27.1), un subcompte no pot tenir saldo
per l'API: els tests que en necessiten (EL-04, EL-07) el preparen al repositori i
només corren en memòria, com diu «Com fer servir aquest document».

Executar des de backend/:  python -m pytest tests/test_subaccount_delete.py
"""

import threading
import time
from collections.abc import Iterator
from datetime import timedelta

import pytest
from fastapi.testclient import TestClient

from app.data.seed import DEMO_IDENTIFIER, DEMO_USER_ID, EMPTY_USER_ID, SEED_PASSWORD, SeedData, build_seed
from app.main import create_app
from app.models import KIND_OTHER, TYPE_EXPENSE, TYPE_INCOME, SubaccountMovement, now_madrid
from app.repositories import MovementRepository, SubaccountRepository
from app.services.errors import SUBACCOUNT_NOT_FOUND, ApiError
from app.services.subaccount_service import delete_subaccount

EMPTY_USER = {"X-User-Id": str(EMPTY_USER_ID)}
OK = {"status": "ok"}
MAIN_SEED = {"id": "main", "currency": "EUR", "balance": 379521, "isMain": True, "rateBps": 10000}
NOT_FOUND = {"code": "SUBACCOUNT_NOT_FOUND", "message": "No s'ha trobat el subcompte."}
MAIN_NOT_DELETABLE = {"code": "MAIN_ACCOUNT_NOT_DELETABLE", "message": "El compte en euros no es pot eliminar."}
NOT_EMPTY = {"code": "SUBACCOUNT_NOT_EMPTY", "message": "Només pots eliminar un subcompte amb saldo 0."}


def _create(client: TestClient, currency: str, headers: dict[str, str] | None = None):
    return client.post("/api/subaccounts", json={"currency": currency}, headers=headers)


def _delete(client: TestClient, subaccount_id: str, headers: dict[str, str] | None = None):
    return client.post(f"/api/subaccounts/{subaccount_id}/delete", headers=headers)


def _history(client: TestClient, subaccount_id: str, headers: dict[str, str] | None = None):
    return client.get(f"/api/subaccounts/{subaccount_id}/movements", headers=headers)


def _seed(client: TestClient) -> SeedData:
    return client.app.state.seed


# --- Eliminar (§12.5) -----------------------------------------------------------------


def test_el01_delete_a_subaccount_at_zero(client: TestClient) -> None:
    _create(client, "USD")  # DV-03

    response = _delete(client, "sub-01")

    assert response.status_code == 200
    assert response.json() == OK
    assert client.get("/api/subaccounts").json() == {"items": [MAIN_SEED], "totalInEuros": 379521}


def test_el02_the_currency_is_available_again_with_a_new_id_and_an_empty_history(client: TestClient) -> None:
    _create(client, "USD")
    _delete(client, "sub-01")  # EL-01

    response = _create(client, "USD")

    assert response.status_code == 201
    assert response.json() == {"id": "sub-02", "currency": "USD", "balance": 0, "isMain": False, "rateBps": 9123}
    assert _history(client, "sub-02").json() == {"items": []}


def test_el03_the_main_account_is_never_deleted_even_with_money(client: TestClient) -> None:
    # Té 379521: el compte principal es comprova abans que el saldo.
    response = _delete(client, "main")

    assert response.status_code == 422
    assert response.json() == MAIN_NOT_DELETABLE
    assert client.get("/api/subaccounts").json()["items"] == [MAIN_SEED]


@pytest.mark.memory_only
def test_el04_a_subaccount_with_one_cent_is_not_deleted(client: TestClient) -> None:
    # Al navegador surt de CV-14; aquí el saldo es prepara al repositori.
    _create(client, "USD")
    _seed(client).subaccounts[0].balance = 1

    response = _delete(client, "sub-01")

    assert response.status_code == 422
    assert response.json() == NOT_EMPTY
    usd = client.get("/api/subaccounts").json()["items"][1]
    assert usd == {"id": "sub-01", "currency": "USD", "balance": 1, "isMain": False, "rateBps": 9123}


def test_el05_unknown_subaccount(client: TestClient) -> None:
    response = _delete(client, "sub-99")

    assert response.status_code == 404
    assert response.json() == NOT_FOUND


def test_el06_another_users_subaccount_answers_as_unknown(client: TestClient) -> None:
    _create(client, "USD")  # de l'usuari 1

    response = _delete(client, "sub-01", headers=EMPTY_USER)

    assert response.status_code == 404
    assert response.json() == NOT_FOUND
    assert [item["id"] for item in client.get("/api/subaccounts").json()["items"]] == ["main", "sub-01"]


@pytest.mark.memory_only
def test_el07_the_euro_movements_stay_and_the_deleted_history_is_not_found(client: TestClient) -> None:
    # CV-06 i després EL-01. Sense la T27.1, el canvi d'anada i tornada es prepara al
    # repositori: dos moviments al compte principal i dues entrades a l'historial.
    seed = _seed(client)
    _create(client, "USD")
    when = now_madrid().replace(microsecond=0)
    account_id = seed.accounts[DEMO_USER_ID].id
    movements = MovementRepository(seed)
    movements.add(
        account_id=account_id,
        amount=29405,
        concept="Canvi EUR → USD",
        date=when,
        type=TYPE_EXPENSE,
        icon="transfer",
        kind=KIND_OTHER,
    )
    movements.add(
        account_id=account_id,
        amount=28542,
        concept="Canvi USD → EUR",
        date=when + timedelta(minutes=1),
        type=TYPE_INCOME,
        icon="transfer",
        kind=KIND_OTHER,
    )
    entries = SubaccountRepository(seed)
    entries.add_movement(subaccount_id="sub-01", amount=31755, concept="Canvi EUR → USD", date=when, type=TYPE_INCOME)
    entries.add_movement(
        subaccount_id="sub-01",
        amount=31755,
        concept="Canvi USD → EUR",
        date=when + timedelta(minutes=1),
        type=TYPE_EXPENSE,
    )
    assert [entry["id"] for entry in _history(client, "sub-01").json()["items"]] == ["smov-02", "smov-01"]

    assert _delete(client, "sub-01").json() == OK

    first_two = client.get("/api/movements").json()["items"][:2]
    assert [(m["id"], m["concept"], m["amount"]) for m in first_two] == [
        ("mov-32", "Canvi USD → EUR", 28542),
        ("mov-31", "Canvi EUR → USD", 29405),
    ]
    response = _history(client, "sub-01")
    assert response.status_code == 404
    assert response.json() == NOT_FOUND
    # Les entrades es queden desades (§12.11), encara que ja no es puguin consultar.
    assert [entry.id for entry in seed.subaccount_movements] == ["smov-01", "smov-02"]


def test_el08_deleting_twice_is_not_found(client: TestClient) -> None:
    _create(client, "USD")
    _delete(client, "sub-01")  # EL-01

    response = _delete(client, "sub-01")

    assert response.status_code == 404
    assert response.json() == NOT_FOUND


@pytest.mark.memory_only
def test_two_deletions_at_once_only_one_wins(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    # L'espera dins de l'esborrat obre la finestra entre comprovar i esborrar: sense
    # `atomic.run(...)`, totes dues peticions passarien la comprovació.
    seed = _seed(client)
    _create(client, "USD")
    original_delete = SubaccountRepository.delete

    def slow_delete(self: SubaccountRepository, subaccount_id: str) -> None:
        time.sleep(0.1)
        original_delete(self, subaccount_id)

    monkeypatch.setattr(SubaccountRepository, "delete", slow_delete)
    run = client.app.state.atomic
    barrier = threading.Barrier(2)
    outcomes: list[str] = []

    def delete_at_once() -> None:
        barrier.wait()
        try:
            run.run(lambda: delete_subaccount(DEMO_USER_ID, "sub-01", SubaccountRepository(seed)))
            outcomes.append("ok")
        except ApiError as error:
            outcomes.append(error.code)

    threads = [threading.Thread(target=delete_at_once) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert sorted(outcomes) == [SUBACCOUNT_NOT_FOUND, "ok"]
    assert seed.subaccounts == []


# --- Historial (§12.6) ----------------------------------------------------------------


def test_a_new_subaccount_has_an_empty_history(client: TestClient) -> None:
    _create(client, "USD")

    response = _history(client, "sub-01")

    assert response.status_code == 200
    assert response.json() == {"items": []}


@pytest.mark.memory_only
def test_history_is_newest_first_and_a_tie_goes_to_the_one_created_later(client: TestClient) -> None:
    # P4: amb la mateixa data, primer la creada més tard.
    _create(client, "JPY")
    entries = SubaccountRepository(_seed(client))
    when = now_madrid().replace(microsecond=0)
    entries.add_movement(subaccount_id="sub-01", amount=1754, concept="Canvi EUR → JPY", date=when, type=TYPE_INCOME)
    entries.add_movement(subaccount_id="sub-01", amount=100, concept="Canvi JPY → EUR", date=when, type=TYPE_EXPENSE)
    entries.add_movement(
        subaccount_id="sub-01",
        amount=500,
        concept="Canvi EUR → JPY",
        date=when - timedelta(days=1),
        type=TYPE_INCOME,
    )

    items = _history(client, "sub-01").json()["items"]

    assert [(item["id"], item["amount"], item["type"]) for item in items] == [
        ("smov-02", 100, "expense"),
        ("smov-01", 1754, "income"),
        ("smov-03", 500, "income"),
    ]
    assert items[1] == {
        "id": "smov-01",
        "amount": 1754,
        "concept": "Canvi EUR → JPY",
        "date": when.isoformat(),
        "type": "income",
    }


def test_el10_the_main_account_has_no_subaccount_history(client: TestClient) -> None:
    # L'historial del compte en euros és GET /api/movements (decisió del PO).
    response = _history(client, "main")

    assert response.status_code == 404
    assert response.json() == NOT_FOUND


def test_el11_another_users_history_answers_as_unknown(client: TestClient) -> None:
    _create(client, "USD")  # de l'usuari 1

    response = _history(client, "sub-01", headers=EMPTY_USER)

    assert response.status_code == 404
    assert response.json() == NOT_FOUND


def test_unknown_subaccount_history(client: TestClient) -> None:
    response = _history(client, "sub-99")

    assert response.status_code == 404
    assert response.json() == NOT_FOUND


# --- Sense sessió (EL-09) -------------------------------------------------------------


@pytest.fixture
def strict_client(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    """App amb ALLOW_X_USER_ID=0, com al desplegament des de la T03.5."""
    monkeypatch.setenv("ALLOW_X_USER_ID", "0")
    with TestClient(create_app()) as client:
        yield client


@pytest.mark.parametrize(
    ("method", "path"),
    [("POST", "/api/subaccounts/sub-01/delete"), ("GET", "/api/subaccounts/sub-01/movements")],
)
def test_el09_routes_need_a_session(strict_client: TestClient, method: str, path: str) -> None:
    response = strict_client.request(method, path)

    assert response.status_code == 401
    assert response.json() == {"code": "UNAUTHENTICATED", "message": "Cal iniciar sessió."}


def test_el09_routes_work_with_a_session(strict_client: TestClient) -> None:
    login = strict_client.post("/api/auth/login", json={"identifier": DEMO_IDENTIFIER, "password": SEED_PASSWORD})
    headers = {"Authorization": f"Bearer {login.json()['token']}"}
    _create(strict_client, "USD", headers=headers)

    assert _history(strict_client, "sub-01", headers=headers).json() == {"items": []}
    assert _delete(strict_client, "sub-01", headers=headers).json() == OK


# --- Model i repositori ---------------------------------------------------------------


def _entry(**overrides: object) -> SubaccountMovement:
    values: dict[str, object] = {
        "id": "smov-01",
        "subaccount_id": "sub-01",
        "amount": 10961,
        "concept": "Canvi EUR → USD",
        "date": now_madrid().replace(microsecond=0),
        "type": "income",
        "seq": 1,
    }
    values.update(overrides)
    return SubaccountMovement(**values)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("overrides", "error"),
    [
        ({"id": ""}, TypeError),
        ({"amount": 0}, ValueError),
        ({"amount": -5}, ValueError),
        ({"amount": 10.5}, TypeError),
        ({"amount": True}, TypeError),
        ({"type": "transfer"}, ValueError),
        ({"date": now_madrid().replace(tzinfo=None, microsecond=0)}, ValueError),
        ({"date": now_madrid().replace(microsecond=5)}, ValueError),
    ],
)
def test_subaccount_movement_model_rejects_invalid_data(overrides: dict[str, object], error: type[Exception]) -> None:
    with pytest.raises(error):
        _entry(**overrides)


def test_repository_delete_keeps_the_history_and_an_unknown_id_is_an_error() -> None:
    seed = build_seed()
    repository = SubaccountRepository(seed)
    created = repository.add(user_id=DEMO_USER_ID, currency="USD")
    when = now_madrid().replace(microsecond=0)
    repository.add_movement(subaccount_id=created.id, amount=1, concept="Canvi EUR → USD", date=when, type="income")

    repository.delete(created.id)

    assert repository.get_by_user(DEMO_USER_ID, created.id) is None
    assert [entry.id for entry in seed.subaccount_movements] == ["smov-01"]
    with pytest.raises(KeyError):
        repository.delete(created.id)


def test_repository_add_movement_does_not_spend_an_id_when_the_model_fails() -> None:
    seed = build_seed()
    repository = SubaccountRepository(seed)
    when = now_madrid().replace(microsecond=0)

    with pytest.raises(ValueError):
        repository.add_movement(subaccount_id="sub-01", amount=0, concept="x", date=when, type="income")

    assert seed.subaccount_movements == []
    assert seed.next_subaccount_movement_number == 1
    assert repository.add_movement(subaccount_id="sub-01", amount=5, concept="x", date=when, type="income").id == (
        "smov-01"
    )
