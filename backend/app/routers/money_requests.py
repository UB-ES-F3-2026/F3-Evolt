"""Endpoints de les sol·licituds de diners (US-15, docs/api.md §14.2 a §14.4)."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, ConfigDict, StrictInt, StrictStr
from pydantic.alias_generators import to_camel

from app.repositories import MoneyRequestRepository, OutboxRepository, UserRepository
from app.repositories.atomic import Atomic
from app.routers.current_user import current_user_id
from app.routers.dependencies import atomic, money_request_repository, outbox_repository, user_repository
from app.routers.users import UserSummaryResponse
from app.services.money_request_service import SentRequest, cancel_request, create_request, list_sent

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
