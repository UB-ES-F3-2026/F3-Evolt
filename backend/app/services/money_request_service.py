"""Sol·licituds de diners: crear, llistar, cancel·lar i pagar (US-15, US-16 i US-39, docs/api.md §14 i §15).

Ordre de les validacions en crear (s'aturen al primer error, §14.2):
  1. Format del cos → el router, VALIDATION_ERROR.
  2. El destinatari no existeix o és pendent → RECIPIENT_NOT_FOUND.
  3. El destinatari és qui demana → SELF_REQUEST.
  4. `amount ≤ 0` → INVALID_AMOUNT.
  5. `amount` més d'1.000.000,00 € → AMOUNT_OVER_LIMIT.
  6. Concepte buit o de més de 140 caràcters → INVALID_CONCEPT.
Una sol·licitud no mou diners: només es desa i deixa un avís a la bústia (tot o res).

`expired` no es desa mai: es calcula en llegir pel dia natural de Madrid (§14.5).

Ordre de les validacions en pagar una rebuda (§15.3, P89):
  1. No existeix, no és rebuda per l'usuari o s'ha cancel·lat → REQUEST_NOT_FOUND.
  2. Ja no és pendent → REQUEST_NOT_PENDING.
  3. i 4. Les de l'enviament de la US-14: INSUFFICIENT_BALANCE i TRANSFER_LIMIT_EXCEEDED.
Pagar és l'enviament de la US-14 i el canvi a `paid`, tot o res.
"""

import threading
from dataclasses import dataclass
from datetime import datetime, timedelta

from app.models import (
    MADRID_TZ,
    MAX_REQUEST_AMOUNT,
    MAX_REQUEST_CONCEPT,
    REQUEST_EXPIRED,
    REQUEST_PAID,
    REQUEST_PENDING,
    MoneyRequest,
    Movement,
    now_madrid,
)
from app.repositories import (
    AccountRepository,
    MoneyRequestRepository,
    MovementRepository,
    OutboxRepository,
    UserRepository,
)
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
from app.services.transfer_service import send_money
from app.services.user_search import UserSummary, find_active_user, public_user_id

# Una sol·licitud sense resposta caduca als 7 dies naturals (US-15).
LIFETIME_DAYS = 7

# Pagar i rebutjar llegeixen l'estat i després l'escriuen. El router ja ho fa dins
# d'`atomic.run(...)`; el pany protegeix també les crides directes al servei, perquè
# dos pagaments alhora (o pagar i rebutjar alhora) no passin tots dos (§15.3).
_RESPOND_LOCK = threading.RLock()


@dataclass(frozen=True)
class SentRequest:
    """Una sol·licitud tal com la veu qui l'ha enviada (§14.1). La forma JSON la decideix el router."""

    request: MoneyRequest
    to: UserSummary
    status: str
    expires_at: datetime


@dataclass(frozen=True)
class ReceivedRequest:
    """Una sol·licitud tal com la veu qui l'ha rebut (§15.1): amb `from` en lloc de `to`."""

    request: MoneyRequest
    sender: UserSummary
    status: str
    expires_at: datetime


@dataclass(frozen=True)
class PaymentResult:
    """Resultat de pagar una sol·licitud (§15.3). La forma JSON la decideix el router."""

    balance: int
    movement: Movement
    request: ReceivedRequest


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


def list_received(
    user_id: int, requests: MoneyRequestRepository, users: UserRepository, now: datetime | None = None
) -> list[ReceivedRequest]:
    """Les rebudes per l'usuari, en qualsevol estat, de la més recent a la més antiga (§15.2)."""
    moment = now or now_madrid()
    received = []
    for request in requests.list_by_recipient(user_id):
        requester = users.get(request.requester_id)
        if requester is None:
            raise LookupError(f"Qui ha fet la sol·licitud {request.requester_id} no existeix")
        received.append(
            ReceivedRequest(
                request,
                UserSummary.from_user(requester),
                current_status(request, moment),
                expires_at(request.created_at),
            )
        )
    return received


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


def pay_request(
    user_id: int,
    request_id: str,
    users: UserRepository,
    accounts: AccountRepository,
    movements: MovementRepository,
    requests: MoneyRequestRepository,
    outbox: OutboxRepository,
    now: datetime | None = None,
) -> PaymentResult:
    """Paga una sol·licitud pendent que ha rebut l'usuari (§15.3).

    És un enviament de la US-14 a qui la va fer, amb l'import i el concepte de la
    sol·licitud, i després el canvi a `paid`. Si l'enviament falla, el mateix
    `send_money` ja desfà el que havia escrit i la sol·licitud continua pendent. Amb
    Firestore, el canvi d'estat va al final perquè totes les lectures de la
    transacció han d'anar abans de les escriptures.
    """
    moment = now or now_madrid()
    with _RESPOND_LOCK:
        request = _pending_received(user_id, request_id, requests, moment)
        requester = users.get(request.requester_id)
        if requester is None:
            raise LookupError(f"Qui ha fet la sol·licitud {request.requester_id} no existeix")
        transfer = send_money(
            user_id,
            public_user_id(request.requester_id),
            request.amount,
            request.concept,
            users,
            accounts,
            movements,
            outbox,
            now=moment,
        )
        requests.set_status(request.id, REQUEST_PAID)
        received = ReceivedRequest(request, UserSummary.from_user(requester), REQUEST_PAID, expires_at(request.created_at))
        return PaymentResult(transfer.balance, transfer.movement, received)


def _pending_received(user_id: int, request_id: str, requests: MoneyRequestRepository, now: datetime) -> MoneyRequest:
    """La sol·licitud pendent que ha rebut l'usuari, o l'error de §15.3 (passos 1 i 2)."""
    request = requests.get(request_id)
    if request is None or request.recipient_id != user_id:
        raise ApiError(REQUEST_NOT_FOUND)
    if current_status(request, now) != REQUEST_PENDING:
        # El text de «Sol·licituds rebudes» (§15.7); el de cancel·lar és un altre.
        raise ApiError(REQUEST_NOT_PENDING, message="Aquesta sol·licitud ja no està pendent.")
    return request
