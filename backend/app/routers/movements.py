"""Endpoint del llistat de moviments (T08.1 · US-08, docs/api.md §4.2)."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

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
) -> MovementsPageResponse:
    page = list_movements(user_id, accounts, movements, offset=offset, limit=limit)
    return MovementsPageResponse.from_page(page)
