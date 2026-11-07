"""Repositori de codis de verificació (T02.1, docs/api.md §8.6 i §8.13).

Llegeix i escriu les dades en memòria del SeedData. Si un codi és correcte,
caducat o bloquejat ho decideix el servei.
"""

from datetime import datetime

from app.data.seed import SeedData
from app.models import VerificationCode


class VerificationCodeRepository:
    """Codi vigent de cada usuari pendent (T02.1). Com a màxim un per usuari."""

    def __init__(self, seed: SeedData) -> None:
        self._seed = seed

    def replace(self, user_id: int, code: str, now: datetime) -> VerificationCode:
        """Desa un codi nou per a l'usuari. L'anterior, si n'hi havia, deixa de servir."""
        verification = VerificationCode(user_id=user_id, code=code, created_at=now)
        self._seed.verification_codes[user_id] = verification
        return verification

    def get(self, user_id: int) -> VerificationCode | None:
        """Codi vigent de l'usuari, o None si no en té."""
        return self._seed.verification_codes.get(user_id)

    def record_failure(self, user_id: int) -> int:
        """Suma un intent fallit al codi vigent i retorna el total."""
        verification = self._seed.verification_codes[user_id]
        verification.failed_attempts += 1
        return verification.failed_attempts

    def delete(self, user_id: int) -> None:
        """Esborra el codi de l'usuari (p. ex. un cop fet servir). Si no n'hi ha, no fa res."""
        self._seed.verification_codes.pop(user_id, None)
