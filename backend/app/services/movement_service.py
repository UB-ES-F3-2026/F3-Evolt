"""Llistat paginat de moviments (T08.1 · US-08, docs/api.md §4.2).

L'ordre (data descendent, desempat per `seq`) i el tall per `offset`/`limit` els fa
el repositori; aquest servei resol el compte de l'usuari i decideix si hi ha una
pàgina següent.
"""

from dataclasses import dataclass

from app.models import Movement
from app.repositories import AccountRepository, MovementRepository

DEFAULT_LIMIT = 20
MAX_LIMIT = 50


@dataclass(frozen=True)
class MovementsPage:
    """Una pàgina del llistat. La forma JSON la decideix el router."""

    items: list[Movement]
    # `None` quan aquesta és l'última pàgina: el frontend deixa de demanar-ne més.
    next_offset: int | None


def list_movements(
    user_id: int,
    accounts: AccountRepository,
    movements: MovementRepository,
    offset: int = 0,
    limit: int = DEFAULT_LIMIT,
) -> MovementsPage:
    """Moviments d'un usuari, del més recent al més antic, en pàgines."""
    # El router ja valida el rang i respon VALIDATION_ERROR; això només protegeix
    # el servei d'una crida interna incorrecta.
    if offset < 0 or not 1 <= limit <= MAX_LIMIT:
        raise ValueError(f"offset={offset} o limit={limit} fora de rang")

    account = accounts.get_by_user(user_id)
    if account is None:
        # `current_user_id` ja rebutja els usuaris inexistents amb un 422: arribar
        # aquí és un error de programació i ha d'acabar en INTERNAL_ERROR.
        raise LookupError(f"L'usuari {user_id} no té compte principal")

    items = movements.list_by_account(account.id, offset, limit)
    end = offset + len(items)
    # Un offset >= total no és un error (P3): pàgina buida i nextOffset null.
    has_more = end < movements.count_by_account(account.id)
    return MovementsPage(items=items, next_offset=end if has_more else None)
