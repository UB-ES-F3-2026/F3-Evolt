"""Registre d'un compte nou (T01.2 · US-01, docs/api.md §8.5).

Ordre de les validacions (s'aturen al primer error):
  1. Format → VALIDATION_ERROR: els tipus del cos els comprova el router; aquí,
     `acceptedTerms` ha de ser `true`, l'identificador ha de ser vàlid i la
     contrasenya no pot passar de 72 bytes.
  2. Política de contrasenya → WEAK_PASSWORD.
  3. Identificador ja registrat, pendent o actiu → ALREADY_REGISTERED.
Tot o res: primer es valida tot i només al final s'escriu.

En acabar, l'usuari rep el codi de verificació a la bústia simulada (T02.1).
El hash es fa fora de l'`atomic` (TR01.1): només la comprovació del duplicat i
les escriptures hi van a dins.
"""

import threading
from datetime import datetime

from app.models import STATUS_PENDING, User
from app.repositories import (
    AccountRepository,
    OutboxRepository,
    UserRepository,
    VerificationCodeRepository,
)
from app.repositories.atomic import DIRECT, Atomic
from app.services.errors import (
    ALREADY_REGISTERED,
    VALIDATION_ERROR,
    WEAK_PASSWORD,
    ApiError,
)
from app.services.identifier import InvalidIdentifier, normalize_identifier
from app.services.password_hashing import hash_password
from app.services.password_policy import fits_password_hash, is_strong_password
from app.services.verification_service import issue_code

# El registre no demana nom (US-01). El camp existeix al model per a l'usuari del seed.
NEW_USER_NAME = ""

# Les rutes síncrones de FastAPI corren en un pool de fils: sense aquest pany, dos
# registres alhora amb el mateix email podrien passar tots dos la comprovació del
# duplicat i crear dos usuaris. Protegeix «comprovar el duplicat + escriure» mentre
# les dades siguin en memòria; amb Firestore (#106) ho farà una transacció.
_REGISTRATION_LOCK = threading.Lock()


def register(
    raw_identifier: str,
    password: str,
    accepted_terms: bool,
    users: UserRepository,
    accounts: AccountRepository,
    codes: VerificationCodeRepository,
    outbox: OutboxRepository,
    now: datetime | None = None,
    atomic: Atomic = DIRECT,
) -> User:
    """Crea l'usuari en estat «pendent» amb el seu compte principal a 0, i li envia el codi.

    No obre cap sessió (US-01): la sessió s'obre en verificar el codi (US-02).
    """
    if accepted_terms is not True:
        raise ApiError(VALIDATION_ERROR)
    try:
        identifier = normalize_identifier(raw_identifier)
    except InvalidIdentifier:
        raise ApiError(VALIDATION_ERROR) from None
    if not fits_password_hash(password):
        raise ApiError(VALIDATION_ERROR)

    if not is_strong_password(password):
        raise ApiError(WEAK_PASSWORD)

    if users.find_by_identifier(identifier.value) is not None:
        raise ApiError(ALREADY_REGISTERED)

    # bcrypt és lent a propòsit: el hash es fa fora del pany i de l'`atomic`, perquè
    # els registres no aturin les altres escriptures mentre es calcula.
    password_hash = hash_password(password)

    def write() -> User:
        with _REGISTRATION_LOCK:
            # Es torna a comprovar a dins: un altre registre amb el mateix email pot
            # haver acabat mentre es feia el hash.
            if users.find_by_identifier(identifier.value) is not None:
                raise ApiError(ALREADY_REGISTERED)
            # Escriptures que han d'anar juntes (a Firestore, a la mateixa
            # transacció): no ha de quedar mai un usuari sense compte o sense codi.
            user = users.add(
                name=NEW_USER_NAME,
                identifier=identifier.value,
                identifier_type=identifier.type,
                password_hash=password_hash,
                status=STATUS_PENDING,
            )
            accounts.create_for_user(user.id)
            issue_code(user, codes, outbox, now)
            return user

    return atomic.run(write)
