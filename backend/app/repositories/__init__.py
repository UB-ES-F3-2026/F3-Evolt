"""Repositoris en memòria (T07.4). Única capa que llegeix i escriu les dades del seed; els serveis no accedeixen mai a seed.py directament."""

from app.repositories.account import AccountRepository
from app.repositories.movement import MovementRepository
from app.repositories.movement_report import MovementReportRepository
from app.repositories.outbox import OutboxRepository
from app.repositories.pot import PotRepository
from app.repositories.session import SessionRepository
from app.repositories.user import UserRepository
from app.repositories.verification_code import VerificationCodeRepository

__all__ = [
    "AccountRepository",
    "MovementReportRepository",
    "MovementRepository",
    "OutboxRepository",
    "PotRepository",
    "SessionRepository",
    "UserRepository",
    "VerificationCodeRepository",
]
