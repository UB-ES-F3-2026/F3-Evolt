"""Rutes d'accés (docs/api.md §8).

Registre (T01.2, §8.5), verificació i reenviament del codi (T02.1, §8.6 i §8.7),
login i logout (T03.1, §8.8 i §8.9), bloqueig als 5 errors (T03.2) i
recuperació de la contrasenya (T04.1, §8.10 i §8.11).

Les rutes `/api/auth/*` són públiques: no resolen l'usuari actual.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Header, status
from pydantic import BaseModel, Field, StrictBool, StrictStr

from app.models import User
from app.repositories import (
    AccountRepository,
    OutboxRepository,
    PasswordResetTokenRepository,
    SessionRepository,
    UserRepository,
    VerificationCodeRepository,
)
from app.repositories.atomic import Atomic
from app.routers.current_user import bearer_token
from app.routers.dependencies import (
    account_repository,
    atomic,
    frontend_url,
    outbox_repository,
    password_reset_token_repository,
    session_repository,
    user_repository,
    verification_code_repository,
)
from app.services.password_reset_service import forgot_password, reset_password
from app.services.registration_service import register
from app.services.session_service import login, logout
from app.services.verification_service import resend, verify

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    """Cos de la petició: `{ identifier, password, acceptedTerms }`.

    Tipus estrictes, com el `amount` de la recàrrega (P5): un número en lloc
    del text, o `"true"` en lloc de `true`, és un `422 VALIDATION_ERROR`.
    """

    identifier: StrictStr
    password: StrictStr
    accepted_terms: StrictBool = Field(alias="acceptedTerms")


class RegisterResponse(BaseModel):
    """Cos de la resposta `201`: `{ identifier, status }`. Sense token: no obre sessió."""

    identifier: str
    status: str

    @classmethod
    def from_user(cls, user: User) -> "RegisterResponse":
        return cls(identifier=user.identifier, status=user.status)


@router.post("/register", status_code=status.HTTP_201_CREATED)
def create_account(
    body: RegisterRequest,
    users: Annotated[UserRepository, Depends(user_repository)],
    accounts: Annotated[AccountRepository, Depends(account_repository)],
    codes: Annotated[VerificationCodeRepository, Depends(verification_code_repository)],
    outbox: Annotated[OutboxRepository, Depends(outbox_repository)],
    run: Annotated[Atomic, Depends(atomic)],
) -> RegisterResponse:
    # Tot o res: el duplicat, l'usuari, el compte i el codi (TR01.1). El servei fa
    # el hash fora de l'`atomic`.
    user = register(body.identifier, body.password, body.accepted_terms, users, accounts, codes, outbox, atomic=run)
    return RegisterResponse.from_user(user)


class LoginRequest(BaseModel):
    """Cos de la petició: `{ identifier, password }`. No es valida la política de contrasenya."""

    identifier: StrictStr
    password: StrictStr


class SessionResponse(BaseModel):
    """Cos de la resposta `200`: `{ token }`. La verificació (T02.1) també el farà servir."""

    token: str


class StatusResponse(BaseModel):
    """Cos `{ status: "ok" }`. Sempre amb JSON: l'apiClient del frontend l'espera (§8.9)."""

    status: str = "ok"


@router.post("/login")
def start_session(
    body: LoginRequest,
    users: Annotated[UserRepository, Depends(user_repository)],
    sessions: Annotated[SessionRepository, Depends(session_repository)],
    outbox: Annotated[OutboxRepository, Depends(outbox_repository)],
) -> SessionResponse:
    """El 5è error seguit bloqueja el compte i deixa l'avís a la bústia (T03.2)."""
    return SessionResponse(token=login(body.identifier, body.password, users, sessions, outbox))


@router.post("/logout")
def end_session(
    sessions: Annotated[SessionRepository, Depends(session_repository)],
    authorization: Annotated[str | None, Header()] = None,
) -> StatusResponse:
    logout(bearer_token(authorization), sessions)
    return StatusResponse()


class VerifyRequest(BaseModel):
    """Cos de la petició: `{ identifier, code }`. El codi és un string per no perdre els zeros."""

    identifier: StrictStr
    code: StrictStr


class ResendCodeRequest(BaseModel):
    """Cos de la petició: `{ identifier }`."""

    identifier: StrictStr


@router.post("/verify")
def verify_account(
    body: VerifyRequest,
    users: Annotated[UserRepository, Depends(user_repository)],
    codes: Annotated[VerificationCodeRepository, Depends(verification_code_repository)],
    sessions: Annotated[SessionRepository, Depends(session_repository)],
    run: Annotated[Atomic, Depends(atomic)],
) -> SessionResponse:
    """Codi correcte → compte actiu i sessió oberta: la mateixa resposta que el login (P9).

    Tot o res (TR01.1): dos codis incorrectes alhora compten com a dos intents.
    """
    return SessionResponse(token=run.run(lambda: verify(body.identifier, body.code, users, codes, sessions)))


@router.post("/resend-code")
def resend_code(
    body: ResendCodeRequest,
    users: Annotated[UserRepository, Depends(user_repository)],
    codes: Annotated[VerificationCodeRepository, Depends(verification_code_repository)],
    outbox: Annotated[OutboxRepository, Depends(outbox_repository)],
) -> StatusResponse:
    """Sempre la mateixa resposta, existeixi o no el compte (§8.7)."""
    resend(body.identifier, users, codes, outbox)
    return StatusResponse()


class ForgotPasswordRequest(BaseModel):
    """Cos de la petició: `{ identifier }`, email o telèfon."""

    identifier: StrictStr


class ResetPasswordRequest(BaseModel):
    """Cos de la petició: `{ token, password }`. El `token` ve de l'URL de l'enllaç."""

    token: StrictStr
    password: StrictStr


@router.post("/forgot-password")
def request_password_reset(
    body: ForgotPasswordRequest,
    users: Annotated[UserRepository, Depends(user_repository)],
    tokens: Annotated[PasswordResetTokenRepository, Depends(password_reset_token_repository)],
    outbox: Annotated[OutboxRepository, Depends(outbox_repository)],
    base_url: Annotated[str, Depends(frontend_url)],
    run: Annotated[Atomic, Depends(atomic)],
) -> StatusResponse:
    """Sempre la mateixa resposta, existeixi o no el compte (§8.10).

    Tot o res (TR01.1): mai no queden dos enllaços vàlids per al mateix usuari.
    """
    run.run(lambda: forgot_password(body.identifier, users, tokens, outbox, base_url))
    return StatusResponse()


@router.post("/reset-password")
def change_password(
    body: ResetPasswordRequest,
    users: Annotated[UserRepository, Depends(user_repository)],
    tokens: Annotated[PasswordResetTokenRepository, Depends(password_reset_token_repository)],
    sessions: Annotated[SessionRepository, Depends(session_repository)],
    run: Annotated[Atomic, Depends(atomic)],
) -> StatusResponse:
    """Contrasenya nova i totes les sessions tancades. No obre cap sessió (§8.11).

    Tot o res (TR01.1): el token, la contrasenya, el desbloqueig i les sessions.
    El servei fa el hash fora de l'`atomic`.
    """
    reset_password(body.token, body.password, users, tokens, sessions, atomic=run)
    return StatusResponse()
