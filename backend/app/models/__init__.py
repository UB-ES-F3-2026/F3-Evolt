"""Models interns del backend (T07.3).

Són classes de dades pures: no saben res de FastAPI ni de JSON.
La conversió a la forma de l'API (camelCase, sense `kind` ni `seq`) es fa als routers.
"""

from app.models.account import Account
from app.models.clock import MADRID_TZ, now_madrid
from app.models.movement import (
    ICONS,
    KIND_OTHER,
    KIND_TOPUP,
    KINDS,
    MOVEMENT_STATUS_COMPLETED,
    MOVEMENT_STATUS_PENDING,
    MOVEMENT_STATUSES,
    SAVINGS_ICON,
    TOPUP_CONCEPT,
    TOPUP_ICON,
    TYPE_EXPENSE,
    TYPE_INCOME,
    TYPES,
    Movement,
)
from app.models.outbox import (
    CHANNEL_EMAIL,
    CHANNEL_SMS,
    MESSAGE_ACCOUNT_LOCKED,
    MESSAGE_PASSWORD_RESET,
    MESSAGE_VERIFICATION_CODE,
    OutboxMessage,
)
from app.models.pot import (
    DEFAULT_POT_COLOR,
    POT_COLORS,
    POT_CONTRIBUTION_CONCEPT,
    POT_INITIAL_CONCEPT,
    Pot,
    PotMovement,
)
from app.models.session import Session
from app.models.user import (
    IDENTIFIER_EMAIL,
    IDENTIFIER_PHONE,
    IDENTIFIER_TYPES,
    STATUS_ACTIVE,
    STATUS_PENDING,
    USER_STATUSES,
    User,
)
from app.models.verification import CODE_LENGTH, VerificationCode

__all__ = [
    "Account",
    "Movement",
    "Pot",
    "OutboxMessage",
    "PotMovement",
    "Session",
    "User",
    "DEFAULT_POT_COLOR",
    "VerificationCode",
    "CHANNEL_EMAIL",
    "CHANNEL_SMS",
    "CODE_LENGTH",
    "MESSAGE_ACCOUNT_LOCKED",
    "MESSAGE_PASSWORD_RESET",
    "MESSAGE_VERIFICATION_CODE",
    "ICONS",
    "IDENTIFIER_EMAIL",
    "IDENTIFIER_PHONE",
    "IDENTIFIER_TYPES",
    "STATUS_ACTIVE",
    "STATUS_PENDING",
    "USER_STATUSES",
    "KINDS",
    "KIND_OTHER",
    "KIND_TOPUP",
    "MADRID_TZ",
    "MOVEMENT_STATUS_COMPLETED",
    "MOVEMENT_STATUS_PENDING",
    "MOVEMENT_STATUSES",
    "POT_COLORS",
    "POT_CONTRIBUTION_CONCEPT",
    "POT_INITIAL_CONCEPT",
    "SAVINGS_ICON",
    "TOPUP_CONCEPT",
    "TOPUP_ICON",
    "now_madrid",
    "TYPES",
    "TYPE_EXPENSE",
    "TYPE_INCOME",
]
