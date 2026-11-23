"""Repositori de subcomptes en divisa (T25.2, docs/api.md §12.11).

Llegeix i escriu les dades en memòria del SeedData. No decideix regles de
negoci (una divisa per usuari, la llista tancada): això és feina del servei.
"""

from datetime import datetime

from app.data.seed import SeedData, subaccount_id, subaccount_movement_id
from app.models import Subaccount, SubaccountMovement


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

    def set_balance(self, subaccount_id: str, balance: int) -> None:
        """Assigna el saldo d'un subcompte (T27.1).

        És un SET i no un delta, com `PotRepository.set_balance`: l'aritmètica la
        decideix el servei, que també manté l'invariant «el saldo és la suma de
        l'historial». Un id desconegut és error de programació (KeyError).
        """
        if not isinstance(balance, int) or isinstance(balance, bool):
            raise TypeError("balance ha de ser un enter en la unitat menor de la divisa")
        if balance < 0:
            raise ValueError("un subcompte no pot tenir saldo negatiu")
        for sub in self._seed.subaccounts:
            if sub.id == subaccount_id:
                sub.balance = balance
                return
        raise KeyError(subaccount_id)

    def delete(self, subaccount_id: str) -> None:
        """Esborra el subcompte (T26.1, §12.5). Les entrades del seu historial es queden.

        No comprova res: el servei ja ha mirat que és de l'usuari i que té saldo 0.
        Un id desconegut és error de programació (KeyError).
        """
        for index, sub in enumerate(self._seed.subaccounts):
            if sub.id == subaccount_id:
                del self._seed.subaccounts[index]
                return
        raise KeyError(subaccount_id)

    def list_movements(self, subaccount_id: str) -> list[SubaccountMovement]:
        """Historial d'un subcompte, de la més recent a la més antiga (T26.1, §12.6).

        Si dues entrades tenen la mateixa data, va primer la creada més tard (P4).
        """
        entries = [entry for entry in self._seed.subaccount_movements if entry.subaccount_id == subaccount_id]
        return sorted(entries, key=SubaccountMovement.sort_key, reverse=True)

    def add_movement(
        self,
        *,
        subaccount_id: str,
        amount: int,
        concept: str,
        date: datetime,
        type: str,
    ) -> SubaccountMovement:
        """Crea i desa una entrada de l'historial, i la retorna (la fa servir el canvi, T27.1).

        No toca el saldo del subcompte: el manté el servei. Tot o res: si la
        construcció falla (__post_init__), no es desa res i el comptador no avança.
        """
        number = self._seed.next_subaccount_movement_number
        entry = SubaccountMovement(
            id=subaccount_movement_id(number),
            subaccount_id=subaccount_id,
            amount=amount,
            concept=concept,
            date=date,
            type=type,
            seq=number,
        )
        self._seed.next_subaccount_movement_number = number + 1
        self._seed.subaccount_movements.append(entry)
        return entry

    def remove_movement(self, entry: SubaccountMovement) -> None:
        """Treu una entrada acabada de crear, per desfer un canvi que ha fallat (T27.1).

        Si és l'última que s'ha creat, el comptador torna enrere i no queda cap forat.
        """
        self._seed.subaccount_movements.remove(entry)
        if entry.seq == self._seed.next_subaccount_movement_number - 1:
            self._seed.next_subaccount_movement_number = entry.seq
