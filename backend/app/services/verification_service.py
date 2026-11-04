"""Codi de verificació del registre (T02.1 · US-02, docs/api.md §8.1, §8.6 i §8.7).

- En registrar-se (i en «Envia'm un codi nou»), l'usuari pendent rep un codi de
  6 xifres que caduca als 10 minuts; un codi nou invalida l'anterior.
- Amb el codi correcte, el compte passa a actiu i s'obre la sessió (P9).
- Al 5è codi incorrecte el codi queda bloquejat: cal demanar-ne un de nou.
"""

import re
import secrets
from datetime import datetime, timedelta

from app.models import CODE_LENGTH, STATUS_ACTIVE, STATUS_PENDING, User, now_madrid
from app.repositories import (
    OutboxRepository,
    SessionRepository,
    UserRepository,
    VerificationCodeRepository,
)
from app.services.errors import (
    CODE_EXPIRED,
    INVALID_CODE,
    TOO_MANY_ATTEMPTS,
    VALIDATION_ERROR,
    ApiError,
)
from app.services.identifier import InvalidIdentifier, normalize_identifier
from app.services.notifications import send_verification_code

CODE_VALIDITY = timedelta(minutes=10)
MAX_FAILED_ATTEMPTS = 5

# Exactament 6 xifres 0-9 (re.ASCII: sense ell, `\d` accepta xifres d'altres alfabets).
_CODE_FORMAT = re.compile(rf"\d{{{CODE_LENGTH}}}", re.ASCII)


def issue_code(
    user: User,
    codes: VerificationCodeRepository,
    outbox: OutboxRepository,
    now: datetime | None = None,
) -> str:
    """Genera un codi nou per a l'usuari, n'invalida l'anterior i l'«envia» a la bústia.

    `secrets` i no `random`: el codi és una credencial. `randbelow` dona de 0 a
    999999 i es completa amb zeros a l'esquerra (`"048213"`).
    """
    now = now or now_madrid()
    code = f"{secrets.randbelow(10**CODE_LENGTH):0{CODE_LENGTH}d}"
    codes.replace(user.id, code, now)
    send_verification_code(user, code, now, outbox)
    return code


def verify(
    raw_identifier: str,
    code: str,
    users: UserRepository,
    codes: VerificationCodeRepository,
    sessions: SessionRepository,
    now: datetime | None = None,
) -> str:
    """Comprova el codi, activa el compte i obre una sessió. Retorna el token.

    Ordre (§8.6), s'atura al primer error:
      1. Format: identificador no vàlid o codi que no són 6 xifres → VALIDATION_ERROR.
      2. Cap compte pendent amb aquest identificador → INVALID_CODE (no compta).
      3. Codi bloquejat per 5 errors → TOO_MANY_ATTEMPTS, encara que ara sigui correcte.
      4. Codi caducat → CODE_EXPIRED (no compta).
      5. Codi incorrecte → suma un intent: al 5è, TOO_MANY_ATTEMPTS; si no, INVALID_CODE.
    """
    now = now or now_madrid()
    try:
        identifier = normalize_identifier(raw_identifier).value
    except InvalidIdentifier:
        raise ApiError(VALIDATION_ERROR) from None
    if not _CODE_FORMAT.fullmatch(code):
        raise ApiError(VALIDATION_ERROR)

    user = users.find_by_identifier(identifier)
    current = codes.get(user.id) if user and user.status == STATUS_PENDING else None
    if current is None:
        # No es diu si el compte no existeix o ja està actiu (§8.6, pas 2).
        raise ApiError(INVALID_CODE)

    if current.failed_attempts >= MAX_FAILED_ATTEMPTS:
        raise ApiError(TOO_MANY_ATTEMPTS)
    if now - current.created_at >= CODE_VALIDITY:
        raise ApiError(CODE_EXPIRED)
    # compare_digest: triga el mateix encara que el codi sigui incorrecte.
    if not secrets.compare_digest(code, current.code):
        failed = codes.record_failure(user.id)
        raise ApiError(TOO_MANY_ATTEMPTS if failed >= MAX_FAILED_ATTEMPTS else INVALID_CODE)

    users.set_status(user.id, STATUS_ACTIVE)
    codes.delete(user.id)
    return sessions.create(user.id, now).token


def resend(
    raw_identifier: str,
    users: UserRepository,
    codes: VerificationCodeRepository,
    outbox: OutboxRepository,
    now: datetime | None = None,
) -> None:
    """«Envia'm un codi nou» (§8.7).

    Identificador mal format → VALIDATION_ERROR. Si no hi ha cap compte pendent
    amb aquest identificador, no es fa res i la resposta és la mateixa, perquè
    no es pugui saber quins comptes existeixen.
    """
    try:
        identifier = normalize_identifier(raw_identifier).value
    except InvalidIdentifier:
        raise ApiError(VALIDATION_ERROR) from None
    user = users.find_by_identifier(identifier)
    if user is not None and user.status == STATUS_PENDING:
        issue_code(user, codes, outbox, now)
