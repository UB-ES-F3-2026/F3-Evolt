"""Despeses dividides: dividir una despesa en sol·licituds de diners (US-30, docs/api.md §17).

Ordre de les validacions en dividir (s'aturen al primer error, §17.2, P100):
  1. Format del cos (al router) i un participant repetit → VALIDATION_ERROR.
  2. Algun participant no existeix o és pendent → RECIPIENT_NOT_FOUND.
  3. Algun participant és qui divideix → SELF_REQUEST.
  4. `total ≤ 0` → INVALID_AMOUNT.
  5. `total` més d'1.000.000,00 € → AMOUNT_OVER_LIMIT.
  6. Concepte buit o de més de 140 caràcters → INVALID_CONCEPT.
  7. Alguna part, o la meva, és `≤ 0` → INVALID_SHARE.
  8. Les parts no sumen el total → SHARES_DO_NOT_MATCH.
Tot o res: la despesa, totes les sol·licituds i tots els avisos, o res. No mou diners.

L'estat, «X de Y han pagat» i el pendent es calculen en llegir (§17.7): no es desen mai.
"""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from app.models import (
    MAX_REQUEST_AMOUNT,
    MAX_REQUEST_CONCEPT,
    REQUEST_PAID,
    REQUEST_PENDING,
    MoneyRequest,
    SplitExpense,
    SplitPart,
    now_madrid,
)
from app.repositories import MoneyRequestRepository, OutboxRepository, SplitExpenseRepository, UserRepository
from app.services.errors import (
    AMOUNT_OVER_LIMIT,
    INVALID_AMOUNT,
    INVALID_CONCEPT,
    INVALID_SHARE,
    RECIPIENT_NOT_FOUND,
    SELF_REQUEST,
    SHARES_DO_NOT_MATCH,
    VALIDATION_ERROR,
    ApiError,
)
from app.services.money_request_service import current_status
from app.services.money_text import format_euros
from app.services.notifications import send_money_request
from app.services.user_search import UserSummary, find_active_user

# Estats de la despesa (§17.7).
SPLIT_PENDING = "pending"
SPLIT_COMPLETED = "completed"
SPLIT_CLOSED = "closed"


@dataclass(frozen=True)
class PartView:
    """Una part tal com la veu qui ha dividit la despesa: la seva sol·licitud més recent."""

    request_id: str
    to: UserSummary
    amount: int
    status: str


@dataclass(frozen=True)
class SplitView:
    """Una `SplitExpense` del contracte (§17.1). La forma JSON la decideix el router."""

    split: SplitExpense
    status: str
    people: int
    paid_count: int
    pending_amount: int
    parts: list[PartView]


def create_split(
    user_id: int,
    raw_concept: str,
    total: int,
    my_share: int,
    raw_parts: list[tuple[str, int]],
    users: UserRepository,
    splits: SplitExpenseRepository,
    requests: MoneyRequestRepository,
    outbox: OutboxRepository,
    now: datetime | None = None,
) -> SplitView:
    """Divideix una despesa: una sol·licitud per participant, amb la seva part (§17.2)."""
    raw_ids = [raw_id for raw_id, _ in raw_parts]
    if len(set(raw_ids)) != len(raw_ids):
        raise ApiError(VALIDATION_ERROR)
    participants = []
    for raw_id, _ in raw_parts:
        participant = find_active_user(raw_id, users)
        if participant is None:
            raise ApiError(RECIPIENT_NOT_FOUND)
        participants.append(participant)
    if any(participant.id == user_id for participant in participants):
        raise ApiError(SELF_REQUEST)
    if total <= 0:
        raise ApiError(INVALID_AMOUNT)
    if total > MAX_REQUEST_AMOUNT:
        raise ApiError(AMOUNT_OVER_LIMIT, message=f"L'import màxim és d'{format_euros(MAX_REQUEST_AMOUNT)}.")
    concept = raw_concept.strip()
    if not concept or len(concept) > MAX_REQUEST_CONCEPT:
        raise ApiError(INVALID_CONCEPT)
    amounts = [amount for _, amount in raw_parts]
    if my_share <= 0 or any(amount <= 0 for amount in amounts):
        raise ApiError(INVALID_SHARE)
    if my_share + sum(amounts) != total:
        raise ApiError(SHARES_DO_NOT_MATCH)

    requester = users.get(user_id)
    if requester is None:
        # `current_user_id` ja rebutja els usuaris inexistents: és un error de programació.
        raise LookupError(f"L'usuari {user_id} no existeix")

    date = now or now_madrid()
    # Cada escriptura deixa com es desfà, com a l'enviament: si una falla, es desfan
    # les anteriors abans de deixar sortir l'error (US-30, criteri 8).
    undo: list[Callable[[], None]] = []
    try:
        split = splits.add(
            requester_id=user_id,
            concept=concept,
            total=total,
            my_share=my_share,
            created_at=date,
            parts=[SplitPart(user_id=p.id, amount=amount) for p, amount in zip(participants, amounts, strict=True)],
        )
        undo.append(lambda: splits.undo_add(split))
        created = []
        for participant, amount in zip(participants, amounts, strict=True):
            request = requests.add(
                requester_id=user_id,
                recipient_id=participant.id,
                amount=amount,
                concept=concept,
                created_at=date,
                split_id=split.id,
            )
            undo.append(lambda request=request: requests.undo_add(request))
            created.append(request)
        for participant, request in zip(participants, created, strict=True):
            message = send_money_request(requester, participant, request.amount, concept, date, outbox)
            undo.append(lambda message=message: outbox.remove(message))
    except Exception:
        for undo_write in reversed(undo):
            undo_write()
        raise
    return split_view(split, created, users, date)


def split_view(
    split: SplitExpense, split_requests: list[MoneyRequest], users: UserRepository, now: datetime
) -> SplitView:
    """L'estat d'ara d'una despesa, amb la sol·licitud més recent de cada participant (§17.7)."""
    latest: dict[int, MoneyRequest] = {}
    for request in sorted(split_requests, key=lambda r: r.seq):
        latest[request.recipient_id] = request
    parts = []
    for part in split.parts:
        request = latest.get(part.user_id)
        participant = users.get(part.user_id)
        if request is None or participant is None:
            raise LookupError(f"Falta la sol·licitud o l'usuari {part.user_id} de la despesa {split.id}")
        parts.append(PartView(request.id, UserSummary.from_user(participant), part.amount, current_status(request, now)))
    statuses = [part.status for part in parts]
    if REQUEST_PENDING in statuses:
        status = SPLIT_PENDING
    elif all(s == REQUEST_PAID for s in statuses):
        status = SPLIT_COMPLETED
    else:
        status = SPLIT_CLOSED
    return SplitView(
        split=split,
        status=status,
        people=len(parts) + 1,
        paid_count=statuses.count(REQUEST_PAID),
        pending_amount=sum(part.amount for part in parts if part.status == REQUEST_PENDING),
        parts=parts,
    )
