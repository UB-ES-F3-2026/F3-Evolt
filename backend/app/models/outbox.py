"""Missatge de la bústia simulada (T02.1, docs/api.md §8.12).

En lloc d'enviar emails o SMS de veritat, el backend els desa aquí.
"""

from dataclasses import dataclass
from datetime import datetime

CHANNEL_EMAIL = "email"
CHANNEL_SMS = "sms"
CHANNELS = frozenset({CHANNEL_EMAIL, CHANNEL_SMS})

MESSAGE_VERIFICATION_CODE = "verification_code"
MESSAGE_ACCOUNT_LOCKED = "account_locked"  # T03.2
MESSAGE_PASSWORD_RESET = "password_reset"  # T04.1
MESSAGE_TYPES = frozenset({MESSAGE_VERIFICATION_CODE, MESSAGE_ACCOUNT_LOCKED, MESSAGE_PASSWORD_RESET})


@dataclass(frozen=True)
class OutboxMessage:
    """Un email o SMS «enviat». `code` i `link` només en tenen alguns tipus."""

    to: str
    channel: str
    type: str
    text: str
    date: datetime
    code: str | None = None
    link: str | None = None

    def __post_init__(self) -> None:
        if self.channel not in CHANNELS:
            raise ValueError(f"channel desconegut: {self.channel!r}")
        if self.type not in MESSAGE_TYPES:
            raise ValueError(f"type desconegut: {self.type!r}")
        if self.date.tzinfo is None:
            raise ValueError("date ha de portar zona horària")
