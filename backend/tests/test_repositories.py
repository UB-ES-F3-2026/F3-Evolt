"""Tests de T07.4: repositoris en memòria.

Executar des de backend/:  python -m pytest tests/
"""

from datetime import date, datetime, timedelta, timezone

import pytest

from app.data.seed import (
    DEMO_USER_ID,
    EMPTY_USER_ID,
    MADRID_TZ,
    TOPUP_CONCEPT,
    build_seed,
)
from app.models import KIND_OTHER, KIND_TOPUP, TYPE_EXPENSE, TYPE_INCOME
from app.repositories import AccountRepository, MovementRepository, PotRepository

# Data fixa perquè els tests no depenguin del dia en què s'executen.
NOW = datetime(2026, 10, 13, 15, 0, 0, tzinfo=MADRID_TZ)


@pytest.fixture
def seed():
    return build_seed(now=NOW)


def _movement_kwargs(**overrides):
    """Arguments per defecte de MovementRepository.add()."""
    data = dict(
        account_id=DEMO_USER_ID,
        amount=1000,
        concept="Prova",
        date=NOW,
        type=TYPE_EXPENSE,
        icon="other",
        kind=KIND_OTHER,
    )
    data.update(overrides)
    return data


def _page(repository, account_id, offset, limit):
    """Ids d'una pàgina, per comparar llistes senceres d'un cop."""
    return [movement.id for movement in repository.list_by_account(account_id, offset, limit)]


# --- AccountRepository ----------------------------------------------------------


def test_get_account_by_demo_user(seed):
    account = AccountRepository(seed).get_by_user(DEMO_USER_ID)
    assert account is not None
    assert account.user_id == DEMO_USER_ID
    assert account.balance > 0
    assert account.balance == sum(m.signed_amount for m in seed.movements)


def test_get_account_by_empty_user(seed):
    account = AccountRepository(seed).get_by_user(EMPTY_USER_ID)
    assert account is not None
    assert account.balance == 0


def test_get_account_unknown_user_returns_none(seed):
    assert AccountRepository(seed).get_by_user(999) is None


def test_set_balance_writes_through_the_repository(seed):
    accounts = AccountRepository(seed)
    accounts.set_balance(DEMO_USER_ID, 12345)
    assert accounts.get_by_user(DEMO_USER_ID).balance == 12345
    assert accounts.get_by_user(EMPTY_USER_ID).balance == 0
    # Objecte viu: el canvi es veu sobre el seed original, no sobre una còpia.
    assert seed.accounts[DEMO_USER_ID].balance == 12345


@pytest.mark.parametrize("balance_cents", [12.5, "100", True, None])
def test_set_balance_rejects_non_int(seed, balance_cents):
    accounts = AccountRepository(seed)
    original = seed.accounts[DEMO_USER_ID].balance
    with pytest.raises(TypeError):
        accounts.set_balance(DEMO_USER_ID, balance_cents)
    assert seed.accounts[DEMO_USER_ID].balance == original


def test_set_balance_unknown_user_raises(seed):
    accounts = AccountRepository(seed)
    with pytest.raises(KeyError):
        accounts.set_balance(999, 1000)


# --- PotRepository --------------------------------------------------------------


def test_list_pots_by_demo_user(seed):
    pots = PotRepository(seed).list_by_user(DEMO_USER_ID)
    assert [(pot.name, pot.balance) for pot in pots] == [
        ("Vacances", 15000),
        ("Emergències", 10000),
        ("Regal d'aniversari", 5000),
    ]
    assert all(pot.user_id == DEMO_USER_ID for pot in pots)


def test_list_pots_by_empty_user_returns_empty(seed):
    assert PotRepository(seed).list_by_user(EMPTY_USER_ID) == []


# --- MovementRepository: llistat i paginació ------------------------------------


def test_list_returns_newest_first(seed):
    movements = MovementRepository(seed)
    account_id = seed.accounts[DEMO_USER_ID].id
    assert _page(movements, account_id, 0, 30) == [f"mov-{number:02d}" for number in range(30, 0, -1)]
    page = movements.list_by_account(account_id, 0, 30)
    assert all(first.date >= second.date for first, second in zip(page, page[1:]))


def test_tie_on_date_puts_later_created_first(seed):
    movements = MovementRepository(seed)
    account_id = seed.accounts[DEMO_USER_ID].id
    page = movements.list_by_account(account_id, 0, 3)
    assert [movement.id for movement in page] == ["mov-30", "mov-29", "mov-28"]
    # mov-29 i mov-28 tenen la data idèntica a propòsit; guanya el seq més gran (P4).
    assert page[1].concept == "Bizum enviat" and page[1].seq == 29
    assert page[2].concept == "Supermercat" and page[2].seq == 28
    assert page[1].date == page[2].date


def test_pages_are_stable_and_contiguous(seed):
    movements = MovementRepository(seed)
    account_id = seed.accounts[DEMO_USER_ID].id
    assert _page(movements, account_id, 0, 3) + _page(movements, account_id, 3, 3) == _page(
        movements, account_id, 0, 6
    )


def test_last_page_is_partial(seed):
    movements = MovementRepository(seed)
    account_id = seed.accounts[DEMO_USER_ID].id
    assert _page(movements, account_id, 28, 5) == ["mov-02", "mov-01"]


@pytest.mark.parametrize("offset", [30, 31, 999])
def test_offset_beyond_total_returns_empty_page(seed, offset):
    movements = MovementRepository(seed)
    account_id = seed.accounts[DEMO_USER_ID].id
    # offset ≥ total no és error: pàgina buida (P3), l'error el faria el router.
    assert _page(movements, account_id, offset, 20) == []
    assert movements.count_by_account(account_id) == 30


def test_count_by_account(seed):
    movements = MovementRepository(seed)
    assert movements.count_by_account(seed.accounts[DEMO_USER_ID].id) == 30
    assert movements.count_by_account(seed.accounts[EMPTY_USER_ID].id) == 0


def test_list_by_empty_account_returns_empty(seed):
    movements = MovementRepository(seed)
    account_id = seed.accounts[EMPTY_USER_ID].id
    assert _page(movements, account_id, 0, 20) == []


@pytest.mark.parametrize("offset, limit", [(-1, 20), (0, 0), (0, -5)])
def test_list_rejects_invalid_pagination(seed, offset, limit):
    movements = MovementRepository(seed)
    account_id = seed.accounts[DEMO_USER_ID].id
    with pytest.raises(ValueError):
        movements.list_by_account(account_id, offset, limit)


# --- MovementRepository: add ----------------------------------------------------


def test_add_assigns_id_and_seq_from_counters(seed):
    movements = MovementRepository(seed)
    first = movements.add(**_movement_kwargs())
    assert (first.id, first.seq) == ("mov-31", 31)
    assert seed.next_movement_number == 32
    assert seed.next_movement_seq == 32
    second = movements.add(**_movement_kwargs())
    assert (second.id, second.seq) == ("mov-32", 32)
    assert len(seed.movements) == 32
    assert len({movement.id for movement in seed.movements}) == 32
    assert len({movement.seq for movement in seed.movements}) == 32


def test_added_movement_is_visible_and_lists_first(seed):
    movements = MovementRepository(seed)
    account_id = seed.accounts[DEMO_USER_ID].id
    added = movements.add(**_movement_kwargs())
    assert movements.count_by_account(account_id) == 31
    page = movements.list_by_account(account_id, 0, 1)
    assert page[0] is added


@pytest.mark.parametrize(
    "overrides",
    [
        {"amount": 0},
        {"icon": "pizza"},
        {"kind": KIND_TOPUP, "type": TYPE_EXPENSE},
        {"date": NOW.replace(microsecond=1)},
    ],
)
def test_add_invalid_data_stores_nothing(seed, overrides):
    movements = MovementRepository(seed)
    with pytest.raises((ValueError, TypeError)):
        movements.add(**_movement_kwargs(**overrides))
    # Tot o res: res desat i comptadors intactes.
    assert movements.count_by_account(seed.accounts[DEMO_USER_ID].id) == 30
    assert len(seed.movements) == 30
    assert seed.next_movement_number == 31
    assert seed.next_movement_seq == 31


# --- MovementRepository: sum_topups_on_day --------------------------------------


def test_sum_topups_on_day_matches_seed_topups(seed):
    movements = MovementRepository(seed)
    account_id = seed.accounts[DEMO_USER_ID].id
    assert movements.sum_topups_on_day(account_id, (NOW - timedelta(days=30)).date()) == 20000
    assert movements.sum_topups_on_day(account_id, (NOW - timedelta(days=15)).date()) == 15000
    # El dia anterior té moviments, però cap recàrrega.
    assert movements.sum_topups_on_day(account_id, (NOW - timedelta(days=1)).date()) == 0
    # El seed no té cap recàrrega avui (§6).
    assert movements.sum_topups_on_day(account_id, NOW.date()) == 0


def test_sum_topups_ignores_other_kind_with_topup_concept(seed):
    movements = MovementRepository(seed)
    account_id = seed.accounts[DEMO_USER_ID].id
    movements.add(
        **_movement_kwargs(
            kind=KIND_OTHER,
            concept=TOPUP_CONCEPT,
            icon="transfer",
            type=TYPE_INCOME,
            date=NOW,
        )
    )
    # Es filtra per kind, mai pel text del concepte (§6).
    assert movements.sum_topups_on_day(account_id, NOW.date()) == 0


def test_sum_topups_counts_only_the_given_account(seed):
    movements = MovementRepository(seed)
    demo_account = seed.accounts[DEMO_USER_ID].id
    empty_account = seed.accounts[EMPTY_USER_ID].id
    movements.add(
        **_movement_kwargs(
            account_id=empty_account,
            kind=KIND_TOPUP,
            icon="topup",
            type=TYPE_INCOME,
            date=NOW,
        )
    )
    assert movements.sum_topups_on_day(demo_account, NOW.date()) == 0
    assert movements.sum_topups_on_day(empty_account, NOW.date()) == 1000


@pytest.mark.parametrize(
    "moment, expected",
    [
        (datetime(2026, 10, 13, 0, 0, 0, tzinfo=MADRID_TZ), 1000),
        (datetime(2026, 10, 13, 23, 59, 59, tzinfo=MADRID_TZ), 1000),
        (datetime(2026, 10, 12, 23, 59, 59, tzinfo=MADRID_TZ), 0),
        (datetime(2026, 10, 14, 0, 0, 0, tzinfo=MADRID_TZ), 0),
    ],
)
def test_sum_topups_day_boundaries(seed, moment, expected):
    movements = MovementRepository(seed)
    account_id = seed.accounts[DEMO_USER_ID].id
    movements.add(**_movement_kwargs(kind=KIND_TOPUP, icon="topup", type=TYPE_INCOME, date=moment))
    assert movements.sum_topups_on_day(account_id, NOW.date()) == expected


def test_sum_topups_handles_dst_and_foreign_offsets(seed):
    movements = MovementRepository(seed)
    account_id = seed.accounts[DEMO_USER_ID].id
    # El 25/10/2026 Madrid passa de +02:00 a +01:00.
    morning = datetime(2026, 10, 25, 0, 30, tzinfo=MADRID_TZ)
    evening = datetime(2026, 10, 25, 23, 30, tzinfo=MADRID_TZ)
    # 23:30 UTC = 26/10 00:30 a Madrid: un altre dia, malgrat la mateixa data UTC.
    utc_instant = datetime(2026, 10, 25, 23, 30, tzinfo=timezone.utc)
    for moment in (morning, evening, utc_instant):
        movements.add(**_movement_kwargs(kind=KIND_TOPUP, icon="topup", type=TYPE_INCOME, date=moment))
    assert movements.sum_topups_on_day(account_id, date(2026, 10, 25)) == 2000
    assert movements.sum_topups_on_day(account_id, date(2026, 10, 26)) == 1000
