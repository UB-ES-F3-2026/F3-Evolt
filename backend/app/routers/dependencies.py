"""Dependències de FastAPI que donen els repositoris als routers.

Els repositoris treballen sobre les dades en memòria de l'app (`app.state.seed`,
creades al `lifespan` de `main.py`). Quan hi hagi base de dades, només canviarà
aquest fitxer i `repositories/`.
"""

from fastapi import Request

from app.repositories import (
    AccountRepository,
    MovementReportRepository,
    MovementRepository,
    OutboxRepository,
    PasswordResetTokenRepository,
    PotRepository,
    SessionRepository,
    UserRepository,
    VerificationCodeRepository,
)


def user_repository(request: Request) -> UserRepository:
    return UserRepository(request.app.state.seed)


def account_repository(request: Request) -> AccountRepository:
    return AccountRepository(request.app.state.seed)


def pot_repository(request: Request) -> PotRepository:
    return PotRepository(request.app.state.seed)


def movement_repository(request: Request) -> MovementRepository:
    return MovementRepository(request.app.state.seed)


def session_repository(request: Request) -> SessionRepository:
    return SessionRepository(request.app.state.seed)


def verification_code_repository(request: Request) -> VerificationCodeRepository:
    return VerificationCodeRepository(request.app.state.seed)


def outbox_repository(request: Request) -> OutboxRepository:
    return OutboxRepository(request.app.state.seed)


def password_reset_token_repository(request: Request) -> PasswordResetTokenRepository:
    return PasswordResetTokenRepository(request.app.state.seed)


def frontend_url(request: Request) -> str:
    """Base de l'enllaç de recuperació (`FRONTEND_URL`, docs/api.md §8.10)."""
    return request.app.state.settings.frontend_url


def movement_report_repository(request: Request) -> MovementReportRepository:
    return MovementReportRepository(request.app.state.seed)
