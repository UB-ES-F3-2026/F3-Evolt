"""Tests de T08.1: GET /api/movements (docs/api.md §4.2).

Executar des de backend/:  python -m pytest tests/test_movements.py

Els esperats surten de les dades en memòria de l'app del test, no de números
escrits a mà: així els tests no s'han de tocar si canvia el seed.
"""

import pytest
from fastapi.testclient import TestClient

from app.data.seed import DEMO_USER_ID, EMPTY_USER_ID, SeedData
from app.models import Movement

PAGE_KEYS = {"items", "nextOffset"}
MOVEMENT_KEYS = {"id", "amount", "concept", "date", "type", "icon"}


def _seed(client: TestClient) -> SeedData:
    return client.app.state.seed


def _expected_ids(client: TestClient, user_id: int) -> list[str]:
    """Ids de tots els moviments de l'usuari, del més recent al més antic."""
    seed = _seed(client)
    account_id = seed.accounts[user_id].id
    own = [m for m in seed.movements if m.account_id == account_id]
    return [m.id for m in sorted(own, key=Movement.sort_key, reverse=True)]


# --- Criteris de fet de T08.1 ----------------------------------------------------------


def test_demo_user_pages_all_movements_in_two_pages(client: TestClient) -> None:
    first = client.get("/api/movements")
    assert first.status_code == 200
    first_body = first.json()
    assert len(first_body["items"]) == 20
    assert first_body["nextOffset"] == 20

    second_body = client.get("/api/movements", params={"offset": 20}).json()
    assert len(second_body["items"]) == 10
    assert second_body["nextOffset"] is None

    ids = [m["id"] for m in first_body["items"] + second_body["items"]]
    assert ids == _expected_ids(client, DEMO_USER_ID)


def test_empty_user_gets_empty_page(client: TestClient) -> None:
    response = client.get("/api/movements", headers={"X-User-Id": str(EMPTY_USER_ID)})

    assert response.status_code == 200
    assert response.json() == {"items": [], "nextOffset": None}


# --- Forma de la resposta ----------------------------------------------------------------


def test_response_has_only_contract_keys(client: TestClient) -> None:
    body = client.get("/api/movements").json()

    assert set(body) == PAGE_KEYS
    for movement in body["items"]:
        # Ni `kind`, ni `seq`, ni `account_id` surten a l'API (§3, §6).
        assert set(movement) == MOVEMENT_KEYS
        assert isinstance(movement["amount"], int) and movement["amount"] > 0
        assert movement["date"][-6:] in {"+02:00", "+01:00"}


def test_next_offset_is_present_even_when_null(client: TestClient) -> None:
    raw = client.get("/api/movements", params={"limit": 50}).text
    assert '"nextOffset":null' in raw


def test_first_five_match_home_last_movements(client: TestClient) -> None:
    # §4.1: `lastMovements` coincideix amb els 5 primers del llistat.
    listed = client.get("/api/movements", params={"limit": 5}).json()["items"]
    home = client.get("/api/home").json()["lastMovements"]
    assert listed == home


# --- Paginació -----------------------------------------------------------------------------


def test_custom_limit_and_offset(client: TestClient) -> None:
    body = client.get("/api/movements", params={"offset": 5, "limit": 5}).json()

    assert [m["id"] for m in body["items"]] == _expected_ids(client, DEMO_USER_ID)[5:10]
    assert body["nextOffset"] == 10


@pytest.mark.parametrize("offset", [30, 31, 1000])
def test_offset_beyond_total_is_empty_not_error(client: TestClient, offset: int) -> None:
    # P3: un offset >= total retorna 200 amb pàgina buida.
    response = client.get("/api/movements", params={"offset": offset})

    assert response.status_code == 200
    assert response.json() == {"items": [], "nextOffset": None}


@pytest.mark.parametrize("limit", [1, 50])
def test_limit_bounds_are_accepted(client: TestClient, limit: int) -> None:
    response = client.get("/api/movements", params={"limit": limit})

    assert response.status_code == 200
    assert len(response.json()["items"]) == min(limit, 30)


# --- Paràmetres no vàlids ------------------------------------------------------------------


@pytest.mark.parametrize(
    "params",
    [
        {"offset": -1},
        {"limit": 0},
        {"limit": 51},
        {"limit": "abc"},
        {"offset": "1.5"},
    ],
)
def test_invalid_parameters_return_validation_error(client: TestClient, params: dict) -> None:
    response = client.get("/api/movements", params=params)

    assert response.status_code == 422
    assert response.json() == {
        "code": "VALIDATION_ERROR",
        "message": "Les dades de la petició no són vàlides.",
    }


def test_unknown_user_header_is_a_validation_error(client: TestClient) -> None:
    response = client.get("/api/movements", headers={"X-User-Id": "99"})

    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"
