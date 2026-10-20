"""Resum de la pantalla principal (T07.5, docs/api.md §4.1)."""

from dataclasses import dataclass

from app.models import Movement
from app.repositories import AccountRepository, MovementRepository, PotRepository

# US-07, criteri 3: la pantalla principal mostra els 5 últims moviments.
LAST_MOVEMENTS_COUNT = 5


@dataclass(frozen=True)
class HomeSummary:
    """Dades del resum, amb imports en cèntims. La forma JSON la decideix el router."""

    balance: int
    total_saved: int
    last_movements: list[Movement]


def get_home_summary(
    user_id: int,
    accounts: AccountRepository,
    pots: PotRepository,
    movements: MovementRepository,
) -> HomeSummary:
    """Saldo, total estalviat a les guardioles i últims moviments d'un usuari."""
    account = accounts.get_by_user(user_id)
    if account is None:
        # `current_user_id` ja rebutja els usuaris inexistents amb un 422: arribar
        # aquí és un error de programació i ha d'acabar en INTERNAL_ERROR.
        raise LookupError(f"L'usuari {user_id} no té compte principal")

    return HomeSummary(
        balance=account.balance,
        total_saved=sum(pot.balance for pot in pots.list_by_user(user_id)),
        last_movements=movements.list_by_account(
            account.id, offset=0, limit=LAST_MOVEMENTS_COUNT
        ),
    )
