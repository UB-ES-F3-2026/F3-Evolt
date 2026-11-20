"""Usuari de l'app (T07.3; dades d'accés de T01.2, docs/api.md §8.13)."""

import re
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

# Caràcters d'un `@usuari` (docs/api.md §13.9): minúscules, xifres, `.`, `_` i `-`.
USERNAME_PATTERN = re.compile(r"[a-z0-9._-]+")
# `@usuari` dels que no en tenen un que surti del correu: `usuari9` per a l'usuari 9.
USERNAME_FALLBACK_PREFIX = "usuari"


@dataclass
class User:
    """Usuari amb les seves credencials.

    `identifier` ja està normalitzat (email en minúscules, telèfon amb prefix) i
    `password_hash` és el hash de bcrypt: la contrasenya en clar no es desa mai.
    `failed_logins` compta els errors de login seguits i `locked_until` diu fins
    quan està bloquejat el compte, o `None` si no ho està (T03.2, §8.1).

    `name` és el nom visible: buit vol dir que no en té (els registrats a US-01).
    `username` és l'`@usuari` sense l'`@`, únic; buit en els usuaris d'abans de la
    T13.2, que fan servir `usuari<id>` (§13.9). `phone` és el telèfon normalitzat,
    o `None` si no en té (US-13).
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
    username: str = ""
    phone: str | None = None

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
        if self.username and not USERNAME_PATTERN.fullmatch(self.username):
            raise ValueError(f"username no vàlid: {self.username!r}")
        if self.phone is not None and not self.phone.startswith("+"):
            raise ValueError("phone ha d'estar normalitzat, amb el prefix (+34…)")

    @property
    def visible_username(self) -> str:
        """L'`@usuari` que es mostra: el desat o, si no en té (usuaris d'abans de la T13.2), `usuari<id>`."""
        return self.username or f"{USERNAME_FALLBACK_PREFIX}{self.id}"
