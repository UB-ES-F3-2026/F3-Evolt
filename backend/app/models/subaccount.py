from dataclasses import dataclass
from datetime import datetime

from app.models.currency import CURRENCIES, MAIN_CURRENCY
from app.models.movement import TYPES


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


@dataclass
class SubaccountMovement:
    """Entrada de l'historial d'un subcompte en divisa (US-26, docs/api.md §12.6).

    Com l'historial de les guardioles (`PotMovement`, §9.8).
    Camps de l'API: id, amount, concept, date, type. `amount` és en la unitat
    menor de la divisa del subcompte, i `type` és des del punt de vista del
    subcompte: si hi entren diners, income.
    Camps interns (mai a les respostes):
      - subaccount_id: subcompte al qual pertany. En eliminar el subcompte,
        l'entrada es queda desada però ja no es pot consultar (§12.5).
      - seq: ordre de creació (creixent). Desempata quan dues dates coincideixen:
        va primer el de seq més gran (P4).
    Les entrades les crea el canvi (T27.1); la T26.1 només les llegeix.
    """

    id: str
    subaccount_id: str
    amount: int
    concept: str
    date: datetime
    type: str
    seq: int

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id:
            raise TypeError("id ha de ser un string no buit")
        if not isinstance(self.amount, int) or isinstance(self.amount, bool):
            raise TypeError("amount ha de ser un enter en la unitat menor de la divisa")
        if self.amount <= 0:
            raise ValueError("amount ha de ser > 0; el sentit el dona type")
        if self.type not in TYPES:
            raise ValueError(f"type no vàlid: {self.type!r}")
        if self.date.tzinfo is None:
            raise ValueError("date ha de portar zona horària")
        if self.date.microsecond != 0:
            raise ValueError("date ha de tenir precisió de segons (P7)")

    def sort_key(self) -> tuple[datetime, int]:
        """Clau d'ordenació. Fes servir reverse=True: més recent primer."""
        return (self.date, self.seq)
