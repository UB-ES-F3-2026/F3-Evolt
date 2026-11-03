"""Inici i tancament de sessió (T03.1 · US-03, docs/api.md §8.2, §8.8 i §8.9).

El bloqueig als 5 errors i la caducitat als 5 minuts sense activitat (§8.1) els
afegeix la T03.2: aquí ja es desa l'hora de l'última activitat de cada sessió.
"""

from datetime import datetime

from app.models import STATUS_PENDING, now_madrid
from app.repositories import SessionRepository, UserRepository
from app.services.errors import (
    ACCOUNT_NOT_VERIFIED,
    INVALID_CREDENTIALS,
    UNAUTHENTICATED,
    ApiError,
)
from app.services.identifier import InvalidIdentifier, normalize_identifier
from app.services.password_hashing import verify_password
from app.services.password_policy import fits_password_hash

# Hash de bcrypt d'un text aleatori que ningú no coneix. Quan l'identificador no
# existeix, es comprova la contrasenya contra aquest hash igualment: així la
# resposta triga el mateix que amb un compte real i no es pot saber, pel temps,
# quins emails estan registrats (US-03: missatge genèric).
_UNKNOWN_USER_HASH = "$2b$12$gXqgQNA3wxsQMlUujfS1RunEG4hKC.xnE5h.SBvvVaWAKr/HemhZ2"


def login(
    raw_identifier: str,
    password: str,
    users: UserRepository,
    sessions: SessionRepository,
    now: datetime | None = None,
) -> str:
    """Comprova les credencials i obre una sessió nova. Retorna el token.

    Ordre (§8.8, sense el bloqueig de la T03.2):
      1. Identificador no vàlid, compte inexistent o contrasenya incorrecta →
         INVALID_CREDENTIALS, sempre el mateix error.
      2. Contrasenya correcta però compte pendent → ACCOUNT_NOT_VERIFIED (P8).
    """
    now = now or now_madrid()

    try:
        identifier = normalize_identifier(raw_identifier).value
    except InvalidIdentifier:
        identifier = None
    user = users.find_by_identifier(identifier) if identifier else None

    # bcrypt no admet més de 72 bytes; una contrasenya així no pot ser la bona.
    if not fits_password_hash(password):
        raise ApiError(INVALID_CREDENTIALS)
    password_hash = user.password_hash if user else _UNKNOWN_USER_HASH
    if not verify_password(password, password_hash) or user is None:
        raise ApiError(INVALID_CREDENTIALS)

    if user.status == STATUS_PENDING:
        raise ApiError(ACCOUNT_NOT_VERIFIED)

    return sessions.create(user.id, now).token


def logout(token: str | None, sessions: SessionRepository) -> None:
    """Tanca la sessió del token, si n'hi ha. No falla mai (P14)."""
    if token:
        sessions.delete(token)


def user_id_for_token(token: str, sessions: SessionRepository, now: datetime | None = None) -> int:
    """Usuari de la sessió d'aquest token, i n'apunta l'activitat.

    Token desconegut o ja tancat → UNAUTHENTICATED. La T03.2 hi afegirà la
    caducitat per inactivitat (SESSION_EXPIRED).
    """
    session = sessions.get(token)
    if session is None:
        raise ApiError(UNAUTHENTICATED)
    sessions.touch(token, now or now_madrid())
    return session.user_id
