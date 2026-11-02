"""Tests de la política i el hash de contrasenyes (T01.2, docs/api.md §8.4).

Executar des de backend/:  python -m pytest tests/test_password_policy.py
"""

import pytest

from app.services.password_hashing import hash_password, verify_password
from app.services.password_policy import (
    MAX_PASSWORD_BYTES,
    fits_password_hash,
    is_strong_password,
)

# --- Política ----------------------------------------------------------------------


@pytest.mark.parametrize(
    "password",
    [
        "Platja2026",
        "Evolt2026",
        "Àlgebra26",  # R-09: la majúscula accentuada compta
        "abcdefG1",  # exactament 8 caràcters
        "amb Espais 1",
    ],
)
def test_strong_passwords(password: str) -> None:
    assert is_strong_password(password)


@pytest.mark.parametrize(
    "password",
    [
        "curta1A",  # R-06: 7 caràcters
        "platja2026",  # R-07: sense majúscula
        "PlatjaNova",  # R-08: sense número
        "",
        "PLATJA²²²",  # «²» no és una xifra 0-9
    ],
)
def test_weak_passwords(password: str) -> None:
    assert not is_strong_password(password)


def test_password_up_to_72_bytes_fits_the_hash() -> None:
    assert fits_password_hash("A1" + "a" * (MAX_PASSWORD_BYTES - 2))
    assert not fits_password_hash("A1" + "a" * (MAX_PASSWORD_BYTES - 1))


def test_bytes_and_not_characters_are_counted() -> None:
    # «à» ocupa 2 bytes en UTF-8: 36 «à» són 72 bytes, 37 ja no hi caben.
    assert fits_password_hash("à" * 36)
    assert not fits_password_hash("à" * 37)


# --- Hash --------------------------------------------------------------------------


def test_hash_is_not_the_password_and_verifies() -> None:
    password_hash = hash_password("Platja2026")

    assert password_hash != "Platja2026"
    assert "Platja2026" not in password_hash
    assert verify_password("Platja2026", password_hash)
    assert not verify_password("Platja2027", password_hash)


def test_same_password_gives_different_hashes() -> None:
    # Cada hash porta una sal nova: dos usuaris amb la mateixa contrasenya no es delaten.
    assert hash_password("Platja2026") != hash_password("Platja2026")
