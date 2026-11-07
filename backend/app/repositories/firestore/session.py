"""Sessions a Firestore (TR01.1). Mateixos mètodes que `repositories/session.py`.

Col·lecció `sessions`. L'id del document és el **hash** del token, no el token:
si algú llegís la base de dades, no podria fer-se passar per ningú.
"""

import hashlib
import secrets
from datetime import datetime

from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

from app.models import Session
from app.repositories.firestore import _tx

SESSIONS = "sessions"
_TOKEN_BYTES = 32


class FirestoreSessionRepository:
    def __init__(self, client: firestore.Client) -> None:
        self._sessions = client.collection(SESSIONS)

    def create(self, user_id: int, now: datetime) -> Session:
        session = Session(token=secrets.token_urlsafe(_TOKEN_BYTES), user_id=user_id, last_activity=now)
        _tx.create(self._doc(session.token), {"user_id": user_id, "last_activity": now})
        return session

    def get(self, token: str) -> Session | None:
        snapshot = _tx.get(self._doc(token))
        if not snapshot.exists:
            return None
        data = snapshot.to_dict()
        return Session(token=token, user_id=data["user_id"], last_activity=_tx.to_madrid(data["last_activity"]))

    def touch(self, token: str, now: datetime) -> None:
        _tx.update(self._doc(token), {"last_activity": now})

    def delete(self, token: str) -> None:
        _tx.delete(self._doc(token))

    def delete_for_user(self, user_id: int) -> None:
        """Tanca totes les sessions de l'usuari (T04.1)."""
        query = self._sessions.where(filter=FieldFilter("user_id", "==", user_id))
        for snapshot in _tx.query(query):
            _tx.delete(snapshot.reference)

    def _doc(self, token: str) -> firestore.DocumentReference:
        return self._sessions.document(token_key(token))


def token_key(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
