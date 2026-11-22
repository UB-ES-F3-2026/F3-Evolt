"""Repositori de subcomptes en divisa (T25.2, docs/api.md §12.11).

Llegeix i escriu les dades en memòria del SeedData. No decideix regles de
negoci (una divisa per usuari, la llista tancada): això és feina del servei.
"""

from app.data.seed import SeedData, subaccount_id
from app.models import Subaccount


class SubaccountRepository:
    """Subcomptes en divisa. El compte en euros és l'`Account` (AccountRepository)."""

    def __init__(self, seed: SeedData) -> None:
        self._seed = seed

    def list_by_user(self, user_id: int) -> list[Subaccount]:
        """Subcomptes d'un usuari, per ordre de creació (§12.3). Sense cap → []."""
        return [sub for sub in self._seed.subaccounts if sub.user_id == user_id]

    def get_by_user(self, user_id: int, subaccount_id: str) -> Subaccount | None:
        """Subcompte amb aquest id si és de l'usuari, o None.

        Dona None tant si no existeix com si és d'un altre usuari: el contracte no
        distingeix els dos casos (§12.5).
        """
        return next(
            (sub for sub in self._seed.subaccounts if sub.id == subaccount_id and sub.user_id == user_id),
            None,
        )

    def add(self, *, user_id: int, currency: str) -> Subaccount:
        """Crea i desa un subcompte amb un id nou i saldo 0, i el retorna (§12.4).

        Tot o res: si la construcció falla (__post_init__), no es desa res i el
        comptador no avança. Dues creacions alhora les ordena `atomic.run(...)`
        al router, que també protegeix aquest comptador.
        """
        number = self._seed.next_subaccount_number
        subaccount = Subaccount(
            id=subaccount_id(number),
            user_id=user_id,
            currency=currency,
            balance=0,
            number=number,
        )
        self._seed.next_subaccount_number = number + 1
        self._seed.subaccounts.append(subaccount)
        return subaccount
