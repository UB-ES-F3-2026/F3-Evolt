"""Repositori de sessions (T03.1, docs/api.md §8.2 i §8.13).

Llegeix i escriu les dades en memòria del SeedData. No decideix regles de
negoci: si una sessió ha caducat ho decideix el servei.
"""

import secrets
from datetime import datetime

from app.data.seed import SeedData
from app.models import Session

# 32 bytes aleatoris → 43 caràcters en base64 d'URL: impossible d'endevinar.
_TOKEN_BYTES = 32


class SessionRepository:
    """Sessions obertes, una per dispositiu (T03.1)."""

    def __init__(self, seed: SeedData) -> None:
        self._seed = seed

    def create(self, user_id: int, now: datetime) -> Session:
        """Obre una sessió nova amb un token opac i aleatori.

        `secrets` i no `random`: el token és una credencial.
        """
        session = Session(token=secrets.token_urlsafe(_TOKEN_BYTES), user_id=user_id, last_activity=now)
        self._seed.sessions[session.token] = session
        return session

    def get(self, token: str) -> Session | None:
        """Sessió d'aquest token, o None si no existeix o ja s'ha tancat."""
        return self._seed.sessions.get(token)

    def touch(self, token: str, now: datetime) -> None:
        """Apunta `now` com a última activitat de la sessió."""
        self._seed.sessions[token].last_activity = now

    def delete(self, token: str) -> None:
        """Tanca la sessió. Si ja no existia, no fa res."""
        self._seed.sessions.pop(token, None)

    def delete_for_user(self, user_id: int) -> None:
        """Tanca totes les sessions de l'usuari, a tots els dispositius (T04.1).

        Es recorre una còpia: un login alhora (un altre fil del pool) pot afegir
        una sessió mentre es recorre, i el diccionari no es pot canviar a mig
        recórrer. `pop` i no `del`: un logout alhora pot haver tancat la mateixa.
        """
        sessions = self._seed.sessions
        for token in [t for t, session in list(sessions.items()) if session.user_id == user_id]:
            sessions.pop(token, None)
