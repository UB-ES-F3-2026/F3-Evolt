"""Rutes d'accés (docs/api.md §8). De moment, el registre (T01.2 · US-01, §8.5).

Les rutes `/api/auth/*` són públiques: no resolen l'usuari actual.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field, StrictBool, StrictStr

from app.models import User
from app.repositories import AccountRepository, UserRepository
from app.routers.dependencies import account_repository, user_repository
from app.services.registration_service import register

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
