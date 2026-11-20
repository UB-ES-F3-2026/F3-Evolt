"""Missatges a la bústia simulada (docs/api.md §8.12).

L'únic lloc que decideix el canal (email o SMS) i el text de cada missatge:
el codi de verificació (T02.1), l'avís de bloqueig (T03.2), l'enllaç de
recuperació (T04.1) i els avisos d'enviament (T14.2, §13.7).
"""

from datetime import datetime

from app.models import (
    CHANNEL_EMAIL,
    CHANNEL_SMS,
    IDENTIFIER_EMAIL,
    MESSAGE_ACCOUNT_LOCKED,
    MESSAGE_PASSWORD_RESET,
    MESSAGE_TRANSFER_RECEIVED,
    MESSAGE_TRANSFER_SENT,
    MESSAGE_VERIFICATION_CODE,
    OutboxMessage,
    User,
)
from app.repositories import OutboxRepository
from app.services.errors import VALIDATION_ERROR, ApiError
from app.services.identifier import InvalidIdentifier, normalize_identifier
from app.services.money_format import format_euros


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


# Avisos d'enviament (US-14, T14.2, §13.7). Els noms arriben ja fets: són els noms
# visibles (el `name` o `@username`), els mateixos que el `counterparty` dels dos
# moviments, i els decideix el servei de l'enviament (T14.1). Els crida dins de la
# mateixa operació tot o res que mou els saldos: si l'enviament falla, no queda cap avís.


def send_transfer_sent(sender: User, recipient_name: str, amount: int, now: datetime, outbox: OutboxRepository) -> None:
    """Avís a qui envia: «Has enviat 20,00 € a Usuari nou.»"""
    outbox.add(
        OutboxMessage(
            to=sender.identifier,
            channel=_channel(sender),
            type=MESSAGE_TRANSFER_SENT,
            text=f"Has enviat {format_euros(amount)} a {recipient_name}.",
            date=now,
        )
    )


def send_transfer_received(
    recipient: User,
    sender_name: str,
    amount: int,
    concept: str | None,
    now: datetime,
    outbox: OutboxRepository,
) -> None:
    """Avís a qui rep: «Usuari demo t'ha enviat 20,00 €: El sopar de divendres.»

    Sense concepte (`None` o buit), el text acaba a l'import: «Usuari demo t'ha enviat 20,00 €.»
    """
    text = f"{sender_name} t'ha enviat {format_euros(amount)}"
    text += f": {concept}." if concept else "."
    outbox.add(
        OutboxMessage(
            to=recipient.identifier,
            channel=_channel(recipient),
            type=MESSAGE_TRANSFER_RECEIVED,
            text=text,
            date=now,
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
