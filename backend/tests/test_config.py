"""Tests de la configuració de desplegament (TR06.1).

Executar des de backend/:  python -m pytest tests/test_config.py
"""

import logging

from fastapi.testclient import TestClient

from app.config import DEFAULT_FRONTEND_ORIGIN, load_app_settings
from app.main import create_app
from app.services.errors import INTERNAL_ERROR

DEPLOYED_ORIGIN = "https://evolt.example.app"


def test_load_settings_unset_keeps_local_defaults() -> None:
    """Sense variables, el backend accepta Vite i exposa /api/dev."""
    settings = load_app_settings({})

    assert settings.frontend_origins == (DEFAULT_FRONTEND_ORIGIN,)
    assert settings.dev_routes_enabled


def test_load_settings_parses_origin_list() -> None:
    """La llista separada per comes es neteja d'espais i barres finals."""
    settings = load_app_settings(
        {"FRONTEND_ORIGINS": f" {DEPLOYED_ORIGIN}/ , {DEFAULT_FRONTEND_ORIGIN}"}
    )

    assert settings.frontend_origins == (DEPLOYED_ORIGIN, DEFAULT_FRONTEND_ORIGIN)


def test_load_settings_invalid_origins_fall_back_with_warning(caplog) -> None:
    """Un origen sense esquema s'ignora; si no en queda cap, es fa servir Vite."""
    with caplog.at_level(logging.WARNING, logger="evolt"):
        settings = load_app_settings({"FRONTEND_ORIGINS": "evolt.example.app"})

    assert settings.frontend_origins == (DEFAULT_FRONTEND_ORIGIN,)
    assert "FRONTEND_ORIGINS" in caplog.text


def test_load_settings_dev_routes_values() -> None:
    """ENABLE_DEV_ROUTES accepta true/1/yes i false/0/no sense distingir majúscules."""
    for raw in ("true", "1", "YES"):
        assert load_app_settings({"ENABLE_DEV_ROUTES": raw}).dev_routes_enabled
    for raw in ("false", "0", "No"):
        assert not load_app_settings({"ENABLE_DEV_ROUTES": raw}).dev_routes_enabled


def test_load_settings_malformed_dev_routes_disables_with_warning(caplog) -> None:
    """Un valor mal escrit desactiva les rutes de desenvolupament."""
    with caplog.at_level(logging.WARNING, logger="evolt"):
        settings = load_app_settings({"ENABLE_DEV_ROUTES": "flase"})

    assert not settings.dev_routes_enabled
    assert "ENABLE_DEV_ROUTES" in caplog.text


def test_configured_origin_is_allowed_by_cors(monkeypatch) -> None:
    """L'origen desplegat rep CORS; el de Vite ja no, si no és a la llista."""
    monkeypatch.setenv("FRONTEND_ORIGINS", DEPLOYED_ORIGIN)
    app = create_app()

    with TestClient(app) as client:
        deployed = client.get("/api/health", headers={"Origin": DEPLOYED_ORIGIN})
        local = client.get("/api/health", headers={"Origin": DEFAULT_FRONTEND_ORIGIN})

    assert deployed.headers["access-control-allow-origin"] == DEPLOYED_ORIGIN
    assert "access-control-allow-origin" not in local.headers


def test_dev_routes_disabled_are_not_registered(monkeypatch) -> None:
    """Amb ENABLE_DEV_ROUTES=false, /api/dev/reset no existeix.

    Com qualsevol ruta inexistent, respon 500 INTERNAL_ERROR (docs/api.md §5).
    """
    monkeypatch.setenv("ENABLE_DEV_ROUTES", "false")
    app = create_app()

    with TestClient(app) as client:
        response = client.post("/api/dev/reset")

    assert "/api/dev/reset" not in app.openapi()["paths"]
    assert response.status_code == 500
    assert response.json()["code"] == INTERNAL_ERROR
