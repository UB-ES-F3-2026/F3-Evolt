"""Tests de T07.5: GET /api/home (docs/api.md §4.1).

Executar des de backend/:  python -m pytest tests/test_home.py

Els valors esperats surten de les dades en memòria de l'app del test, no de
números escrits a mà: així els tests no s'han de tocar si canvia el seed.
"""

from fastapi.testclient import TestClient

from app.data.seed import DEMO_USER_ID, EMPTY_USER_ID, SeedData
from app.models import Movement

HOME_KEYS = {"balance", "totalSaved", "lastMovements"}
MOVEMENT_KEYS = {"id", "amount", "concept", "date", "type", "icon"}


def _seed(client: TestClient) -> SeedData:
    """Dades en memòria que fa servir l'app (el `client` en crea unes de noves a cada test)."""
    return client.app.state.seed


def _most_recent(seed: SeedData, user_id: int, count: int) -> list[Movement]:
    account_id = seed.accounts[user_id].id
    own = [movement for movement in seed.movements if movement.account_id == account_id]
    return sorted(own, key=Movement.sort_key, reverse=True)[:count]


def _as_contract(movement: Movement) -> dict[str, object]:
    """Un moviment del seed tal com l'ha de retornar l'API (§3)."""
    return {
        "id": movement.id,
        "amount": movement.amount,
        "concept": movement.concept,
        "date": movement.date.isoformat(),
        "type": movement.type,
        "icon": movement.icon,
    }


# --- Usuari 1 -------------------------------------------------------------------


def test_demo_user_balance_matches_seed(client: TestClient) -> None:
    response = client.get("/api/home")

    assert response.status_code == 200
    assert response.json()["balance"] == _seed(client).accounts[DEMO_USER_ID].balance


def test_demo_user_total_saved_is_the_sum_of_all_pots(client: TestClient) -> None:
    seed = _seed(client)
    expected = sum(pot.balance for pot in seed.pots if pot.user_id == DEMO_USER_ID)

    response = client.get("/api/home")

    assert expected > 0
    assert response.json()["totalSaved"] == expected


def test_demo_user_gets_the_five_most_recent_movements_newest_first(
    client: TestClient,
) -> None:
    expected = [_as_contract(m) for m in _most_recent(_seed(client), DEMO_USER_ID, 5)]

    last_movements = client.get("/api/home").json()["lastMovements"]

    assert len(last_movements) == 5
    assert last_movements == expected


def test_last_movements_can_be_fewer_than_five(client: TestClient) -> None:
    # Deixa l'usuari 1 amb només els seus 3 moviments més recents.
    seed = _seed(client)
    kept = _most_recent(seed, DEMO_USER_ID, 3)
    seed.movements[:] = kept

    last_movements = client.get("/api/home").json()["lastMovements"]

    assert last_movements == [_as_contract(m) for m in kept]


# --- Usuari 2 -------------------------------------------------------------------


def test_empty_user_has_no_savings_and_no_movements(client: TestClient) -> None:
    response = client.get("/api/home", headers={"X-User-Id": str(EMPTY_USER_ID)})

    body = response.json()
    assert response.status_code == 200
    assert body["balance"] == _seed(client).accounts[EMPTY_USER_ID].balance
    assert body["totalSaved"] == 0
    assert body["lastMovements"] == []


# --- Forma de la resposta -------------------------------------------------------


def test_response_has_only_contract_keys(client: TestClient) -> None:
    body = client.get("/api/home").json()

    assert set(body) == HOME_KEYS
    assert isinstance(body["balance"], int)
    assert isinstance(body["totalSaved"], int)
    for movement in body["lastMovements"]:
        # Ni `kind` ni cap altre camp intern surt a l'API (§3, §6).
        assert set(movement) == MOVEMENT_KEYS


def test_movement_dates_carry_the_madrid_offset(client: TestClient) -> None:
    for movement in client.get("/api/home").json()["lastMovements"]:
        assert movement["date"][-6:] in {"+02:00", "+01:00"}


def test_unknown_user_header_is_a_validation_error(client: TestClient) -> None:
    response = client.get("/api/home", headers={"X-User-Id": "99"})

    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"
