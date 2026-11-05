"""Recuperació de la contrasenya (T04.1 · US-04, docs/api.md §8.1, §8.10 i §8.11).

- «He oblidat la contrasenya»: si el compte existeix, rep un enllaç d'un sol ús
  que caduca als 30 minuts; un enllaç nou invalida l'anterior.
- «Nova contrasenya»: amb l'enllaç vàlid, la contrasenya canvia, es tanquen totes
  les sessions i el compte es desbloqueja (P15).
"""

import threading
from datetime import datetime, timedelta

from app.models import now_madrid
from app.repositories import (
    OutboxRepository,
    PasswordResetTokenRepository,
    SessionRepository,
    UserRepository,
)
from app.repositories.atomic import DIRECT, Atomic
from app.services.errors import RESET_LINK_EXPIRED, VALIDATION_ERROR, WEAK_PASSWORD, ApiError
from app.services.identifier import InvalidIdentifier, normalize_identifier
from app.services.notifications import send_password_reset
from app.services.password_hashing import hash_password
from app.services.password_policy import fits_password_hash, is_strong_password

LINK_VALIDITY = timedelta(minutes=30)
# Ruta del frontend que llegeix el token de l'URL (T04.2).
RESET_PATH = "/nova-contrasenya"

# Dues peticions alhora amb el mateix enllaç no poden canviar la contrasenya
# totes dues: protegeix «comprovar que el token és vàlid + gastar-lo». Amb
# Firestore (#106) ho farà una transacció. bcrypt es fa fora del pany.
_RESET_LOCK = threading.Lock()


def forgot_password(
    raw_identifier: str,
    users: UserRepository,
    tokens: PasswordResetTokenRepository,
    outbox: OutboxRepository,
    frontend_url: str,
    now: datetime | None = None,
) -> None:
    """«He oblidat la contrasenya» (§8.10).

    Identificador mal format → VALIDATION_ERROR. Si el compte no existeix, no es
    fa res i la resposta és la mateixa, perquè no es pugui saber quins comptes
    hi ha. Qualsevol compte que existeixi rep l'enllaç: pendent, actiu o bloquejat.
    """
    now = now or now_madrid()
    try:
        identifier = normalize_identifier(raw_identifier).value
    except InvalidIdentifier:
        raise ApiError(VALIDATION_ERROR) from None

    user = users.find_by_identifier(identifier)
    if user is None:
        return
    reset = tokens.replace(user.id, now)
    send_password_reset(user, f"{frontend_url}{RESET_PATH}?token={reset.token}", now, outbox)


def reset_password(
    token: str,
    password: str,
    users: UserRepository,
    tokens: PasswordResetTokenRepository,
    sessions: SessionRepository,
    now: datetime | None = None,
    atomic: Atomic = DIRECT,
) -> None:
    """«Nova contrasenya» amb el token de l'enllaç (§8.11).

    Ordre, s'atura al primer error:
      1. Contrasenya de més de 72 bytes → VALIDATION_ERROR (els tipus del cos els
         comprova el router).
      2. Token desconegut, substituït, ja gastat o caducat → RESET_LINK_EXPIRED.
      3. Política de contrasenya → WEAK_PASSWORD. El token no es gasta.
    Si tot és correcte: contrasenya nova, token gastat, totes les sessions
    tancades i compte desbloquejat. L'estat (pendent o actiu) no canvia, i no
    s'obre cap sessió: cal iniciar-la amb la contrasenya nova.
    El hash es fa fora de l'`atomic` (TR01.1): només les escriptures hi van a dins.
    """
    now = now or now_madrid()
    if not fits_password_hash(password):
        raise ApiError(VALIDATION_ERROR)
    _check_link(token, tokens, now)
    if not is_strong_password(password):
        raise ApiError(WEAK_PASSWORD)

    password_hash = hash_password(password)

    def write() -> None:
        with _RESET_LOCK:
            # Es torna a comprovar a dins: una altra petició pot haver gastat el
            # token, o n'hi pot haver un de nou, mentre es feia el hash.
            user_id = _check_link(token, tokens, now)
            # Primer les sessions: tancar-les llegeix quines hi ha, i en una
            # transacció de Firestore les lectures van abans de les escriptures.
            sessions.delete_for_user(user_id)
            tokens.mark_used(token)
            users.set_password_hash(user_id, password_hash)
            users.set_login_state(user_id, failed_logins=0, locked_until=None)

    atomic.run(write)


def _check_link(token: str, tokens: PasswordResetTokenRepository, now: datetime) -> int:
    """Usuari de l'enllaç, si encara serveix. Si no, RESET_LINK_EXPIRED, sigui quin sigui el motiu."""
    reset = tokens.get(token)
    if reset is None or reset.used or now - reset.created_at >= LINK_VALIDITY:
        raise ApiError(RESET_LINK_EXPIRED)
    return reset.user_id
