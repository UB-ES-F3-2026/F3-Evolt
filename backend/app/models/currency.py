"""Divises, tipus de canvi i total en euros (US-25, docs/api.md §12.1 i §12.11).

Un sol mòdul per a la taula de divises i els càlculs que en depenen: la
conversió, el total i la comissió del canvi (T27.1, §12.7). La US-29 (canvi
sense comissió) el podrà ampliar sense tocar els serveis. Tot es calcula amb
enters, mai amb decimals.
"""

from dataclasses import dataclass

# La divisa del compte principal (`Account`): no es desa com a subcompte (§12.11).
MAIN_CURRENCY = "EUR"
# L'`id` del compte principal a les respostes de multidivisa (§12.2).
MAIN_SUBACCOUNT_ID = "main"
# `rateBps` de l'euro: un cèntim d'euro val 1 cèntim d'euro × 10.000 (§12.1).
EURO_RATE_BPS = 10000
# Comissió del canvi (D2, §12.7): l'1,5 % (150 punts bàsics sobre 10.000) amb un
# mínim de 0,50 €, sempre. La paga l'origen, en la seva divisa.
COMMISSION_BPS = 150
BASIS_POINTS = 10000
MIN_COMMISSION_EURO_CENTS = 50


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


def convert(amount: int, from_code: str, to_code: str) -> int:
    """`amount` unitats menors de `from_code` en unitats menors de `to_code` (§12.1).

    `arrodonir(amount × rateBps[origen] / rateBps[destí])`. Exemple: `10000` € són
    `10961` $.
    """
    return round_half_up(amount * rate_bps(from_code), rate_bps(to_code))


def reaches_one_unit(amount: int, from_code: str, to_code: str) -> bool:
    """Si el convertit **exacte**, abans d'arrodonir, arriba a una unitat menor del destí.

    És la regla d'`AMOUNT_TOO_SMALL` (§12.7, pas 5): 0,01 $ són 0,9123 cèntims
    d'euro i no hi arriben, encara que arrodonits donarien 1.
    """
    return amount * rate_bps(from_code) >= rate_bps(to_code)


def minimum_commission(code: str) -> int:
    """La comissió mínima de 0,50 € en la unitat menor de `code`, arrodonida cap amunt.

    `⌈50 × 10000 / rateBps⌉` (§12.7): així mai val menys de 0,50 €. USD → `55`, JPY → `88`.
    """
    return -(-MIN_COMMISSION_EURO_CENTS * EURO_RATE_BPS // rate_bps(code))


def commission(amount: int, code: str) -> int:
    """La comissió d'un canvi de `amount` unitats menors de `code`, en la mateixa divisa.

    `max(arrodonir(amount × 150 / 10000), mínim[origen])` (§12.7). `10000` € → `150`;
    `1000` € → `50`, el mínim.
    """
    return max(round_half_up(amount * COMMISSION_BPS, BASIS_POINTS), minimum_commission(code))
