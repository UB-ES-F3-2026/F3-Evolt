"""Guardioles: llistar, crear, aportar i historial (US-17 i US-18, docs/api.md §9).

Ordre de les validacions en crear (s'aturen al primer error):
  1. Format del cos (`name` string, `target` enter estricte o null, `color` de la
     llista tancada) → el router, VALIDATION_ERROR.
  2. Nom buit o només amb espais → aquí, INVALID_POT_NAME.
  3. `target ≤ 0` → aquí, INVALID_TARGET.
Tot o res: primer es valida tot i només al final s'escriu.

Ordre de les validacions en aportar (T18.1, §9.4):
  1. Format del cos (`amount` enter estricte) → el router, VALIDATION_ERROR.
  2. La guardiola no existeix o és d'un altre usuari → aquí, POT_NOT_FOUND.
  3. `amount ≤ 0` → aquí, INVALID_AMOUNT.
  4. `amount` més gran que el saldo del compte → aquí, INSUFFICIENT_BALANCE.
Una aportació fa quatre escriptures: o es fan totes, o no en queda cap.
"""

import threading
from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import datetime

from app.models import (
    DEFAULT_POT_COLOR,
    KIND_OTHER,
    POT_CONTRIBUTION_CONCEPT,
    SAVINGS_ICON,
    TYPE_EXPENSE,
    TYPE_INCOME,
    Movement,
    Pot,
    PotMovement,
    now_madrid,
)
from app.repositories import AccountRepository, MovementRepository, PotRepository
from app.services.errors import (
    INSUFFICIENT_BALANCE,
    INVALID_AMOUNT,
    INVALID_POT_NAME,
    INVALID_TARGET,
    POT_NOT_FOUND,
    ApiError,
)

# Les rutes síncrones de FastAPI corren en un pool de fils: sense aquest pany, dues
# aportacions alhora podrien llegir el mateix saldo, deixar-lo negatiu o perdre'n una.
# Protegeix «validar + escriure» mentre les dades siguin en memòria; amb Firestore
# (#106) ho farà una transacció.
_CONTRIBUTION_LOCK = threading.Lock()


@dataclass(frozen=True)
class ContributionResult:
    """Resultat de l'aportació. La forma JSON la decideix el router."""

    balance: int
    pot: Pot
    movement: Movement


def list_pots(user_id: int, pots: PotRepository) -> list[Pot]:
    """Guardioles de l'usuari, de la més antiga a la més nova (§9.2).

    Un usuari sense guardioles rep `[]`: és l'estat buit de US-17 (criteri 2).
    """
    return pots.list_by_user(user_id)


def create_pot(
    user_id: int,
    name: str,
    target: int | None,
    color: str | None,
    pots: PotRepository,
) -> Pot:
    """Crea una guardiola de l'usuari amb saldo 0 (§9.3).

    El nom es desa sense els espais del principi i del final, i es pot repetir.
    Sense `target` la guardiola no té objectiu; sense `color`, és `purple`.
    """
    clean_name = name.strip()
    if not clean_name:
        raise ApiError(INVALID_POT_NAME)
    if target is not None and target <= 0:
        raise ApiError(INVALID_TARGET)

    return pots.add(
        user_id=user_id,
        name=clean_name,
        balance=0,
        target=target,
        color=color or DEFAULT_POT_COLOR,
    )


def contribute(
    user_id: int,
    pot_id: str,
    amount: int,
    accounts: AccountRepository,
    pots: PotRepository,
    movements: MovementRepository,
    now: datetime | None = None,
) -> ContributionResult:
    """Passa `amount` cèntims del compte principal a una guardiola (§9.4).

    `now` permet fixar el moment als tests. Aportar no dona XP en aquest sprint.
    """
    with _CONTRIBUTION_LOCK:
        pot = pots.get_by_user(user_id, pot_id)
        if pot is None:
            raise ApiError(POT_NOT_FOUND)
        if amount <= 0:
            raise ApiError(INVALID_AMOUNT)

        account = accounts.get_by_user(user_id)
        if account is None:
            # `current_user_id` ja rebutja els usuaris inexistents amb un 422: arribar
            # aquí és un error de programació i ha d'acabar en INTERNAL_ERROR.
            raise LookupError(f"L'usuari {user_id} no té compte principal")
        if amount > account.balance:
            raise ApiError(INSUFFICIENT_BALANCE)

        previous_balance = account.balance
        previous_pot_balance = pot.balance
        date = now or now_madrid()

        # Cada escriptura feta deixa aquí com es desfà. Si una falla, es desfan les
        # anteriors, de l'última a la primera, abans de deixar sortir l'error.
        undo: list[Callable[[], None]] = []
        try:
            movement = movements.add(
                account_id=account.id,
                amount=amount,
                concept=f"{POT_CONTRIBUTION_CONCEPT} a {pot.name}",
                date=date,
                type=TYPE_EXPENSE,
                icon=SAVINGS_ICON,
                kind=KIND_OTHER,
            )
            undo.append(lambda: movements.remove(movement))
            entry = pots.add_movement(
                pot_id=pot.id,
                amount=amount,
                concept=POT_CONTRIBUTION_CONCEPT,
                date=date,
                type=TYPE_INCOME,
            )
            undo.append(lambda: pots.remove_movement(entry))
            accounts.set_balance(user_id, previous_balance - amount)
            undo.append(lambda: accounts.set_balance(user_id, previous_balance))
            pots.set_balance(pot.id, previous_pot_balance + amount)
        except Exception:
            for undo_write in reversed(undo):
                undo_write()
            raise

        # Una còpia amb el saldo nou: la resposta ha de dir el saldo d'aquesta
        # aportació, encara que tot seguit n'arribi una altra a la mateixa guardiola.
        # No es llegeix de `pot`: amb Firestore (TR01.1) és una lectura d'abans.
        return ContributionResult(
            balance=previous_balance - amount,
            pot=replace(pot, balance=previous_pot_balance + amount),
            movement=movement,
        )


def list_pot_movements(user_id: int, pot_id: str, pots: PotRepository) -> list[PotMovement]:
    """Historial d'una guardiola de l'usuari, del més recent al més antic (§9.5)."""
    if pots.get_by_user(user_id, pot_id) is None:
        raise ApiError(POT_NOT_FOUND)
    return pots.list_movements(pot_id)
