"""Tests de T10.2: counterparty, status i reference de Movement (docs/api.md §10.1 i §10.7).

Proves F-01 a F-07 de docs/proves-moviments.md, més el model i `MovementRepository.add`.

Executar des de backend/:  python -m pytest tests/test_movement_fields.py
"""

from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from app.data.seed import DEMO_USER_ID, SeedData, build_seed
from app.models import (
    KIND_OTHER,
    MADRID_TZ,
    MOVEMENT_STATUS_COMPLETED,
    MOVEMENT_STATUS_PENDING,
    MOVEMENT_STATUSES,
    TYPE_EXPENSE,
    Movement,
)
from app.repositories import MovementRepository, PotRepository

MOVEMENT_KEYS = {"id", "amount", "concept", "date", "type", "icon", "counterparty", "status", "reference"}
# Dades de partida de docs/proves-moviments.md (§10.7).
COUNTERPARTIES = {
    "mov-03": "Empresa Demo SL",
    "mov-09": "Marta Puig",
    "mov-10": "Jordi Serra",
    "mov-17": "Empresa Demo SL",
    "mov-18": "Laia Vidal",
    "mov-24": "Pau Ferrer",
    "mov-29": "Núria Soler",
}
NOW = datetime(2026, 11, 3, 10, 0, 0, tzinfo=MADRID_TZ)


def _seed(client: TestClient) -> SeedData:
    return client.app.state.seed


def _listed(client: TestClient) -> list[dict[str, object]]:
    return client.get("/api/movements", params={"limit": 50}).json()["items"]


# --- Seed (§10.7) -----------------------------------------------------------------------


def test_every_movement_has_the_new_fields(client: TestClient) -> None:
    # F-01
    items = _listed(client)

    assert len(items) == 30
    for item in items:
        assert "counterparty" in item
        assert item["status"] in MOVEMENT_STATUSES
        assert item["reference"]
    assert len({item["reference"] for item in items}) == 30


def test_reference_follows_the_creation_order() -> None:
    # P37: el mateix número que l'id.
    for number, movement in enumerate(build_seed(now=NOW).movements, start=1):
        assert movement.id == f"mov-{number:02d}"
        assert movement.reference == f"EVT-{number:06d}"


def test_counterparties_are_the_ones_of_the_contract(client: TestClient) -> None:
    # F-02, i `null` a la resta (P35).
    for item in _listed(client):
        assert item["counterparty"] == COUNTERPARTIES.get(item["id"])


def test_transfers_and_salaries_have_a_counterparty_and_topups_do_not() -> None:
    # F-02 i F-03, mirant la regla i no els ids.
    for movement in build_seed(now=NOW).movements:
        if movement.icon in {"transfer", "salary"}:
            assert movement.counterparty
        else:
            assert movement.counterparty is None


def test_only_the_most_recent_movement_is_pending(client: TestClient) -> None:
    # F-04
    items = _listed(client)

    assert [item["id"] for item in items if item["status"] == MOVEMENT_STATUS_PENDING] == ["mov-30"]
    assert items[0]["id"] == "mov-30"
    assert sum(item["status"] == MOVEMENT_STATUS_COMPLETED for item in items) == 29


def test_a_pending_movement_already_counts_for_the_balance(client: TestClient) -> None:
    # F-07
    seed = _seed(client)

    assert client.get("/api/home").json()["balance"] == sum(m.signed_amount for m in seed.movements)
    assert any(m.status == MOVEMENT_STATUS_PENDING for m in seed.movements)


# --- Respostes de l'API -----------------------------------------------------------------


def test_home_list_topup_and_contribution_return_exactly_the_contract_keys(client: TestClient) -> None:
    # F-05, i també l'aportació: el moviment és el mateix objecte a totes les respostes (§3).
    responses = [
        *client.get("/api/home").json()["lastMovements"],
        *_listed(client),
        client.post("/api/topups", json={"amount": 1000}).json()["movement"],
        client.post("/api/pots/pot-01/contributions", json={"amount": 1000}).json()["movement"],
    ]

    for movement in responses:
        assert set(movement) == MOVEMENT_KEYS


def test_bizum_of_the_contract_example(client: TestClient) -> None:
    # L'exemple del §10.1, llevat de la data, que és relativa a avui.
    bizum = next(item for item in _listed(client) if item["id"] == "mov-29")

    assert {key: value for key, value in bizum.items() if key != "date"} == {
        "id": "mov-29",
        "amount": 1000,
        "concept": "Bizum enviat",
        "type": "expense",
        "icon": "transfer",
        "counterparty": "Núria Soler",
        "status": "completed",
        "reference": "EVT-000029",
    }


# --- Moviments nous (§10.1, P38) --------------------------------------------------------


def test_new_topup_is_completed_with_a_new_reference(client: TestClient) -> None:
    # F-06
    movement = client.post("/api/topups", json={"amount": 1000}).json()["movement"]

    assert movement["status"] == "completed"
    assert movement["counterparty"] is None
    assert movement["reference"] == "EVT-000031"
    references = [item["reference"] for item in _listed(client)]
    assert references.count("EVT-000031") == 1


def test_new_contribution_is_completed_with_a_new_reference(client: TestClient) -> None:
    # L'exemple del §9.4.
    movement = client.post("/api/pots/pot-01/contributions", json={"amount": 3000}).json()["movement"]

    assert movement["status"] == "completed"
    assert movement["counterparty"] is None
    assert movement["reference"] == "EVT-000031"


def test_new_movements_get_consecutive_references(client: TestClient) -> None:
    topup = client.post("/api/topups", json={"amount": 1000}).json()["movement"]
    contribution = client.post("/api/pots/pot-01/contributions", json={"amount": 1000}).json()["movement"]

    assert (topup["reference"], contribution["reference"]) == ("EVT-000031", "EVT-000032")


def test_rejected_topup_does_not_spend_a_reference(client: TestClient) -> None:
    assert client.post("/api/topups", json={"amount": 0}).status_code == 422

    assert client.post("/api/topups", json={"amount": 1000}).json()["movement"]["reference"] == "EVT-000031"


def test_contribution_that_fails_halfway_does_not_spend_a_reference(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    # El moviment ja s'ha creat quan falla l'historial: en desfer-lo, la referència queda lliure.
    def fail(*args: object, **kwargs: object) -> None:
        raise RuntimeError("escriptura fallida")

    monkeypatch.setattr(PotRepository, "add_movement", fail)
    assert client.post("/api/pots/pot-01/contributions", json={"amount": 3000}).status_code == 500
    monkeypatch.undo()

    response = client.post("/api/pots/pot-01/contributions", json={"amount": 3000})

    assert response.json()["movement"]["reference"] == "EVT-000031"


def test_reset_restores_the_references(client: TestClient) -> None:
    client.post("/api/topups", json={"amount": 1000})

    client.post("/api/dev/reset")

    assert client.post("/api/topups", json={"amount": 1000}).json()["movement"]["reference"] == "EVT-000031"


# --- Model i repositori -----------------------------------------------------------------


def _movement_kwargs(**overrides):
    """Arguments per defecte d'un moviment vàlid."""
    kwargs = {
        "id": "mov-99",
        "account_id": DEMO_USER_ID,
        "amount": 100,
        "concept": "Prova",
        "date": NOW,
        "type": TYPE_EXPENSE,
        "icon": "other",
        "kind": KIND_OTHER,
        "seq": 99,
        "counterparty": None,
        "status": MOVEMENT_STATUS_COMPLETED,
        "reference": "EVT-000099",
    }
    kwargs.update(overrides)
    return kwargs


@pytest.mark.parametrize(
    "overrides, error",
    [
        ({"counterparty": ""}, ValueError),
        ({"counterparty": "   "}, ValueError),
        ({"counterparty": 5}, ValueError),
        ({"status": "done"}, ValueError),
        ({"status": None}, ValueError),
        ({"reference": ""}, TypeError),
        ({"reference": None}, TypeError),
        ({"reference": 31}, TypeError),
    ],
)
def test_model_rejects_invalid_new_fields(overrides, error) -> None:
    with pytest.raises(error):
        Movement(**_movement_kwargs(**overrides))


@pytest.mark.parametrize("status", sorted(MOVEMENT_STATUSES))
def test_model_accepts_both_statuses_and_a_counterparty(status: str) -> None:
    movement = Movement(**_movement_kwargs(status=status, counterparty="Marta Puig"))

    assert (movement.status, movement.counterparty) == (status, "Marta Puig")


def _add_kwargs(**overrides):
    """Arguments per defecte de MovementRepository.add()."""
    kwargs = {
        "account_id": DEMO_USER_ID,
        "amount": 100,
        "concept": "Prova",
        "date": NOW,
        "type": TYPE_EXPENSE,
        "icon": "other",
        "kind": KIND_OTHER,
    }
    kwargs.update(overrides)
    return kwargs


def test_repository_add_generates_the_reference_with_the_defaults() -> None:
    movement = MovementRepository(build_seed(now=NOW)).add(**_add_kwargs())

    assert movement.reference == "EVT-000031"
    assert movement.status == MOVEMENT_STATUS_COMPLETED
    assert movement.counterparty is None


def test_repository_add_keeps_the_given_fields() -> None:
    movement = MovementRepository(build_seed(now=NOW)).add(
        **_add_kwargs(counterparty="Marta Puig", status=MOVEMENT_STATUS_PENDING)
    )

    assert movement.counterparty == "Marta Puig"
    assert movement.status == MOVEMENT_STATUS_PENDING


def test_repository_add_with_invalid_fields_stores_nothing() -> None:
    seed = build_seed(now=NOW)

    with pytest.raises(ValueError):
        MovementRepository(seed).add(**_add_kwargs(status="done"))

    assert len(seed.movements) == 30
    assert seed.next_movement_number == 31


def test_removing_the_latest_movement_frees_its_reference() -> None:
    seed = build_seed(now=NOW)
    movements = MovementRepository(seed)

    movements.remove(movements.add(**_add_kwargs()))

    assert movements.add(**_add_kwargs()).reference == "EVT-000031"
