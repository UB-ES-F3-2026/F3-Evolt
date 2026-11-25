"""Dades del compte i transferències d'un altre banc (T12.2 · US-12, docs/api.md §16).

L'IBAN no es desa: es calcula del número intern de l'usuari amb la regla de §16.2
(P94), i així l'usuari 1 té el dels mockups, `ES91 2100 0418 4502 0005 1332`.

Ordre de les validacions de la transferència rebuda (§16.3, P97):
  1. Format del cos (al router) i ordenant buit o de més de 70 caràcters → VALIDATION_ERROR.
  2. L'IBAN no és de cap usuari actiu → RECIPIENT_NOT_FOUND.
  3. `amount ≤ 0` → INVALID_AMOUNT.
  4. `amount` més d'1.000.000,00 € → AMOUNT_OVER_LIMIT.
Tot o res: el moviment, el saldo i l'avís es fan tots o cap.
"""

import threading
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from app.models import KIND_TRANSFER_IN, TYPE_INCOME, Movement, User, now_madrid
from app.repositories import AccountRepository, MovementRepository, OutboxRepository, UserRepository
from app.services.errors import (
    AMOUNT_OVER_LIMIT,
    INVALID_AMOUNT,
    RECIPIENT_NOT_FOUND,
    VALIDATION_ERROR,
    ApiError,
)
from app.services.money_text import format_euros
from app.services.notifications import send_incoming_transfer
from app.services.transfer_service import TRANSFER_ICON, TRANSFER_RECEIVED_CONCEPT, display_name
from app.services.user_search import find_active_user, public_user_id

# Regla de l'IBAN (§16.2): entitat, oficina i el número de compte de l'usuari 0.
BANK_CODE = "2100"
BRANCH_CODE = "0418"
ACCOUNT_NUMBER_BASE = 200_051_331
# El mateix BIC per a tothom (decisió D, 24/11, P95).
BIC = "EVOLESB1XXX"

# Pesos dels dígits de control del CCC, d'esquerra a dreta.
_CCC_WEIGHTS = (1, 2, 4, 8, 5, 10, 9, 7, 3, 6)
# Les lletres «ES» passades a números per al residu de l'IBAN: E = 14, S = 28.
_SPAIN_DIGITS = "1428"

MAX_PAYER_LENGTH = 70
# 1.000.000,00 €, com el màxim d'una sol·licitud (§16.3).
MAX_INCOMING_AMOUNT = 100_000_000

# La transferència llegeix el saldo i després l'escriu. El router ja ho fa dins
# d'`atomic.run(...)`; el pany protegeix també les crides directes al servei.
_INCOMING_LOCK = threading.RLock()


@dataclass(frozen=True)
class AccountDetails:
    """Resposta de `GET /api/account` (§16.1). La forma JSON la decideix el router."""

    iban: str
    bic: str
    holder: str


@dataclass(frozen=True)
class IncomingTransferResult:
    balance: int
    movement: Movement


def _ccc_digit(digits: str) -> int:
    """Un dígit de control del CCC: 11 menys el residu entre 11 (11 → 0 i 10 → 1)."""
    rest = 11 - sum(int(digit) * weight for digit, weight in zip(digits, _CCC_WEIGHTS, strict=True)) % 11
    return {11: 0, 10: 1}.get(rest, rest)


def iban_for(user_id: int) -> str:
    """L'IBAN d'un usuari, sense espais: sempre el mateix i diferent per a cada usuari (§16.2)."""
    account_number = f"{ACCOUNT_NUMBER_BASE + user_id:010d}"
    control = f"{_ccc_digit('00' + BANK_CODE + BRANCH_CODE)}{_ccc_digit(account_number)}"
    bban = BANK_CODE + BRANCH_CODE + control + account_number
    check = 98 - int(bban + _SPAIN_DIGITS + "00") % 97
    return f"ES{check:02d}{bban}"


def user_id_for_iban(raw_iban: str) -> int | None:
    """El número d'usuari d'un IBAN d'Evolt, o None si no ho és (§16.5).

    Accepta espais i minúscules. Es treu el número del compte i es comprova que
    l'IBAN sencer és exactament el que toca a aquell usuari.
    """
    iban = raw_iban.replace(" ", "").upper()
    if len(iban) != 24 or not iban[2:].isdigit():
        return None
    user_id = int(iban[14:]) - ACCOUNT_NUMBER_BASE
    if user_id <= 0 or iban_for(user_id) != iban:
        return None
    return user_id


def account_details(user_id: int, users: UserRepository) -> AccountDetails:
    """L'IBAN, el BIC i el titular del compte de l'usuari (§16.1)."""
    user = users.get(user_id)
    if user is None:
        # `current_user_id` ja rebutja els usuaris inexistents: és un error de programació.
        raise LookupError(f"L'usuari {user_id} no existeix")
    return AccountDetails(iban=iban_for(user_id), bic=BIC, holder=display_name(user))


def receive_external_transfer(
    raw_iban: str,
    amount: int,
    raw_payer: str,
    users: UserRepository,
    accounts: AccountRepository,
    movements: MovementRepository,
    outbox: OutboxRepository,
    now: datetime | None = None,
) -> IncomingTransferResult:
    """Suma una transferència d'un altre banc al compte de l'IBAN (§16.3). Eina de desenvolupament."""
    payer = raw_payer.strip()
    if not payer or len(payer) > MAX_PAYER_LENGTH:
        raise ApiError(VALIDATION_ERROR)
    with _INCOMING_LOCK:
        recipient = _active_user_for_iban(raw_iban, users)
        if recipient is None:
            raise ApiError(RECIPIENT_NOT_FOUND)
        if amount <= 0:
            raise ApiError(INVALID_AMOUNT)
        if amount > MAX_INCOMING_AMOUNT:
            raise ApiError(AMOUNT_OVER_LIMIT, message=f"L'import màxim és d'{format_euros(MAX_INCOMING_AMOUNT)}.")

        account = accounts.get_by_user(recipient.id)
        if account is None:
            raise LookupError(f"L'usuari {recipient.id} no té compte principal")
        balance = account.balance
        date = now or now_madrid()

        # Com a l'enviament: cada escriptura deixa com es desfà, i si una falla es
        # desfan les anteriors abans de deixar sortir l'error.
        undo: list[Callable[[], None]] = []
        try:
            movement = movements.add(
                account_id=account.id,
                amount=amount,
                concept=f"{TRANSFER_RECEIVED_CONCEPT} · {payer}",
                date=date,
                type=TYPE_INCOME,
                icon=TRANSFER_ICON,
                kind=KIND_TRANSFER_IN,
                counterparty=payer,
            )
            undo.append(lambda: movements.remove(movement))
            accounts.set_balance(recipient.id, balance + amount)
            undo.append(lambda: accounts.set_balance(recipient.id, balance))
            send_incoming_transfer(recipient, payer, amount, date, outbox)
        except Exception:
            for undo_write in reversed(undo):
                undo_write()
            raise
        return IncomingTransferResult(balance=balance + amount, movement=movement)


def _active_user_for_iban(raw_iban: str, users: UserRepository) -> User | None:
    user_id = user_id_for_iban(raw_iban)
    return find_active_user(public_user_id(user_id), users) if user_id is not None else None
