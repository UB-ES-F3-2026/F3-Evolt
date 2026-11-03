"""Rutes d'accés (docs/api.md §8): registre (T01.2, §8.5), login i logout (T03.1, §8.8 i §8.9).

Les rutes `/api/auth/*` són públiques: no resolen l'usuari actual.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Header, status
from pydantic import BaseModel, Field, StrictBool, StrictStr

from app.models import User
from app.repositories import AccountRepository, SessionRepository, UserRepository
from app.routers.current_user import bearer_token
from app.routers.dependencies import account_repository, session_repository, user_repository
from app.services.registration_service import register
from app.services.session_service import login, logout

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
) -> RegisterResponse:
    user = register(body.identifier, body.password, body.accepted_terms, users, accounts)
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
) -> SessionResponse:
    return SessionResponse(token=login(body.identifier, body.password, users, sessions))


@router.post("/logout")
def end_session(
    sessions: Annotated[SessionRepository, Depends(session_repository)],
    authorization: Annotated[str | None, Header()] = None,
) -> StatusResponse:
    logout(bearer_token(authorization), sessions)
    return StatusResponse()
