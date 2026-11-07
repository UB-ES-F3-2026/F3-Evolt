"""Tests de T10.3: filtres de GET /api/movements (docs/api.md §10.2).

Proves M-01 a M-20 de docs/proves-moviments.md, més la funció `fold_text`,
`MovementFilters` i el repositori.

Executar des de backend/:  python -m pytest tests/test_movement_filters.py
"""

from datetime import UTC, date, datetime

import pytest
from fastapi.testclient import TestClient

from app.data.seed import DEMO_USER_ID, EMPTY_USER_ID, SeedData, build_seed
from app.models import (
    KIND_OTHER,
    MADRID_TZ,
    MOVEMENT_STATUS_COMPLETED,
    TYPE_EXPENSE,
    TYPE_INCOME,
    Movement,
    MovementFilters,
    fold_text,
)
from app.repositories import AccountRepository, MovementRepository
from app.services.errors import VALIDATION_ERROR, ApiError
from app.services.movement_service import list_movements

# T0 de docs/proves-moviments.md: les dates del seed són relatives a aquest dia.
T0 = datetime(2026, 11, 3, 10, 0, 0, tzinfo=MADRID_TZ)
EMPTY_USER = {"X-User-Id": str(EMPTY_USER_ID)}
EMPTY_PAGE = {"items": [], "nextOffset": None}
VALIDATION_BODY = {"code": "VALIDATION_ERROR", "message": "Les dades de la petició no són vàlides."}


@pytest.fixture
def seed(client: TestClient) -> SeedData:
    """Seed de les proves, amb el rellotge a T0. Els repositoris el llegeixen a cada petició."""
    fixed = build_seed(now=T0)
    client.app.state.seed = fixed
    return fixed


def _page(client: TestClient, headers: dict[str, str] | None = None, **params):
    return client.get("/api/movements", params=params, headers=headers)


def _ids(client: TestClient, **params) -> list[str]:
    params.setdefault("limit", 50)
    return [item["id"] for item in _page(client, **params).json()["items"]]


def _newest_first(seed: SeedData) -> list[Movement]:
    return sorted(seed.movements, key=Movement.sort_key, reverse=True)


def _madrid_day(movement: Movement) -> date:
    return movement.date.astimezone(MADRID_TZ).date()


def _all_pages(client: TestClient, **params) -> list[dict[str, object]]:
    """Segueix `nextOffset` fins al final, com el frontend. Retorna les pàgines."""
    pages = []
    offset = 0
    while offset is not None:
        body = _page(client, offset=offset, **params).json()
        pages.append(body)
        offset = body["nextOffset"]
    return pages


# --- Text ------------------------------------------------------------------------------


def test_type_and_text_find_exactly_the_supermarket_movements(client: TestClient, seed: SeedData) -> None:
    # M-01
    response = _page(client, type="expense", q="super")

    expected = [m.id for m in _newest_first(seed) if m.concept == "Supermercat"]
    assert [item["id"] for item in response.json()["items"]] == expected
    assert expected == ["mov-28", "mov-23", "mov-13", "mov-06"]
    assert response.json()["nextOffset"] is None


def test_text_without_accent_finds_the_accented_concept(client: TestClient, seed: SeedData) -> None:
    # M-02
    assert _ids(client, q="recarrega") == ["mov-16", "mov-07"]


@pytest.mark.parametrize("text", ["SUPER", "Super", "sUpErMeRcAt"])
def test_text_ignores_case(client: TestClient, seed: SeedData, text: str) -> None:
    # M-03
    assert _ids(client, q=text) == _ids(client, q="super")


def test_accented_text_finds_the_same_as_without_accent(client: TestClient, seed: SeedData) -> None:
    assert _ids(client, q="RECÀRREGA") == _ids(client, q="recarrega")


def test_text_finds_the_counterparty(client: TestClient, seed: SeedData) -> None:
    # M-06
    assert _ids(client, q="marta") == ["mov-09"]


def test_text_finds_the_counterparty_without_accent(client: TestClient, seed: SeedData) -> None:
    # M-07
    assert _ids(client, q="nuria") == ["mov-29"]


def test_text_ignores_the_spaces_at_the_ends(client: TestClient, seed: SeedData) -> None:
    assert _ids(client, q="  marta  ") == ["mov-09"]


@pytest.mark.parametrize("text", ["", "   "])
def test_empty_text_does_not_filter(client: TestClient, seed: SeedData, text: str) -> None:
    # M-16
    assert _page(client, q=text).json() == _page(client).json()
    assert _page(client, q=text).json()["nextOffset"] == 20


@pytest.mark.parametrize("text", ["EVT-000009", "shopping", "completed", "%", ".*", "mov-09"])
def test_text_only_looks_in_the_concept_and_the_counterparty(client: TestClient, seed: SeedData, text: str) -> None:
    # Ni la referència, ni la icona, ni l'estat; i `%` o `.*` són text, no comodins.
    assert _page(client, q=text).json() == EMPTY_PAGE


def test_text_finds_a_new_contribution(client: TestClient, seed: SeedData) -> None:
    created = client.post("/api/pots/pot-01/contributions", json={"amount": 100}).json()["movement"]

    assert _ids(client, q="aportacio vacances") == []
    assert _ids(client, q="aportacio a vacances") == [created["id"]]


# --- Tipus -----------------------------------------------------------------------------


def test_expense_never_returns_an_income(client: TestClient, seed: SeedData) -> None:
    # M-04
    items = _page(client, type="expense", limit=50).json()["items"]

    assert len(items) == sum(m.type == TYPE_EXPENSE for m in seed.movements) == 23
    assert {item["type"] for item in items} == {"expense"}


def test_income_never_returns_an_expense(client: TestClient, seed: SeedData) -> None:
    # M-05
    items = _page(client, type="income", limit=50).json()["items"]

    assert len(items) == sum(m.type == TYPE_INCOME for m in seed.movements) == 7
    assert {item["type"] for item in items} == {"income"}


# --- Dates -----------------------------------------------------------------------------


def test_dates_include_both_ends(client: TestClient, seed: SeedData) -> None:
    # M-08
    assert _ids(client, dateFrom="2026-11-01", dateTo="2026-11-02") == ["mov-30", "mov-29", "mov-28"]


def test_a_single_day(client: TestClient, seed: SeedData) -> None:
    # M-09
    assert _ids(client, dateFrom="2026-11-01", dateTo="2026-11-01") == ["mov-29", "mov-28"]


def test_only_the_start_date(client: TestClient, seed: SeedData) -> None:
    start = date(2026, 10, 25)

    expected = [m.id for m in _newest_first(seed) if _madrid_day(m) >= start]
    assert _ids(client, dateFrom=start.isoformat()) == expected
    assert 0 < len(expected) < 30


def test_only_the_end_date(client: TestClient, seed: SeedData) -> None:
    end = date(2026, 10, 25)

    expected = [m.id for m in _newest_first(seed) if _madrid_day(m) <= end]
    assert _ids(client, dateTo=end.isoformat()) == expected
    assert 0 < len(expected) < 30


# --- Errors de format ------------------------------------------------------------------


def test_start_after_end_is_a_validation_error(client: TestClient, seed: SeedData) -> None:
    # M-10
    response = _page(client, dateFrom="2026-11-02", dateTo="2026-11-01")

    assert response.status_code == 422
    assert response.json() == VALIDATION_BODY


@pytest.mark.parametrize("parameter", ["dateFrom", "dateTo"])
@pytest.mark.parametrize(
    "value",
    [
        "2026-13-01",  # M-11: el dia no existeix
        "2026-02-30",
        "01/11/2026",  # M-11: un altre format
        "2026-11-1",
        "20261101",
        "2026-W45-2",
        "1793232000",  # el tipus `date` sol l'acceptaria com a marca de temps
        "2026-11-01T00:00:00",
        "",
    ],
)
def test_badly_formed_day_is_a_validation_error(client: TestClient, seed: SeedData, parameter: str, value: str) -> None:
    response = _page(client, **{parameter: value})

    assert response.status_code == 422
    assert response.json() == VALIDATION_BODY


@pytest.mark.parametrize("value", ["refund", "Income", "EXPENSE", ""])
def test_unknown_type_is_a_validation_error(client: TestClient, seed: SeedData, value: str) -> None:
    # M-12
    response = _page(client, type=value)

    assert response.status_code == 422
    assert response.json() == VALIDATION_BODY


# --- Paginació -------------------------------------------------------------------------


def test_filtered_pages_follow_next_offset(client: TestClient, seed: SeedData) -> None:
    # M-13
    first = _page(client, type="expense", q="super", limit=2).json()
    second = _page(client, type="expense", q="super", limit=2, offset=2).json()

    assert [item["id"] for item in first["items"]] == ["mov-28", "mov-23"]
    assert first["nextOffset"] == 2
    assert [item["id"] for item in second["items"]] == ["mov-13", "mov-06"]
    assert second["nextOffset"] is None


def test_walking_all_the_pages_does_not_repeat_movements(client: TestClient, seed: SeedData) -> None:
    # M-14
    pages = _all_pages(client, type="expense", limit=2)

    walked = [item["id"] for page in pages for item in page["items"]]
    assert len(pages) == 12
    assert len(walked) == len(set(walked)) == 23
    assert walked == [m.id for m in _newest_first(seed) if m.type == TYPE_EXPENSE]
    assert pages[-1]["nextOffset"] is None


def test_offset_beyond_the_filtered_result_is_not_an_error(client: TestClient, seed: SeedData) -> None:
    # M-19
    response = _page(client, type="expense", q="super", offset=4)

    assert response.status_code == 200
    assert response.json() == EMPTY_PAGE


def test_limit_is_still_validated_with_filters(client: TestClient, seed: SeedData) -> None:
    assert _page(client, q="super", limit=51).json() == VALIDATION_BODY


# --- Combinats i sense resultats -------------------------------------------------------


def test_no_results(client: TestClient, seed: SeedData) -> None:
    # M-15
    response = _page(client, q="xyz")

    assert response.status_code == 200
    assert response.json() == EMPTY_PAGE


def test_dates_type_and_text_combine(client: TestClient, seed: SeedData) -> None:
    # M-18: `mov-03` també és una nòmina, però és anterior a la data d'inici.
    assert _ids(client, dateFrom="2026-10-01", type="income", q="nomina") == ["mov-17"]


def test_filters_only_see_your_own_movements(client: TestClient, seed: SeedData) -> None:
    # M-17
    response = _page(client, headers=EMPTY_USER, q="super")

    assert response.status_code == 200
    assert response.json() == EMPTY_PAGE


def test_home_has_no_filters(client: TestClient, seed: SeedData) -> None:
    # M-20
    assert client.get("/api/home", params={"q": "super"}).json() == client.get("/api/home").json()


def test_without_filters_the_list_is_the_same_as_before(client: TestClient, seed: SeedData) -> None:
    body = _page(client).json()

    assert [item["id"] for item in body["items"]] == [m.id for m in _newest_first(seed)][:20]
    assert body["nextOffset"] == 20


# --- fold_text -------------------------------------------------------------------------


@pytest.mark.parametrize(
    "text, expected",
    [
        ("Recàrrega", "recarrega"),
        ("Núria Soler", "nuria soler"),
        ("SUPER", "super"),
        ("Restaurant La Plaça", "restaurant la placa"),
        ("Nòmina", "nomina"),
        ("ÀÉÏÒÚ", "aeiou"),
        ("col·legi", "col·legi"),
        ("  amb espais  ", "  amb espais  "),
        ("", ""),
    ],
)
def test_fold_text(text: str, expected: str) -> None:
    assert fold_text(text) == expected


# --- MovementFilters i capes -----------------------------------------------------------


def _movement(moment: datetime, **overrides) -> Movement:
    kwargs = {
        "id": "mov-99",
        "account_id": DEMO_USER_ID,
        "amount": 100,
        "concept": "Prova",
        "date": moment,
        "type": TYPE_EXPENSE,
        "icon": "other",
        "kind": KIND_OTHER,
        "seq": 99,
        "counterparty": None,
        "status": MOVEMENT_STATUS_COMPLETED,
        "reference": "EVT-000099",
    }
    kwargs.update(overrides)
    return Movement(**kwargs)


@pytest.mark.parametrize(
    "moment, madrid_day",
    [
        # Encara és l'1/11 en UTC, però ja és el 2/11 a Madrid (+01:00).
        (datetime(2026, 11, 1, 23, 30, tzinfo=UTC), date(2026, 11, 2)),
        # A l'estiu, Madrid va a +02:00.
        (datetime(2026, 7, 1, 22, 30, tzinfo=UTC), date(2026, 7, 2)),
        # Dia del canvi d'hora.
        (datetime(2026, 10, 24, 22, 30, tzinfo=UTC), date(2026, 10, 25)),
    ],
)
def test_dates_are_days_in_madrid(moment: datetime, madrid_day: date) -> None:
    movement = _movement(moment)

    assert MovementFilters(date_from=madrid_day, date_to=madrid_day).matches(movement)
    assert not MovementFilters(date_to=date.fromordinal(madrid_day.toordinal() - 1)).matches(movement)


def test_filters_without_values_match_everything() -> None:
    assert MovementFilters().matches(_movement(T0))


def test_service_rejects_a_start_after_the_end() -> None:
    seed = build_seed(now=T0)
    filters = MovementFilters(date_from=date(2026, 11, 2), date_to=date(2026, 11, 1))

    with pytest.raises(ApiError) as error:
        list_movements(DEMO_USER_ID, AccountRepository(seed), MovementRepository(seed), filters=filters)

    assert error.value.code == VALIDATION_ERROR


def test_repository_filters_before_paging_and_counts_with_the_same_filters() -> None:
    seed = build_seed(now=T0)
    movements = MovementRepository(seed)
    filters = MovementFilters(type=TYPE_EXPENSE, text="super")

    assert [m.id for m in movements.list_by_account(DEMO_USER_ID, 1, 2, filters)] == ["mov-23", "mov-13"]
    assert movements.count_by_account(DEMO_USER_ID, filters) == 4
    assert movements.count_by_account(DEMO_USER_ID) == 30
