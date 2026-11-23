"""Canvi de divisa entre dos comptes de l'usuari (US-27, docs/api.md §12.7 i §12.8).

Ordre de les validacions (s'aturen al primer error, §12.7):
  1. Format del cos (divises string, `amount` enter estricte) → el router, VALIDATION_ERROR.
  2. `fromCurrency` i `toCurrency` són la mateixa → aquí, SAME_CURRENCY.
  3. Alguna de les dues no és un compte de l'usuari, també si el codi no és a la
     llista → aquí, SUBACCOUNT_NOT_FOUND.
  4. `amount ≤ 0` → aquí, INVALID_AMOUNT.
  5. El convertit exacte no arriba a una unitat menor del destí → aquí, AMOUNT_TOO_SMALL.
  6. `amount + commission` supera el saldo de l'origen → aquí, INSUFFICIENT_BALANCE.

Un canvi fa quatre escriptures: un moviment i el saldo de cada compte. O es fan
totes, o no en queda cap. El router el fa dins d'`atomic.run(...)`: dos canvis
alhora des del mateix compte van un darrere l'altre, i el segon es valida amb el
saldo que ha deixat el primer.

El tipus de canvi i la comissió surten de `app.models.currency` (D2): aquí no hi
ha cap xifra.
"""

from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import datetime

from app.models import (
    KIND_OTHER,
    MAIN_CURRENCY,
    MAIN_SUBACCOUNT_ID,
    TYPE_EXPENSE,
    TYPE_INCOME,
    Account,
    commission,
    convert,
    now_madrid,
    rate_bps,
    reaches_one_unit,
)
from app.repositories import AccountRepository, MovementRepository, SubaccountRepository
from app.services.errors import (
    AMOUNT_TOO_SMALL,
    INSUFFICIENT_BALANCE,
    INVALID_AMOUNT,
    SAME_CURRENCY,
    SUBACCOUNT_NOT_FOUND,
    ApiError,
)
from app.services.subaccount_service import AccountInCurrency

# Icona dels moviments del compte principal que fa un canvi (§12.8).
EXCHANGE_ICON = "transfer"


@dataclass(frozen=True)
class ExchangeResult:
    """Resultat del canvi (§12.7). La forma JSON la decideix el router."""

    from_account: AccountInCurrency
    to_account: AccountInCurrency
    amount: int
    commission: int
    received: int


def exchange_concept(from_currency: str, to_currency: str) -> str:
    """El concepte dels dos moviments: «Canvi EUR → USD» (decisió del PO, §12.8)."""
    return f"Canvi {from_currency} → {to_currency}"


def exchange(
    user_id: int,
    from_currency: str,
    to_currency: str,
    amount: int,
    accounts: AccountRepository,
    subaccounts: SubaccountRepository,
    movements: MovementRepository,
    now: datetime | None = None,
) -> ExchangeResult:
    """Passa `amount` (unitat menor de l'origen) d'un compte de l'usuari a un altre (§12.7).

    `now` permet fixar el moment als tests.
    """
    if from_currency == to_currency:
        raise ApiError(SAME_CURRENCY)
    origin = _account_in(user_id, from_currency, accounts, subaccounts)
    destination = _account_in(user_id, to_currency, accounts, subaccounts)
    if amount <= 0:
        raise ApiError(INVALID_AMOUNT)
    if not reaches_one_unit(amount, from_currency, to_currency):
        raise ApiError(AMOUNT_TOO_SMALL)
    fee = commission(amount, from_currency)
    charge = amount + fee
    if charge > origin.balance:
        raise ApiError(INSUFFICIENT_BALANCE)
    received = convert(amount, from_currency, to_currency)
    # Totes les lectures abans de la primera escriptura: amb Firestore és una
    # regla de les transaccions.
    main_account_id = _main_account(user_id, accounts).id if MAIN_CURRENCY in (from_currency, to_currency) else None

    concept = exchange_concept(from_currency, to_currency)
    date = now or now_madrid()
    new_origin_balance = origin.balance - charge
    new_destination_balance = destination.balance + received

    # Cada escriptura feta deixa aquí com es desfà. Si una falla, es desfan les
    # anteriors, de l'última a la primera, abans de deixar sortir l'error (com
    # `pot_service.contribute`). Primer els dos moviments i després els dos saldos.
    undo: list[Callable[[], None]] = []
    try:
        _add_movement(main_account_id, origin, charge, concept, date, TYPE_EXPENSE, subaccounts, movements, undo)
        _add_movement(
            main_account_id, destination, received, concept, date, TYPE_INCOME, subaccounts, movements, undo
        )
        _set_balance(user_id, origin, new_origin_balance, accounts, subaccounts, undo)
        _set_balance(user_id, destination, new_destination_balance, accounts, subaccounts, undo)
    except Exception:
        for undo_write in reversed(undo):
            undo_write()
        raise

    # Còpies amb el saldo nou: no es tornen a llegir (amb Firestore, la lectura
    # seria la d'abans del canvi, dins de la mateixa transacció).
    return ExchangeResult(
        from_account=replace(origin, balance=new_origin_balance),
        to_account=replace(destination, balance=new_destination_balance),
        amount=amount,
        commission=fee,
        received=received,
    )


def _account_in(
    user_id: int, currency: str, accounts: AccountRepository, subaccounts: SubaccountRepository
) -> AccountInCurrency:
    """El compte de l'usuari en aquesta divisa, o SUBACCOUNT_NOT_FOUND (§12.7, pas 3).

    L'EUR és sempre el compte principal (`main`). Una divisa sense subcompte, o un
    codi fora de la llista, no té compte: tots dos casos són SUBACCOUNT_NOT_FOUND.
    """
    if currency == MAIN_CURRENCY:
        return AccountInCurrency(
            id=MAIN_SUBACCOUNT_ID,
            currency=MAIN_CURRENCY,
            balance=_main_account(user_id, accounts).balance,
            is_main=True,
            rate_bps=rate_bps(MAIN_CURRENCY),
        )
    subaccount = next((sub for sub in subaccounts.list_by_user(user_id) if sub.currency == currency), None)
    if subaccount is None:
        raise ApiError(SUBACCOUNT_NOT_FOUND)
    return AccountInCurrency.from_subaccount(subaccount)


def _main_account(user_id: int, accounts: AccountRepository) -> Account:
    account = accounts.get_by_user(user_id)
    if account is None:
        # `current_user_id` ja rebutja els usuaris inexistents: arribar aquí és un
        # error de programació i ha d'acabar en INTERNAL_ERROR.
        raise LookupError(f"L'usuari {user_id} no té compte principal")
    return account


def _add_movement(
    main_account_id: int | None,
    account: AccountInCurrency,
    amount: int,
    concept: str,
    date: datetime,
    type: str,
    subaccounts: SubaccountRepository,
    movements: MovementRepository,
    undo: list[Callable[[], None]],
) -> None:
    """El moviment d'un costat del canvi (§12.8).

    Al compte principal, un `Movement` normal, que surt a Inici i a la llista. A un
    subcompte, una entrada del seu historial (T26.1), que només surt allà.
    """
    if account.is_main:
        movement = movements.add(
            account_id=main_account_id,
            amount=amount,
            concept=concept,
            date=date,
            type=type,
            icon=EXCHANGE_ICON,
            kind=KIND_OTHER,
        )
        undo.append(lambda: movements.remove(movement))
    else:
        entry = subaccounts.add_movement(
            subaccount_id=account.id, amount=amount, concept=concept, date=date, type=type
        )
        undo.append(lambda: subaccounts.remove_movement(entry))


def _set_balance(
    user_id: int,
    account: AccountInCurrency,
    balance: int,
    accounts: AccountRepository,
    subaccounts: SubaccountRepository,
    undo: list[Callable[[], None]],
) -> None:
    """Assigna el saldo nou d'un costat del canvi i deixa com es desfà."""
    if account.is_main:
        accounts.set_balance(user_id, balance)
        undo.append(lambda: accounts.set_balance(user_id, account.balance))
    else:
        subaccounts.set_balance(account.id, balance)
        undo.append(lambda: subaccounts.set_balance(account.id, account.balance))
