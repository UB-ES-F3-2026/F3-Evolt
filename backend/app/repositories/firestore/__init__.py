"""Repositoris de Firestore (TR01.1, docs/api.md §8.13).

Mateixos mètodes que els de memòria (`app/repositories/`): els serveis no saben
on es guarden les dades. Quin es fa servir ho decideix `STORAGE`
(`app/routers/dependencies.py`).
"""

from app.repositories.firestore.account import FirestoreAccountRepository
from app.repositories.firestore.movement import FirestoreMovementRepository
from app.repositories.firestore.movement_report import FirestoreMovementReportRepository
from app.repositories.firestore.outbox import FirestoreOutboxRepository
from app.repositories.firestore.password_reset import FirestorePasswordResetTokenRepository
from app.repositories.firestore.pot import FirestorePotRepository
from app.repositories.firestore.session import FirestoreSessionRepository
from app.repositories.firestore.user import FirestoreUserRepository
from app.repositories.firestore.verification_code import FirestoreVerificationCodeRepository

__all__ = [
    "FirestoreAccountRepository",
    "FirestoreMovementReportRepository",
    "FirestoreMovementRepository",
    "FirestoreOutboxRepository",
    "FirestorePasswordResetTokenRepository",
    "FirestorePotRepository",
    "FirestoreSessionRepository",
    "FirestoreUserRepository",
    "FirestoreVerificationCodeRepository",
]
