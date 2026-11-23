"""Progrés d'una guardiola cap al seu objectiu (US-20, docs/api.md §11.1 i §11.6).

Una sola funció pura per a totes les respostes que porten una guardiola: la llista,
la creació, l'aportació i la retirada. No es desa res: es calcula a cada resposta,
amb el saldo d'aquell moment.
"""

from typing import Literal, NamedTuple

GoalStatus = Literal["in_progress", "achieved"]
GOAL_IN_PROGRESS: GoalStatus = "in_progress"
GOAL_ACHIEVED: GoalStatus = "achieved"
# Mentre no s'arriba a l'objectiu, el percentatge es queda com a màxim a 99: el 100 %
# només surt amb l'objectiu assolit (decisió de PO a la #194).
MAX_PERCENTAGE_IN_PROGRESS = 99


class PotProgress(NamedTuple):
    """`percentage` i `goalStatus` d'una guardiola. Tots dos `None` si no té objectiu."""

    percentage: int | None
    goal_status: GoalStatus | None


def pot_progress(balance: int, target: int | None) -> PotProgress:
    """Percentatge arrodonit a l'enter (els mitjos cap amunt) i estat de l'objectiu.

    Per sota de l'objectiu, com a màxim 99. Pot passar de 100: per sobre de
    l'objectiu diu el valor real (125).
    """
    if target is None:
        return PotProgress(percentage=None, goal_status=None)
    # Amb enters: round() arrodoniria 62,5 a 62 (arrodoniment bancari) i els
    # decimals de coma flotant poden quedar-se una mica per sota del mig.
    percentage = (200 * balance + target) // (2 * target)
    if balance >= target:
        return PotProgress(percentage=percentage, goal_status=GOAL_ACHIEVED)
    # 7999 de 8000 arrodoniria a 100, però encara no s'hi ha arribat: «99 %».
    return PotProgress(percentage=min(percentage, MAX_PERCENTAGE_IN_PROGRESS), goal_status=GOAL_IN_PROGRESS)
