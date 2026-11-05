"""Llistat paginat de moviments (T08.1 · US-08, docs/api.md §4.2), detall i informe de
problema (T11.1 · US-11, §10.3 i §10.4).

L'ordre (data descendent, desempat per `seq`) i el tall per `offset`/`limit` els fa
el repositori; aquest servei resol el compte de l'usuari i decideix si hi ha una
pàgina següent. Els filtres (T10.3, §10.2) els aplica el repositori, abans de paginar.
"""

from dataclasses import dataclass
from datetime import datetime

from app.models import (
    MAX_REPORT_DESCRIPTION,
    Movement,
    MovementFilters,
    MovementReport,
    now_madrid,
)
from app.repositories import AccountRepository, MovementReportRepository, MovementRepository
from app.services.errors import (
    INVALID_DESCRIPTION,
    MOVEMENT_NOT_FOUND,
    VALIDATION_ERROR,
    ApiError,
)

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
    filters: MovementFilters | None = None,
) -> MovementsPage:
    """Moviments d'un usuari, del més recent al més antic, en pàgines."""
    # El router ja valida el rang i respon VALIDATION_ERROR; això només protegeix
    # el servei d'una crida interna incorrecta.
    if offset < 0 or not 1 <= limit <= MAX_LIMIT:
        raise ValueError(f"offset={offset} o limit={limit} fora de rang")

    if filters and filters.date_from and filters.date_to and filters.date_from > filters.date_to:
        raise ApiError(VALIDATION_ERROR)

    account = accounts.get_by_user(user_id)
    if account is None:
        # `current_user_id` ja rebutja els usuaris inexistents amb un 422: arribar
        # aquí és un error de programació i ha d'acabar en INTERNAL_ERROR.
        raise LookupError(f"L'usuari {user_id} no té compte principal")

    items = movements.list_by_account(account.id, offset, limit, filters)
    end = offset + len(items)
    # Un offset >= total no és un error (P3): pàgina buida i nextOffset null.
    has_more = end < movements.count_by_account(account.id, filters)
    return MovementsPage(items=items, next_offset=end if has_more else None)


def get_movement(
    user_id: int,
    movement_id: str,
    accounts: AccountRepository,
    movements: MovementRepository,
) -> Movement:
    """Un moviment de l'usuari (§10.3).

    Si no existeix o és d'un altre usuari → MOVEMENT_NOT_FOUND, amb la mateixa resposta,
    perquè no es pugui saber si un moviment d'un altre usuari existeix.
    """
    account = accounts.get_by_user(user_id)
    if account is None:
        # `current_user_id` ja rebutja els usuaris inexistents: arribar aquí és un error
        # de programació i ha d'acabar en INTERNAL_ERROR.
        raise LookupError(f"L'usuari {user_id} no té compte principal")

    movement = movements.get_by_account(account.id, movement_id)
    if movement is None:
        raise ApiError(MOVEMENT_NOT_FOUND)
    return movement


def report_movement(
    user_id: int,
    movement_id: str,
    description: str,
    accounts: AccountRepository,
    movements: MovementRepository,
    reports: MovementReportRepository,
    now: datetime | None = None,
) -> MovementReport:
    """Desa l'informe d'un problema amb un moviment de l'usuari (§10.4).

    Ordre de les validacions (s'aturen al primer error):
      1. Format del cos (`description` string) → el router, VALIDATION_ERROR.
      2. El moviment no existeix o és d'un altre usuari → MOVEMENT_NOT_FOUND.
      3. Descripció buida, només amb espais o de més de 500 caràcters un cop trets
         els espais dels extrems → INVALID_DESCRIPTION.
    Si hi ha un error, no es desa res. L'informe es queda en memòria i no s'envia enlloc.
    `now` permet fixar el moment als tests.
    """
    movement = get_movement(user_id, movement_id, accounts, movements)

    clean_description = description.strip()
    if not clean_description or len(clean_description) > MAX_REPORT_DESCRIPTION:
        raise ApiError(INVALID_DESCRIPTION)

    return reports.add(
        movement_id=movement.id,
        user_id=user_id,
        description=clean_description,
        created_at=now or now_madrid(),
    )
