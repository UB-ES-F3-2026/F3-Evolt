"""Tests de T20.1: percentatge i estat de l'objectiu de les guardioles (docs/api.md §11.1).

Proves O-01 a O-08 de docs/proves-estalvi.md, inclosa la O-04 (retirar torna la
guardiola a «En progrés»), que es pot provar des que la US-19 és a `develop`.

Executar des de backend/:  python -m pytest tests/test_pot_progress.py
"""

import pytest
from fastapi.testclient import TestClient

from app.services.pot_progress import GOAL_ACHIEVED, GOAL_IN_PROGRESS, pot_progress

POT_KEYS = {"id", "name", "balance", "target", "color", "percentage", "goalStatus"}


def _pots(client: TestClient) -> dict[str, dict]:
    return {pot["id"]: pot for pot in client.get("/api/pots").json()["items"]}


def _contribute(client: TestClient, pot_id: str, amount: int) -> dict:
    response = client.post(f"/api/pots/{pot_id}/contributions", json={"amount": amount})
    assert response.status_code == 201
    return response.json()["pot"]


# --- Funció pura (§11.6) -----------------------------------------------------------------


@pytest.mark.parametrize(
    ("balance", "target", "percentage"),
    [
        (5000, 8000, 63),  # 62,5: els mitjos cap amunt, no l'arrodoniment bancari de round()
        (4990, 8000, 62),  # 62,375
        (1, 8, 13),  # 12,5
        (10, 2000, 1),  # 0,5
        (3, 2000, 0),  # 0,15
        (7999, 8000, 99),  # 99,9875: es queda a 99 fins a arribar-hi (decisió de PO, #194)
        (0, 30000, 0),
    ],
)
def test_percentage_rounds_halves_up_and_stays_in_progress_below_target(
    balance: int, target: int, percentage: int
) -> None:
    # O-07: per sota de l'objectiu sempre és «En progrés».
    assert pot_progress(balance, target) == (percentage, GOAL_IN_PROGRESS)


@pytest.mark.parametrize(("balance", "target"), [(7999, 8000), (99_960, 100_000), (999, 1000)])
def test_never_100_before_reaching_the_target(balance: int, target: int) -> None:
    # Decisió de PO (#194): 79,99 € de 80,00 € és «99 %» i «En progrés», no 100 %.
    assert pot_progress(balance, target) == (99, GOAL_IN_PROGRESS)


def test_reaching_the_target_exactly_is_achieved() -> None:
    # O-07: amb el saldo igual a l'objectiu, 100 % i «Objectiu assolit».
    assert pot_progress(8000, 8000) == (100, GOAL_ACHIEVED)


def test_above_the_target_the_percentage_is_the_real_value() -> None:
    # O-03: per sobre de l'objectiu, el valor real (125) i «Objectiu assolit».
    assert pot_progress(10000, 8000) == (125, GOAL_ACHIEVED)


def test_a_pot_without_target_has_no_progress() -> None:
    # O-01 i O-05: sense objectiu, `percentage` i `goalStatus` són tots dos null.
    assert pot_progress(10000, None) == (None, None)


# --- Respostes de l'API (§11.1) ------------------------------------------------------------


def test_seed_pots_come_with_their_progress(client: TestClient) -> None:
    # O-01: Vacances 15 %, Emergències sense objectiu i Regal d'aniversari 63 % (62,5).
    pots = _pots(client)

    assert (pots["pot-01"]["percentage"], pots["pot-01"]["goalStatus"]) == (15, "in_progress")
    assert (pots["pot-02"]["percentage"], pots["pot-02"]["goalStatus"]) == (None, None)
    assert (pots["pot-03"]["percentage"], pots["pot-03"]["goalStatus"]) == (63, "in_progress")


def test_contributing_up_to_the_target_achieves_it(client: TestClient) -> None:
    # O-02: Regal d'aniversari passa de 5000 a 8000, igual que l'objectiu.
    pot = _contribute(client, "pot-03", 3000)

    assert (pot["balance"], pot["percentage"], pot["goalStatus"]) == (8000, 100, "achieved")


def test_contributing_past_the_target_shows_the_real_percentage(client: TestClient) -> None:
    # O-03: 10000 de 8000 és el 125 %, i continua assolit.
    _contribute(client, "pot-03", 3000)

    pot = _contribute(client, "pot-03", 2000)

    assert (pot["balance"], pot["percentage"], pot["goalStatus"]) == (10000, 125, "achieved")


def test_withdrawing_below_the_target_returns_the_pot_to_in_progress(client: TestClient) -> None:
    # O-04 (US-19 + US-20): retirar torna la guardiola de «Objectiu assolit» a «En progrés».
    _contribute(client, "pot-03", 3000)
    _contribute(client, "pot-03", 2000)  # 10000 de 8000: 125 % i «Objectiu assolit».

    response = client.post("/api/pots/pot-03/withdrawals", json={"amount": 3000})

    assert response.status_code == 201
    pot = response.json()["pot"]
    # 7000 de 8000 és 87,5: arrodonit mig cap amunt, 88, i mai assolit sota l'objectiu.
    assert (pot["balance"], pot["percentage"], pot["goalStatus"]) == (7000, 88, GOAL_IN_PROGRESS)
    # La lectura posterior (la llista de la pantalla) dona exactament el mateix.
    assert _pots(client)["pot-03"] == pot


def test_new_pots_start_at_zero_or_without_progress(client: TestClient) -> None:
    # O-05: Viatge amb objectiu comença al 0 %; Fons, sense objectiu, no té progrés.
    trip = client.post("/api/pots", json={"name": "Viatge", "target": 30000}).json()
    fund = client.post("/api/pots", json={"name": "Fons"}).json()

    assert (trip["percentage"], trip["goalStatus"]) == (0, "in_progress")
    assert (fund["percentage"], fund["goalStatus"]) == (None, None)


def test_every_pot_answer_has_the_same_keys(client: TestClient) -> None:
    # O-06: la llista, la creació i l'aportació porten exactament les mateixes claus.
    listed = client.get("/api/pots").json()["items"]
    created = client.post("/api/pots", json={"name": "Viatge"}).json()
    contributed = _contribute(client, "pot-01", 100)

    assert all(set(pot) == POT_KEYS for pot in listed)
    assert set(created) == POT_KEYS
    assert set(contributed) == POT_KEYS


def test_progress_is_computed_on_every_read(client: TestClient) -> None:
    # O-08: després d'arribar a l'objectiu, la llista també el dona assolit.
    _contribute(client, "pot-03", 3000)

    pot = _pots(client)["pot-03"]

    assert (pot["percentage"], pot["goalStatus"]) == (100, "achieved")
