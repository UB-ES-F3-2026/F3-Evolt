"""Repositori de comptes (T07.4).

Llegeix i escriu les dades en memòria del SeedData. No decideix regles de
negoci: això és feina dels serveis.
"""

from app.data.seed import SeedData
from app.models import Account


class AccountRepository:
    """Compte principal de cada usuari (T07.4)."""

    def __init__(self, seed: SeedData) -> None:
        self._seed = seed

    def get_by_user(self, user_id: int) -> Account | None:
        """Compte principal d'un usuari, o None si l'usuari no existeix (T07.4).

        Retorna l'objecte viu del seed: les escriptures s'han de fer a través
        dels mètodes del repositori. Què respondre davant d'un usuari
        desconegut ho decideix el servei, no aquí.
        """
        return self._seed.accounts.get(user_id)

    def set_balance(self, user_id: int, balance_cents: int) -> None:
        """Assigna el saldo d'un compte (T07.4).

        És un SET i no un delta: l'aritmètica (sumar o restar) la decideix el
        servei. Invariant financer: balance == suma dels signed_amount dels
        moviments del compte; qui canvia el saldo manté aquesta coherència.

        `balance_cents` ha de ser un enter en cèntims (TypeError) i l'usuari
        ha d'existir (KeyError): el router/servei ja ha validat l'usuari, de
        manera que un id desconegut és error de programació. El signe no es
        comprova aquí: és regla de negoci del servei.
        """
        if not isinstance(balance_cents, int) or isinstance(balance_cents, bool):
            raise TypeError("balance_cents ha de ser un enter en cèntims")
        self._seed.accounts[user_id].balance = balance_cents
