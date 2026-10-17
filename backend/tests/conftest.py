"""Fixtures compartides dels tests de l'API (T07.2).

Executar des de backend/:  python -m pytest tests/

Les rutes `/api/probe/...` són **només de proves**: viuen aquí, mai a
l'aplicació enviada. El mòdul `app.main` exposa la instància de producció
(`app.main.app`), que es crea sense aquestes probes.
"""

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
