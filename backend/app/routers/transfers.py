"""Endpoints dels enviaments (T14.1 · US-14, docs/api.md §13.4 i §13.5)."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field, StrictInt, StrictStr

from app.models import now_madrid
from app.repositories import AccountRepository, MovementRepository, OutboxRepository, UserRepository
from app.repositories.atomic import Atomic
from app.routers.current_user import current_user_id
from app.routers.dependencies import (
    account_repository,
    atomic,
    movement_repository,
    outbox_repository,
    user_repository,
)
from app.routers.schemas import MovementResponse
from app.routers.users import UserSummaryResponse
from app.services.transfer_service import (
    MAX_DAILY_TRANSFER,
    TransferResult,
    remaining_today,
    send_money,
)

router = APIRouter(tags=["transfers"])

# El concepte, com a màxim 140 caràcters (§13.4). Es compta abans de treure els espais.
MAX_CONCEPT_LENGTH = 140


class TransferRequest(BaseModel):
    """Cos de la petició: `{ toUserId, amount, concept? }`.

    `StrictInt` i `StrictStr` (P5): `"2000"`, `20.0` o `toUserId: 2` no es converteixen,
    sinó que fallen i el handler respon `422 VALIDATION_ERROR`.
    """

    to_user_id: StrictStr = Field(alias="toUserId")
    amount: StrictInt
    concept: StrictStr | None = Field(default=None, max_length=MAX_CONCEPT_LENGTH)


class TransferResponse(BaseModel):
    """Cos de la resposta `201`: `{ balance, movement, recipient }`."""

    balance: int
    movement: MovementResponse
    recipient: UserSummaryResponse

    @classmethod
    def from_result(cls, result: TransferResult) -> "TransferResponse":
        return cls(
            balance=result.balance,
            movement=MovementResponse.from_movement(result.movement),
            recipient=UserSummaryResponse.from_summary(result.recipient),
        )


class TransferLimitResponse(BaseModel):
    """Cos de `GET /api/transfers/limit`: `{ dailyLimit, remainingToday }` (P84)."""

    dailyLimit: int
    remainingToday: int


@router.post("/transfers", status_code=status.HTTP_201_CREATED)
def create_transfer(
    body: TransferRequest,
    user_id: Annotated[int, Depends(current_user_id)],
    users: Annotated[UserRepository, Depends(user_repository)],
    accounts: Annotated[AccountRepository, Depends(account_repository)],
    movements: Annotated[MovementRepository, Depends(movement_repository)],
    outbox: Annotated[OutboxRepository, Depends(outbox_repository)],
    run: Annotated[Atomic, Depends(atomic)],
) -> TransferResponse:
    # Tot o res: les validacions i les sis escriptures (§13.9).
    result = run.run(
        lambda: send_money(user_id, body.to_user_id, body.amount, body.concept, users, accounts, movements, outbox)
    )
    return TransferResponse.from_result(result)


@router.get("/transfers/limit")
def get_transfer_limit(
    user_id: Annotated[int, Depends(current_user_id)],
    accounts: Annotated[AccountRepository, Depends(account_repository)],
    movements: Annotated[MovementRepository, Depends(movement_repository)],
) -> TransferLimitResponse:
    left = remaining_today(user_id, accounts, movements, now_madrid())
    return TransferLimitResponse(dailyLimit=MAX_DAILY_TRANSFER, remainingToday=left)
