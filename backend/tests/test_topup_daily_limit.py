"""Tests de T09.2: límit diari de recàrrega i recàrregues sense XP (US-09, criteris 4 i 6).

Executar des de backend/:  python -m pytest tests/test_topup_daily_limit.py

Es fan per HTTP i amb els imports en cèntims. El `client` de conftest.py torna a
construir les dades a cada test, així que cada test comença amb zero recàrregues avui.
"""

from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from httpx import Response

from app.data.seed import DEMO_USER_ID, EMPTY_USER_ID, SeedData, build_seed
from app.models import MADRID_TZ
from app.repositories import AccountRepository, MovementRepository
from app.services.errors import DAILY_LIMIT_EXCEEDED, ApiError
from app.services.topup_service import top_up


def _seed(client: TestClient) -> SeedData:
    """Dades en memòria de l'app del test."""
    return client.app.state.seed


def _topup(client: TestClient, amount: int, user_id: int = DEMO_USER_ID) -> Response:
    return client.post("/api/topups", json={"amount": amount}, headers={"X-User-Id": str(user_id)})


def _statuses(client: TestClient, *amounts: int) -> list[int]:
    return [_topup(client, amount).status_code for amount in amounts]


# --- Criteri 4: com a màxim 1.000 € al dia ----------------------------------------


def test_third_topup_of_500_is_rejected_with_nothing_left_today(client: TestClient) -> None:
    assert _statuses(client, 50000, 50000) == [201, 201]

    response = _topup(client, 50000)

    assert response.status_code == 422
    assert response.json() == {
        "code": "DAILY_LIMIT_EXCEEDED",
        "message": "Has superat el límit diari de recàrrega. Avui encara pots recarregar 0,00 €.",
        "details": {"remainingToday": 0},
    }


def test_rejection_says_how_much_can_still_be_topped_up_today(client: TestClient) -> None:
    assert _statuses(client, 50000, 40000) == [201, 201]

    response = _topup(client, 10001)  # 100,01 €

    body = response.json()
    assert response.status_code == 422
    assert body["code"] == "DAILY_LIMIT_EXCEEDED"
    assert body["details"] == {"remainingToday": 10000}
    assert body["message"] == (
        "Has superat el límit diari de recàrrega. Avui encara pots recarregar 100,00 €."
    )


def test_reaching_exactly_1000_euros_in_a_day_is_allowed(client: TestClient) -> None:
    assert _statuses(client, 50000, 40000, 10000) == [201, 201, 201]


def test_rejected_topup_changes_neither_balance_nor_movements(client: TestClient) -> None:
    assert _statuses(client, 50000, 50000) == [201, 201]
    seed = _seed(client)
    balance_before = seed.accounts[DEMO_USER_ID].balance
    movement_count_before = len(seed.movements)
    home_before = client.get("/api/home").json()

    assert _topup(client, 100).status_code == 422

    assert seed.accounts[DEMO_USER_ID].balance == balance_before
    assert len(seed.movements) == movement_count_before
    assert client.get("/api/home").json() == home_before


def test_per_topup_limit_is_checked_before_the_daily_limit(client: TestClient) -> None:
    assert _statuses(client, 50000, 50000) == [201, 201]

    response = _topup(client, 50001)

    assert response.json()["code"] == "AMOUNT_OVER_LIMIT"


def test_each_user_has_their_own_daily_limit(client: TestClient) -> None:
    assert _statuses(client, 50000, 50000) == [201, 201]

    assert _topup(client, 50000, user_id=EMPTY_USER_ID).status_code == 201


# --- Criteri 6: les recàrregues no donen XP ---------------------------------------


def test_topups_do_not_change_any_user_xp(client: TestClient) -> None:
    users = _seed(client).users
    xp_before = {user_id: user.xp for user_id, user in users.items()}

    # Tres acceptades i una rebutjada pel límit diari.
    assert _statuses(client, 50000, 40000, 10000, 1) == [201, 201, 201, 422]

    assert {user_id: user.xp for user_id, user in users.items()} == xp_before


# --- Canvi de dia (servei, amb el moment fixat) ------------------------------------

NOW = datetime(2026, 10, 17, 10, 0, 0, tzinfo=MADRID_TZ)


def test_yesterday_topups_do_not_count_today() -> None:
    seed = build_seed(now=NOW)
    accounts, movements = AccountRepository(seed), MovementRepository(seed)
    late_yesterday = (NOW - timedelta(days=1)).replace(hour=23, minute=59, second=59)

    for moment in (late_yesterday, late_yesterday, NOW, NOW):
        top_up(DEMO_USER_ID, 50000, accounts, movements, now=moment)

    # Avui ja s'han recarregat 1.000 €, però els d'ahir no hi compten.
    with pytest.raises(ApiError) as rejected:
        top_up(DEMO_USER_ID, 1, accounts, movements, now=NOW)
    assert rejected.value.code == DAILY_LIMIT_EXCEEDED
    assert rejected.value.details == {"remainingToday": 0}
