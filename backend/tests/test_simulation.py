"""Tests de la simulació de retard i errors (T08.2).

Executar des de backend/:  python -m pytest tests/test_simulation.py
"""

import asyncio
import logging

from fastapi.testclient import TestClient

from app.config import DEFAULT_FRONTEND_ORIGIN as FRONTEND_ORIGIN
from app.main import create_app
from app.middleware import load_simulation_settings
from app.services.errors import ERROR_MESSAGES, INTERNAL_ERROR


def test_load_settings_unset_is_disabled() -> None:
    """Sense variables, la simulació és a 0 i està desactivada."""
    settings = load_simulation_settings({})

    assert settings.delay_ms == 0
    assert settings.error_rate == 0.0
    assert not settings.enabled


def test_load_settings_parses_valid_values() -> None:
    """Els valors vàlids es passen tal qual a la configuració."""
    settings = load_simulation_settings(
        {"SIMULATE_DELAY_MS": "250", "SIMULATE_ERROR_RATE": "12.5"}
    )

    assert settings.delay_ms == 250
    assert settings.error_rate == 12.5
    assert settings.enabled


def test_load_settings_malformed_disables_with_warning(caplog) -> None:
    """Un valor mal format o fora de rang es descarta amb un avís."""
    cases = [
        ({"SIMULATE_DELAY_MS": "abc"}, "SIMULATE_DELAY_MS"),
        ({"SIMULATE_DELAY_MS": "-5"}, "SIMULATE_DELAY_MS"),
        ({"SIMULATE_ERROR_RATE": "150"}, "SIMULATE_ERROR_RATE"),
    ]
    for env, var_name in cases:
        with caplog.at_level(logging.WARNING, logger="evolt"):
            settings = load_simulation_settings(env)

        assert (settings.delay_ms, settings.error_rate) == (0, 0.0)
        assert not settings.enabled
        assert any(var_name in record.message for record in caplog.records)
        caplog.clear()

    # Un valor buit és "desactivat", no un error: no ha d'avisar.
    settings = load_simulation_settings(
        {"SIMULATE_DELAY_MS": "", "SIMULATE_ERROR_RATE": ""}
    )

    assert (settings.delay_ms, settings.error_rate) == (0, 0.0)
    assert not caplog.records


def test_without_env_requests_are_normal(monkeypatch) -> None:
    """Sense variables a l'entorn, l'API es comporta com sempre."""
    monkeypatch.delenv("SIMULATE_DELAY_MS", raising=False)
    monkeypatch.delenv("SIMULATE_ERROR_RATE", raising=False)
    app = create_app()

    with TestClient(app) as client:
        response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_delay_calls_asyncio_sleep(monkeypatch) -> None:
    """El retard es demana a asyncio.sleep convertit a segons (50 ms → 0.05)."""
    calls: list[float] = []
    real_sleep = asyncio.sleep

    async def record_sleep(seconds: float) -> None:
        calls.append(seconds)
        # Cedeix el sense fer res: no volem el retard real al test, però
        # mantenir el sleep original evita trencar l'event loop del TestClient.
        await real_sleep(0)

    monkeypatch.setenv("SIMULATE_DELAY_MS", "50")
    monkeypatch.setattr("app.middleware.simulation.asyncio.sleep", record_sleep)
    app = create_app()

    with TestClient(app) as client:
        response = client.get("/api/health")

    assert response.status_code == 200
    assert calls == [0.05]


def test_error_rate_100_returns_contract_internal_error(monkeypatch) -> None:
    """Amb un 100% d'error, cada petició rep el 500 del contracte."""
    monkeypatch.setenv("SIMULATE_ERROR_RATE", "100")
    app = create_app()

    with TestClient(app) as client:
        response = client.get("/api/health")

    assert response.status_code == 500
    assert response.json() == {
        "code": INTERNAL_ERROR,
        "message": ERROR_MESSAGES[INTERNAL_ERROR],
    }
    assert "details" not in response.json()


def test_error_rate_0_never_fails(monkeypatch) -> None:
    """Amb un 0% d'error, cap petició falla."""
    monkeypatch.setenv("SIMULATE_ERROR_RATE", "0")
    app = create_app()

    with TestClient(app) as client:
        responses = [client.get("/api/health") for _ in range(5)]

    assert [r.status_code for r in responses] == [200] * 5


def test_simulated_500_keeps_cors_header(monkeypatch) -> None:
    """La 500 simulada surt per CORS: el frontend hi pot llegir el body."""
    monkeypatch.setenv("SIMULATE_ERROR_RATE", "100")
    app = create_app()

    with TestClient(app) as client:
        response = client.get("/api/health", headers={"Origin": FRONTEND_ORIGIN})

    assert response.status_code == 500
    assert response.headers["access-control-allow-origin"] == FRONTEND_ORIGIN
