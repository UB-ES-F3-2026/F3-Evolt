"""Endpoints de les sol·licituds de diners (US-15, US-16 i US-39, docs/api.md §14.2 a §14.4, §15.2 i §15.3)."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictStr
from pydantic.alias_generators import to_camel

from app.repositories import (
    AccountRepository,
    MoneyRequestRepository,
    MovementRepository,
    OutboxRepository,
    UserRepository,
)
from app.repositories.atomic import Atomic
from app.routers.current_user import current_user_id
from app.routers.dependencies import (
    account_repository,
    atomic,
    money_request_repository,
    movement_repository,
    outbox_repository,
    user_repository,
)
from app.routers.schemas import MovementResponse
from app.routers.users import UserSummaryResponse
from app.services.money_request_service import (
    PaymentResult,
    ReceivedRequest,
    SentRequest,
    cancel_request,
    create_request,
    list_received,
    list_sent,
    pay_request,
)

router = APIRouter(tags=["money-requests"])


class CreateMoneyRequestRequest(BaseModel):
    """Cos de la petició: `{ toUserId, amount, concept }` (§14.2), amb tipus estrictes (P5)."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    to_user_id: StrictStr
    amount: StrictInt
    concept: StrictStr


class MoneyRequestResponse(BaseModel):
    """Objecte `MoneyRequest` del contracte (§14.1), amb les claus en camelCase."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: str
    to: UserSummaryResponse
    amount: int
    concept: str
    status: str
    created_at: str
    expires_at: str

    @classmethod
    def from_sent(cls, sent: SentRequest) -> "MoneyRequestResponse":
        return cls(
            id=sent.request.id,
            to=UserSummaryResponse.from_summary(sent.to),
            amount=sent.request.amount,
            concept=sent.request.concept,
            status=sent.status,
            # isoformat() conserva el desplaçament de Madrid que demana §1.
            created_at=sent.request.created_at.isoformat(),
            expires_at=sent.expires_at.isoformat(),
        )


class MoneyRequestListResponse(BaseModel):
    """Cos de `GET /api/money-requests`: `{ items }`."""

    items: list[MoneyRequestResponse]


class ReceivedMoneyRequestResponse(BaseModel):
    """Objecte `ReceivedMoneyRequest` (§15.1): com `MoneyRequest`, però amb `from` en lloc de `to`."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: str
    # `from` és una paraula reservada de Python: el camp es diu `sender` i surt com a `from`.
    sender: UserSummaryResponse = Field(alias="from")
    amount: int
    concept: str
    status: str
    created_at: str
    expires_at: str

    @classmethod
    def from_received(cls, received: ReceivedRequest) -> "ReceivedMoneyRequestResponse":
        return cls(
            id=received.request.id,
            sender=UserSummaryResponse.from_summary(received.sender),
            amount=received.request.amount,
            concept=received.request.concept,
            status=received.status,
            created_at=received.request.created_at.isoformat(),
            expires_at=received.expires_at.isoformat(),
        )


class ReceivedMoneyRequestListResponse(BaseModel):
    """Cos de `GET /api/money-requests/received`: `{ items }`."""

    items: list[ReceivedMoneyRequestResponse]


class PaymentResponse(BaseModel):
    """Cos de la resposta `201` de pagar: `{ balance, movement, request }` (§15.3)."""

    balance: int
    movement: MovementResponse
    request: ReceivedMoneyRequestResponse

    @classmethod
    def from_result(cls, result: PaymentResult) -> "PaymentResponse":
        return cls(
            balance=result.balance,
            movement=MovementResponse.from_movement(result.movement),
            request=ReceivedMoneyRequestResponse.from_received(result.request),
        )


class StatusResponse(BaseModel):
    status: str


@router.post("/money-requests", status_code=status.HTTP_201_CREATED)
def post_money_request(
    body: CreateMoneyRequestRequest,
    user_id: Annotated[int, Depends(current_user_id)],
    users: Annotated[UserRepository, Depends(user_repository)],
    requests: Annotated[MoneyRequestRepository, Depends(money_request_repository)],
    outbox: Annotated[OutboxRepository, Depends(outbox_repository)],
    run: Annotated[Atomic, Depends(atomic)],
) -> MoneyRequestResponse:
    # La sol·licitud i l'avís van junts (§14.2): transacció a Firestore, pany en memòria.
    sent = run.run(
        lambda: create_request(user_id, body.to_user_id, body.amount, body.concept, users, requests, outbox)
    )
    return MoneyRequestResponse.from_sent(sent)


@router.get("/money-requests")
def get_money_requests(
    user_id: Annotated[int, Depends(current_user_id)],
    users: Annotated[UserRepository, Depends(user_repository)],
    requests: Annotated[MoneyRequestRepository, Depends(money_request_repository)],
) -> MoneyRequestListResponse:
    return MoneyRequestListResponse(
        items=[MoneyRequestResponse.from_sent(sent) for sent in list_sent(user_id, requests, users)]
    )


@router.get("/money-requests/received")
def get_received_money_requests(
    user_id: Annotated[int, Depends(current_user_id)],
    users: Annotated[UserRepository, Depends(user_repository)],
    requests: Annotated[MoneyRequestRepository, Depends(money_request_repository)],
) -> ReceivedMoneyRequestListResponse:
    return ReceivedMoneyRequestListResponse(
        items=[ReceivedMoneyRequestResponse.from_received(r) for r in list_received(user_id, requests, users)]
    )


@router.post("/money-requests/{request_id}/cancel")
def post_cancel_money_request(
    request_id: str,
    user_id: Annotated[int, Depends(current_user_id)],
    requests: Annotated[MoneyRequestRepository, Depends(money_request_repository)],
    run: Annotated[Atomic, Depends(atomic)],
) -> StatusResponse:
    # Llegir i esborrar, junts: dues cancel·lacions alhora no poden passar totes dues.
    run.run(lambda: cancel_request(user_id, request_id, requests))
    return StatusResponse(status="ok")


@router.post("/money-requests/{request_id}/pay", status_code=status.HTTP_201_CREATED)
def post_pay_money_request(
    request_id: str,
    user_id: Annotated[int, Depends(current_user_id)],
    users: Annotated[UserRepository, Depends(user_repository)],
    accounts: Annotated[AccountRepository, Depends(account_repository)],
    movements: Annotated[MovementRepository, Depends(movement_repository)],
    requests: Annotated[MoneyRequestRepository, Depends(money_request_repository)],
    outbox: Annotated[OutboxRepository, Depends(outbox_repository)],
    run: Annotated[Atomic, Depends(atomic)],
) -> PaymentResponse:
    # L'enviament de la US-14 i el canvi a `paid`, en una sola operació (§15.8).
    result = run.run(lambda: pay_request(user_id, request_id, users, accounts, movements, requests, outbox))
    return PaymentResponse.from_result(result)
