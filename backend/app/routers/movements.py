"""Endpoints dels moviments (docs/api.md): llistat (T08.1 · US-08, §4.2), filtres
(T10.3 · US-10, §10.2), detall i informe de problema (T11.1 · US-11, §10.3 i §10.4).
"""

import re
from datetime import date
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel, BeforeValidator, ConfigDict, StrictStr
from pydantic.alias_generators import to_camel

from app.models import TYPE_EXPENSE, TYPE_INCOME, MovementFilters, MovementReport
from app.repositories import AccountRepository, MovementReportRepository, MovementRepository
from app.repositories.atomic import Atomic
from app.routers.current_user import current_user_id
from app.routers.dependencies import (
    account_repository,
    atomic,
    movement_report_repository,
    movement_repository,
)
from app.routers.schemas import MovementResponse
from app.services.movement_service import (
    DEFAULT_LIMIT,
    MAX_LIMIT,
    MovementsPage,
    get_movement,
    list_movements,
    report_movement,
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


class MovementReportRequest(BaseModel):
    """Cos de la petició: `{ description }` (§10.4).

    `StrictStr`: un número o `null` són un `422 VALIDATION_ERROR`, com a la resta de cossos.
    """

    description: StrictStr


class MovementReportResponse(BaseModel):
    """Cos de la resposta `201`: `{ id, movementId, description, createdAt }`, sense `user_id`."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: str
    movement_id: str
    description: str
    created_at: str

    @classmethod
    def from_report(cls, report: MovementReport) -> "MovementReportResponse":
        return cls(
            id=report.id,
            movement_id=report.movement_id,
            description=report.description,
            # isoformat() conserva el desplaçament de Madrid (+02:00 / +01:00) que demana §1.
            created_at=report.created_at.isoformat(),
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


@router.get("/movements/{movement_id}")
def get_movement_detail(
    movement_id: str,
    user_id: Annotated[int, Depends(current_user_id)],
    accounts: Annotated[AccountRepository, Depends(account_repository)],
    movements: Annotated[MovementRepository, Depends(movement_repository)],
) -> MovementResponse:
    return MovementResponse.from_movement(get_movement(user_id, movement_id, accounts, movements))


@router.post("/movements/{movement_id}/reports", status_code=status.HTTP_201_CREATED)
def post_movement_report(
    movement_id: str,
    body: MovementReportRequest,
    user_id: Annotated[int, Depends(current_user_id)],
    accounts: Annotated[AccountRepository, Depends(account_repository)],
    movements: Annotated[MovementRepository, Depends(movement_repository)],
    reports: Annotated[MovementReportRepository, Depends(movement_report_repository)],
    run: Annotated[Atomic, Depends(atomic)],
) -> MovementReportResponse:
    # Amb Firestore, el comptador dels ids i l'informe nou van junts (TR01.1).
    report = run.run(lambda: report_movement(user_id, movement_id, body.description, accounts, movements, reports))
    return MovementReportResponse.from_report(report)
