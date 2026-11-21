"""Sol·licituds de diners: crear, llistar les enviades i cancel·lar (US-15, docs/api.md §14).

Ordre de les validacions en crear (s'aturen al primer error, §14.2):
  1. Format del cos → el router, VALIDATION_ERROR.
  2. El destinatari no existeix o és pendent → RECIPIENT_NOT_FOUND.
  3. El destinatari és qui demana → SELF_REQUEST.
  4. `amount ≤ 0` → INVALID_AMOUNT.
  5. `amount` més d'1.000.000,00 € → AMOUNT_OVER_LIMIT.
  6. Concepte buit o de més de 140 caràcters → INVALID_CONCEPT.
Una sol·licitud no mou diners: només es desa i deixa un avís a la bústia (tot o res).

`expired` no es desa mai: es calcula en llegir pel dia natural de Madrid (§14.5).
"""

from dataclasses import dataclass
from datetime import datetime, timedelta

from app.models import (
    MADRID_TZ,
    MAX_REQUEST_AMOUNT,
    MAX_REQUEST_CONCEPT,
    REQUEST_EXPIRED,
    REQUEST_PENDING,
    MoneyRequest,
    now_madrid,
)
from app.repositories import MoneyRequestRepository, OutboxRepository, UserRepository
from app.services.errors import (
    AMOUNT_OVER_LIMIT,
    INVALID_AMOUNT,
    INVALID_CONCEPT,
    RECIPIENT_NOT_FOUND,
    REQUEST_NOT_FOUND,
    REQUEST_NOT_PENDING,
    SELF_REQUEST,
    ApiError,
)
from app.services.money_text import format_euros
from app.services.notifications import send_money_request
from app.services.user_search import UserSummary, find_active_user

# Una sol·licitud sense resposta caduca als 7 dies naturals (US-15).
LIFETIME_DAYS = 7


@dataclass(frozen=True)
class SentRequest:
    """Una sol·licitud tal com la veu qui l'ha enviada (§14.1). La forma JSON la decideix el router."""

    request: MoneyRequest
    to: UserSummary
    status: str
    expires_at: datetime


def expires_at(created_at: datetime) -> datetime:
    """Les 00:00 de Madrid del setè dia després del de creació (§14.5).

    Una del 14 de novembre (a qualsevol hora) caduca a les 00:00 del 21.
    """
    day = created_at.astimezone(MADRID_TZ).date() + timedelta(days=LIFETIME_DAYS)
    return datetime(day.year, day.month, day.day, tzinfo=MADRID_TZ)


def current_status(request: MoneyRequest, now: datetime) -> str:
    """L'estat d'ara: `expired` si és pendent i ja ha arribat l'hora; si no, el desat."""
    if request.status == REQUEST_PENDING and now >= expires_at(request.created_at):
        return REQUEST_EXPIRED
    return request.status


def create_request(
    user_id: int,
    raw_recipient_id: str,
    amount: int,
    raw_concept: str,
    users: UserRepository,
    requests: MoneyRequestRepository,
    outbox: OutboxRepository,
    now: datetime | None = None,
) -> SentRequest:
    """Desa una sol·licitud pendent i avisa el destinatari (§14.2)."""
    recipient = find_active_user(raw_recipient_id, users)
    if recipient is None:
        raise ApiError(RECIPIENT_NOT_FOUND)
    if recipient.id == user_id:
        raise ApiError(SELF_REQUEST)
    if amount <= 0:
        raise ApiError(INVALID_AMOUNT)
    if amount > MAX_REQUEST_AMOUNT:
        raise ApiError(AMOUNT_OVER_LIMIT, message=f"L'import màxim és d'{format_euros(MAX_REQUEST_AMOUNT)}.")
    concept = raw_concept.strip()
    if not concept or len(concept) > MAX_REQUEST_CONCEPT:
        raise ApiError(INVALID_CONCEPT)

    requester = users.get(user_id)
    if requester is None:
        # `current_user_id` ja rebutja els usuaris inexistents: és un error de programació.
        raise LookupError(f"L'usuari {user_id} no existeix")

    date = now or now_madrid()
    request = requests.add(
        requester_id=user_id,
        recipient_id=recipient.id,
        amount=amount,
        concept=concept,
        created_at=date,
    )
    try:
        send_money_request(requester, recipient, amount, concept, date, outbox)
    except Exception:
        # Tot o res: sense avís, la sol·licitud no es queda.
        requests.undo_add(request)
        raise
    return SentRequest(request, UserSummary.from_user(recipient), REQUEST_PENDING, expires_at(date))


def list_sent(
    user_id: int, requests: MoneyRequestRepository, users: UserRepository, now: datetime | None = None
) -> list[SentRequest]:
    """Les enviades per l'usuari, de la més recent a la més antiga, amb l'estat d'ara (§14.3)."""
    moment = now or now_madrid()
    sent = []
    for request in requests.list_by_requester(user_id):
        recipient = users.get(request.recipient_id)
        if recipient is None:
            raise LookupError(f"El destinatari {request.recipient_id} no existeix")
        sent.append(
            SentRequest(
                request,
                UserSummary.from_user(recipient),
                current_status(request, moment),
                expires_at(request.created_at),
            )
        )
    return sent


def cancel_request(
    user_id: int, request_id: str, requests: MoneyRequestRepository, now: datetime | None = None
) -> None:
    """Esborra una sol·licitud pendent de l'usuari (§14.4)."""
    request = requests.get(request_id)
    if request is None or request.requester_id != user_id:
        raise ApiError(REQUEST_NOT_FOUND)
    if current_status(request, now or now_madrid()) != REQUEST_PENDING:
        raise ApiError(REQUEST_NOT_PENDING)
    requests.delete(request.id)
