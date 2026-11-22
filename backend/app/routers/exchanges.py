"""Endpoint del canvi de divisa (US-27, docs/api.md §12.7)."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictStr
from pydantic.alias_generators import to_camel

from app.repositories import AccountRepository, MovementRepository, SubaccountRepository
from app.repositories.atomic import Atomic
from app.routers.current_user import current_user_id
from app.routers.dependencies import account_repository, atomic, movement_repository, subaccount_repository
from app.routers.subaccounts import SubaccountResponse
from app.services.exchange_service import ExchangeResult, exchange

router = APIRouter(tags=["exchanges"])


class ExchangeRequest(BaseModel):
    """Cos de la petició: `{ fromCurrency, toCurrency, amount }` (§12.7).

    `StrictStr` i `StrictInt` (P5): un codi numèric (`978`), `"1000"`, `10.5` o
    `true` són un `422 VALIDATION_ERROR`. Una divisa fora de la llista no és d'aquí:
    és SUBACCOUNT_NOT_FOUND, del servei.
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    from_currency: StrictStr
    to_currency: StrictStr
    amount: StrictInt


class ExchangeResponse(BaseModel):
    """Cos de la resposta `201`: `{ from, to, amount, commission, received }` (§12.7)."""

    model_config = ConfigDict(populate_by_name=True)

    # `from` és paraula reservada de Python: el camp es diu `origin` i surt com a `from`.
    origin: SubaccountResponse = Field(serialization_alias="from")
    to: SubaccountResponse
    amount: int
    commission: int
    received: int

    @classmethod
    def from_result(cls, result: ExchangeResult) -> "ExchangeResponse":
        return cls(
            origin=SubaccountResponse.from_account(result.from_account),
            to=SubaccountResponse.from_account(result.to_account),
            amount=result.amount,
            commission=result.commission,
            received=result.received,
        )


@router.post("/exchanges", status_code=status.HTTP_201_CREATED, response_model_by_alias=True)
def post_exchange(
    body: ExchangeRequest,
    user_id: Annotated[int, Depends(current_user_id)],
    accounts: Annotated[AccountRepository, Depends(account_repository)],
    subaccounts: Annotated[SubaccountRepository, Depends(subaccount_repository)],
    movements: Annotated[MovementRepository, Depends(movement_repository)],
    run: Annotated[Atomic, Depends(atomic)],
) -> ExchangeResponse:
    # Validar i les quatre escriptures, tot o res (§12.7). Dos canvis alhora van
    # un darrere l'altre: el segon veu el saldo que ha deixat el primer.
    result = run.run(
        lambda: exchange(
            user_id, body.from_currency, body.to_currency, body.amount, accounts, subaccounts, movements
        )
    )
    return ExchangeResponse.from_result(result)
