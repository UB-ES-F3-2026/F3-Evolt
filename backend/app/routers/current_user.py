"""Resolució de l'usuari actual de les rutes protegides (T07.2; sessió de T03.1).

Ordre (docs/api.md §8.2, «Transició des d'X-User-Id»):
  1. Amb `Authorization: Bearer <token>` → l'usuari de la sessió. Si el token no
     és vàlid → `401 UNAUTHENTICATED`, i `X-User-Id` s'ignora.
  2. Sense token i amb `ALLOW_X_USER_ID` activada → les regles de l'Sprint 0
     (§2): sense capçalera, usuari 1; un valor no vàlid, `422 VALIDATION_ERROR`.
  3. Sense token i amb `ALLOW_X_USER_ID` desactivada → `401 UNAUTHENTICATED`.
"""

from typing import Annotated

from fastapi import Depends, Header, Request

from app.data.seed import DEMO_USER_ID
from app.repositories import SessionRepository, UserRepository
from app.routers.dependencies import session_repository, user_repository
from app.services.errors import UNAUTHENTICATED, VALIDATION_ERROR, ApiError
from app.services.session_service import user_id_for_token

_BEARER = "bearer"


def bearer_token(authorization: str | None) -> str | None:
    """Token d'una capçalera `Authorization: Bearer <token>`, o None si no n'hi ha.

    L'esquema no distingeix majúscules (`bearer` també val). Una capçalera
    present però mal formada retorna "" perquè qui crida la pugui rebutjar.
    """
    if authorization is None:
        return None
    scheme, _, token = authorization.strip().partition(" ")
    if scheme.lower() != _BEARER:
        return ""
    return token.strip()


def current_user_id(
    request: Request,
    users: Annotated[UserRepository, Depends(user_repository)],
    sessions: Annotated[SessionRepository, Depends(session_repository)],
    authorization: Annotated[str | None, Header()] = None,
    x_user_id: Annotated[str | None, Header()] = None,
) -> int:
    """Id de l'usuari de la petició. Els serveis el reben com a paràmetre."""
    token = bearer_token(authorization)
    if token is not None:
        if not token:
            raise ApiError(UNAUTHENTICATED)
        return user_id_for_token(token, sessions)

    if not request.app.state.settings.allow_x_user_id:
        raise ApiError(UNAUTHENTICATED)
    return _user_id_from_header(x_user_id, users)


def _user_id_from_header(x_user_id: str | None, users: UserRepository) -> int:
    """Regles de l'Sprint 0 per a `X-User-Id` (docs/api.md §2)."""
    if x_user_id is None:
        return DEMO_USER_ID
    try:
        user_id = int(x_user_id)
    except ValueError:
        raise ApiError(VALIDATION_ERROR) from None
    if users.get(user_id) is None:
        raise ApiError(VALIDATION_ERROR)
    return user_id
