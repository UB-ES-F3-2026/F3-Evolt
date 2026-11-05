"""Inici i tancament de sessió (T03.1 i T03.2 · US-03, docs/api.md §8.1, §8.2, §8.8 i §8.9).

Regles de la T03.2 (§8.1):
  - 5 errors de login seguits bloquegen el compte 15 minuts i envien un avís.
  - 5 minuts sense activitat tanquen la sessió.
"""

import threading
from datetime import datetime, timedelta

from app.models import STATUS_PENDING, User, now_madrid
from app.repositories import OutboxRepository, SessionRepository, UserRepository
from app.services.errors import (
    ACCOUNT_LOCKED,
    ACCOUNT_NOT_VERIFIED,
    INVALID_CREDENTIALS,
    SESSION_EXPIRED,
    UNAUTHENTICATED,
    ApiError,
)
from app.services.identifier import InvalidIdentifier, normalize_identifier
from app.services.notifications import send_account_locked
from app.services.password_hashing import verify_password
from app.services.password_policy import fits_password_hash

MAX_FAILED_LOGINS = 5
LOCK_DURATION = timedelta(minutes=15)
INACTIVITY_LIMIT = timedelta(minutes=5)

# Hash de bcrypt d'un text aleatori que ningú no coneix. Quan l'identificador no
# existeix, es comprova la contrasenya contra aquest hash igualment: així la
# resposta triga el mateix que amb un compte real i no es pot saber, pel temps,
# quins emails estan registrats (US-03: missatge genèric).
_UNKNOWN_USER_HASH = "$2b$12$gXqgQNA3wxsQMlUujfS1RunEG4hKC.xnE5h.SBvvVaWAKr/HemhZ2"

# Les rutes síncrones corren en un pool de fils: sense aquest pany, dos logins
# fallits alhora podrien llegir el mateix comptador i comptar-ne només un.
# Protegeix «llegir el comptador + escriure'l»; amb Firestore (#106) ho farà una
# transacció. bcrypt es fa fora del pany perquè els logins no s'esperin entre ells.
_LOGIN_STATE_LOCK = threading.Lock()


def login(
    raw_identifier: str,
    password: str,
    users: UserRepository,
    sessions: SessionRepository,
    outbox: OutboxRepository,
    now: datetime | None = None,
) -> str:
    """Comprova les credencials i obre una sessió nova. Retorna el token.

    Ordre (§8.8):
      1. Identificador no vàlid o compte inexistent → INVALID_CREDENTIALS. Mai no
         bloqueja res: no hi ha compte.
      2. Compte bloquejat → ACCOUNT_LOCKED, encara que la contrasenya sigui la
         bona. Aquest intent no compta.
      3. Contrasenya incorrecta → compta l'error. El 5è seguit bloqueja el compte
         15 minuts, envia l'avís i respon ACCOUNT_LOCKED; els altres,
         INVALID_CREDENTIALS.
      4. Contrasenya correcta però compte pendent → ACCOUNT_NOT_VERIFIED (P8).
    Amb la contrasenya correcta el comptador torna a zero.
    """
    now = now or now_madrid()

    try:
        identifier = normalize_identifier(raw_identifier).value
    except InvalidIdentifier:
        identifier = None
    user = users.find_by_identifier(identifier) if identifier else None

    if user is None:
        # bcrypt igualment, perquè el temps no delati quins comptes existeixen.
        if fits_password_hash(password):
            verify_password(password, _UNKNOWN_USER_HASH)
        raise ApiError(INVALID_CREDENTIALS)

    if _is_locked(user, now):
        raise _locked_error(user)

    # bcrypt no admet més de 72 bytes; una contrasenya així no pot ser la bona.
    if not (fits_password_hash(password) and verify_password(password, user.password_hash)):
        _count_failed_login(user, users, outbox, now)

    users.set_login_state(user.id, failed_logins=0, locked_until=None)
    if user.status == STATUS_PENDING:
        raise ApiError(ACCOUNT_NOT_VERIFIED)

    return sessions.create(user.id, now).token


def _is_locked(user: User, now: datetime) -> bool:
    return user.locked_until is not None and now < user.locked_until


def _locked_error(user: User) -> ApiError:
    return ApiError(ACCOUNT_LOCKED, details={"lockedUntil": user.locked_until.isoformat()})


def _count_failed_login(user: User, users: UserRepository, outbox: OutboxRepository, now: datetime) -> None:
    """Suma un error de login. Sempre llança: INVALID_CREDENTIALS o, al 5è, ACCOUNT_LOCKED."""
    with _LOGIN_STATE_LOCK:
        # Un altre login pot haver bloquejat el compte mentre es feia el bcrypt.
        if _is_locked(user, now):
            raise _locked_error(user)
        failed_logins = user.failed_logins + 1
        if failed_logins < MAX_FAILED_LOGINS:
            users.set_login_state(user.id, failed_logins=failed_logins, locked_until=None)
            raise ApiError(INVALID_CREDENTIALS)
        users.set_login_state(user.id, failed_logins=0, locked_until=now + LOCK_DURATION)
    send_account_locked(user, now, outbox)
    raise _locked_error(user)


def logout(token: str | None, sessions: SessionRepository) -> None:
    """Tanca la sessió del token, si n'hi ha. No falla mai (P14)."""
    if token:
        sessions.delete(token)


def user_id_for_token(token: str, sessions: SessionRepository, now: datetime | None = None) -> int:
    """Usuari de la sessió d'aquest token, i n'apunta l'activitat.

    Token desconegut o ja tancat → UNAUTHENTICATED. 5 minuts o més sense activitat
    → la sessió es tanca i SESSION_EXPIRED; el mateix token després ja és
    UNAUTHENTICATED. Qualsevol petició amb sessió vàlida compta com a activitat,
    també si acaba amb un error de negoci.
    """
    now = now or now_madrid()
    session = sessions.get(token)
    if session is None:
        raise ApiError(UNAUTHENTICATED)
    if now - session.last_activity >= INACTIVITY_LIMIT:
        sessions.delete(token)
        raise ApiError(SESSION_EXPIRED)
    sessions.touch(token, now)
    return session.user_id
