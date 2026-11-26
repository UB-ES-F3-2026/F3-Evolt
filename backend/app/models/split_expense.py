"""Despesa dividida en sol·licituds de diners (US-30 i US-31, docs/api.md §17.1 i §17.9)."""

from dataclasses import dataclass, field
from datetime import datetime

# Com a màxim 9 participants a més de qui divideix (US-30).
MAX_SPLIT_PARTS = 9


@dataclass(frozen=True)
class SplitPart:
    """Un participant i la seva part, en cèntims."""

    user_id: int
    amount: int


@dataclass
class SplitExpense:
    """Camps interns de §17.9. L'estat, el pendent i qui ha pagat es calculen en llegir (§17.7)."""

    id: str
    requester_id: int
    concept: str
    total: int
    my_share: int
    created_at: datetime
    seq: int
    parts: list[SplitPart] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.parts or len(self.parts) > MAX_SPLIT_PARTS:
            raise ValueError("una despesa dividida té d'1 a 9 participants")
        if self.my_share <= 0 or any(part.amount <= 0 for part in self.parts):
            raise ValueError("cada part ha de ser > 0")
        if self.my_share + sum(part.amount for part in self.parts) != self.total:
            raise ValueError("les parts han de sumar el total")
        if self.created_at.tzinfo is None:
            raise ValueError("created_at ha de portar zona horària")

    def sort_key(self) -> tuple[datetime, int]:
        """Clau d'ordenació. Fes servir reverse=True: més recent primer (§17.3, P4)."""
        return (self.created_at, self.seq)
