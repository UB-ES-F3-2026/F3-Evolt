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
    TOPUP_CONCEPT,
    TOPUP_ICON,
    TYPE_EXPENSE,
    TYPE_INCOME,
    TYPES,
    Movement,
)
from app.models.pot import Pot
from app.models.user import User

__all__ = [
    "Account",
    "Movement",
    "Pot",
    "User",
    "ICONS",
    "KINDS",
    "KIND_OTHER",
    "KIND_TOPUP",
    "MADRID_TZ",
    "TOPUP_CONCEPT",
    "TOPUP_ICON",
    "now_madrid",
    "TYPES",
    "TYPE_EXPENSE",
    "TYPE_INCOME",
]
