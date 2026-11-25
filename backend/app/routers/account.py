"""Endpoints de les dades del compte (T12.2 · US-12, docs/api.md §16.1 i §16.3)."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, StrictInt, StrictStr

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
from app.services.account_service import account_details, receive_external_transfer

router = APIRouter(tags=["account"])
# La transferència d'un altre banc és una eina de desenvolupament: `app.main` només
# registra aquest router amb les rutes de desenvolupament actives (§16.3, P96).
dev_router = APIRouter(tags=["dev"])


class AccountResponse(BaseModel):
    """Cos de `GET /api/account`: `{ iban, bic, holder }` (§16.1)."""

    iban: str
    bic: str
    holder: str


class IncomingTransferRequest(BaseModel):
    """Cos de la petició: `{ iban, amount, payer }`, amb tipus estrictes (P5)."""

    iban: StrictStr
    amount: StrictInt
    payer: StrictStr


class IncomingTransferResponse(BaseModel):
    """Cos de la resposta `201`: `{ balance, movement }` (§16.3)."""

    balance: int
    movement: MovementResponse


@router.get("/account")
def get_account(
    user_id: Annotated[int, Depends(current_user_id)],
    users: Annotated[UserRepository, Depends(user_repository)],
) -> AccountResponse:
    details = account_details(user_id, users)
    return AccountResponse(iban=details.iban, bic=details.bic, holder=details.holder)


@dev_router.post("/dev/incoming-transfers", status_code=status.HTTP_201_CREATED)
def post_incoming_transfer(
    body: IncomingTransferRequest,
    users: Annotated[UserRepository, Depends(user_repository)],
    accounts: Annotated[AccountRepository, Depends(account_repository)],
    movements: Annotated[MovementRepository, Depends(movement_repository)],
    outbox: Annotated[OutboxRepository, Depends(outbox_repository)],
    run: Annotated[Atomic, Depends(atomic)],
) -> IncomingTransferResponse:
    # El moviment, el saldo i l'avís, junts (§16.5).
    result = run.run(
        lambda: receive_external_transfer(body.iban, body.amount, body.payer, users, accounts, movements, outbox)
    )
    return IncomingTransferResponse(balance=result.balance, movement=MovementResponse.from_movement(result.movement))
