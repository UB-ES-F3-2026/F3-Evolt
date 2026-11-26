"""Repositori de despeses dividides (T30.2, docs/api.md §17.9).

Llegeix i escriu les dades en memòria del SeedData. No decideix regles de negoci
(qui pot veure-la, quin estat té): això és feina del servei.
"""

from datetime import datetime

from app.data.seed import SeedData, split_expense_id
from app.models import SplitExpense, SplitPart


class SplitExpenseRepository:
    """Despeses dividides (T30.2)."""

    def __init__(self, seed: SeedData) -> None:
        self._seed = seed

    def add(
        self,
        *,
        requester_id: int,
        concept: str,
        total: int,
        my_share: int,
        created_at: datetime,
        parts: list[SplitPart],
    ) -> SplitExpense:
        """Crea i desa una despesa amb un id nou. Si el model no és vàlid, no gasta cap número."""
        number = self._seed.next_split_expense_number
        split = SplitExpense(
            id=split_expense_id(number),
            requester_id=requester_id,
            concept=concept,
            total=total,
            my_share=my_share,
            created_at=created_at,
            seq=number,
            parts=list(parts),
        )
        self._seed.next_split_expense_number = number + 1
        self._seed.split_expenses.append(split)
        return split

    def get(self, split_id: str) -> SplitExpense | None:
        """La despesa amb aquest id, de qualsevol usuari, o None."""
        return next((split for split in self._seed.split_expenses if split.id == split_id), None)

    def list_by_requester(self, requester_id: int) -> list[SplitExpense]:
        """Les de l'usuari, de la més recent a la més antiga (§17.3, P4)."""
        mine = [split for split in self._seed.split_expenses if split.requester_id == requester_id]
        return sorted(mine, key=SplitExpense.sort_key, reverse=True)

    def undo_add(self, split: SplitExpense) -> None:
        """Treu una despesa acabada de crear, si alguna sol·licitud o avís ha fallat (tot o res)."""
        self._seed.split_expenses = [s for s in self._seed.split_expenses if s.id != split.id]
        if split.seq == self._seed.next_split_expense_number - 1:
            self._seed.next_split_expense_number = split.seq
