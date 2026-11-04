"""Endpoint del llistat de moviments (T08.1 · US-08, docs/api.md §4.2) i els seus filtres (T10.3 · US-10, §10.2)."""

import re
from datetime import date
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, BeforeValidator, ConfigDict
from pydantic.alias_generators import to_camel

from app.models import TYPE_EXPENSE, TYPE_INCOME, MovementFilters
from app.repositories import AccountRepository, MovementRepository
from app.routers.current_user import current_user_id
from app.routers.dependencies import account_repository, movement_repository
from app.routers.schemas import MovementResponse
from app.services.movement_service import (
    DEFAULT_LIMIT,
    MAX_LIMIT,
    MovementsPage,
    list_movements,
)

router = APIRouter(tags=["movements"])

_DAY_FORMAT = re.compile(r"\d{4}-\d{2}-\d{2}")


def _parse_day(value: object) -> date:
    """Un dia real amb el format `YYYY-MM-DD` del contracte (§10.2).

    El tipus `date` de Pydantic sol ja accepta altres formes, com una marca de temps.
    Un `ValueError` aquí és un `422 VALIDATION_ERROR`.
    """
    if not isinstance(value, str) or not _DAY_FORMAT.fullmatch(value):
        raise ValueError("dia fora del format YYYY-MM-DD")
    return date.fromisoformat(value)


Day = Annotated[date, BeforeValidator(_parse_day)]


class MovementsPageResponse(BaseModel):
    """Cos de `GET /api/movements`: `{ items, nextOffset }`."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    items: list[MovementResponse]
    # Sense valor per defecte: `nextOffset: null` ha de sortir sempre al JSON.
    next_offset: int | None

    @classmethod
    def from_page(cls, page: MovementsPage) -> "MovementsPageResponse":
        return cls(
            items=[MovementResponse.from_movement(movement) for movement in page.items],
            next_offset=page.next_offset,
        )


@router.get("/movements")
def get_movements(
    user_id: Annotated[int, Depends(current_user_id)],
    accounts: Annotated[AccountRepository, Depends(account_repository)],
    movements: Annotated[MovementRepository, Depends(movement_repository)],
    # Un valor fora de rang o no enter → RequestValidationError → 422 VALIDATION_ERROR.
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=MAX_LIMIT)] = DEFAULT_LIMIT,
    date_from: Annotated[Day | None, Query(alias="dateFrom")] = None,
    date_to: Annotated[Day | None, Query(alias="dateTo")] = None,
    type: Literal[TYPE_INCOME, TYPE_EXPENSE] | None = None,
    q: str | None = None,
) -> MovementsPageResponse:
    filters = MovementFilters(date_from=date_from, date_to=date_to, type=type, text=q)
    page = list_movements(user_id, accounts, movements, offset=offset, limit=limit, filters=filters)
    return MovementsPageResponse.from_page(page)
