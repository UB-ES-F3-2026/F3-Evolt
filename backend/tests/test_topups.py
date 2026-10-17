"""Tests de T09.1: POST /api/topups (docs/api.md §4.3).

Executar des de backend/:  python -m pytest tests/test_topups.py
"""

import pytest
from fastapi.testclient import TestClient

from app.data.seed import DEMO_USER_ID, EMPTY_USER_ID, SeedData

FRONTEND_ORIGIN = "http://localhost:5173"
MOVEMENT_KEYS = {"id", "amount", "concept", "date", "type", "icon"}


def _seed(client: TestClient) -> SeedData:
    return client.app.state.seed


def _balance(client: TestClient, user_id: int = DEMO_USER_ID) -> int:
    return _seed(client).accounts[user_id].balance


def _state(client: TestClient):
    """Estat que una recàrrega fallida no pot canviar."""
    seed = _seed(client)
    return (
        {user_id: account.balance for user_id, account in seed.accounts.items()},
        [m.id for m in seed.movements],
    )


# --- Recàrrega correcta -----------------------------------------------------------------


def test_topup_returns_201_with_new_balance_and_movement(client: TestClient) -> None:
    before = _balance(client)

    response = client.post("/api/topups", json={"amount": 50000})

    assert response.status_code == 201
    body = response.json()
    assert set(body) == {"balance", "movement"}
    assert body["balance"] == before + 50000
    movement = body["movement"]
    # Ni `kind`, ni `seq`, ni `account_id` surten a l'API (§3, §6).
    assert set(movement) == MOVEMENT_KEYS
    assert movement["amount"] == 50000
    assert movement["concept"] == "Recàrrega"
    assert movement["type"] == "income"
    assert movement["icon"] == "topup"
    assert movement["id"] == "mov-31"


def test_topup_date_follows_the_contract(client: TestClient) -> None:
    date = client.post("/api/topups", json={"amount": 100}).json()["movement"]["date"]

    # 2026-10-17T16:30:00+02:00: desplaçament de Madrid i precisió de segons (P7).
    assert date[-6:] in {"+02:00", "+01:00"}
    assert len(date) == len("2026-10-17T16:30:00+02:00")


# --- Criteri de fet de T09.1 ---------------------------------------------------------------


def test_home_and_movements_show_the_topup_first(client: TestClient) -> None:
    created = client.post("/api/topups", json={"amount": 2500}).json()

    home = client.get("/api/home").json()
    assert home["balance"] == created["balance"]
    assert home["lastMovements"][0] == created["movement"]

    listed = client.get("/api/movements").json()
    assert listed["items"][0] == created["movement"]


def test_empty_user_can_top_up(client: TestClient) -> None:
    headers = {"X-User-Id": str(EMPTY_USER_ID)}

    response = client.post("/api/topups", json={"amount": 1000}, headers=headers)

    assert response.status_code == 201
    assert response.json()["balance"] == 1000
    assert client.get("/api/movements", headers=headers).json()["items"] == [
        response.json()["movement"]
    ]


@pytest.mark.parametrize("amount", [1, 50000])
def test_limits_of_a_single_topup_are_allowed(client: TestClient, amount: int) -> None:
    assert client.post("/api/topups", json={"amount": amount}).status_code == 201


# --- Límits per recàrrega ------------------------------------------------------------------


@pytest.mark.parametrize(
    "amount, code, message",
    [
        (0, "INVALID_AMOUNT", "L'import ha de ser més gran que 0."),
        (-100, "INVALID_AMOUNT", "L'import ha de ser més gran que 0."),
        (50001, "AMOUNT_OVER_LIMIT", "L'import màxim per recàrrega és de 500,00 €."),
        (60000, "AMOUNT_OVER_LIMIT", "L'import màxim per recàrrega és de 500,00 €."),
    ],
)
def test_amount_out_of_limits_is_rejected(
    client: TestClient, amount: int, code: str, message: str
) -> None:
    before = _state(client)

    response = client.post("/api/topups", json={"amount": amount})

    assert response.status_code == 422
    # Sense `details` (P6).
    assert response.json() == {"code": code, "message": message}
    assert _state(client) == before


# --- Format del cos (P5) -------------------------------------------------------------------


@pytest.mark.parametrize(
    "body",
    [
        {"amount": "500"},  # string
        {"amount": 500.0},  # decimal, encara que sigui ".0"
        {"amount": 500.5},
        {"amount": True},
        {"amount": None},
        {},  # falta amount
        [50000],  # no és un objecte
    ],
)
def test_malformed_body_is_a_validation_error(client: TestClient, body) -> None:
    before = _state(client)

    response = client.post("/api/topups", json=body)

    assert response.status_code == 422
    assert response.json() == {
        "code": "VALIDATION_ERROR",
        "message": "Les dades de la petició no són vàlides.",
    }
    assert _state(client) == before


def test_body_that_is_not_json_is_a_validation_error(client: TestClient) -> None:
    response = client.post(
        "/api/topups", content="amount=500", headers={"Content-Type": "application/json"}
    )

    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"


def test_format_is_checked_before_limits(client: TestClient) -> None:
    # Ordre del contracte: un 60000.0 és VALIDATION_ERROR, no AMOUNT_OVER_LIMIT.
    response = client.post("/api/topups", json={"amount": 60000.0})
    assert response.json()["code"] == "VALIDATION_ERROR"


# --- Usuari i navegador ----------------------------------------------------------------------


def test_unknown_user_header_is_a_validation_error(client: TestClient) -> None:
    before = _state(client)

    response = client.post("/api/topups", json={"amount": 100}, headers={"X-User-Id": "99"})

    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"
    assert _state(client) == before


def test_preflight_from_frontend_is_allowed(client: TestClient) -> None:
    # El navegador pregunta abans d'un POST amb JSON i X-User-Id.
    response = client.options(
        "/api/topups",
        headers={
            "Origin": FRONTEND_ORIGIN,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type,x-user-id",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == FRONTEND_ORIGIN


def test_get_is_not_a_route(client: TestClient) -> None:
    # Mètode no definit → INTERNAL_ERROR (docs/api.md §5).
    response = client.get("/api/topups")
    assert response.status_code == 500
    assert response.json()["code"] == "INTERNAL_ERROR"
