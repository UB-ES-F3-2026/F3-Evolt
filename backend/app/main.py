"""Composició de l'API (T07.2).

Arrel de composició: cableja el router de salut, el CORS i els handlers que
converteixen qualsevol error a la forma del contracte `{ code, message,
details? }` (docs/api.md §5). **No conté regles de negoci**: les regles viuen
als serveis, i aquest mòdul només decideix com es transformen els errors.
"""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.data.seed import build_seed
from app.routers import health, home, movements, topups
from app.services.errors import (
    ERROR_MESSAGES,
    ERROR_STATUS,
    INTERNAL_ERROR,
    VALIDATION_ERROR,
    ApiError,
)

logger = logging.getLogger("evolt")

# Origen del Vite dev server: casa amb el BASE_URL per defecte de l'apiClient
# del frontend (localhost:8000 ↔ localhost:5173).
FRONTEND_ORIGIN = "http://localhost:5173"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Es reconstrueix a cada arrencada: així cada `with TestClient(...)` rep un
    # seed net i els tests no depenen de l'ordre en què s'executen.
    app.state.seed = build_seed()
    yield


def _error_body(
    code: str,
    message: str,
    details: dict[str, object] | None,
) -> dict[str, object]:
    # P6 (docs/api.md §5): la clau `details` mai no apareix buida ni null.
    body: dict[str, object] = {"code": code, "message": message}
    if details:
        body["details"] = details
    return body


class ContractExceptionMiddleware(BaseHTTPMiddleware):
    """Converteix excepcions inesperades en INTERNAL_ERROR dins del CORS.

    Els handlers registrats amb ``@app.exception_handler`` viuen a
    ``ExceptionMiddleware``, que queda per fora de ``CORSMiddleware``; per això
    una 500 no portava ``Access-Control-Allow-Origin``. Aquest middleware
    captura l'excepció *abans* que surti i deixa que el CORS (extern) hi
    afegeixi la capçalera. Els errors de contracte coneguts es re-llancen
    perquè els tractin els handlers habituals.
    """

    async def dispatch(self, request, call_next):
        try:
            return await call_next(request)
        except (ApiError, RequestValidationError, StarletteHTTPException):
            raise
        except Exception:  # noqa: BLE001
            logger.exception(
                "Error inesperat a %s %s", request.method, request.url.path
            )
            return JSONResponse(
                status_code=ERROR_STATUS[INTERNAL_ERROR],
                content=_error_body(
                    INTERNAL_ERROR, ERROR_MESSAGES[INTERNAL_ERROR], None
                ),
            )


def _register_error_handlers(app: FastAPI) -> None:
    """Registra els quatre handlers del contracte (docs/api.md §5)."""

    @app.exception_handler(ApiError)
    async def handle_api_error(request: Request, exc: ApiError) -> JSONResponse:
        return JSONResponse(
            status_code=ERROR_STATUS[exc.code],
            content=_error_body(exc.code, exc.message, exc.details),
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        # El detall de quin camp ha fallat és per als logs, mai per al client:
        # el contracte no el publica en aquest error.
        logger.warning("Petició invàlida: %s", exc.errors())
        return JSONResponse(
            status_code=ERROR_STATUS[VALIDATION_ERROR],
            content=_error_body(
                VALIDATION_ERROR, ERROR_MESSAGES[VALIDATION_ERROR], None
            ),
        )

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_exception(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        # El contracte només defineix dos cubells d'estat HTTP i el frontend
        # només decideix amb `code`: 422 VALIDATION_ERROR i 500 INTERNAL_ERROR.
        # Un 422 explícit s'hi queda; qualsevol altre estat (404, 405, ...)
        # es converteix en INTERNAL_ERROR. Invariant: VALIDATION_ERROR ↔ 422,
        # INTERNAL_ERROR ↔ 500.
        if exc.status_code == 422:
            return JSONResponse(
                status_code=ERROR_STATUS[VALIDATION_ERROR],
                content=_error_body(
                    VALIDATION_ERROR, ERROR_MESSAGES[VALIDATION_ERROR], None
                ),
            )
        return JSONResponse(
            status_code=ERROR_STATUS[INTERNAL_ERROR],
            content=_error_body(
                INTERNAL_ERROR, ERROR_MESSAGES[INTERNAL_ERROR], None
            ),
        )

    @app.exception_handler(Exception)
    async def handle_unexpected(request: Request, exc: Exception) -> JSONResponse:
        # El traceback i el text de l'excepció només van als logs del servidor:
        # el client rep sempre el missatge segur del contracte.
        logger.exception(
            "Error inesperat a %s %s", request.method, request.url.path
        )
        return JSONResponse(
            status_code=ERROR_STATUS[INTERNAL_ERROR],
            content=_error_body(
                INTERNAL_ERROR, ERROR_MESSAGES[INTERNAL_ERROR], None
            ),
        )


def create_app() -> FastAPI:
    """Fabriquen una aplicació nova. Els tests la fan servir per afegir-hi
    rutes de proves sense tocar la instància de producció."""
    app = FastAPI(title="F3-Evolt API", lifespan=lifespan)
    # Primer l'intern (captura excepcions), després el CORS (extern): així
    # la resposta d'error surt amb Access-Control-Allow-Origin.
    app.add_middleware(ContractExceptionMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[FRONTEND_ORIGIN],
        # Mètodes i capçaleres explícits = autodocumentats contra l'apiClient
        # del frontend; sense credencials perquè a l'Sprint 0 no hi ha cookies.
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type", "X-User-Id"],
    )
    # El prefix /api es declara un sol cop aquí; els routers declaren rutes
    # relatives (docs/api.md §4).
    app.include_router(health.router, prefix="/api")
    app.include_router(home.router, prefix="/api")
    app.include_router(movements.router, prefix="/api")
    app.include_router(topups.router, prefix="/api")
    _register_error_handlers(app)
    return app


# Per a `uvicorn app.main:app --reload`.
app = create_app()
