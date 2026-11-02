"""Política de contrasenya (docs/api.md §8.4).

Regla compartida: la fan servir el registre (US-01, T01.2) i la contrasenya
nova de la recuperació (US-04, T04.1), amb el mateix error `WEAK_PASSWORD`.

Mòdul pur: rep un text i retorna un booleà.
"""

MIN_PASSWORD_LENGTH = 8

# bcrypt només fa servir els primers 72 bytes: una contrasenya més llarga es
# rebutja abans (P16) per no desar un hash que ignora part del que s'ha escrit.
MAX_PASSWORD_BYTES = 72

# Només les xifres 0–9: `str.isdigit()` també accepta caràcters com «²».
_DIGITS = frozenset("0123456789")


def fits_password_hash(password: str) -> bool:
    """La contrasenya cap sencera en el hash (com a màxim 72 bytes en UTF-8)."""
    return len(password.encode("utf-8")) <= MAX_PASSWORD_BYTES


def is_strong_password(password: str) -> bool:
    """Mínim 8 caràcters, almenys una majúscula i almenys una xifra.

    Qualsevol majúscula compta, també les accentuades (`À`, `É`...).
    """
    return (
        len(password) >= MIN_PASSWORD_LENGTH
        and any(char.isupper() for char in password)
        and any(char in _DIGITS for char in password)
    )
