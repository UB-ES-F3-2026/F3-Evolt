"""Models interns del backend (T07.3).

Són classes de dades pures: no saben res de FastAPI ni de JSON.
La conversió a la forma de l'API (camelCase, sense `kind` ni `seq`) es fa als routers.
"""

from app.models.account import Account
from app.models.clock import MADRID_TZ, now_madrid
from app.models.currency import (
    CURRENCIES,
    MAIN_CURRENCY,
    MAIN_SUBACCOUNT_ID,
    Currency,
    commission,
    convert,
    rate_bps,
    reaches_one_unit,
    total_in_euros,
)
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
    MovementFilters,
)
from app.models.movement_report import MAX_REPORT_DESCRIPTION, MovementReport
from app.models.outbox import (
    CHANNEL_EMAIL,
    CHANNEL_SMS,
    MESSAGE_ACCOUNT_LOCKED,
    MESSAGE_PASSWORD_RESET,
    MESSAGE_VERIFICATION_CODE,
    OutboxMessage,
)
from app.models.password_reset import PasswordResetToken
from app.models.pot import (
    DEFAULT_POT_COLOR,
    POT_COLORS,
    POT_CONTRIBUTION_CONCEPT,
    POT_INITIAL_CONCEPT,
    Pot,
    PotMovement,
)
from app.models.session import Session
from app.models.subaccount import Subaccount, SubaccountMovement
from app.models.text import fold_text
from app.models.user import (
    IDENTIFIER_EMAIL,
    IDENTIFIER_PHONE,
    IDENTIFIER_TYPES,
    STATUS_ACTIVE,
    STATUS_PENDING,
    USER_STATUSES,
    USERNAME_FALLBACK_PREFIX,
    USERNAME_PATTERN,
    User,
)
from app.models.verification import CODE_LENGTH, VerificationCode

__all__ = [
    "Account",
    "Currency",
    "CURRENCIES",
    "MAIN_CURRENCY",
    "MAIN_SUBACCOUNT_ID",
    "Subaccount",
    "SubaccountMovement",
    "commission",
    "convert",
    "rate_bps",
    "reaches_one_unit",
    "total_in_euros",
    "Movement",
    "MovementFilters",
    "MovementReport",
    "Pot",
    "OutboxMessage",
    "PasswordResetToken",
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
    "USERNAME_FALLBACK_PREFIX",
    "USERNAME_PATTERN",
    "KINDS",
    "KIND_OTHER",
    "KIND_TOPUP",
    "MADRID_TZ",
    "MAX_REPORT_DESCRIPTION",
    "MOVEMENT_STATUS_COMPLETED",
    "MOVEMENT_STATUS_PENDING",
    "MOVEMENT_STATUSES",
    "POT_COLORS",
    "POT_CONTRIBUTION_CONCEPT",
    "POT_INITIAL_CONCEPT",
    "SAVINGS_ICON",
    "TOPUP_CONCEPT",
    "TOPUP_ICON",
    "fold_text",
    "now_madrid",
    "TYPES",
    "TYPE_EXPENSE",
    "TYPE_INCOME",
]
