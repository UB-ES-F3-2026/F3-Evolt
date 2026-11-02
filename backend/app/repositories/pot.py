"""Repositori de guardioles (T07.4).

Llegeix i escriu les dades en memòria del SeedData. No decideix regles de
negoci: això és feina dels serveis.
"""

import threading

from app.data.seed import SeedData, pot_id
from app.models import Pot

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
