"""Missatges a la bústia simulada (docs/api.md §8.12).

L'únic lloc que decideix el canal (email o SMS) i el text de cada missatge.
El codi de verificació (T02.1) l'envia d'aquí; l'avís de bloqueig (T03.2) i
l'enllaç de recuperació (T04.1) s'hi afegiran.
"""

from datetime import datetime

from app.models import (
    CHANNEL_EMAIL,
    CHANNEL_SMS,
    IDENTIFIER_EMAIL,
    MESSAGE_ACCOUNT_LOCKED,
    MESSAGE_PASSWORD_RESET,
    MESSAGE_VERIFICATION_CODE,
    OutboxMessage,
    User,
)
from app.repositories import OutboxRepository
from app.services.errors import VALIDATION_ERROR, ApiError
from app.services.identifier import InvalidIdentifier, normalize_identifier


def _channel(user: User) -> str:
    """Un email rep un email; un telèfon, un SMS (§8.3)."""
    return CHANNEL_EMAIL if user.identifier_type == IDENTIFIER_EMAIL else CHANNEL_SMS


def send_verification_code(user: User, code: str, now: datetime, outbox: OutboxRepository) -> None:
    outbox.add(
        OutboxMessage(
            to=user.identifier,
            channel=_channel(user),
            type=MESSAGE_VERIFICATION_CODE,
            text=f"El teu codi d'Evolt és {code}. Caduca en 10 minuts.",
            date=now,
            code=code,
        )
    )


def send_account_locked(user: User, now: datetime, outbox: OutboxRepository) -> None:
    """Avís de bloqueig després de 5 errors de login seguits (US-03, T03.2)."""
    outbox.add(
        OutboxMessage(
            to=user.identifier,
            channel=_channel(user),
            type=MESSAGE_ACCOUNT_LOCKED,
            text=(
                "Hem bloquejat el teu compte d'Evolt durant 15 minuts després de 5 intents "
                "fallits. Si no has estat tu, canvia la contrasenya."
            ),
            date=now,
        )
    )


def send_password_reset(user: User, link: str, now: datetime, outbox: OutboxRepository) -> None:
    """Enllaç «He oblidat la contrasenya» (US-04, T04.1). Caduca en 30 minuts."""
    outbox.add(
        OutboxMessage(
            to=user.identifier,
            channel=_channel(user),
            type=MESSAGE_PASSWORD_RESET,
            text=f"Per canviar la contrasenya d'Evolt, obre aquest enllaç. Caduca en 30 minuts: {link}",
            date=now,
            link=link,
        )
    )


def messages_for(raw_to: str | None, outbox: OutboxRepository) -> list[OutboxMessage]:
    """Missatges de la bústia; amb `raw_to`, es normalitza com al registre (§8.12).

    Un destinatari mal format → VALIDATION_ERROR, com a la resta de rutes d'accés.
    """
    if raw_to is None:
        return outbox.list()
    try:
        to = normalize_identifier(raw_to).value
    except InvalidIdentifier:
        raise ApiError(VALIDATION_ERROR) from None
    return outbox.list(to)
