"""Usuari de l'app (T07.3; dades d'accés de T01.2, docs/api.md §8.13)."""

from dataclasses import dataclass
from datetime import datetime

# Estat del compte (US-01): neix pendent i passa a actiu en verificar el codi (US-02).
STATUS_PENDING = "pending"
STATUS_ACTIVE = "active"
USER_STATUSES = frozenset({STATUS_PENDING, STATUS_ACTIVE})

# Tipus d'identificador (docs/api.md §8.3): decideix si els missatges surten per email o per SMS.
IDENTIFIER_EMAIL = "email"
IDENTIFIER_PHONE = "phone"
IDENTIFIER_TYPES = frozenset({IDENTIFIER_EMAIL, IDENTIFIER_PHONE})


@dataclass
class User:
    """Usuari amb les seves credencials.

    `identifier` ja està normalitzat (email en minúscules, telèfon amb prefix) i
    `password_hash` és el hash de bcrypt: la contrasenya en clar no es desa mai.
    `failed_logins` compta els errors de login seguits i `locked_until` diu fins
    quan està bloquejat el compte, o `None` si no ho està (T03.2, §8.1).
    """

    id: int
    name: str
    identifier: str
    identifier_type: str
    password_hash: str
    status: str = STATUS_PENDING
    xp: int = 0  # Les recàrregues no el modifiquen (US-09, criteri 6).
    failed_logins: int = 0
    locked_until: datetime | None = None

    def __post_init__(self) -> None:
        if self.xp < 0:
            raise ValueError("xp no pot ser negatiu")
        if not self.identifier:
            raise ValueError("identifier no pot ser buit")
        if self.identifier_type not in IDENTIFIER_TYPES:
            raise ValueError(f"identifier_type desconegut: {self.identifier_type!r}")
        if not self.password_hash:
            raise ValueError("password_hash no pot ser buit")
        if self.failed_logins < 0:
            raise ValueError("failed_logins no pot ser negatiu")
        if self.locked_until is not None and self.locked_until.tzinfo is None:
            raise ValueError("locked_until ha de portar zona horària")
        if self.status not in USER_STATUSES:
            raise ValueError(f"status desconegut: {self.status!r}")
