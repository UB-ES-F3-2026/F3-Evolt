from dataclasses import dataclass


@dataclass
class Pot:
    """Guardiola (hucha). Imports en cèntims."""

    id: int
    user_id: int
    name: str
    balance: int

    def __post_init__(self) -> None:
        if not isinstance(self.balance, int) or isinstance(self.balance, bool):
            raise TypeError("balance ha de ser un enter en cèntims")
        if self.balance < 0:
            raise ValueError("una guardiola no pot tenir saldo negatiu")
