"""Endpoints de les despeses dividides (US-30 i US-31, docs/api.md §17)."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictStr
from pydantic.alias_generators import to_camel

from app.models import MAX_SPLIT_PARTS
from app.repositories import MoneyRequestRepository, OutboxRepository, SplitExpenseRepository, UserRepository
from app.repositories.atomic import Atomic
from app.routers.current_user import current_user_id
from app.routers.dependencies import (
    atomic,
    money_request_repository,
    outbox_repository,
    split_expense_repository,
    user_repository,
)
from app.routers.users import UserSummaryResponse
from app.services.split_expense_service import SplitView, create_split, get_split, list_splits, resend_part

router = APIRouter(tags=["split-expenses"])


class SplitPartRequest(BaseModel):
    """Una part del cos: `{ toUserId, amount }`, amb tipus estrictes (P5)."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    to_user_id: StrictStr
    amount: StrictInt


class CreateSplitExpenseRequest(BaseModel):
    """Cos de la petició: `{ concept, total, myShare, parts }` (§17.2). D'1 a 9 parts."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    concept: StrictStr
    total: StrictInt
    my_share: StrictInt
    parts: list[SplitPartRequest] = Field(min_length=1, max_length=MAX_SPLIT_PARTS)


class SplitPartResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    request_id: str
    to: UserSummaryResponse
    amount: int
    status: str


class SplitExpenseResponse(BaseModel):
    """Objecte `SplitExpense` del contracte (§17.1), amb les claus en camelCase."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: str
    concept: str
    total: int
    my_share: int
    created_at: str
    status: str
    people: int
    paid_count: int
    pending_amount: int
    parts: list[SplitPartResponse]

    @classmethod
    def from_view(cls, view: SplitView) -> "SplitExpenseResponse":
        return cls(
            id=view.split.id,
            concept=view.split.concept,
            total=view.split.total,
            my_share=view.split.my_share,
            # isoformat() conserva el desplaçament de Madrid que demana §1.
            created_at=view.split.created_at.isoformat(),
            status=view.status,
            people=view.people,
            paid_count=view.paid_count,
            pending_amount=view.pending_amount,
            parts=[
                SplitPartResponse(
                    request_id=part.request_id,
                    to=UserSummaryResponse.from_summary(part.to),
                    amount=part.amount,
                    status=part.status,
                )
                for part in view.parts
            ],
        )


class SplitExpenseListResponse(BaseModel):
    """Cos de `GET /api/split-expenses`: `{ items }` (§17.3)."""

    items: list[SplitExpenseResponse]


@router.post("/split-expenses", status_code=status.HTTP_201_CREATED)
def post_split_expense(
    body: CreateSplitExpenseRequest,
    user_id: Annotated[int, Depends(current_user_id)],
    users: Annotated[UserRepository, Depends(user_repository)],
    splits: Annotated[SplitExpenseRepository, Depends(split_expense_repository)],
    requests: Annotated[MoneyRequestRepository, Depends(money_request_repository)],
    outbox: Annotated[OutboxRepository, Depends(outbox_repository)],
    run: Annotated[Atomic, Depends(atomic)],
) -> SplitExpenseResponse:
    # La despesa, les sol·licituds i els avisos van junts (§17.9): transacció a Firestore, pany en memòria.
    parts = [(part.to_user_id, part.amount) for part in body.parts]
    view = run.run(
        lambda: create_split(user_id, body.concept, body.total, body.my_share, parts, users, splits, requests, outbox)
    )
    return SplitExpenseResponse.from_view(view)


@router.get("/split-expenses")
def get_split_expenses(
    user_id: Annotated[int, Depends(current_user_id)],
    users: Annotated[UserRepository, Depends(user_repository)],
    splits: Annotated[SplitExpenseRepository, Depends(split_expense_repository)],
    requests: Annotated[MoneyRequestRepository, Depends(money_request_repository)],
) -> SplitExpenseListResponse:
    return SplitExpenseListResponse(
        items=[SplitExpenseResponse.from_view(view) for view in list_splits(user_id, splits, requests, users)]
    )


@router.get("/split-expenses/{split_id}")
def get_split_expense(
    split_id: str,
    user_id: Annotated[int, Depends(current_user_id)],
    users: Annotated[UserRepository, Depends(user_repository)],
    splits: Annotated[SplitExpenseRepository, Depends(split_expense_repository)],
    requests: Annotated[MoneyRequestRepository, Depends(money_request_repository)],
) -> SplitExpenseResponse:
    return SplitExpenseResponse.from_view(get_split(user_id, split_id, splits, requests, users))


@router.post("/split-expenses/{split_id}/parts/{participant_id}/resend", status_code=status.HTTP_201_CREATED)
def post_resend_split_part(
    split_id: str,
    participant_id: str,
    user_id: Annotated[int, Depends(current_user_id)],
    users: Annotated[UserRepository, Depends(user_repository)],
    splits: Annotated[SplitExpenseRepository, Depends(split_expense_repository)],
    requests: Annotated[MoneyRequestRepository, Depends(money_request_repository)],
    outbox: Annotated[OutboxRepository, Depends(outbox_repository)],
    run: Annotated[Atomic, Depends(atomic)],
) -> SplitExpenseResponse:
    # La sol·licitud nova i l'avís van junts (§17.5).
    view = run.run(lambda: resend_part(user_id, split_id, participant_id, users, splits, requests, outbox))
    return SplitExpenseResponse.from_view(view)
