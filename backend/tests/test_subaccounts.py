"""Tests de T25.2: GET /api/subaccounts i POST /api/subaccounts (docs/api.md §12.1–§12.4).

Proves DV-01 a DV-16 de docs/proves-multidivisa.md, més la taula de divises, el
total en euros, el model `Subaccount` i el repositori.

Executar des de backend/:  python -m pytest tests/test_subaccounts.py
"""

import threading
import time
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.data.seed import DEMO_IDENTIFIER, DEMO_USER_ID, EMPTY_USER_ID, SEED_PASSWORD, build_seed
from app.main import create_app
from app.models import CURRENCIES, Subaccount, rate_bps, total_in_euros
from app.repositories import SubaccountRepository
from app.repositories.atomic import MemoryAtomic
from app.services.errors import CURRENCY_EXISTS, ApiError
from app.services.subaccount_service import create_subaccount

EMPTY_USER = {"X-User-Id": str(EMPTY_USER_ID)}
MAIN_SEED = {"id": "main", "currency": "EUR", "balance": 379521, "isMain": True, "rateBps": 10000}
CURRENCY_EXISTS_BODY = {"code": "CURRENCY_EXISTS", "message": "Ja tens un subcompte en aquesta divisa."}
NOT_SUPPORTED_BODY = {
    "code": "CURRENCY_NOT_SUPPORTED",
    "message": "Aquesta divisa no és a la llista de divises disponibles.",
}


def _create(client: TestClient, currency: object, headers: dict[str, str] | None = None):
    return client.post("/api/subaccounts", json={"currency": currency}, headers=headers)


def _items(client: TestClient, headers: dict[str, str] | None = None) -> list[dict[str, object]]:
    return client.get("/api/subaccounts", headers=headers).json()["items"]


# --- Llistar (§12.3) ----------------------------------------------------------------


def test_dv01_demo_user_only_has_the_main_euro_account(client: TestClient) -> None:
    response = client.get("/api/subaccounts")

    assert response.status_code == 200
    assert response.json() == {"items": [MAIN_SEED], "totalInEuros": 379521}


def test_dv02_new_user_has_the_main_account_at_zero(client: TestClient) -> None:
    response = client.get("/api/subaccounts", headers=EMPTY_USER)

    assert response.status_code == 200
    assert response.json() == {
        "items": [{"id": "main", "currency": "EUR", "balance": 0, "isMain": True, "rateBps": 10000}],
        "totalInEuros": 0,
    }


@pytest.mark.memory_only
def test_total_in_euros_uses_the_fixed_rate_table(client: TestClient) -> None:
    # Criteri de la #167 i exemple de §12.3: 1.250,50 € i 317,55 $ → «Total ≈ 1.540,20 €».
    # Sense «Aportar» ni canvi (T27.1), el saldo del subcompte es prepara al seed.
    seed = client.app.state.seed
    seed.accounts[DEMO_USER_ID].balance = 125050
    _create(client, "USD")
    seed.subaccounts[0].balance = 31755

    response = client.get("/api/subaccounts")

    assert response.json() == {
        "items": [
            {"id": "main", "currency": "EUR", "balance": 125050, "isMain": True, "rateBps": 10000},
            {"id": "sub-01", "currency": "USD", "balance": 31755, "isMain": False, "rateBps": 9123},
        ],
        "totalInEuros": 154020,
    }


# --- Crear (§12.4) ------------------------------------------------------------------


def test_dv03_create_a_dollar_subaccount_at_zero(client: TestClient) -> None:
    response = _create(client, "USD")

    assert response.status_code == 201
    assert response.json() == {"id": "sub-01", "currency": "USD", "balance": 0, "isMain": False, "rateBps": 9123}


def test_dv04_new_subaccount_goes_after_main_and_does_not_move_the_total(client: TestClient) -> None:
    _create(client, "USD")

    response = client.get("/api/subaccounts")

    assert response.json() == {
        "items": [MAIN_SEED, {"id": "sub-01", "currency": "USD", "balance": 0, "isMain": False, "rateBps": 9123}],
        "totalInEuros": 379521,
    }


def test_dv05_repeated_currency_is_rejected(client: TestClient) -> None:
    _create(client, "USD")

    response = _create(client, "USD")

    assert response.status_code == 422
    assert response.json() == CURRENCY_EXISTS_BODY
    assert len(_items(client)) == 2


def test_dv06_euro_already_exists_as_the_main_account(client: TestClient) -> None:
    response = _create(client, "EUR")

    assert response.status_code == 422
    assert response.json() == CURRENCY_EXISTS_BODY
    assert _items(client) == [MAIN_SEED]


@pytest.mark.parametrize(
    "currency",
    [
        "BTC",  # DV-07: fora de la llista
        "usd",  # DV-08: el codi distingeix majúscules
    ],
)
def test_dv07_dv08_currency_outside_the_closed_list_is_not_supported(client: TestClient, currency: str) -> None:
    response = _create(client, currency)

    assert response.status_code == 422
    assert response.json() == NOT_SUPPORTED_BODY
    assert _items(client) == [MAIN_SEED]


@pytest.mark.parametrize("body", [{}, {"currency": 840}, {"currency": None}])
def test_dv09_malformed_body_is_a_validation_error(client: TestClient, body: dict[str, object]) -> None:
    response = client.post("/api/subaccounts", json=body)

    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"
    assert _items(client) == [MAIN_SEED]


def test_dv10_an_error_does_not_spend_an_id(client: TestClient) -> None:
    assert _create(client, "BTC").status_code == 422
    assert _create(client, "EUR").status_code == 422

    response = _create(client, "USD")

    assert response.status_code == 201
    assert response.json()["id"] == "sub-01"


def test_dv11_yen_subaccount(client: TestClient) -> None:
    response = _create(client, "JPY")

    assert response.status_code == 201
    assert response.json() == {"id": "sub-01", "currency": "JPY", "balance": 0, "isMain": False, "rateBps": 5700}


def test_dv12_the_four_foreign_currencies_in_creation_order(client: TestClient) -> None:
    created = [_create(client, code) for code in ("USD", "GBP", "CHF", "JPY")]

    assert [response.status_code for response in created] == [201, 201, 201, 201]
    assert [response.json()["id"] for response in created] == ["sub-01", "sub-02", "sub-03", "sub-04"]
    items = _items(client)
    assert [(item["id"], item["currency"]) for item in items] == [
        ("main", "EUR"),
        ("sub-01", "USD"),
        ("sub-02", "GBP"),
        ("sub-03", "CHF"),
        ("sub-04", "JPY"),
    ]
    assert [item["rateBps"] for item in items] == [10000, 9123, 11680, 10355, 5700]


@pytest.mark.memory_only
def test_dv13_two_creations_at_once_only_one_wins(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    # L'espera dins de l'escriptura obre la finestra entre comprovar la divisa i crear el
    # subcompte: sense `atomic.run(...)`, totes dues peticions passarien la comprovació.
    seed = client.app.state.seed
    original_add = SubaccountRepository.add

    def slow_add(self: SubaccountRepository, **kwargs: object) -> Subaccount:
        time.sleep(0.1)
        return original_add(self, **kwargs)

    monkeypatch.setattr(SubaccountRepository, "add", slow_add)
    run = client.app.state.atomic
    barrier = threading.Barrier(2)
    outcomes: list[str] = []

    def create_at_once() -> None:
        barrier.wait()
        try:
            run.run(lambda: create_subaccount(DEMO_USER_ID, "USD", SubaccountRepository(seed)))
            outcomes.append("ok")
        except ApiError as error:
            outcomes.append(error.code)

    threads = [threading.Thread(target=create_at_once) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert isinstance(run, MemoryAtomic)
    assert sorted(outcomes) == sorted(["ok", CURRENCY_EXISTS])
    assert [item["id"] for item in _items(client)] == ["main", "sub-01"]


def test_dv14_ids_are_unique_across_users_and_each_user_sees_only_theirs(client: TestClient) -> None:
    _create(client, "USD")

    response = _create(client, "USD", headers=EMPTY_USER)

    assert response.status_code == 201
    assert response.json()["id"] == "sub-02"
    assert [item["id"] for item in _items(client)] == ["main", "sub-01"]
    assert [item["id"] for item in _items(client, headers=EMPTY_USER)] == ["main", "sub-02"]


def test_dv16_dev_reset_removes_the_subaccounts(client: TestClient) -> None:
    _create(client, "USD")

    assert client.post("/api/dev/reset").status_code == 200

    assert _items(client) == [MAIN_SEED]
    assert _create(client, "GBP").json()["id"] == "sub-01"


# --- Sense sessió (DV-15) -------------------------------------------------------------


@pytest.fixture
def strict_client(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    """App amb ALLOW_X_USER_ID=0, com al desplegament des de la T03.5."""
    monkeypatch.setenv("ALLOW_X_USER_ID", "0")
    with TestClient(create_app()) as client:
        yield client


@pytest.mark.parametrize("method", ["GET", "POST"])
def test_dv15_routes_need_a_session(strict_client: TestClient, method: str) -> None:
    response = strict_client.request(method, "/api/subaccounts", json={"currency": "USD"})

    assert response.status_code == 401
    assert response.json() == {"code": "UNAUTHENTICATED", "message": "Cal iniciar sessió."}


def test_dv15_routes_work_with_a_session(strict_client: TestClient) -> None:
    login = strict_client.post("/api/auth/login", json={"identifier": DEMO_IDENTIFIER, "password": SEED_PASSWORD})
    headers = {"Authorization": f"Bearer {login.json()['token']}"}

    assert strict_client.post("/api/subaccounts", json={"currency": "USD"}, headers=headers).status_code == 201
    assert len(strict_client.get("/api/subaccounts", headers=headers).json()["items"]) == 2


# --- Taula de divises i total (§12.1) ---------------------------------------------------


def test_closed_list_of_five_currencies_with_fixed_rates() -> None:
    assert {code: (c.decimals, c.rate_bps) for code, c in CURRENCIES.items()} == {
        "EUR": (2, 10000),
        "USD": (2, 9123),
        "GBP": (2, 11680),
        "CHF": (2, 10355),
        "JPY": (0, 5700),
    }
    assert rate_bps("JPY") == 5700


def test_total_rounds_each_account_half_up_before_adding() -> None:
    # §12.1: 31755 $ × 9123 / 10000 = 28970,08… → 28970; 1 ¥ = 0,57 cèntims → 1; 1 $ = 0,9123 → 1.
    assert total_in_euros([(125050, "EUR"), (31755, "USD")]) == 154020
    assert total_in_euros([(1, "JPY")]) == 1
    assert total_in_euros([(1, "USD"), (1, "JPY")]) == 2
    assert total_in_euros([]) == 0


# --- Model i repositori -----------------------------------------------------------------


def _subaccount(**overrides: object) -> Subaccount:
    kwargs: dict[str, object] = {"id": "sub-99", "user_id": DEMO_USER_ID, "currency": "USD", "balance": 0, "number": 99}
    kwargs.update(overrides)
    return Subaccount(**kwargs)


@pytest.mark.parametrize(
    "overrides, error",
    [
        ({"currency": "BTC"}, ValueError),
        ({"currency": "EUR"}, ValueError),
        ({"balance": -1}, ValueError),
        ({"balance": 1.5}, TypeError),
        ({"balance": True}, TypeError),
        ({"id": ""}, TypeError),
    ],
)
def test_subaccount_model_rejects_invalid_data(overrides: dict[str, object], error: type[Exception]) -> None:
    with pytest.raises(error):
        _subaccount(**overrides)


def test_repository_add_does_not_spend_an_id_when_the_model_fails() -> None:
    seed = build_seed()
    repository = SubaccountRepository(seed)

    with pytest.raises(ValueError):
        repository.add(user_id=DEMO_USER_ID, currency="EUR")

    assert seed.subaccounts == []
    assert repository.add(user_id=DEMO_USER_ID, currency="CHF").id == "sub-01"


def test_repository_get_by_user_hides_other_users_subaccounts() -> None:
    repository = SubaccountRepository(build_seed())
    created = repository.add(user_id=DEMO_USER_ID, currency="GBP")

    assert repository.get_by_user(DEMO_USER_ID, created.id) == created
    assert repository.get_by_user(EMPTY_USER_ID, created.id) is None
    assert repository.get_by_user(DEMO_USER_ID, "sub-77") is None
