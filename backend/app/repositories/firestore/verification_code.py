"""Codis de verificació a Firestore (TR01.1). Mateixos mètodes que `repositories/verification_code.py`.

Col·lecció `verification_codes`, un document per usuari pendent amb el seu id:
com a màxim un codi vigent per usuari.
"""

from datetime import datetime

from google.cloud import firestore

from app.models import VerificationCode
from app.repositories.firestore import _tx

VERIFICATION_CODES = "verification_codes"


class FirestoreVerificationCodeRepository:
    def __init__(self, client: firestore.Client) -> None:
        self._codes = client.collection(VERIFICATION_CODES)

    def replace(self, user_id: int, code: str, now: datetime) -> VerificationCode:
        verification = VerificationCode(user_id=user_id, code=code, created_at=now)
        _tx.set_doc(self._codes.document(str(user_id)), {"code": code, "created_at": now, "failed_attempts": 0})
        return verification

    def get(self, user_id: int) -> VerificationCode | None:
        snapshot = _tx.get(self._codes.document(str(user_id)))
        if not snapshot.exists:
            return None
        data = snapshot.to_dict()
        return VerificationCode(
            user_id=user_id,
            code=data["code"],
            created_at=_tx.to_madrid(data["created_at"]),
            failed_attempts=data["failed_attempts"],
        )

    def record_failure(self, user_id: int) -> int:
        """Suma un intent fallit i retorna el total. Dins d'`atomic`, dos intents alhora no se'n mengen cap."""
        ref = self._codes.document(str(user_id))
        failed = _tx.get(ref).to_dict()["failed_attempts"] + 1
        _tx.update(ref, {"failed_attempts": failed})
        return failed

    def delete(self, user_id: int) -> None:
        _tx.delete(self._codes.document(str(user_id)))
