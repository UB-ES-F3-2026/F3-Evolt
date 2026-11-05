"""Enllaç de recuperació de la contrasenya (T04.1, docs/api.md §8.10, §8.11 i §8.13)."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class PasswordResetToken:
    """El token d'un enllaç «He oblidat la contrasenya». Com a màxim un de vàlid per usuari.

    `used` passa a `True` quan s'ha canviat la contrasenya: l'enllaç és d'un sol ús.
    """

    token: str
    user_id: int
    created_at: datetime
    used: bool = False

    def __post_init__(self) -> None:
        if not self.token:
            raise ValueError("token no pot ser buit")
        if self.created_at.tzinfo is None:
            raise ValueError("created_at ha de portar zona horària")
