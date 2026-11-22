"""Subcomptes en divisa: llistar, crear, eliminar i veure'n l'historial
(US-25 i US-26, docs/api.md §12.2 a §12.6).

Ordre de les validacions en crear (s'aturen al primer error, §12.4):
  1. Format del cos (`currency` string) → el router, VALIDATION_ERROR.
  2. El codi no és a la llista tancada → aquí, CURRENCY_NOT_SUPPORTED.
  3. L'usuari ja té un compte en aquesta divisa, també si és l'EUR principal →
     aquí, CURRENCY_EXISTS.
Un error no crea res ni gasta cap id. El router fa la creació dins
d'`atomic.run(...)`: de dues peticions alhora per a la mateixa divisa, la segona
ja veu el subcompte de la primera i rep CURRENCY_EXISTS.

Eliminar (§12.5) també va dins d'`atomic.run(...)`, perquè la comprovació del
saldo i l'esborrat no es puguin separar d'un canvi que arribi alhora (T27.1).
"""

from dataclasses import dataclass

from app.models import (
    CURRENCIES,
    MAIN_CURRENCY,
    MAIN_SUBACCOUNT_ID,
    Subaccount,
    SubaccountMovement,
    rate_bps,
    total_in_euros,
)
from app.repositories import AccountRepository, SubaccountRepository
from app.services.errors import (
    CURRENCY_EXISTS,
    CURRENCY_NOT_SUPPORTED,
    MAIN_ACCOUNT_NOT_DELETABLE,
    SUBACCOUNT_NOT_EMPTY,
    SUBACCOUNT_NOT_FOUND,
    ApiError,
)


@dataclass(frozen=True)
class AccountInCurrency:
    """Un compte de l'usuari tal com el veu l'API (`Subaccount`, §12.2).

    El compte principal en euros no es desa com a subcompte: es construeix a partir
    de l'`Account`, amb l'id `main`. La forma JSON la decideix el router.
    """

    id: str
    currency: str
    balance: int
    is_main: bool
    rate_bps: int

    @classmethod
    def from_subaccount(cls, subaccount: Subaccount) -> "AccountInCurrency":
        return cls(
            id=subaccount.id,
            currency=subaccount.currency,
            balance=subaccount.balance,
            is_main=False,
            rate_bps=rate_bps(subaccount.currency),
        )


@dataclass(frozen=True)
class SubaccountList:
    """Resultat de `GET /api/subaccounts` (§12.3)."""

    items: list[AccountInCurrency]
    total_in_euros: int


def list_subaccounts(
    user_id: int,
    accounts: AccountRepository,
    subaccounts: SubaccountRepository,
) -> SubaccountList:
    """Tots els comptes de l'usuari: primer l'EUR principal i després els subcomptes
    per ordre de creació, amb el total aproximat en cèntims d'euro (§12.3).
    """
    main = _main_account(user_id, accounts)
    items = [main] + [AccountInCurrency.from_subaccount(sub) for sub in subaccounts.list_by_user(user_id)]
    total = total_in_euros([(item.balance, item.currency) for item in items])
    return SubaccountList(items=items, total_in_euros=total)


def create_subaccount(user_id: int, currency: str, subaccounts: SubaccountRepository) -> AccountInCurrency:
    """Crea un subcompte de l'usuari en una divisa nova, amb saldo 0 (§12.4)."""
    if currency not in CURRENCIES:
        raise ApiError(CURRENCY_NOT_SUPPORTED)
    # L'EUR és el compte principal, que tots els usuaris ja tenen.
    if currency == MAIN_CURRENCY or any(sub.currency == currency for sub in subaccounts.list_by_user(user_id)):
        raise ApiError(CURRENCY_EXISTS)
    return AccountInCurrency.from_subaccount(subaccounts.add(user_id=user_id, currency=currency))


def delete_subaccount(user_id: int, subaccount_id: str, subaccounts: SubaccountRepository) -> None:
    """Elimina un subcompte en divisa de l'usuari que té saldo 0 (US-26, §12.5).

    Ordre de les validacions (s'aturen al primer error):
      1. No existeix o és d'un altre usuari → SUBACCOUNT_NOT_FOUND.
      2. És el compte principal → MAIN_ACCOUNT_NOT_DELETABLE, tingui el saldo que tingui.
      3. El saldo no és exactament 0 → SUBACCOUNT_NOT_EMPTY.
    `main` existeix sempre i és de l'usuari, així que el pas 1 no l'atura mai: per
    això es mira primer, abans de buscar-lo al repositori (on no hi és, §12.11).
    Només s'esborra el subcompte: el seu historial es queda desat, i els moviments
    del compte principal no es toquen.
    """
    if subaccount_id == MAIN_SUBACCOUNT_ID:
        raise ApiError(MAIN_ACCOUNT_NOT_DELETABLE)
    subaccount = subaccounts.get_by_user(user_id, subaccount_id)
    if subaccount is None:
        raise ApiError(SUBACCOUNT_NOT_FOUND)
    if subaccount.balance != 0:
        raise ApiError(SUBACCOUNT_NOT_EMPTY)
    subaccounts.delete(subaccount.id)


def list_subaccount_movements(
    user_id: int, subaccount_id: str, subaccounts: SubaccountRepository
) -> list[SubaccountMovement]:
    """Historial d'un subcompte en divisa de l'usuari, del més recent al més antic (§12.6).

    `main` respon SUBACCOUNT_NOT_FOUND: l'historial del compte en euros és
    `GET /api/movements` (decisió del PO). Un subcompte eliminat, també.
    """
    if subaccounts.get_by_user(user_id, subaccount_id) is None:
        raise ApiError(SUBACCOUNT_NOT_FOUND)
    return subaccounts.list_movements(subaccount_id)


def _main_account(user_id: int, accounts: AccountRepository) -> AccountInCurrency:
    account = accounts.get_by_user(user_id)
    if account is None:
        # `current_user_id` ja rebutja els usuaris inexistents: arribar aquí és un
        # error de programació i ha d'acabar en INTERNAL_ERROR.
        raise LookupError(f"L'usuari {user_id} no té compte principal")
    return AccountInCurrency(
        id=MAIN_SUBACCOUNT_ID,
        currency=MAIN_CURRENCY,
        balance=account.balance,
        is_main=True,
        rate_bps=rate_bps(MAIN_CURRENCY),
    )
