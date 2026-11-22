from dataclasses import dataclass

from app.models.currency import CURRENCIES, MAIN_CURRENCY


@dataclass
class Subaccount:
    """Subcompte en una divisa que no és l'euro (US-25, docs/api.md §12.11).

    Camps de l'API: id, currency, balance (§12.2). `isMain` és sempre false i
    `rateBps` surt de la taula de divises: no es desen.
    Camps interns (mai a les respostes):
      - user_id: propietari.
      - number: ordre de creació (creixent). Ordena els subcomptes de l'usuari.
    El compte en euros és l'`Account` de l'usuari i no es desa com a subcompte:
    així el saldo no es duplica.
    """

    id: str
    user_id: int
    currency: str
    balance: int
    number: int

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id:
            raise TypeError("id ha de ser un string no buit")
        if self.currency not in CURRENCIES:
            raise ValueError(f"divisa fora de la llista: {self.currency!r}")
        if self.currency == MAIN_CURRENCY:
            raise ValueError("l'euro és el compte principal, no un subcompte")
        if not isinstance(self.balance, int) or isinstance(self.balance, bool):
            raise TypeError("balance ha de ser un enter en la unitat menor de la divisa")
        if self.balance < 0:
            raise ValueError("un subcompte no pot tenir saldo negatiu")
