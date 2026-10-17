"""Repositori de guardioles (T07.4).

Llegeix i escriu les dades en memòria del SeedData. No decideix regles de
negoci: això és feina dels serveis.
"""

from app.data.seed import SeedData
from app.models import Pot


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
