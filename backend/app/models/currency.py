"""Divises, tipus de canvi i total en euros (US-25, docs/api.md §12.1 i §12.11).

Un sol mòdul per a la taula de divises i els càlculs que en depenen: la T27.1
(canvi) hi afegirà la comissió sense tocar els serveis. Tot es calcula amb
enters, mai amb decimals.
"""

from dataclasses import dataclass

# La divisa del compte principal (`Account`): no es desa com a subcompte (§12.11).
MAIN_CURRENCY = "EUR"
# L'`id` del compte principal a les respostes de multidivisa (§12.2).
MAIN_SUBACCOUNT_ID = "main"
# `rateBps` de l'euro: un cèntim d'euro val 1 cèntim d'euro × 10.000 (§12.1).
EURO_RATE_BPS = 10000


@dataclass(frozen=True)
class Currency:
    """Una divisa de la llista tancada (§12.1).

    - decimals: 2 si la unitat menor és el cèntim; 0 al JPY (iens sencers).
    - rate_bps: quants cèntims d'euro val una unitat menor, × 10.000.
    """

    code: str
    name: str
    symbol: str
    decimals: int
    rate_bps: int


# Llista tancada i tipus fixos, en l'ordre de la taula de §12.1 (P50). Són els de
# frontend/src/models/currency.ts: si en canvia un, s'ha de canviar també allà.
CURRENCIES: dict[str, Currency] = {
    currency.code: currency
    for currency in (
        Currency("EUR", "Euro", "€", 2, EURO_RATE_BPS),
        Currency("USD", "Dòlar nord-americà", "$", 2, 9123),
        Currency("GBP", "Lliura esterlina", "£", 2, 11680),
        Currency("CHF", "Franc suís", "CHF", 2, 10355),
        Currency("JPY", "Ien japonès", "¥", 0, 5700),
    )
}


def rate_bps(code: str) -> int:
    """El tipus fix d'una divisa de la llista. Un codi desconegut és KeyError."""
    return CURRENCIES[code].rate_bps


def round_half_up(numerator: int, denominator: int) -> int:
    """`arrodonir(n / d)` de §12.1: `⌊(2n + d) / (2d)⌋`, la meitat cap amunt.

    Només per a imports `≥ 0` i `d > 0`, que són els únics que surten als càlculs.
    """
    return (2 * numerator + denominator) // (2 * denominator)


def to_euro_cents(balance: int, code: str) -> int:
    """El valor aproximat en cèntims d'euro d'un saldo en la unitat menor de `code`."""
    return round_half_up(balance * rate_bps(code), EURO_RATE_BPS)


def total_in_euros(balances: list[tuple[int, str]]) -> int:
    """«Total ≈ … €» (US-25, §12.1): cada compte s'arrodoneix per separat i es suma.

    `balances` són parells (saldo en unitat menor, codi de divisa).
    """
    return sum(to_euro_cents(balance, code) for balance, code in balances)
