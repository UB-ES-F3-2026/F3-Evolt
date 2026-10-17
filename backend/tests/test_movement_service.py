"""Tests del servei de llistat de moviments (T08.1, docs/api.md §4.2).

Executar des de backend/:  python -m pytest tests/test_movement_service.py
"""

from datetime import datetime

import pytest

from app.data.seed import DEMO_USER_ID, EMPTY_USER_ID, MADRID_TZ, build_seed
from app.repositories import AccountRepository, MovementRepository
from app.services.movement_service import DEFAULT_LIMIT, MAX_LIMIT, list_movements

# Data fixa perquè els tests no depenguin del dia en què s'executen.
NOW = datetime(2026, 10, 16, 21, 0, 0, tzinfo=MADRID_TZ)


@pytest.fixture
def repos():
    # Dades noves a cada test: l'ordre d'execució no importa.
    seed = build_seed(now=NOW)
    return AccountRepository(seed), MovementRepository(seed)


def page(repos, user_id=DEMO_USER_ID, **kwargs):
    accounts, movements = repos
    return list_movements(user_id, accounts, movements, **kwargs)


# --- Criteri de fet: l'usuari 1 pagina els seus 30 moviments en dues pàgines --------


def test_demo_user_pages_30_movements_in_two_pages(repos):
    first = page(repos)
    assert len(first.items) == DEFAULT_LIMIT == 20
    assert first.next_offset == 20

    second = page(repos, offset=first.next_offset)
    assert len(second.items) == 10
    assert second.next_offset is None

    ids = [m.id for m in first.items + second.items]
    assert len(ids) == len(set(ids)) == 30


def test_empty_user_gets_empty_page(repos):
    result = page(repos, user_id=EMPTY_USER_ID)
    assert result.items == []
    assert result.next_offset is None


# --- Ordre ---------------------------------------------------------------------------


def test_movements_are_newest_first(repos):
    items = page(repos, limit=MAX_LIMIT).items
    dates = [m.date for m in items]
    assert dates == sorted(dates, reverse=True)
    assert items[0].concept == "Restaurant La Plaça"  # el d'ahir


def test_equal_dates_put_the_later_created_first(repos):
    # El seed té "Supermercat" i "Bizum enviat" amb la mateixa data (P4).
    items = page(repos, limit=MAX_LIMIT).items
    tied = [m for m in items if m.date == items[1].date]
    assert [m.concept for m in tied] == ["Bizum enviat", "Supermercat"]


def test_order_is_stable_across_pages(repos):
    all_at_once = [m.id for m in page(repos, limit=30).items]
    by_pages = [m.id for off in range(0, 30, 7) for m in page(repos, offset=off, limit=7).items]
    assert by_pages == all_at_once


# --- nextOffset ----------------------------------------------------------------------


def test_last_page_that_ends_exactly_at_total_has_no_next(repos):
    result = page(repos, offset=10, limit=20)
    assert len(result.items) == 20
    assert result.next_offset is None


def test_max_limit_returns_everything_in_one_page(repos):
    result = page(repos, limit=MAX_LIMIT)
    assert len(result.items) == 30
    assert result.next_offset is None


@pytest.mark.parametrize("offset", [30, 31, 1000])
def test_offset_at_or_beyond_total_is_empty_not_error(repos, offset):
    # P3: no és un error.
    result = page(repos, offset=offset)
    assert result.items == []
    assert result.next_offset is None


def test_middle_page(repos):
    result = page(repos, offset=5, limit=5)
    assert len(result.items) == 5
    assert result.next_offset == 10


# --- Crides incorrectes ---------------------------------------------------------------


@pytest.mark.parametrize(
    "kwargs",
    [{"offset": -1}, {"limit": 0}, {"limit": MAX_LIMIT + 1}, {"limit": -5}],
)
def test_out_of_range_parameters_are_rejected(repos, kwargs):
    # El router respon VALIDATION_ERROR abans d'arribar aquí; el servei es protegeix igualment.
    with pytest.raises(ValueError):
        page(repos, **kwargs)


def test_user_without_account_is_a_programming_error(repos):
    # `current_user_id` ja filtra els usuaris inexistents.
    with pytest.raises(LookupError):
        page(repos, user_id=999)
