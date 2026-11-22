"""Enviar diners a un altre usuari (T14.1 · US-14, docs/api.md §13.4, §13.5 i §13.9).

Ordre de les validacions (s'aturen al primer error, P70):
  1. Format del cos → el router, VALIDATION_ERROR.
  2. El destinatari no existeix o està pendent → RECIPIENT_NOT_FOUND.
  3. El destinatari és l'usuari de la sessió → SELF_TRANSFER.
  4. `amount ≤ 0` → INVALID_AMOUNT.
  5. Més que el saldo de qui envia → INSUFFICIENT_BALANCE.
  6. Enviat avui + `amount` > límit diari → TRANSFER_LIMIT_EXCEEDED.

Tot o res: es valida tot abans d'escriure, i les sis escriptures (dos saldos, dos
moviments i dos avisos) es fan totes o cap, com l'aportació (`pot_service.contribute`).
"""

import threading
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from app.models import (
    KIND_TRANSFER_IN,
    KIND_TRANSFER_OUT,
    MADRID_TZ,
    TYPE_EXPENSE,
    TYPE_INCOME,
    Movement,
    User,
    now_madrid,
)
from app.repositories import AccountRepository, MovementRepository, OutboxRepository, UserRepository
from app.services.errors import (
    INSUFFICIENT_BALANCE,
    INVALID_AMOUNT,
    RECIPIENT_NOT_FOUND,
    SELF_TRANSFER,
    TRANSFER_LIMIT_EXCEEDED,
    ApiError,
)
from app.services.notifications import send_transfer_received, send_transfer_sent
from app.services.user_search import UserSummary, find_active_user

# US-14 i §13.5: com a màxim 1.000,00 € enviats per dia natural a Madrid. Arribar just
# al límit està permès. És una regla diferent del límit de recàrrega (P71), encara que
# avui valguin el mateix: per això té la seva pròpia constant.
MAX_DAILY_TRANSFER = 100_000

# Concepte quan qui envia no n'escriu cap (P72).
TRANSFER_SENT_CONCEPT = "Transferència enviada"
TRANSFER_RECEIVED_CONCEPT = "Transferència rebuda"
TRANSFER_ICON = "transfer"

# Dos enviaments alhora podrien llegir el mateix saldo o el mateix límit. El router
# ja ho fa dins d'`atomic.run(...)`; el pany protegeix també les crides directes al
# servei, com a l'aportació.
_TRANSFER_LOCK = threading.RLock()


@dataclass(frozen=True)
class TransferResult:
    """Resultat de l'enviament. La forma JSON la decideix el router."""

    balance: int
    movement: Movement
    recipient: UserSummary


def display_name(user: User) -> str:
    """Nom visible d'un usuari: el `name` o, si no en té, `@username` (§13.4, P35)."""
    return user.name or f"@{user.visible_username}"


def remaining_today(user_id: int, accounts: AccountRepository, movements: MovementRepository, now: datetime) -> int:
    """El que l'usuari encara pot enviar avui, en cèntims; mai menys de 0 (§13.5)."""
    account = _account_of(user_id, accounts)
    today = now.astimezone(MADRID_TZ).date()
    return max(0, MAX_DAILY_TRANSFER - movements.sum_transfers_sent_on_day(account.id, today))


def send_money(
    sender_id: int,
    to_user_id: str,
    amount: int,
    concept: str | None,
    users: UserRepository,
    accounts: AccountRepository,
    movements: MovementRepository,
    outbox: OutboxRepository,
    now: datetime | None = None,
) -> TransferResult:
    """Passa `amount` cèntims del compte de qui envia al de qui rep (§13.4).

    `now` permet fixar el moment als tests. Enviar o rebre no toca l'XP.
    """
    clean_concept = concept.strip() if concept else ""
    with _TRANSFER_LOCK:
        recipient = find_active_user(to_user_id, users)
        if recipient is None:
            raise ApiError(RECIPIENT_NOT_FOUND)
        if recipient.id == sender_id:
            raise ApiError(SELF_TRANSFER)
        if amount <= 0:
            raise ApiError(INVALID_AMOUNT)

        sender = users.get(sender_id)
        if sender is None:
            # `current_user_id` ja rebutja els usuaris inexistents: és un error de programació.
            raise LookupError(f"L'usuari {sender_id} no existeix")
        sender_account = _account_of(sender_id, accounts)
        recipient_account = _account_of(recipient.id, accounts)
        if amount > sender_account.balance:
            raise ApiError(INSUFFICIENT_BALANCE)

        date = now or now_madrid()
        left_today = remaining_today(sender_id, accounts, movements, date)
        if amount > left_today:
            raise ApiError(TRANSFER_LIMIT_EXCEEDED, details={"remainingToday": left_today})

        sender_name = display_name(sender)
        recipient_name = display_name(recipient)
        sender_balance = sender_account.balance
        recipient_balance = recipient_account.balance

        # Cada escriptura feta deixa aquí com es desfà. Si una falla, es desfan les
        # anteriors, de l'última a la primera, abans de deixar sortir l'error. Els avisos
        # van al final: la bústia no es pot desfer, i amb Firestore tot és una transacció.
        undo: list[Callable[[], None]] = []
        try:
            sent = movements.add(
                account_id=sender_account.id,
                amount=amount,
                concept=clean_concept or TRANSFER_SENT_CONCEPT,
                date=date,
                type=TYPE_EXPENSE,
                icon=TRANSFER_ICON,
                kind=KIND_TRANSFER_OUT,
                counterparty=recipient_name,
            )
            undo.append(lambda: movements.remove(sent))
            received = movements.add(
                account_id=recipient_account.id,
                amount=amount,
                concept=clean_concept or TRANSFER_RECEIVED_CONCEPT,
                date=date,
                type=TYPE_INCOME,
                icon=TRANSFER_ICON,
                kind=KIND_TRANSFER_IN,
                counterparty=sender_name,
            )
            undo.append(lambda: movements.remove(received))
            accounts.set_balance(sender_id, sender_balance - amount)
            undo.append(lambda: accounts.set_balance(sender_id, sender_balance))
            accounts.set_balance(recipient.id, recipient_balance + amount)
            undo.append(lambda: accounts.set_balance(recipient.id, recipient_balance))
            send_transfer_sent(sender, recipient_name, amount, date, outbox)
            send_transfer_received(recipient, sender_name, amount, clean_concept or None, date, outbox)
        except Exception:
            for undo_write in reversed(undo):
                undo_write()
            raise

        return TransferResult(
            balance=sender_balance - amount,
            movement=sent,
            recipient=UserSummary.from_user(recipient),
        )


def _account_of(user_id: int, accounts: AccountRepository):
    account = accounts.get_by_user(user_id)
    if account is None:
        # Tot usuari actiu té compte principal: arribar aquí ha d'acabar en INTERNAL_ERROR.
        raise LookupError(f"L'usuari {user_id} no té compte principal")
    return account
