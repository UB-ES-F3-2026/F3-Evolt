"""Endpoints dels subcomptes en divisa (US-25 i US-26, docs/api.md §12.3 a §12.6)."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, ConfigDict, StrictStr
from pydantic.alias_generators import to_camel

from app.models import SubaccountMovement
from app.repositories import AccountRepository, SubaccountRepository
from app.repositories.atomic import Atomic
from app.routers.current_user import current_user_id
from app.routers.dependencies import account_repository, atomic, subaccount_repository
from app.services.subaccount_service import (
    AccountInCurrency,
    SubaccountList,
    create_subaccount,
    delete_subaccount,
    list_subaccount_movements,
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


class DeleteSubaccountResponse(BaseModel):
    """Cos de `POST /api/subaccounts/{subaccountId}/delete`: `{ status: "ok" }` (§12.5)."""

    status: str = "ok"


class SubaccountMovementResponse(BaseModel):
    """Entrada de l'historial (§12.6), sense els camps interns `subaccount_id` i `seq`."""

    id: str
    amount: int
    concept: str
    date: str
    type: str

    @classmethod
    def from_entry(cls, entry: SubaccountMovement) -> "SubaccountMovementResponse":
        return cls(
            id=entry.id,
            amount=entry.amount,
            concept=entry.concept,
            # isoformat() conserva el desplaçament de Madrid (+02:00 / +01:00) que demana §1.
            date=entry.date.isoformat(),
            type=entry.type,
        )


class SubaccountMovementListResponse(BaseModel):
    """Cos de `GET /api/subaccounts/{subaccountId}/movements`: `{ items }`."""

    items: list[SubaccountMovementResponse]


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


@router.post("/subaccounts/{subaccount_id}/delete")
def post_delete_subaccount(
    subaccount_id: str,
    user_id: Annotated[int, Depends(current_user_id)],
    subaccounts: Annotated[SubaccountRepository, Depends(subaccount_repository)],
    run: Annotated[Atomic, Depends(atomic)],
) -> DeleteSubaccountResponse:
    # Comprovar el saldo i esborrar van junts: un canvi que arribi alhora (T27.1) no
    # pot deixar diners en un subcompte que ja s'ha esborrat (§12.5).
    run.run(lambda: delete_subaccount(user_id, subaccount_id, subaccounts))
    return DeleteSubaccountResponse()


@router.get("/subaccounts/{subaccount_id}/movements")
def get_subaccount_movements(
    subaccount_id: str,
    user_id: Annotated[int, Depends(current_user_id)],
    subaccounts: Annotated[SubaccountRepository, Depends(subaccount_repository)],
) -> SubaccountMovementListResponse:
    entries = list_subaccount_movements(user_id, subaccount_id, subaccounts)
    return SubaccountMovementListResponse(items=[SubaccountMovementResponse.from_entry(entry) for entry in entries])
