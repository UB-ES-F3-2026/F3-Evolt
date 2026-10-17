"""Tests del servei de recàrrega (T09.1, docs/api.md §4.3).

Executar des de backend/:  python -m pytest tests/test_topup_service.py
"""

from datetime import datetime

import pytest

from app.data.seed import DEMO_USER_ID, EMPTY_USER_ID, build_seed
from app.models import KIND_TOPUP, MADRID_TZ
from app.repositories import AccountRepository, MovementRepository
from app.services.errors import AMOUNT_OVER_LIMIT, INVALID_AMOUNT, ApiError
from app.services.topup_service import MAX_TOPUP, top_up

# Data fixa perquè els tests no depenguin del dia en què s'executen.
NOW = datetime(2026, 10, 17, 16, 30, 0, tzinfo=MADRID_TZ)


@pytest.fixture
def seed():
    # Dades noves a cada test: l'ordre d'execució no importa.
    return build_seed(now=NOW)


def topup(seed, amount, user_id=DEMO_USER_ID):
    return top_up(user_id, amount, AccountRepository(seed), MovementRepository(seed), now=NOW)


def snapshot(seed):
    """Estat que una recàrrega fallida no pot canviar."""
    return (
        {user_id: account.balance for user_id, account in seed.accounts.items()},
        [m.id for m in seed.movements],
        {user_id: user.xp for user_id, user in seed.users.items()},
        seed.next_movement_number,
    )


# --- Recàrrega correcta -----------------------------------------------------------------


def test_topup_adds_the_amount_to_the_balance(seed):
    before = seed.accounts[DEMO_USER_ID].balance

    result = topup(seed, 12345)

    assert result.balance == before + 12345
    assert seed.accounts[DEMO_USER_ID].balance == before + 12345


def test_topup_creates_a_recarrega_income_movement(seed):
    movement = topup(seed, 5000).movement

    assert movement.amount == 5000
    assert movement.concept == "Recàrrega"
    assert movement.type == "income"
    assert movement.icon == "topup"
    assert movement.kind == KIND_TOPUP
    assert movement.date == NOW
    assert movement.account_id == seed.accounts[DEMO_USER_ID].id
    assert movement in seed.movements


def test_topup_gets_the_next_id(seed):
    assert topup(seed, 100).movement.id == "mov-31"
    assert topup(seed, 100).movement.id == "mov-32"


def test_topup_is_the_newest_movement(seed):
    movement = topup(seed, 100).movement

    account_id = seed.accounts[DEMO_USER_ID].id
    first = MovementRepository(seed).list_by_account(account_id, offset=0, limit=1)
    assert first == [movement]


def test_balance_stays_consistent_with_movements(seed):
    topup(seed, 40000)
    topup(seed, 1)

    own = [m for m in seed.movements if m.account_id == seed.accounts[DEMO_USER_ID].id]
    assert seed.accounts[DEMO_USER_ID].balance == sum(m.signed_amount for m in own)


@pytest.mark.parametrize("amount", [1, MAX_TOPUP])
def test_limits_of_a_single_topup_are_allowed(seed, amount):
    # 0,01 € i exactament 500,00 € estan permesos.
    assert topup(seed, amount).movement.amount == amount


def test_empty_user_can_top_up(seed):
    demo_before = seed.accounts[DEMO_USER_ID].balance

    result = topup(seed, 2500, user_id=EMPTY_USER_ID)

    assert result.balance == 2500
    assert seed.accounts[EMPTY_USER_ID].balance == 2500
    assert seed.accounts[DEMO_USER_ID].balance == demo_before  # l'usuari 1 no canvia


def test_topup_does_not_change_xp(seed):
    xp_before = seed.users[DEMO_USER_ID].xp
    topup(seed, 10000)
    assert seed.users[DEMO_USER_ID].xp == xp_before


def test_default_now_is_madrid_time_with_seconds_precision(seed):
    movement = top_up(
        DEMO_USER_ID, 100, AccountRepository(seed), MovementRepository(seed)
    ).movement
    assert movement.date.tzinfo is not None
    assert movement.date.microsecond == 0
    assert movement.date.utcoffset() == datetime.now(MADRID_TZ).utcoffset()


# --- Errors: no es modifica res ------------------------------------------------------------


@pytest.mark.parametrize(
    "amount, code",
    [
        (0, INVALID_AMOUNT),
        (-1, INVALID_AMOUNT),
        (-50000, INVALID_AMOUNT),
        (MAX_TOPUP + 1, AMOUNT_OVER_LIMIT),  # 500,01 €
        (60000, AMOUNT_OVER_LIMIT),
    ],
)
def test_invalid_amount_raises_and_changes_nothing(seed, amount, code):
    before = snapshot(seed)

    with pytest.raises(ApiError) as error:
        topup(seed, amount)

    assert error.value.code == code
    assert error.value.details is None
    assert snapshot(seed) == before


def test_user_without_account_is_a_programming_error(seed):
    # `current_user_id` ja filtra els usuaris inexistents.
    before = snapshot(seed)
    with pytest.raises(LookupError):
        topup(seed, 100, user_id=999)
    assert snapshot(seed) == before
