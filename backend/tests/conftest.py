"""Fixtures compartides dels tests de l'API (T07.2).

Executar des de backend/:  python -m pytest tests/

Les rutes `/api/probe/...` són **només de proves**: viuen aquí, mai a
l'aplicació enviada. El mòdul `app.main` exposa la instància de producció
(`app.main.app`), que es crea sense aquestes probes.
"""

import os
import uuid
from collections.abc import Iterator
from typing import Annotated, NoReturn

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.main import create_app
from app.routers.current_user import current_user_id
from app.services.errors import DAILY_LIMIT_EXCEEDED, ApiError


def _add_probes(app: FastAPI) -> None:
    """Rutes de proves per arribar a la validació i als handlers d'error."""

    @app.get("/api/probe/user")
    def probe_user(user_id: Annotated[int, Depends(current_user_id)]) -> dict[str, int]:
        return {"userId": user_id}

    @app.get("/api/probe/validation")
    def probe_validation(limit: int) -> dict[str, int]:
        return {"limit": limit}

    # response_model=None: NoReturn no és un esquema vàlid i el endpoint mai
    # no arriba a respondre.
    @app.get("/api/probe/crash", response_model=None)
    def probe_crash() -> NoReturn:
        raise RuntimeError("boom intern")

    @app.get("/api/probe/api-error", response_model=None)
    def probe_api_error() -> NoReturn:
        raise ApiError(DAILY_LIMIT_EXCEEDED, details={"remainingToday": 10000})


# --- Els mateixos tests amb Firestore (TR01.1) ---------------------------------------
#
# `TEST_STORAGE=firestore` (amb FIRESTORE_EMULATOR_HOST) passa els tests de l'API per
# l'emulador. Cada test té el seu projecte de l'emulador, amb el seed net, com la
# memòria. Sense la variable (la CI i el `pytest` de sempre), les dades són en memòria.
#
# Els tests que llegeixen o canvien les dades en memòria directament no tenen sentit
# amb Firestore i se salten: els de l'API que fan servir el fixture `seed` (el posen
# a `app.state.seed`) i els marcats amb `@pytest.mark.memory_only` (llegeixen
# `app.state.seed` o apedacen un repositori de memòria).

_MEMORY_ONLY = "llegeix o canvia les dades en memòria directament"


def _firestore_run() -> bool:
    return os.environ.get("TEST_STORAGE") == "firestore"


def pytest_configure(config) -> None:
    config.addinivalue_line("markers", f"memory_only: el test {_MEMORY_ONLY} (se salta amb Firestore)")


def pytest_collection_modifyitems(config, items) -> None:
    if not _firestore_run():
        return
    for item in items:
        fixtures = getattr(item, "fixturenames", ())
        # El fixture `seed` només molesta als tests de l'API, que el posen a
        # `app.state.seed`; els tests de serveis i repositoris són de memòria igualment.
        if ("seed" in fixtures and "client" in fixtures) or item.get_closest_marker("memory_only"):
            item.add_marker(pytest.mark.skip(reason=_MEMORY_ONLY))


@pytest.fixture(autouse=True)
def _allow_x_user_id(monkeypatch) -> None:
    """Els tests de l'Sprint 0 encara fan servir `X-User-Id` (§8.2, T03.5).

    Des de la T03.5 la variable és desactivada per defecte, així que els tests
    l'activen. Els que proven el comportament sense la capçalera la tornen a
    desactivar o la treuen (`monkeypatch.setenv` / `delenv` dins del test).
    """
    monkeypatch.setenv("ALLOW_X_USER_ID", "true")


@pytest.fixture(autouse=True)
def _storage(monkeypatch) -> None:
    if _firestore_run():
        monkeypatch.setenv("STORAGE", "firestore")
        monkeypatch.setenv("FIRESTORE_PROJECT_ID", f"test-{uuid.uuid4().hex[:12]}")


@pytest.fixture
def app() -> FastAPI:
    """Aplicació fresca amb les probes de proves afegides."""
    app = create_app()
    _add_probes(app)
    return app


@pytest.fixture
def client(app: FastAPI) -> Iterator[TestClient]:
    # El `with` executa el lifespan: cada test rep un seed fresc.
    with TestClient(app) as c:
        yield c
