"""Tests de T07.3: models i dades hardcodeades.

Executar des de backend/:  python -m pytest tests/test_seed.py
"""

from datetime import datetime, timedelta

import pytest

from app.data.seed import DEMO_USER_ID, EMPTY_USER_ID, MADRID_TZ, build_seed
from app.models import ICONS, KIND_OTHER, KIND_TOPUP, Movement

# Data fixa perquè els tests no depenguin del dia en què s'executen.
NOW = datetime(2026, 10, 13, 15, 0, 0, tzinfo=MADRID_TZ)


@pytest.fixture
def seed():
    return build_seed(now=NOW)


def movements_of(seed, user_id):
    return [m for m in seed.movements if m.account_id == seed.accounts[user_id].id]


# --- Usuari 1 -----------------------------------------------------------------


def test_demo_user_has_30_movements_with_income_and_expense(seed):
    movs = movements_of(seed, DEMO_USER_ID)
    assert len(movs) == 30
    assert {m.type for m in movs} == {"income", "expense"}


def test_demo_balance_matches_movements(seed):
    movs = movements_of(seed, DEMO_USER_ID)
    assert seed.accounts[DEMO_USER_ID].balance == sum(m.signed_amount for m in movs)
    assert seed.accounts[DEMO_USER_ID].balance > 0


def test_demo_user_has_three_pots_with_money(seed):
    pots = [p for p in seed.pots if p.user_id == DEMO_USER_ID]
    assert len(pots) == 3
    assert all(p.balance > 0 for p in pots)


def test_demo_user_has_xp(seed):
    assert seed.users[DEMO_USER_ID].xp > 0


# --- Usuari 2 -----------------------------------------------------------------


def test_empty_user_has_nothing(seed):
    assert movements_of(seed, EMPTY_USER_ID) == []
    assert [p for p in seed.pots if p.user_id == EMPTY_USER_ID] == []
    assert seed.accounts[EMPTY_USER_ID].balance == 0


# --- Regles del contracte -------------------------------------------------------


def test_no_movement_today_or_in_the_future(seed):
    today = NOW.date()
    for m in seed.movements:
        assert m.date.astimezone(MADRID_TZ).date() < today, m


def test_past_topups_are_marked_with_kind(seed):
    topups = [m for m in seed.movements if m.kind == KIND_TOPUP]
    assert topups
    for m in topups:
        assert m.concept == "Recàrrega"
        assert m.icon == "topup"
        assert m.type == "income"
    others = [m for m in seed.movements if m.kind == KIND_OTHER]
    assert all(m.icon != "topup" for m in others)


def test_fields_follow_contract(seed):
    for m in seed.movements:
        assert isinstance(m.id, str)
        assert isinstance(m.amount, int) and m.amount > 0
        assert m.icon in ICONS
        assert m.date.microsecond == 0
        # ISO 8601 amb desplaçament, p. ex. 2026-10-12T22:14:00+02:00
        assert m.date.isoformat()[-6:] in {"+02:00", "+01:00"}


def test_ids_and_seq_are_unique(seed):
    assert len({m.id for m in seed.movements}) == len(seed.movements)
    assert len({m.seq for m in seed.movements}) == len(seed.movements)
    assert seed.next_movement_seq > max(m.seq for m in seed.movements)
    assert seed.next_movement_number == len(seed.movements) + 1


def test_tie_on_date_is_broken_by_seq(seed):
    ordered = sorted(seed.movements, key=Movement.sort_key, reverse=True)
    ties = [(a, b) for a, b in zip(ordered, ordered[1:], strict=False) if a.date == b.date]
    assert ties, "el seed inclou un empat de dates a propòsit (P4)"
    for a, b in ties:
        assert a.seq > b.seq


def test_build_seed_returns_independent_copies():
    a = build_seed(now=NOW)
    b = build_seed(now=NOW)
    a.accounts[DEMO_USER_ID].balance += 50000
    a.movements.pop()
    assert b.accounts[DEMO_USER_ID].balance != a.accounts[DEMO_USER_ID].balance
    assert len(b.movements) == 30


def test_dates_keep_correct_offset_across_dst_change():
    # El 25/10/2026 Madrid passa de +02:00 a +01:00.
    seed = build_seed(now=datetime(2026, 11, 5, 12, 0, tzinfo=MADRID_TZ))
    offsets = {m.date.utcoffset() for m in seed.movements}
    assert offsets == {timedelta(hours=2), timedelta(hours=1)}


# --- Validacions del model Movement --------------------------------------------


def _movement(**overrides):
    data = dict(
        id="mov-99",
        account_id=1,
        amount=100,
        concept="Prova",
        date=NOW,
        type="expense",
        icon="other",
        kind=KIND_OTHER,
        seq=99,
    )
    data.update(overrides)
    return Movement(**data)


@pytest.mark.parametrize(
    "overrides",
    [
        {"amount": 0},
        {"amount": -5},
        {"amount": 10.0},
        {"amount": True},
        {"icon": "pizza"},
        {"type": "refund"},
        {"kind": "bonus"},
        {"id": 7},
        {"date": datetime(2026, 10, 13, 15, 0)},  # sense zona horària
        {"date": NOW.replace(microsecond=123)},  # P7
        {"kind": KIND_TOPUP, "type": "expense", "icon": "topup"},
    ],
)
def test_movement_rejects_invalid_data(overrides):
    with pytest.raises((ValueError, TypeError)):
        _movement(**overrides)


def test_signed_amount():
    assert _movement(type="income").signed_amount == 100
    assert _movement(type="expense").signed_amount == -100
