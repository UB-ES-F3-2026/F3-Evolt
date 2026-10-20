from dataclasses import dataclass
from datetime import datetime

TYPE_INCOME = "income"
TYPE_EXPENSE = "expense"
TYPES = frozenset({TYPE_INCOME, TYPE_EXPENSE})

# Llista tancada d'icones (contracte, apartat 3).
ICONS = frozenset({"topup", "salary", "transfer", "shopping", "food", "transport", "other"})

# Camp intern, no exposat a l'API (contracte, apartat 6).
KIND_TOPUP = "topup"
KIND_OTHER = "other"
KINDS = frozenset({KIND_TOPUP, KIND_OTHER})

# Com es mostra sempre una recàrrega de prova (docs/api.md §4.3).
TOPUP_CONCEPT = "Recàrrega"
TOPUP_ICON = "topup"


@dataclass
class Movement:
    """Moviment del compte principal.

    Camps de l'API: id, amount, concept, date, type, icon.
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

    @property
    def signed_amount(self) -> int:
        """Import amb signe, per calcular saldos. No s'exposa a l'API."""
        return self.amount if self.type == TYPE_INCOME else -self.amount

    def sort_key(self) -> tuple[datetime, int]:
        """Clau d'ordenació. Fes servir reverse=True: més recent primer."""
        return (self.date, self.seq)
