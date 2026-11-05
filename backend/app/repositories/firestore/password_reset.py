"""Enllaços de recuperació a Firestore (TR01.1). Mateixos mètodes que `repositories/password_reset.py`.

Col·lecció `password_reset_tokens`. Com a les sessions, l'id del document és el
**hash** del token: qui llegís la base de dades no podria canviar cap contrasenya.
"""

import secrets
from datetime import datetime

from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

from app.models import PasswordResetToken
from app.repositories.firestore import _tx
from app.repositories.firestore.session import token_key

PASSWORD_RESET_TOKENS = "password_reset_tokens"
_TOKEN_BYTES = 32


class FirestorePasswordResetTokenRepository:
    def __init__(self, client: firestore.Client) -> None:
        self._tokens = client.collection(PASSWORD_RESET_TOKENS)

    def replace(self, user_id: int, now: datetime) -> PasswordResetToken:
        """Token nou per a l'usuari; els anteriors s'esborren i deixen de servir."""
        old = _tx.query(self._tokens.where(filter=FieldFilter("user_id", "==", user_id)))
        for snapshot in old:
            _tx.delete(snapshot.reference)
        reset = PasswordResetToken(token=secrets.token_urlsafe(_TOKEN_BYTES), user_id=user_id, created_at=now)
        _tx.create(self._doc(reset.token), {"user_id": user_id, "created_at": now, "used": False})
        return reset

    def get(self, token: str) -> PasswordResetToken | None:
        snapshot = _tx.get(self._doc(token))
        if not snapshot.exists:
            return None
        data = snapshot.to_dict()
        return PasswordResetToken(
            token=token,
            user_id=data["user_id"],
            created_at=_tx.to_madrid(data["created_at"]),
            used=data["used"],
        )

    def mark_used(self, token: str) -> None:
        _tx.update(self._doc(token), {"used": True})

    def _doc(self, token: str) -> firestore.DocumentReference:
        return self._tokens.document(token_key(token))
