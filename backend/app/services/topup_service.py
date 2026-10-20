"""Recàrrega de prova (T09.1 · US-09, docs/api.md §4.3).

Ordre de les validacions (s'aturen al primer error):
  1. Format del cos (`amount` enter estricte) → el router, VALIDATION_ERROR.
  2. Límits per recàrrega → aquí, INVALID_AMOUNT / AMOUNT_OVER_LIMIT.
  3. Límit diari → aquí, DAILY_LIMIT_EXCEEDED (T09.2).
Tot o res: primer es valida tot i només al final s'escriu.
"""

from dataclasses import dataclass
from datetime import datetime

from app.models import (
    KIND_TOPUP,
    MADRID_TZ,
    TOPUP_CONCEPT,
    TOPUP_ICON,
    TYPE_INCOME,
    Movement,
    now_madrid,
)
from app.repositories import AccountRepository, MovementRepository
from app.services.errors import (
    AMOUNT_OVER_LIMIT,
    DAILY_LIMIT_EXCEEDED,
    INVALID_AMOUNT,
    ApiError,
)

# Màxim per recàrrega, en cèntims (500,00 €). Exactament el màxim està permès.
MAX_TOPUP = 50_000

# US-09, criteri 4: no es pot recarregar més de 1.000,00 € en un mateix dia natural
# a Madrid. Compta la suma de les recàrregues d'avui més la nova; arribar just a
# 1.000,00 € està permès, perquè el criteri diu "no més de".
MAX_DAILY_TOPUP = 100_000


@dataclass(frozen=True)
class TopupResult:
    """Resultat de la recàrrega. La forma JSON la decideix el router."""

    balance: int
    movement: Movement


def top_up(
    user_id: int,
    amount: int,
    accounts: AccountRepository,
    movements: MovementRepository,
    now: datetime | None = None,
) -> TopupResult:
    """Suma `amount` cèntims al saldo i registra el moviment "Recàrrega".

    `now` permet fixar el moment als tests (p. ex. per provar el límit diari).
    Les recàrregues no toquen l'XP de l'usuari (US-09, criteri 6).
    """
    now = now or now_madrid()

    if amount <= 0:
        raise ApiError(INVALID_AMOUNT)
    if amount > MAX_TOPUP:
        raise ApiError(AMOUNT_OVER_LIMIT)

    account = accounts.get_by_user(user_id)
    if account is None:
        # `current_user_id` ja rebutja els usuaris inexistents amb un 422: arribar
        # aquí és un error de programació i ha d'acabar en INTERNAL_ERROR.
        raise LookupError(f"L'usuari {user_id} no té compte principal")

    # Es comprova abans d'escriure res: si es rebutja, el saldo i els moviments no canvien.
    today = now.astimezone(MADRID_TZ).date()
    topped_up_today = movements.sum_topups_on_day(account.id, today)
    if topped_up_today + amount > MAX_DAILY_TOPUP:
        remaining_today = max(0, MAX_DAILY_TOPUP - topped_up_today)
        raise ApiError(
            DAILY_LIMIT_EXCEEDED,
            message=(
                "Has superat el límit diari de recàrrega. "
                f"Avui encara pots recarregar {_format_euros(remaining_today)}."
            ),
            details={"remainingToday": remaining_today},
        )

    movement = movements.add(
        account_id=account.id,
        amount=amount,
        concept=TOPUP_CONCEPT,
        date=now,
        type=TYPE_INCOME,
        icon=TOPUP_ICON,
        kind=KIND_TOPUP,
    )
    new_balance = account.balance + amount
    accounts.set_balance(user_id, new_balance)
    return TopupResult(balance=new_balance, movement=movement)


def _format_euros(cents: int) -> str:
    """Import en format català per al missatge: `100000` → `"1.000,00 €"`."""
    euros, rest = divmod(cents, 100)
    return f"{euros:,}".replace(",", ".") + f",{rest:02d} €"
