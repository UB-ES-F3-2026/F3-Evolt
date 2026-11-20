"""Progrés d'una guardiola cap al seu objectiu (US-20, docs/api.md §11.1 i §11.6).

Una sola funció pura per a totes les respostes que porten una guardiola: la llista,
la creació, l'aportació i la retirada. No es desa res: es calcula a cada resposta,
amb el saldo d'aquell moment.
"""

from typing import NamedTuple

GOAL_IN_PROGRESS = "in_progress"
GOAL_ACHIEVED = "achieved"


class PotProgress(NamedTuple):
    """`percentage` i `goalStatus` d'una guardiola. Tots dos `None` si no té objectiu."""

    percentage: int | None
    goal_status: str | None


def pot_progress(balance: int, target: int | None) -> PotProgress:
    """Percentatge arrodonit a l'enter (els mitjos cap amunt) i estat de l'objectiu.

    Pot passar de 100: per sobre de l'objectiu diu el valor real (125).
    """
    if target is None:
        return PotProgress(percentage=None, goal_status=None)
    # Amb enters: round() arrodoniria 62,5 a 62 (arrodoniment bancari) i els
    # decimals de coma flotant poden quedar-se una mica per sota del mig.
    percentage = (200 * balance + target) // (2 * target)
    # L'estat surt del saldo i no del percentatge arrodonit: amb 7999 de 8000 el
    # percentatge és 100, però encara no s'ha arribat a l'objectiu.
    goal_status = GOAL_ACHIEVED if balance >= target else GOAL_IN_PROGRESS
    return PotProgress(percentage=percentage, goal_status=goal_status)
