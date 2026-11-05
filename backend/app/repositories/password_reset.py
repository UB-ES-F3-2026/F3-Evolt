"""Repositori dels enllaços de recuperació (T04.1, docs/api.md §8.10, §8.11 i §8.13).

Llegeix i escriu les dades en memòria del SeedData. Si un token és vàlid o ha
caducat ho decideix el servei.
"""

import secrets
from datetime import datetime

from app.data.seed import SeedData
from app.models import PasswordResetToken

# 32 bytes aleatoris → 43 caràcters en base64 d'URL, com el token de sessió.
_TOKEN_BYTES = 32


class PasswordResetTokenRepository:
    """Tokens dels enllaços de recuperació, per token."""

    def __init__(self, seed: SeedData) -> None:
        self._seed = seed

    def replace(self, user_id: int, now: datetime) -> PasswordResetToken:
        """Crea un token nou per a l'usuari i esborra els anteriors: l'enllaç vell deixa de servir.

        `secrets` i no `random`: el token és una credencial.
        """
        tokens = self._seed.password_reset_tokens
        # Còpia i `pop`, com a `SessionRepository.delete_for_user`: dos «He oblidat
        # la contrasenya» alhora poden canviar el diccionari mentre es recorre.
        for old in [t for t, reset in list(tokens.items()) if reset.user_id == user_id]:
            tokens.pop(old, None)
        reset = PasswordResetToken(token=secrets.token_urlsafe(_TOKEN_BYTES), user_id=user_id, created_at=now)
        tokens[reset.token] = reset
        return reset

    def get(self, token: str) -> PasswordResetToken | None:
        """Token desat, o None si no existeix o s'ha substituït per un de més nou."""
        return self._seed.password_reset_tokens.get(token)

    def mark_used(self, token: str) -> None:
        """Gasta el token. Ha d'existir (KeyError)."""
        self._seed.password_reset_tokens[token].used = True
