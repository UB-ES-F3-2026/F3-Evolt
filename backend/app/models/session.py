"""Sessió d'un usuari (T03.1, docs/api.md §8.2 i §8.13)."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Session:
    """Sessió oberta amb un token opac.

    `last_activity` és el moment de l'última petició amb aquest token: la
    T03.2 hi compararà l'hora actual per tancar la sessió als 5 minuts.
    """

    token: str
    user_id: int
    last_activity: datetime

    def __post_init__(self) -> None:
        if not self.token:
            raise ValueError("token no pot ser buit")
        if self.last_activity.tzinfo is None:
            raise ValueError("last_activity ha de portar zona horària")
