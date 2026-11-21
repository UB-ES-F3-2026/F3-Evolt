"""Imports en euros per als textos que escriu el backend (docs/api.md §13.7 i §14.6).

La regla de format viu aquí una sola vegada: la fan servir el missatge del límit de
recàrrega i els avisos de la bústia simulada.
"""


def format_euros(cents: int) -> str:
    """Import en format català: `100000` → `"1.000,00 €"`, `2500` → `"25,00 €"`."""
    euros, rest = divmod(cents, 100)
    return f"{euros:,}".replace(",", ".") + f",{rest:02d} €"
