from dataclasses import dataclass

# Llista tancada de colors (docs/api.md §9.1). El to exacte el tria el frontend.
POT_COLORS = frozenset({"purple", "blue", "teal", "orange", "pink", "yellow"})
# Color d'una guardiola creada sense color (§9.3).
DEFAULT_POT_COLOR = "purple"


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
