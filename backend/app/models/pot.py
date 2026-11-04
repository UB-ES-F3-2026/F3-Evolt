from dataclasses import dataclass
from datetime import datetime

from app.models.movement import TYPES

# Llista tancada de colors (docs/api.md §9.1). El to exacte el tria el frontend.
POT_COLORS = frozenset({"purple", "blue", "teal", "orange", "pink", "yellow"})
# Color d'una guardiola creada sense color (§9.3).
DEFAULT_POT_COLOR = "purple"

# Conceptes de l'historial d'una guardiola (§9.5).
POT_INITIAL_CONCEPT = "Saldo inicial"
POT_CONTRIBUTION_CONCEPT = "Aportació"


@dataclass
class Pot:
    """Guardiola (hucha). Imports en cèntims.

    Camps de l'API: id, name, balance, target, color (§9.1).
    Camp intern (mai a les respostes): user_id.
    """

    id: str
    user_id: int
    name: str
    balance: int
    target: int | None
    color: str

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id:
            raise TypeError("id ha de ser un string no buit (P21)")
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("name no pot ser buit")
        if not isinstance(self.balance, int) or isinstance(self.balance, bool):
            raise TypeError("balance ha de ser un enter en cèntims")
        if self.balance < 0:
            raise ValueError("una guardiola no pot tenir saldo negatiu")
        if self.target is not None:
            if not isinstance(self.target, int) or isinstance(self.target, bool):
                raise TypeError("target ha de ser un enter en cèntims o None")
            if self.target <= 0:
                raise ValueError("target ha de ser > 0")
        if self.color not in POT_COLORS:
            raise ValueError(f"color no vàlid: {self.color!r}")


@dataclass
class PotMovement:
    """Entrada de l'historial d'una guardiola (§9.5).

    Camps de l'API: id, amount, concept, date, type. `type` és des del punt de vista
    de la guardiola: una aportació hi fa entrar diners, i per tant és income.
    Camps interns (mai a les respostes):
      - pot_id: guardiola a la qual pertany.
      - seq: ordre de creació (creixent). Desempata quan dues dates coincideixen:
        va primer el de seq més gran (P4).
    """

    id: str
    pot_id: str
    amount: int
    concept: str
    date: datetime
    type: str
    seq: int

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id:
            raise TypeError("id ha de ser un string no buit")
        if not isinstance(self.amount, int) or isinstance(self.amount, bool):
            raise TypeError("amount ha de ser un enter en cèntims")
        if self.amount <= 0:
            raise ValueError("amount ha de ser > 0; el sentit el dona type")
        if self.type not in TYPES:
            raise ValueError(f"type no vàlid: {self.type!r}")
        if self.date.tzinfo is None:
            raise ValueError("date ha de portar zona horària")
        if self.date.microsecond != 0:
            raise ValueError("date ha de tenir precisió de segons (P7)")

    def sort_key(self) -> tuple[datetime, int]:
        """Clau d'ordenació. Fes servir reverse=True: més recent primer."""
        return (self.date, self.seq)
