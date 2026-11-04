"""Codi de verificació del registre (T02.1, docs/api.md §8.6 i §8.13)."""

from dataclasses import dataclass
from datetime import datetime

CODE_LENGTH = 6


@dataclass
class VerificationCode:
    """El codi vigent d'un usuari pendent. N'hi ha com a màxim un per usuari.

    `failed_attempts` compta els codis incorrectes enviats contra aquest codi;
    demanar-ne un de nou el torna a zero.
    """

    user_id: int
    code: str
    created_at: datetime
    failed_attempts: int = 0

    def __post_init__(self) -> None:
        if len(self.code) != CODE_LENGTH or not self.code.isascii() or not self.code.isdigit():
            raise ValueError("el codi ha de tenir exactament 6 xifres")
        if self.created_at.tzinfo is None:
            raise ValueError("created_at ha de portar zona horària")
        if self.failed_attempts < 0:
            raise ValueError("failed_attempts no pot ser negatiu")
