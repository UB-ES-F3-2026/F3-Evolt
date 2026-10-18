"""Simulació de retard i errors per provar el frontend (T08.2).

Lectura de configuració i middleware que, quan les variables d'entorn
`SIMULATE_DELAY_MS` i `SIMULATE_ERROR_RATE` tenen valor, altera **totes** les
respostes de l'API: un retard fix abans de processar i un percentatge de
respostes 500 amb el cos del contracte. Amb les variables buides o sense
definir, el backend es comporta exactament igual que abans (sense retard i
sense errors simulats).
"""

import asyncio
import logging
import os
import random
from collections.abc import Mapping
from dataclasses import dataclass

from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from app.services.errors import (
    ERROR_MESSAGES,
    ERROR_STATUS,
    INTERNAL_ERROR,
    error_body,
)

logger = logging.getLogger("evolt")


@dataclass(frozen=True)
class SimulationSettings:
    """Configuració de simulació, ja validada.

    `delay_ms` és el retard afegit a cada resposta en mil·lisegons;
    `error_rate` és el percentatge (0–100) de respostes substituïdes per un
    500 `INTERNAL_ERROR`.
    """

    delay_ms: int = 0
    error_rate: float = 0.0

    @property
    def enabled(self) -> bool:
        return self.delay_ms > 0 or self.error_rate > 0


def _parse_delay_ms(raw: str) -> int | None:
    try:
        value = int(raw)
    except ValueError:
        return None
    return value if value >= 0 else None


def _parse_error_rate(raw: str) -> float | None:
    try:
        value = float(raw)
    except ValueError:
        return None
    return value if 0.0 <= value <= 100.0 else None


def load_simulation_settings(
    env: Mapping[str, str] | None = None,
) -> SimulationSettings:
    """Llegeix `SIMULATE_DELAY_MS` i `SIMULATE_ERROR_RATE` de l'entorn.

    Un valor buit, mal format o fora de rang es descarta amb un avís i es
    fa servir 0 per a aquesta variable: la simulació és opt-in i un error de
    configuració no ha d'impedir arrencar el backend. Mai no llença.
    """
    source = os.environ if env is None else env

    delay_raw = source.get("SIMULATE_DELAY_MS", "").strip()
    delay_ms: int = 0
    if delay_raw:
        parsed_delay = _parse_delay_ms(delay_raw)
        if parsed_delay is None:
            logger.warning(
                "SIMULATE_DELAY_MS invàlid (%r): s'ignora el retard simulat",
                delay_raw,
            )
        else:
            delay_ms = parsed_delay

    rate_raw = source.get("SIMULATE_ERROR_RATE", "").strip()
    error_rate: float = 0.0
    if rate_raw:
        parsed_rate = _parse_error_rate(rate_raw)
        if parsed_rate is None:
            logger.warning(
                "SIMULATE_ERROR_RATE invàlid (%r): s'ignora l'error simulat",
                rate_raw,
            )
        else:
            error_rate = parsed_rate

    return SimulationSettings(delay_ms=delay_ms, error_rate=error_rate)


class SimulationMiddleware(BaseHTTPMiddleware):
    """Aplica el retard i els errors simulats a cada petició.

    La configuració es llegeix un sol cop a `create_app` (via
    `load_simulation_settings`) en lloc de mirar l'entorn a cada petició:
    així els tests poden fixar l'entorn *abans* de construir l'app i el cost
    per petició és zero.
    """

    def __init__(self, app: ASGIApp, settings: SimulationSettings) -> None:
        super().__init__(app)
        self._settings = settings

    async def dispatch(self, request: Request, call_next) -> Response:
        if self._settings.delay_ms:
            await asyncio.sleep(self._settings.delay_ms / 1000)

        if random.random() * 100 < self._settings.error_rate:
            # Es retorna la resposta directament (no es llença cap excepció)
            # perquè volem el cos exacte del contracte, sense que cap handler
            # ni middleware intermedi la reescriu ni hi afegeixi detalls.
            return JSONResponse(
                status_code=ERROR_STATUS[INTERNAL_ERROR],
                content=error_body(
                    INTERNAL_ERROR, ERROR_MESSAGES[INTERNAL_ERROR], None
                ),
            )

        return await call_next(request)
