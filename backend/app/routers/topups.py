"""Endpoint de la recàrrega de prova (T09.1 · US-09, docs/api.md §4.3)."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, StrictInt

from app.repositories import AccountRepository, MovementRepository
from app.routers.current_user import current_user_id
from app.routers.dependencies import account_repository, movement_repository
from app.routers.schemas import MovementResponse
from app.services.topup_service import TopupResult, top_up

router = APIRouter(tags=["topups"])


class TopupRequest(BaseModel):
    """Cos de la petició: `{ amount }` en cèntims.

    `StrictInt` (P5): `"500"`, `500.0`, `500.5` o `true` no es converteixen a enter,
    sinó que fallen i el handler de T07.2 respon `422 VALIDATION_ERROR`.
    """

    amount: StrictInt


class TopupResponse(BaseModel):
    """Cos de la resposta `201`: `{ balance, movement }`."""

    balance: int
    movement: MovementResponse

    @classmethod
    def from_result(cls, result: TopupResult) -> "TopupResponse":
        return cls(
            balance=result.balance,
            movement=MovementResponse.from_movement(result.movement),
        )


@router.post("/topups", status_code=status.HTTP_201_CREATED)
def create_topup(
    body: TopupRequest,
    user_id: Annotated[int, Depends(current_user_id)],
    accounts: Annotated[AccountRepository, Depends(account_repository)],
    movements: Annotated[MovementRepository, Depends(movement_repository)],
) -> TopupResponse:
    result = top_up(user_id, body.amount, accounts, movements)
    return TopupResponse.from_result(result)
