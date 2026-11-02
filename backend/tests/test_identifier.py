"""Tests de la normalització de l'email o el telèfon (T01.2, docs/api.md §8.3).

Executar des de backend/:  python -m pytest tests/test_identifier.py
"""

import pytest

from app.models import IDENTIFIER_EMAIL, IDENTIFIER_PHONE
from app.services.identifier import InvalidIdentifier, normalize_identifier

# --- Email -------------------------------------------------------------------------


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("ana@x.com", "ana@x.com"),
        ("ANA@X.com", "ana@x.com"),
        ("  Ana@X.com  ", "ana@x.com"),  # exemple del contracte
        ("demo@evolt.test", "demo@evolt.test"),
        ("nom.cognom+evolt@correu.cat", "nom.cognom+evolt@correu.cat"),
    ],
)
def test_email_is_trimmed_and_lowercased(raw: str, expected: str) -> None:
    assert normalize_identifier(raw) == normalize_identifier(expected)
    assert normalize_identifier(raw).value == expected
    assert normalize_identifier(raw).type == IDENTIFIER_EMAIL


@pytest.mark.parametrize(
    "raw",
    [
        "ana@",  # R-11: sense domini
        "@x.com",  # sense res abans de l'@
        "ana@x",  # domini sense punt
        "ana@x.",  # sense text després del punt
        "ana@.com",  # sense text abans del punt
        "ana@@x.com",
        "ana@x@y.com",
        "ana @x.com",  # espai a dins
        "ana@x .com",
    ],
)
def test_invalid_email_is_rejected(raw: str) -> None:
    with pytest.raises(InvalidIdentifier):
        normalize_identifier(raw)


# --- Telèfon -----------------------------------------------------------------------


@pytest.mark.parametrize(
    "raw",
    [
        "612 34 56 78",  # exemple del contracte (R-12)
        "612345678",
        "612-34-56-78",
        "612.34.56.78",
        "(612) 34 56 78",
        "+34 612 34 56 78",
        "+34612345678",
        "0034612345678",  # R-13: 00 passa a +
        "0034 612 34 56 78",
    ],
)
def test_spanish_phone_formats_normalize_to_the_same_number(raw: str) -> None:
    identifier = normalize_identifier(raw)
    assert identifier.value == "+34612345678"
    assert identifier.type == IDENTIFIER_PHONE


def test_phone_with_other_country_prefix_is_kept() -> None:
    assert normalize_identifier("+44 20 7946 0958").value == "+442079460958"


@pytest.mark.parametrize(
    "raw",
    [
        "12ab",  # R-11
        "",
        "   ",
        "61234567",  # 8 xifres sense prefix: no és un número local de 9
        "+0612345678",  # la primera xifra no pot ser 0
        "+1234567",  # massa curt (7 xifres)
        "+1234567890123456",  # massa llarg (16 xifres)
        "+34 612 34 56 7a",
        "٦١٢٣٤٥٦٧٨",  # 9 xifres d'un altre alfabet: només valen 0-9
    ],
)
def test_invalid_phone_is_rejected(raw: str) -> None:
    with pytest.raises(InvalidIdentifier):
        normalize_identifier(raw)


def test_invalid_identifier_is_a_value_error() -> None:
    # Així qui no la coneix encara la pot capturar com a error de valor.
    assert issubclass(InvalidIdentifier, ValueError)
