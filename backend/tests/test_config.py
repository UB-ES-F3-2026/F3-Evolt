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


# --- ALLOW_X_USER_ID (T03.1, docs/api.md §8.2) ------------------------------------------


def test_x_user_id_is_disabled_by_default() -> None:
    # Des de la T03.5 (§8.2) el frontend només envia el token: la porta queda tancada
    # si la variable no hi és o és buida.
    assert not load_app_settings({}).allow_x_user_id
    assert not load_app_settings({"ALLOW_X_USER_ID": "  "}).allow_x_user_id


def test_load_settings_allow_x_user_id_values() -> None:
    for raw in ("true", "1", "YES"):
        assert load_app_settings({"ALLOW_X_USER_ID": raw}).allow_x_user_id
    for raw in ("false", "0", "No"):
        assert not load_app_settings({"ALLOW_X_USER_ID": raw}).allow_x_user_id


def test_load_settings_malformed_allow_x_user_id_disables_with_warning(caplog) -> None:
    """Un valor mal escrit tanca la porta: sense token, cap ruta protegida."""
    with caplog.at_level(logging.WARNING, logger="evolt"):
        settings = load_app_settings({"ALLOW_X_USER_ID": "ture"})

    assert not settings.allow_x_user_id
    assert "ALLOW_X_USER_ID" in caplog.text


# --- Bústia simulada (T02.1, docs/api.md §8.12, P46) ------------------------------------


def test_outbox_follows_dev_routes_when_not_set() -> None:
    assert load_app_settings({}).dev_outbox_enabled
    assert not load_app_settings({"ENABLE_DEV_ROUTES": "false"}).dev_outbox_enabled


def test_outbox_can_be_enabled_on_deploy_with_a_key() -> None:
    settings = load_app_settings(
        {"ENABLE_DEV_ROUTES": "false", "ENABLE_DEV_OUTBOX": "true", "DEV_OUTBOX_KEY": " secreta "}
    )

    assert settings.dev_outbox_enabled
    assert settings.dev_outbox_key == "secreta"


def test_outbox_without_key_on_deploy_stays_closed_with_warning(caplog) -> None:
    with caplog.at_level(logging.WARNING, logger="evolt"):
        settings = load_app_settings({"ENABLE_DEV_ROUTES": "false", "ENABLE_DEV_OUTBOX": "true"})

    assert not settings.dev_outbox_enabled
    assert "DEV_OUTBOX_KEY" in caplog.text


def test_outbox_can_be_disabled_locally() -> None:
    assert not load_app_settings({"ENABLE_DEV_OUTBOX": "false"}).dev_outbox_enabled


def test_empty_key_means_no_key() -> None:
    assert load_app_settings({"DEV_OUTBOX_KEY": "   "}).dev_outbox_key is None


def test_key_is_never_logged(caplog) -> None:
    with caplog.at_level(logging.DEBUG, logger="evolt"):
        load_app_settings({"ENABLE_DEV_ROUTES": "nope", "DEV_OUTBOX_KEY": "molt-secreta"})

    assert "molt-secreta" not in caplog.text


def test_frontend_url_defaults_to_vite() -> None:
    # T04.1 (§8.10): base de l'enllaç de recuperació.
    assert load_app_settings({}).frontend_url == DEFAULT_FRONTEND_ORIGIN


def test_frontend_url_drops_the_trailing_slash() -> None:
    settings = load_app_settings({"FRONTEND_URL": " https://f3-evolt.onrender.com/ "})
    assert settings.frontend_url == "https://f3-evolt.onrender.com"


def test_invalid_frontend_url_falls_back_to_vite(caplog) -> None:
    with caplog.at_level(logging.WARNING, logger="evolt"):
        settings = load_app_settings({"FRONTEND_URL": "f3-evolt.onrender.com"})

    assert settings.frontend_url == DEFAULT_FRONTEND_ORIGIN
    assert "FRONTEND_URL" in caplog.text


def test_dev_routes_never_exist_with_real_firestore(caplog) -> None:
    # Revisió de la #137: /api/dev/reset esborraria totes les col·leccions.
    assert not load_app_settings({"STORAGE": "firestore"}).dev_routes_enabled
    with caplog.at_level(logging.WARNING, logger="evolt"):
        assert not load_app_settings({"STORAGE": "firestore", "ENABLE_DEV_ROUTES": "true"}).dev_routes_enabled
    assert "ENABLE_DEV_ROUTES" in caplog.text


def test_dev_routes_work_with_the_firestore_emulator() -> None:
    settings = load_app_settings({"STORAGE": "firestore", "FIRESTORE_EMULATOR_HOST": "127.0.0.1:8080"})
    assert settings.dev_routes_enabled
    assert load_app_settings({}).dev_routes_enabled
