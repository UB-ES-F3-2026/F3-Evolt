"""Tests de T02.1: GET /api/dev/outbox, la bústia simulada (docs/api.md §8.12, P46).

Proves G-11 a G-14 de docs/proves-acces.md.

Executar des de backend/:  python -m pytest tests/test_outbox.py
"""

import pytest
from fastapi.testclient import TestClient

from app.main import create_app

KEY = "clau-de-prova"


def _register(client: TestClient, identifier: str) -> None:
    client.post(
        "/api/auth/register",
        json={"identifier": identifier, "password": "Platja2026", "acceptedTerms": True},
    )


@pytest.fixture
def make_client(monkeypatch):
    """Crea un client amb les variables d'entorn donades."""
    clients: list[TestClient] = []

    def factory(**env: str) -> TestClient:
        for name, value in env.items():
            monkeypatch.setenv(name, value)
        client = TestClient(create_app())
        client.__enter__()
        clients.append(client)
        return client

    yield factory
    for client in clients:
        client.__exit__(None, None, None)


# --- Contingut ----------------------------------------------------------------------


def test_outbox_is_empty_after_the_seed(client: TestClient) -> None:
    assert client.get("/api/dev/outbox").json() == {"messages": []}


def test_messages_have_the_contract_fields(client: TestClient) -> None:
    _register(client, "ana@x.com")

    [message] = client.get("/api/dev/outbox").json()["messages"]

    assert set(message) == {"to", "channel", "type", "text", "date", "code"}
    assert "link" not in message  # només als enllaços de recuperació (com P6)
    assert message["date"][-6:] in {"+01:00", "+02:00"}


def test_newest_first_and_filtered_by_normalized_recipient(client: TestClient) -> None:
    _register(client, "ana@x.com")
    _register(client, "pau@x.com")
    client.post("/api/auth/resend-code", json={"identifier": "ana@x.com"})

    everything = client.get("/api/dev/outbox").json()["messages"]
    ana = client.get("/api/dev/outbox", params={"to": " ANA@x.com "}).json()["messages"]

    assert [m["to"] for m in everything] == ["ana@x.com", "pau@x.com", "ana@x.com"]
    assert len(ana) == 2
    assert all(m["to"] == "ana@x.com" for m in ana)


def test_malformed_recipient_is_a_validation_error(client: TestClient) -> None:
    assert client.get("/api/dev/outbox", params={"to": "12ab"}).json()["code"] == "VALIDATION_ERROR"


def test_dev_reset_empties_the_outbox(client: TestClient) -> None:
    _register(client, "ana@x.com")

    client.post("/api/dev/reset")

    assert client.get("/api/dev/outbox").json() == {"messages": []}


# --- Disponibilitat i clau (P46) ----------------------------------------------------


def test_outbox_follows_dev_routes_by_default(make_client) -> None:
    # G-11: al desplegament, sense ENABLE_DEV_OUTBOX, ni bústia ni reinici.
    client = make_client(ENABLE_DEV_ROUTES="false")

    assert client.get("/api/dev/outbox").status_code == 500
    assert client.post("/api/dev/reset").status_code == 500


def test_outbox_can_be_enabled_alone_with_a_key(make_client) -> None:
    # G-12: la bústia sí, el reinici no.
    client = make_client(ENABLE_DEV_ROUTES="false", ENABLE_DEV_OUTBOX="true", DEV_OUTBOX_KEY=KEY)

    assert client.get("/api/dev/outbox", headers={"X-Dev-Key": KEY}).status_code == 200
    assert client.post("/api/dev/reset").status_code == 500


def test_outbox_stays_closed_on_deploy_without_a_key(make_client) -> None:
    # Revisió de la #105: si algú l'activa al desplegament i s'oblida la clau, queda tancada.
    client = make_client(ENABLE_DEV_ROUTES="false", ENABLE_DEV_OUTBOX="true")

    assert client.get("/api/dev/outbox").status_code == 500


@pytest.mark.parametrize("headers", [{}, {"X-Dev-Key": "dolenta"}, {"X-Dev-Key": ""}])
def test_wrong_or_missing_key_is_unauthenticated(make_client, headers) -> None:
    # G-13
    client = make_client(DEV_OUTBOX_KEY=KEY)

    response = client.get("/api/dev/outbox", headers=headers)

    assert response.status_code == 401
    assert response.json()["code"] == "UNAUTHENTICATED"


def test_right_key_reads_the_messages(make_client) -> None:
    # G-14
    client = make_client(DEV_OUTBOX_KEY=KEY)
    _register(client, "ana@x.com")

    response = client.get("/api/dev/outbox", headers={"X-Dev-Key": KEY})

    assert response.status_code == 200
    assert len(response.json()["messages"]) == 1


def test_local_development_needs_no_key(client: TestClient) -> None:
    assert client.get("/api/dev/outbox").status_code == 200
