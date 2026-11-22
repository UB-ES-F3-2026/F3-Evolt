"""L'`@usuari` d'un usuari nou (US-13, docs/api.md §13.9, P74).

Decisió de PO: surt de la part local del correu i és únic. Funcions pures: qui
crida diu quins `@usuari` ja estan agafats.
"""

import re
from collections.abc import Callable

from app.models import IDENTIFIER_EMAIL, USERNAME_FALLBACK_PREFIX

# Quan l'`@usuari` no surt del correu (registre amb telèfon, o una part local sense
# cap caràcter vàlid), és `usuari<id>`. No es fa servir el telèfon: l'`@usuari` és visible.
_NOT_ALLOWED = re.compile(r"[^a-z0-9._-]")
# `usuari` + xifres queda reservat per a aquests casos: no pot sortir d'un correu.
_RESERVED = re.compile(rf"{USERNAME_FALLBACK_PREFIX}[0-9]+")


def username_from_email(email: str) -> str:
    """Part local de l'email, en minúscules i només amb `a-z`, `0-9`, `.`, `_` i `-`.

    `Anna.Puig+evolt@x.com` → `anna.puigevolt`. Pot quedar buida.
    """
    local_part = email.split("@", 1)[0].lower()
    return _NOT_ALLOWED.sub("", local_part)


def fallback_username(user_id: int) -> str:
    """`usuari9` per a l'usuari 9."""
    return f"{USERNAME_FALLBACK_PREFIX}{user_id}"


def first_free(base: str, is_taken: Callable[[str], bool]) -> str:
    """`base` si està lliure; si no, `base2`, `base3`… el primer que estigui lliure."""
    candidate, number = base, 2
    while is_taken(candidate):
        candidate, number = f"{base}{number}", number + 1
    return candidate


def email_username_base(identifier: str, identifier_type: str) -> str:
    """La base de l'`@usuari` d'un registre, o `""` si ha de ser `usuari<id>`.

    Una part local amb la forma reservada (`usuari9@x.com`) hi afegeix `_` (`usuari9_`),
    perquè no xoqui amb l'`@usuari` de l'usuari 9.
    """
    if identifier_type != IDENTIFIER_EMAIL:
        return ""
    base = username_from_email(identifier)
    return f"{base}_" if _RESERVED.fullmatch(base) else base
