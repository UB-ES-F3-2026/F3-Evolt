"""Comparar textos com ho fa una persona (docs/api.md §10.2).

La regla «sense distingir majúscules ni accents» viu aquí una sola vegada. És una
funció pura perquè la pugui fer servir qualsevol repositori.
"""

import unicodedata


def fold_text(text: str) -> str:
    """Treu els accents i les majúscules: `Recàrrega` → `recarrega`, `Núria` → `nuria`."""
    decomposed = unicodedata.normalize("NFD", text)
    return "".join(char for char in decomposed if not unicodedata.combining(char)).casefold()
