from dataclasses import dataclass


@dataclass
class Account:
    """Compte principal d'un usuari. Imports en cèntims."""

    id: int
    user_id: int
    balance: int

    def __post_init__(self) -> None:
        if not isinstance(self.balance, int) or isinstance(self.balance, bool):
            raise TypeError("balance ha de ser un enter en cèntims")
