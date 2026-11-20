"""Tests de T14.2: avisos d'enviament a la bústia simulada (US-14, docs/api.md §13.7, P73).

Prova EN-05 de docs/proves-pagaments.md, amb el text, el canal i les claus de cada
avís. Que l'enviament (T14.1) els escrigui dins de la mateixa operació tot o res
es prova amb `POST /api/transfers` (EN-05 i EN-26), quan hi sigui.

Executar des de backend/:  python -m pytest tests/test_transfer_notices.py
"""

from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from app.data.seed import (
    DEMO_IDENTIFIER,
    DEMO_USER_ID,
    EMPTY_IDENTIFIER,
    EMPTY_USER_ID,
    SeedData,
    build_seed,
)
from app.models import (
    CHANNEL_EMAIL,
    CHANNEL_SMS,
    IDENTIFIER_PHONE,
    MADRID_TZ,
    MESSAGE_TRANSFER_RECEIVED,
    MESSAGE_TRANSFER_SENT,
    User,
)
from app.repositories import OutboxRepository
from app.services.money_format import format_euros
from app.services.notifications import send_transfer_received, send_transfer_sent

T0 = datetime(2026, 11, 3, 10, 0, tzinfo=MADRID_TZ)


@pytest.fixture
def seed() -> SeedData:
    return build_seed(now=T0)


def _send_example(seed: SeedData, concept: str | None = "El sopar de divendres") -> OutboxRepository:
    """L'exemple de §13.4: l'usuari 1 envia 20,00 € a l'usuari 2."""
    outbox = OutboxRepository(seed)
    sender, recipient = seed.users[DEMO_USER_ID], seed.users[EMPTY_USER_ID]
    send_transfer_sent(sender, "Usuari nou", 2000, T0, outbox)
    send_transfer_received(recipient, "Usuari demo", 2000, concept, T0, outbox)
    return outbox


# --- Text i destinatari (EN-05) -----------------------------------------------------


def test_en05_the_sender_gets_has_enviat(seed: SeedData) -> None:
    [message] = _send_example(seed).list(DEMO_IDENTIFIER)

    assert message.type == MESSAGE_TRANSFER_SENT
    assert message.text == "Has enviat 20,00 € a Usuari nou."
    assert message.channel == CHANNEL_EMAIL
    assert message.date == T0


def test_en05_the_recipient_gets_t_ha_enviat_with_the_concept(seed: SeedData) -> None:
    [message] = _send_example(seed).list(EMPTY_IDENTIFIER)

    assert message.type == MESSAGE_TRANSFER_RECEIVED
    assert message.text == "Usuari demo t'ha enviat 20,00 €: El sopar de divendres."
    assert message.channel == CHANNEL_EMAIL


@pytest.mark.parametrize("concept", [None, ""])
def test_without_concept_the_text_ends_at_the_amount(seed: SeedData, concept: str | None) -> None:
    [message] = _send_example(seed, concept=concept).list(EMPTY_IDENTIFIER)

    assert message.text == "Usuari demo t'ha enviat 20,00 €."


def test_notices_carry_no_code_or_link(seed: SeedData) -> None:
    for message in _send_example(seed).list():
        assert message.code is None
        assert message.link is None


def test_a_phone_user_gets_the_notice_by_sms(seed: SeedData) -> None:
    # §13.7: el canal surt de l'identificador, com la resta de missatges (§8.12).
    phone_user = User(id=9, name="", identifier="+34611223302", identifier_type=IDENTIFIER_PHONE, password_hash="h")
    outbox = OutboxRepository(seed)

    send_transfer_received(phone_user, "Usuari demo", 2000, None, T0, outbox)

    [message] = outbox.list("+34611223302")
    assert message.channel == CHANNEL_SMS


def test_the_names_are_written_as_given(seed: SeedData) -> None:
    # El servei de l'enviament passa el nom visible: el `name` o, si no en té, `@username`.
    outbox = OutboxRepository(seed)

    send_transfer_sent(seed.users[DEMO_USER_ID], "@buit", 100000, T0, outbox)

    [message] = outbox.list(DEMO_IDENTIFIER)
    assert message.text == "Has enviat 1.000,00 € a @buit."


# --- Format de l'import ---------------------------------------------------------------


@pytest.mark.parametrize(
    ("cents", "text"),
    [
        (2000, "20,00 €"),
        (1, "0,01 €"),
        (98000, "980,00 €"),
        (100000, "1.000,00 €"),
        (377521, "3.775,21 €"),
        (123456789, "1.234.567,89 €"),
    ],
)
def test_amounts_use_the_screen_format(cents: int, text: str) -> None:
    assert format_euros(cents) == text


# --- Per l'API (§8.12) ---------------------------------------------------------------


@pytest.fixture
def app_seed(client: TestClient) -> SeedData:
    """Seed de l'app amb el rellotge a T0. Els repositoris el llegeixen a cada petició."""
    fixed = build_seed(now=T0)
    client.app.state.seed = fixed
    return fixed


@pytest.mark.memory_only
def test_en05_the_outbox_route_returns_both_notices(client: TestClient, app_seed: SeedData) -> None:
    _send_example(app_seed)

    sent = client.get("/api/dev/outbox", params={"to": DEMO_IDENTIFIER}).json()["messages"]
    received = client.get("/api/dev/outbox", params={"to": EMPTY_IDENTIFIER}).json()["messages"]

    assert sent == [
        {
            "to": DEMO_IDENTIFIER,
            "channel": "email",
            "type": "transfer_sent",
            "text": "Has enviat 20,00 € a Usuari nou.",
            "date": "2026-11-03T10:00:00+01:00",
        }
    ]
    assert [(m["type"], m["text"]) for m in received] == [
        ("transfer_received", "Usuari demo t'ha enviat 20,00 €: El sopar de divendres.")
    ]
