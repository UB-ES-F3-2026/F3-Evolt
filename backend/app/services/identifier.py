"""Normalització de l'email o el telèfon (docs/api.md §8.3).

Regla compartida: la fan servir el registre (T01.2) i, més endavant, la
verificació, el reenviament del codi, el login i la recuperació. Viu aquí una
sola vegada perquè `ANA@x.com` i `ana@x.com` siguin sempre el mateix compte.

Mòdul pur: rep un text i retorna un valor, sense llegir ni escriure dades.
"""

import re
from dataclasses import dataclass

from app.models import IDENTIFIER_EMAIL, IDENTIFIER_PHONE

# Prefix que s'afegeix a un número de 9 xifres sense prefix (telèfons espanyols).
DEFAULT_COUNTRY_PREFIX = "+34"
_LOCAL_PHONE_DIGITS = 9

# Format E.164: `+`, una primera xifra que no és 0 i entre 8 i 15 xifres en total.
# re.ASCII: sense ell, `\d` també accepta xifres d'altres alfabets (p. ex. «٣»).
_E164 = re.compile(r"\+[1-9]\d{7,14}", re.ASCII)
# Separadors que la gent escriu en un telèfon i que no formen part del número.
_PHONE_SEPARATORS = str.maketrans("", "", " -.()")


class InvalidIdentifier(ValueError):
    """El text no és ni un email ni un telèfon vàlid."""


@dataclass(frozen=True)
class Identifier:
    """Identificador normalitzat i el seu tipus (`email` o `phone`)."""

    value: str
    type: str


def normalize_identifier(raw: str) -> Identifier:
    """Normalitza un email o un telèfon, o llança `InvalidIdentifier`.

    - Amb `@` és un email: es treuen els espais dels extrems i es passa a minúscules.
      El domini ha de tenir un punt amb text a banda i banda (`x.com`, no `x.` ni `.com`).
    - Sense `@` és un telèfon: es treuen els separadors, `00` passa a `+` i un
      número de 9 xifres sense prefix rep `+34`.
    """
    text = raw.strip()
    if "@" in text:
        return Identifier(_normalize_email(text), IDENTIFIER_EMAIL)
    return Identifier(_normalize_phone(text), IDENTIFIER_PHONE)


def _normalize_email(text: str) -> str:
    email = text.lower()
    local, _, domain = email.partition("@")
    if (
        email.count("@") != 1
        or not local
        # Un punt que no sigui ni el primer ni l'últim caràcter del domini: la
        # mateixa regla que el frontend (`/^[^@\s]+@[^@\s]+\.[^@\s]+$/`).
        or "." not in domain[1:-1]
        or any(char.isspace() for char in email)
    ):
        raise InvalidIdentifier("L'email no és vàlid")
    return email


def _normalize_phone(text: str) -> str:
    phone = text.translate(_PHONE_SEPARATORS)
    if phone.startswith("00"):
        phone = "+" + phone[2:]
    elif phone.isdigit() and len(phone) == _LOCAL_PHONE_DIGITS:
        phone = DEFAULT_COUNTRY_PREFIX + phone
    if not _E164.fullmatch(phone):
        raise InvalidIdentifier("El telèfon no és vàlid")
    return phone
