from dataclasses import dataclass
from datetime import date, datetime

from app.models.clock import MADRID_TZ
from app.models.text import fold_text

TYPE_INCOME = "income"
TYPE_EXPENSE = "expense"
TYPES = frozenset({TYPE_INCOME, TYPE_EXPENSE})

# Llista tancada d'icones (contracte, apartat 3).
ICONS = frozenset({"topup", "salary", "transfer", "shopping", "food", "transport", "savings", "other"})

# Camp intern, no exposat a l'API (contracte, apartat 6).
KIND_TOPUP = "topup"
KIND_OTHER = "other"
KINDS = frozenset({KIND_TOPUP, KIND_OTHER})

# Com es mostra sempre una recàrrega de prova (docs/api.md §4.3).
TOPUP_CONCEPT = "Recàrrega"
TOPUP_ICON = "topup"

# Icona del moviment del compte que crea una aportació a una guardiola (docs/api.md §9.4).
SAVINGS_ICON = "savings"

# Llista tancada d'estats (docs/api.md §10.1). Només canvia l'etiqueta: un moviment
# pendent ja compta al saldo.
MOVEMENT_STATUS_COMPLETED = "completed"
MOVEMENT_STATUS_PENDING = "pending"
MOVEMENT_STATUSES = frozenset({MOVEMENT_STATUS_COMPLETED, MOVEMENT_STATUS_PENDING})


@dataclass
class Movement:
    """Moviment del compte principal.

    Camps de l'API: id, amount, concept, date, type, icon, counterparty, status,
    reference.
    Camps interns (mai a les respostes):
      - account_id: compte al qual pertany.
      - kind: "topup" a les recàrregues, "other" a la resta. Serveix per sumar
        les recàrregues d'un dia sense dependre del concepte.
      - seq: ordre de creació (creixent). Desempata quan dues dates coincideixen:
        va primer el de seq més gran (P4).
    """

    id: str
    account_id: int
    amount: int
    concept: str
    date: datetime
    type: str
    icon: str
    kind: str
    seq: int
    counterparty: str | None
    status: str
    reference: str

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id:
            raise TypeError("id ha de ser un string no buit (P1)")
        if not isinstance(self.amount, int) or isinstance(self.amount, bool):
            raise TypeError("amount ha de ser un enter en cèntims")
        if self.amount <= 0:
            raise ValueError("amount ha de ser > 0; el sentit el dona type")
        if self.type not in TYPES:
            raise ValueError(f"type no vàlid: {self.type!r}")
        if self.icon not in ICONS:
            raise ValueError(f"icon no vàlida: {self.icon!r}")
        if self.kind not in KINDS:
            raise ValueError(f"kind no vàlid: {self.kind!r}")
        if self.date.tzinfo is None:
            raise ValueError("date ha de portar zona horària")
        if self.date.microsecond != 0:
            raise ValueError("date ha de tenir precisió de segons (P7)")
        if self.kind == KIND_TOPUP and self.type != TYPE_INCOME:
            raise ValueError("una recàrrega sempre és income")
        if self.counterparty is not None and (
            not isinstance(self.counterparty, str) or not self.counterparty.strip()
        ):
            raise ValueError("counterparty ha de ser None o un text no buit")
        if self.status not in MOVEMENT_STATUSES:
            raise ValueError(f"status no vàlid: {self.status!r}")
        if not isinstance(self.reference, str) or not self.reference:
            raise TypeError("reference ha de ser un string no buit")

    @property
    def signed_amount(self) -> int:
        """Import amb signe, per calcular saldos. No s'exposa a l'API."""
        return self.amount if self.type == TYPE_INCOME else -self.amount

    def sort_key(self) -> tuple[datetime, int]:
        """Clau d'ordenació. Fes servir reverse=True: més recent primer."""
        return (self.date, self.seq)


@dataclass(frozen=True)
class MovementFilters:
    """Filtres de `GET /api/movements` (T10.3, docs/api.md §10.2). Sense valor, no filtren."""

    date_from: date | None = None
    date_to: date | None = None
    type: str | None = None
    text: str | None = None

    def matches(self, movement: Movement) -> bool:
        """Si el moviment compleix tots els filtres.

        Les dates són dies de Madrid, amb els dos extrems inclosos. El text es busca
        com a part del concepte o de la contrapart; un text només amb espais no filtra.
        """
        day = movement.date.astimezone(MADRID_TZ).date()
        if self.date_from is not None and day < self.date_from:
            return False
        if self.date_to is not None and day > self.date_to:
            return False
        if self.type is not None and movement.type != self.type:
            return False
        text = fold_text(self.text.strip()) if self.text else ""
        if not text:
            return True
        return any(text in fold_text(field) for field in (movement.concept, movement.counterparty or ""))
