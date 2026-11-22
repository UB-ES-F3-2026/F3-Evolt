"""Endpoints dels subcomptes en divisa (US-25, docs/api.md §12.3 i §12.4)."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, ConfigDict, StrictStr
from pydantic.alias_generators import to_camel

from app.repositories import AccountRepository, SubaccountRepository
from app.repositories.atomic import Atomic
from app.routers.current_user import current_user_id
from app.routers.dependencies import account_repository, atomic, subaccount_repository
from app.services.subaccount_service import (
    AccountInCurrency,
    SubaccountList,
    create_subaccount,
    list_subaccounts,
)

router = APIRouter(tags=["subaccounts"])


class SubaccountResponse(BaseModel):
    """Objecte `Subaccount` del contracte (§12.2), amb les claus en camelCase."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: str
    currency: str
    balance: int
    is_main: bool
    rate_bps: int

    @classmethod
    def from_account(cls, account: AccountInCurrency) -> "SubaccountResponse":
        return cls(
            id=account.id,
            currency=account.currency,
            balance=account.balance,
            is_main=account.is_main,
            rate_bps=account.rate_bps,
        )


class SubaccountListResponse(BaseModel):
    """Cos de `GET /api/subaccounts`: `{ items, totalInEuros }` (§12.3)."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    items: list[SubaccountResponse]
    total_in_euros: int

    @classmethod
    def from_list(cls, result: SubaccountList) -> "SubaccountListResponse":
        return cls(
            items=[SubaccountResponse.from_account(item) for item in result.items],
            total_in_euros=result.total_in_euros,
        )


class CreateSubaccountRequest(BaseModel):
    """Cos de la petició: `{ currency }` (§12.4).

    `StrictStr`: un número (`840`) o un `null` són un `422 VALIDATION_ERROR`. Un
    string fora de la llista no és d'aquí: és CURRENCY_NOT_SUPPORTED, del servei.
    """

    currency: StrictStr


@router.get("/subaccounts")
def get_subaccounts(
    user_id: Annotated[int, Depends(current_user_id)],
    accounts: Annotated[AccountRepository, Depends(account_repository)],
    subaccounts: Annotated[SubaccountRepository, Depends(subaccount_repository)],
) -> SubaccountListResponse:
    return SubaccountListResponse.from_list(list_subaccounts(user_id, accounts, subaccounts))


@router.post("/subaccounts", status_code=status.HTTP_201_CREATED)
def post_subaccount(
    body: CreateSubaccountRequest,
    user_id: Annotated[int, Depends(current_user_id)],
    subaccounts: Annotated[SubaccountRepository, Depends(subaccount_repository)],
    run: Annotated[Atomic, Depends(atomic)],
) -> SubaccountResponse:
    # Comprovar la divisa i crear el subcompte van junts: si arriben dues peticions
    # alhora per a la mateixa divisa, només en guanya una (§12.4).
    created = run.run(lambda: create_subaccount(user_id, body.currency, subaccounts))
    return SubaccountResponse.from_account(created)
