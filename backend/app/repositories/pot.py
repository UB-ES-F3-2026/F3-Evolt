"""Repositori de guardioles (T07.4).

Llegeix i escriu les dades en memòria del SeedData. No decideix regles de
negoci: això és feina dels serveis.
"""

import threading
from datetime import datetime

from app.data.seed import SeedData, pot_id, pot_movement_id
from app.models import Pot, PotMovement

# Les rutes síncrones de FastAPI corren en un pool de fils: sense aquest pany, dues
# creacions alhora podrien llegir el mateix comptador i donar el mateix id a dues
# guardioles. Amb Firestore (#106) el comptador anirà dins d'una transacció.
_ADD_LOCK = threading.Lock()


class PotRepository:
    """Guardioles (T07.4)."""

    def __init__(self, seed: SeedData) -> None:
        self._seed = seed

    def list_by_user(self, user_id: int) -> list[Pot]:
        """Guardioles d'un usuari, en l'ordre del seed (T07.4).

        Usuaris sense guardioles → []. Retorna objectes vius: els canvis de
        saldo s'han de fer a través dels mètodes del repositori.
        El `totalSaved` de T07.5 (§4.1) és la suma d'aquests saldos; la suma
        la fa el servei, no el repositori.
        """
        return [pot for pot in self._seed.pots if pot.user_id == user_id]

    def add(
        self,
        *,
        user_id: int,
        name: str,
        balance: int,
        target: int | None,
        color: str,
    ) -> Pot:
        """Crea i desa una guardiola amb un id nou, i la retorna (T17.2).

        Les noves van al final, així `list_by_user` les dona en ordre de creació
        (§9.2). Tot o res: si la construcció del Pot falla (__post_init__), no es
        desa res i el comptador no avança.
        """
        with _ADD_LOCK:
            number = self._seed.next_pot_number
            pot = Pot(
                id=pot_id(number),
                user_id=user_id,
                name=name,
                balance=balance,
                target=target,
                color=color,
            )
            self._seed.next_pot_number = number + 1
            self._seed.pots.append(pot)
        return pot

    def get_by_user(self, user_id: int, pot_id: str) -> Pot | None:
        """Guardiola amb aquest id si és de l'usuari, o None (T18.1).

        Dona None tant si no existeix com si és d'un altre usuari: el contracte no
        distingeix els dos casos (§9.4). Retorna l'objecte viu del seed.
        """
        return next(
            (pot for pot in self._seed.pots if pot.id == pot_id and pot.user_id == user_id),
            None,
        )

    def set_balance(self, pot_id: str, balance_cents: int) -> None:
        """Assigna el saldo d'una guardiola (T18.1).

        És un SET i no un delta, com `AccountRepository.set_balance`: l'aritmètica
        la decideix el servei. Invariant: el saldo és la suma de l'historial, i qui
        canvia el saldo manté aquesta coherència. Un id desconegut és error de
        programació (KeyError).
        """
        if not isinstance(balance_cents, int) or isinstance(balance_cents, bool):
            raise TypeError("balance_cents ha de ser un enter en cèntims")
        if balance_cents < 0:
            raise ValueError("una guardiola no pot tenir saldo negatiu")
        for pot in self._seed.pots:
            if pot.id == pot_id:
                pot.balance = balance_cents
                return
        raise KeyError(pot_id)

    def list_movements(self, pot_id: str) -> list[PotMovement]:
        """Historial d'una guardiola, de la més recent a la més antiga (T18.1, §9.5).

        Si dues entrades tenen la mateixa data, va primer la creada més tard (P4).
        """
        entries = [entry for entry in self._seed.pot_movements if entry.pot_id == pot_id]
        return sorted(entries, key=PotMovement.sort_key, reverse=True)

    def add_movement(
        self,
        *,
        pot_id: str,
        amount: int,
        concept: str,
        date: datetime,
        type: str,
    ) -> PotMovement:
        """Crea i desa una entrada de l'historial, i la retorna (T18.1).

        No toca el saldo de la guardiola: el manté el servei. Tot o res: si la
        construcció falla (__post_init__), no es desa res i el comptador no avança.
        """
        number = self._seed.next_pot_movement_number
        entry = PotMovement(
            id=pot_movement_id(number),
            pot_id=pot_id,
            amount=amount,
            concept=concept,
            date=date,
            type=type,
            seq=number,
        )
        self._seed.next_pot_movement_number = number + 1
        self._seed.pot_movements.append(entry)
        return entry

    def remove_movement(self, entry: PotMovement) -> None:
        """Treu una entrada acabada de crear, per desfer una aportació que ha fallat (T18.1).

        Si és l'última que s'ha creat, el comptador torna enrere i no queda cap forat.
        """
        self._seed.pot_movements.remove(entry)
        if entry.seq == self._seed.next_pot_movement_number - 1:
            self._seed.next_pot_movement_number = entry.seq
