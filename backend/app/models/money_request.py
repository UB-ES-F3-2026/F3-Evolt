"""Sol·licitud de diners a un altre usuari (US-15, docs/api.md §14.1 i §14.8)."""

from dataclasses import dataclass
from datetime import datetime

# Estats del contracte (§14.1). No n'hi ha cap de «Cancel·lada»: cancel·lar esborra.
REQUEST_PENDING = "pending"
REQUEST_PAID = "paid"
REQUEST_REJECTED = "rejected"
REQUEST_EXPIRED = "expired"
# `expired` no es desa mai: es calcula en llegir (§14.5). `paid` i `rejected` arriben amb la US-16.
STORED_REQUEST_STATUSES = frozenset({REQUEST_PENDING, REQUEST_PAID, REQUEST_REJECTED})

MAX_REQUEST_CONCEPT = 140
# 1.000.000,00 € (US-15).
MAX_REQUEST_AMOUNT = 100_000_000


@dataclass
class MoneyRequest:
    """Camps de l'API: id, to (el destinatari), amount, concept, status, createdAt (§14.1).

    Camps interns: requester_id (qui demana), recipient_id i seq (ordre de creació, P4).
    """

    id: str
    requester_id: int
    recipient_id: int
    amount: int
    concept: str
    created_at: datetime
    status: str
    seq: int

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id:
            raise TypeError("id ha de ser un string no buit")
        if not isinstance(self.amount, int) or isinstance(self.amount, bool):
            raise TypeError("amount ha de ser un enter en cèntims")
        if not 0 < self.amount <= MAX_REQUEST_AMOUNT:
            raise ValueError("amount ha de ser > 0 i ≤ 1.000.000,00 €")
        if not self.concept.strip() or len(self.concept) > MAX_REQUEST_CONCEPT:
            raise ValueError("concept ha de tenir entre 1 i 140 caràcters")
        if self.requester_id == self.recipient_id:
            raise ValueError("no es poden demanar diners a un mateix")
        if self.status not in STORED_REQUEST_STATUSES:
            raise ValueError(f"status no vàlid per desar: {self.status!r}")
        if self.created_at.tzinfo is None:
            raise ValueError("created_at ha de portar zona horària")

    def sort_key(self) -> tuple[datetime, int]:
        """Clau d'ordenació. Fes servir reverse=True: més recent primer (§14.3)."""
        return (self.created_at, self.seq)
