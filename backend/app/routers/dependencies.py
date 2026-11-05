"""Dependències de FastAPI que donen els repositoris als routers.

On es guarden les dades ho decideix `STORAGE` (TR01.1, docs/api.md §8.13):

- `memory` (per defecte): les dades de l'app (`app.state.seed`), creades al
  `lifespan` de `main.py`, com a l'Sprint 0.
- `firestore`: el client de `app.state.firestore`.

Els dos repositoris de cada cosa tenen els mateixos mètodes, així que els
routers i els serveis no saben quin reben. Els de Firestore s'importen només
quan calen: amb `memory`, l'app no carrega cap llibreria de Google.
"""

from fastapi import Request

from app.config import STORAGE_FIRESTORE
from app.repositories import (
    AccountRepository,
    MovementRepository,
    OutboxRepository,
    PasswordResetTokenRepository,
    PotRepository,
    SessionRepository,
    UserRepository,
    VerificationCodeRepository,
)
from app.repositories.atomic import Atomic


def _firestore(request: Request):
    """El client de Firestore, o None si les dades són en memòria."""
    if request.app.state.settings.storage == STORAGE_FIRESTORE:
        return request.app.state.firestore
    return None


def user_repository(request: Request) -> UserRepository:
    if client := _firestore(request):
        from app.repositories.firestore import FirestoreUserRepository

        return FirestoreUserRepository(client)
    return UserRepository(request.app.state.seed)


def account_repository(request: Request) -> AccountRepository:
    if client := _firestore(request):
        from app.repositories.firestore import FirestoreAccountRepository

        return FirestoreAccountRepository(client)
    return AccountRepository(request.app.state.seed)


def pot_repository(request: Request) -> PotRepository:
    if client := _firestore(request):
        from app.repositories.firestore import FirestorePotRepository

        return FirestorePotRepository(client)
    return PotRepository(request.app.state.seed)


def movement_repository(request: Request) -> MovementRepository:
    if client := _firestore(request):
        from app.repositories.firestore import FirestoreMovementRepository

        return FirestoreMovementRepository(client)
    return MovementRepository(request.app.state.seed)


def session_repository(request: Request) -> SessionRepository:
    if client := _firestore(request):
        from app.repositories.firestore import FirestoreSessionRepository

        return FirestoreSessionRepository(client)
    return SessionRepository(request.app.state.seed)


def verification_code_repository(request: Request) -> VerificationCodeRepository:
    if client := _firestore(request):
        from app.repositories.firestore import FirestoreVerificationCodeRepository

        return FirestoreVerificationCodeRepository(client)
    return VerificationCodeRepository(request.app.state.seed)


def outbox_repository(request: Request) -> OutboxRepository:
    if client := _firestore(request):
        from app.repositories.firestore import FirestoreOutboxRepository

        return FirestoreOutboxRepository(client)
    return OutboxRepository(request.app.state.seed)


def password_reset_token_repository(request: Request) -> PasswordResetTokenRepository:
    if client := _firestore(request):
        from app.repositories.firestore import FirestorePasswordResetTokenRepository

        return FirestorePasswordResetTokenRepository(client)
    return PasswordResetTokenRepository(request.app.state.seed)


def atomic(request: Request) -> Atomic:
    """Executa una operació tot o res: pany en memòria, transacció a Firestore."""
    return request.app.state.atomic


def frontend_url(request: Request) -> str:
    """Base de l'enllaç de recuperació (`FRONTEND_URL`, docs/api.md §8.10)."""
    return request.app.state.settings.frontend_url
