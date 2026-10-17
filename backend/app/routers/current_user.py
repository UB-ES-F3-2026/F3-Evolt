"""Resolució de l'usuari actual a partir de la capçalera X-User-Id (T07.2).

Segons docs/api.md §2, a l'Sprint 0 no hi ha login: la capçalera `X-User-Id`
és opcional, sense ella es fa servir l'usuari 1, i un valor no vàlid (no
numèric o d'un usuari inexistent) és un `422 VALIDATION_ERROR`.
"""

from typing import Annotated

from fastapi import Header, Request

from app.data.seed import DEMO_USER_ID
from app.services.errors import VALIDATION_ERROR, ApiError


def current_user_id(
    request: Request,
    x_user_id: Annotated[str | None, Header()] = None,
) -> int:
    """Id de l'usuari de la petició (docs/api.md §2).

    Sense capçalera → usuari demo. Amb un valor no numèric o d'un usuari que
    no existeix → `ApiError(VALIDATION_ERROR)`. Els serveixen reben l'id com a
    paràmetre, no tornen a mirar la capçalera.
    """
    if x_user_id is None:
        return DEMO_USER_ID

    try:
        user_id = int(x_user_id)
    except ValueError:
        raise ApiError(VALIDATION_ERROR) from None

    # Interí (T07.2): el seed és l'única font de veritat dels usuaris
    # existents. Quan arribin els repositoris (T07.4) aquesta consulta ha de
    # passar pel repositori.
    if user_id not in request.app.state.seed.users:
        raise ApiError(VALIDATION_ERROR)

    return user_id
