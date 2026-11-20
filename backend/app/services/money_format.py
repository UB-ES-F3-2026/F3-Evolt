"""Imports en euros dins dels textos que escriu el backend.

El mateix format que la pantalla (`1.000,00 €`): el fan servir el missatge del
límit diari de recàrrega (T09.2) i els avisos d'enviament a la bústia (T14.2,
docs/api.md §13.7). Una sola funció perquè tots dos textos no se separin.
"""


def format_euros(cents: int) -> str:
    """`100000` → `"1.000,00 €"`, `2000` → `"20,00 €"`. Només per a imports ≥ 0."""
    euros, rest = divmod(cents, 100)
    return f"{euros:,}".replace(",", ".") + f",{rest:02d} €"
