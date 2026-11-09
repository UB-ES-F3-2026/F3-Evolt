"""Tests de T17.2: GET /api/pots i POST /api/pots (docs/api.md §9.1–§9.3).

Proves P-01 a P-19 de docs/proves-estalvi.md, més el model `Pot` i
`PotRepository.add`.

Executar des de backend/:  python -m pytest tests/test_pots.py
"""

import pytest
from fastapi.testclient import TestClient

from app.data.seed import DEMO_USER_ID, EMPTY_USER_ID, SeedData, build_seed
from app.models import DEFAULT_POT_COLOR, POT_COLORS, Pot
from app.repositories import PotRepository

POT_KEYS = {"id", "name", "balance", "target", "color"}
EMPTY_USER = {"X-User-Id": str(EMPTY_USER_ID)}


def _seed(client: TestClient) -> SeedData:
    return client.app.state.seed


def _as_json(pot: Pot) -> dict[str, object]:
    """Forma JSON del contracte (§9.1) d'una guardiola del seed."""
    return {
        "id": pot.id,
        "name": pot.name,
        "balance": pot.balance,
        "target": pot.target,
        "color": pot.color,
    }


def _seed_pots(client: TestClient, user_id: int = DEMO_USER_ID) -> list[dict[str, object]]:
    return [_as_json(pot) for pot in _seed(client).pots if pot.user_id == user_id]


def _state(client: TestClient):
    """Estat que una creació fallida no pot canviar."""
    seed = _seed(client)
    return ([(pot.id, pot.name) for pot in seed.pots], seed.next_pot_number)


def _create(client: TestClient, body: dict[str, object], headers: dict[str, str] | None = None):
    return client.post("/api/pots", json=body, headers=headers)


# --- Llistar (§9.2) -----------------------------------------------------------------


@pytest.mark.memory_only
def test_list_returns_the_demo_user_pots_in_creation_order(client: TestClient) -> None:
    # P-01
    response = client.get("/api/pots")

    assert response.status_code == 200
    assert response.json() == {"items": _seed_pots(client)}
    assert [pot["id"] for pot in response.json()["items"]] == ["pot-01", "pot-02", "pot-03"]


def test_user_without_pots_gets_an_empty_list(client: TestClient) -> None:
    # P-02: l'estat buit de US-17 (criteri 2).
    response = client.get("/api/pots", headers=EMPTY_USER)

    assert response.status_code == 200
    assert response.json() == {"items": []}


# --- Crear (§9.3) -------------------------------------------------------------------


def test_create_pot_with_target_and_default_color(client: TestClient) -> None:
    # P-03 i P-19: «Viatge» amb objectiu de 300 €, sense color.
    response = _create(client, {"name": "Viatge", "target": 30000})

    assert response.status_code == 201
    assert response.json() == {
        "id": "pot-04",
        "name": "Viatge",
        "balance": 0,
        "target": 30000,
        "color": DEFAULT_POT_COLOR,
    }
    assert set(response.json()) == POT_KEYS


def test_new_pot_is_listed_last_with_zero_balance(client: TestClient) -> None:
    # P-04
    before = client.get("/api/pots").json()["items"]
    created = _create(client, {"name": "Viatge", "target": 30000}).json()

    items = client.get("/api/pots").json()["items"]
    assert items == before + [created]
    assert items[-1]["name"] == "Viatge"
    assert items[-1]["balance"] == 0


@pytest.mark.parametrize("body", [{"name": "Fons"}, {"name": "Fons", "target": None}])
def test_target_is_optional(client: TestClient, body: dict[str, object]) -> None:
    # P-05
    response = _create(client, body)

    assert response.status_code == 201
    assert response.json()["target"] is None


@pytest.mark.parametrize("color", sorted(POT_COLORS))
def test_color_from_the_list_is_kept(client: TestClient, color: str) -> None:
    # P-06, amb tots els colors de la llista tancada.
    response = _create(client, {"name": "Viatge", "target": 30000, "color": color})

    assert response.status_code == 201
    assert response.json()["color"] == color


def test_null_color_is_the_default(client: TestClient) -> None:
    response = _create(client, {"name": "Viatge", "color": None})

    assert response.status_code == 201
    assert response.json()["color"] == DEFAULT_POT_COLOR


@pytest.mark.memory_only
def test_name_is_stored_without_surrounding_spaces(client: TestClient) -> None:
    # P-16
    response = _create(client, {"name": "  Viatge  "})

    assert response.status_code == 201
    assert response.json()["name"] == "Viatge"
    assert _seed(client).pots[-1].name == "Viatge"


def test_names_can_repeat(client: TestClient) -> None:
    first = _create(client, {"name": "Vacances"})
    second = _create(client, {"name": "Vacances"})

    assert (first.status_code, second.status_code) == (201, 201)
    assert first.json()["id"] != second.json()["id"]


def test_each_user_sees_only_their_pots(client: TestClient) -> None:
    # P-17
    demo_before = client.get("/api/pots").json()

    response = _create(client, {"name": "Primera"}, headers=EMPTY_USER)

    assert response.status_code == 201
    assert client.get("/api/pots", headers=EMPTY_USER).json() == {"items": [response.json()]}
    assert client.get("/api/pots").json() == demo_before


def test_creating_a_pot_does_not_move_money(client: TestClient) -> None:
    # P-18: ni el saldo del compte ni el `totalSaved` de la Home canvien.
    home_before = client.get("/api/home").json()

    _create(client, {"name": "Viatge", "target": 30000})

    home_after = client.get("/api/home").json()
    assert home_after["balance"] == home_before["balance"]
    assert home_after["totalSaved"] == home_before["totalSaved"]
    assert home_after["lastMovements"] == home_before["lastMovements"]


# --- Errors de negoci (§9.7) ----------------------------------------------------------


@pytest.mark.memory_only
@pytest.mark.parametrize("name", ["", "   ", "\t\n"])
def test_blank_name_is_rejected(client: TestClient, name: str) -> None:
    # P-07 i P-08
    before = _state(client)

    response = _create(client, {"name": name})

    assert response.status_code == 422
    assert response.json() == {
        "code": "INVALID_POT_NAME",
        "message": "El nom de la guardiola no pot estar buit.",
    }
    assert _state(client) == before
    assert len(client.get("/api/pots").json()["items"]) == len(_seed_pots(client))


@pytest.mark.memory_only
@pytest.mark.parametrize("target", [0, -500])
def test_target_zero_or_negative_is_rejected(client: TestClient, target: int) -> None:
    # P-09 i P-10
    before = _state(client)

    response = _create(client, {"name": "Viatge", "target": target})

    assert response.status_code == 422
    assert response.json() == {
        "code": "INVALID_TARGET",
        "message": "L'objectiu ha de ser més gran que 0.",
    }
    assert _state(client) == before


def test_name_is_checked_before_target(client: TestClient) -> None:
    # P-11
    response = _create(client, {"name": "", "target": 0})

    assert response.status_code == 422
    assert response.json()["code"] == "INVALID_POT_NAME"


# --- Format del cos (P5) ----------------------------------------------------------------


@pytest.mark.memory_only
@pytest.mark.parametrize(
    "body",
    [
        # P-12: `target` ha de ser un enter JSON estricte.
        {"name": "Viatge", "target": "300"},
        {"name": "Viatge", "target": 300.5},
        {"name": "Viatge", "target": 300.0},
        {"name": "Viatge", "target": True},
        # P-13: falta `name` o no és un string.
        {},
        {"target": 30000},
        {"name": 123},
        {"name": None},
        # P-14: el color no és de la llista tancada.
        {"name": "Viatge", "color": "red"},
        {"name": "Viatge", "color": "Purple"},
        {"name": "Viatge", "color": 1},
    ],
)
def test_badly_formed_body_is_a_validation_error(client: TestClient, body: dict[str, object]) -> None:
    before = _state(client)

    response = _create(client, body)

    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"
    assert _state(client) == before


def test_format_is_checked_before_the_name(client: TestClient) -> None:
    # Ordre del §9.3: el format va primer, encara que el nom també sigui buit.
    response = _create(client, {"name": "", "target": "300"})

    assert response.json()["code"] == "VALIDATION_ERROR"


def test_rejected_request_does_not_spend_an_id(client: TestClient) -> None:
    # P-15
    assert _create(client, {"name": "Viatge", "target": "300"}).status_code == 422
    assert _create(client, {"name": "", "target": 30000}).status_code == 422

    response = _create(client, {"name": "Viatge", "target": 30000})

    assert response.status_code == 201
    assert response.json()["id"] == "pot-04"


def test_reset_restores_the_pots_and_the_id_counter(client: TestClient) -> None:
    initial = client.get("/api/pots").json()
    _create(client, {"name": "Viatge"})

    client.post("/api/dev/reset")

    assert client.get("/api/pots").json() == initial
    assert _create(client, {"name": "Viatge"}).json()["id"] == "pot-04"


# --- Seed (§9.8) -----------------------------------------------------------------------


def test_seed_pots_have_the_contract_target_and_color() -> None:
    pots = [pot for pot in build_seed().pots if pot.user_id == DEMO_USER_ID]

    assert [(pot.id, pot.name, pot.balance, pot.target, pot.color) for pot in pots] == [
        ("pot-01", "Vacances", 15000, 100000, "blue"),
        ("pot-02", "Emergències", 10000, None, "orange"),
        ("pot-03", "Regal d'aniversari", 5000, 8000, "pink"),
    ]


def test_seed_counter_continues_after_the_seed_pots() -> None:
    seed = build_seed()

    assert seed.next_pot_number == len(seed.pots) + 1


# --- Model i repositori ----------------------------------------------------------------


def _pot_kwargs(**overrides):
    """Arguments per defecte d'una guardiola vàlida."""
    kwargs = {
        "id": "pot-99",
        "user_id": DEMO_USER_ID,
        "name": "Viatge",
        "balance": 0,
        "target": None,
        "color": DEFAULT_POT_COLOR,
    }
    kwargs.update(overrides)
    return kwargs


@pytest.mark.parametrize(
    "overrides, error",
    [
        ({"id": 1}, TypeError),
        ({"id": ""}, TypeError),
        ({"name": "  "}, ValueError),
        ({"balance": -1}, ValueError),
        ({"balance": 1.5}, TypeError),
        ({"target": 0}, ValueError),
        ({"target": "300"}, TypeError),
        ({"target": True}, TypeError),
        ({"color": "red"}, ValueError),
    ],
)
def test_pot_model_rejects_invalid_values(overrides, error) -> None:
    with pytest.raises(error):
        Pot(**_pot_kwargs(**overrides))


def test_repository_add_appends_with_a_new_id() -> None:
    seed = build_seed()
    repository = PotRepository(seed)

    pot = repository.add(user_id=EMPTY_USER_ID, name="Primera", balance=0, target=None, color="teal")

    assert pot.id == "pot-04"
    assert seed.pots[-1] is pot
    assert repository.list_by_user(EMPTY_USER_ID) == [pot]
    assert seed.next_pot_number == 5


def test_repository_add_with_invalid_values_stores_nothing() -> None:
    seed = build_seed()
    repository = PotRepository(seed)

    with pytest.raises(ValueError):
        repository.add(user_id=DEMO_USER_ID, name="Viatge", balance=0, target=0, color="teal")

    assert len(seed.pots) == 3
    assert seed.next_pot_number == 4
