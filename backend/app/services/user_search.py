"""Cercar usuaris per enviar-los diners (US-13, docs/api.md §13.1 a §13.3).

Un usuari coincideix amb el text per alguna d'aquestes vies (§13.2, P66):
  - `@usuari`: el text, sense l'`@` del principi, és part de l'`@usuari`.
  - Nom: el text és part del nom visible, sense majúscules ni accents.
  - Email: el text, normalitzat, és igual a l'email (mai una part).
  - Telèfon: el text sembla un telèfon i les 9 últimes xifres són les mateixes.
Mai surt l'usuari de la sessió ni un compte pendent, i mai cap dada financera.
"""

import re
from dataclasses import dataclass

from app.models import IDENTIFIER_EMAIL, STATUS_ACTIVE, User, fold_text
from app.repositories import UserRepository
from app.services.errors import RECIPIENT_NOT_FOUND, VALIDATION_ERROR, ApiError
from app.services.identifier import InvalidIdentifier, normalize_identifier

MAX_QUERY_LENGTH = 64
MAX_RESULTS = 10
# Es comparen les 9 últimes xifres: «611 22 33 02» i «+34 611 22 33 02» són el mateix.
PHONE_DIGITS = 9
# Només aquests caràcters fan que el text es tracti com un telèfon.
_PHONE_TEXT = re.compile(r"[0-9 +\-.()]+")
_PUBLIC_ID = re.compile(r"usr-([0-9]+)")


@dataclass(frozen=True)
class UserSummary:
    """Un altre usuari, tal com el veu qui cerca (§13.1). Res més surt a l'API."""

    id: int
    name: str | None
    username: str

    @classmethod
    def from_user(cls, user: User) -> "UserSummary":
        return cls(id=user.id, name=user.name or None, username=user.visible_username)


def public_user_id(user_id: int) -> str:
    """Id opac d'un usuari a l'API (P64): `usr-03`. El frontend no l'ha d'interpretar."""
    return f"usr-{user_id:02d}"


def parse_public_user_id(raw: str) -> int | None:
    """L'id intern d'un `usr-03`, o None si no té exactament aquesta forma."""
    match = _PUBLIC_ID.fullmatch(raw)
    if match is None:
        return None
    user_id = int(match.group(1))
    return user_id if public_user_id(user_id) == raw else None


def search_users(user_id: int, raw_query: str | None, users: UserRepository) -> list[UserSummary]:
    """Els usuaris que coincideixen amb el text, o la llista inicial si és buit (§13.2)."""
    query = (raw_query or "").strip()
    if len(query) > MAX_QUERY_LENGTH:
        raise ApiError(VALIDATION_ERROR)

    others = [user for user in users.list_active() if user.id != user_id]
    found = [user for user in others if _matches(user, query)] if query else others
    found.sort(key=lambda user: (fold_text(user.name or user.visible_username), user.id))
    return [UserSummary.from_user(user) for user in found[:MAX_RESULTS]]


def get_user(raw_id: str, users: UserRepository) -> UserSummary:
    """Un usuari actiu pel seu id públic (§13.3). També el de la sessió: no és cap dada nova."""
    user = find_active_user(raw_id, users)
    if user is None:
        raise ApiError(RECIPIENT_NOT_FOUND)
    return UserSummary.from_user(user)


def find_active_user(raw_id: str, users: UserRepository) -> User | None:
    """L'usuari actiu amb aquest id públic, o None si no n'hi ha cap (el farà servir l'enviament)."""
    user_id = parse_public_user_id(raw_id)
    user = users.get(user_id) if user_id is not None else None
    return user if user is not None and user.status == STATUS_ACTIVE else None


def _matches(user: User, query: str) -> bool:
    handle = query[1:] if query.startswith("@") else query
    if handle.lower() in user.visible_username:
        return True
    if user.name and fold_text(query) in fold_text(user.name):
        return True
    return _same_email(user, query) or _same_phone(user, query)


def _same_email(user: User, query: str) -> bool:
    if user.identifier_type != IDENTIFIER_EMAIL or "@" not in query[1:]:
        return False
    try:
        identifier = normalize_identifier(query)
    except InvalidIdentifier:
        return False
    return identifier.type == IDENTIFIER_EMAIL and identifier.value == user.identifier


def _same_phone(user: User, query: str) -> bool:
    if user.phone is None or not _PHONE_TEXT.fullmatch(query):
        return False
    digits = re.sub(r"[^0-9]", "", query)
    if len(digits) < PHONE_DIGITS:
        return False
    return digits[-PHONE_DIGITS:] == re.sub(r"[^0-9]", "", user.phone)[-PHONE_DIGITS:]
