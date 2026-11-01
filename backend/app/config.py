"""Configuració de desplegament llegida de l'entorn (TR06.1).

Decideix des de quins orígens es pot cridar l'API (CORS) i si les eines de
desenvolupament (`/api/dev/*`) estan actives. Sense cap variable definida, el
backend es comporta exactament igual que en local: accepta el Vite dev server
i exposa `/api/dev/reset`. Al desplegament es fixen totes dues explícitament
(vegeu el README, secció «Deploy»).
"""

import logging
import os
from collections.abc import Mapping
from dataclasses import dataclass

logger = logging.getLogger("evolt")

# Origen del Vite dev server: casa amb el BASE_URL per defecte de l'apiClient
# del frontend (localhost:8000 ↔ localhost:5173).
DEFAULT_FRONTEND_ORIGIN = "http://localhost:5173"

_TRUE_VALUES = {"true", "1", "yes"}
_FALSE_VALUES = {"false", "0", "no"}


@dataclass(frozen=True)
class AppSettings:
    """Configuració de desplegament, ja validada.

    `frontend_origins` són els orígens que el CORS accepta;
    `dev_routes_enabled` indica si es registra el router `/api/dev`.
    """

    frontend_origins: tuple[str, ...] = (DEFAULT_FRONTEND_ORIGIN,)
    dev_routes_enabled: bool = True


def _parse_origins(raw: str) -> tuple[str, ...]:
    origins: list[str] = []
    for item in raw.split(","):
        # El navegador envia l'origen sense barra final; si es copia l'URL
        # amb barra, el CORS no casaria mai.
        origin = item.strip().rstrip("/")
        if not origin:
            continue
        if origin.startswith(("http://", "https://")):
            origins.append(origin)
        else:
            logger.warning("FRONTEND_ORIGINS: s'ignora l'origen invàlid %r", origin)
    return tuple(origins)


def _parse_dev_routes(raw: str) -> bool:
    value = raw.lower()
    if value in _TRUE_VALUES:
        return True
    if value not in _FALSE_VALUES:
        # Un valor mal escrit es tracta com a desactivat: és més segur no
        # exposar el reinici de dades que exposar-lo per error.
        logger.warning(
            "ENABLE_DEV_ROUTES invàlid (%r): les rutes /api/dev queden desactivades",
            raw,
        )
    return False


def load_app_settings(env: Mapping[str, str] | None = None) -> AppSettings:
    """Llegeix `FRONTEND_ORIGINS` i `ENABLE_DEV_ROUTES` de l'entorn.

    `FRONTEND_ORIGINS` és una llista separada per comes; si queda buida, es fa
    servir l'origen de Vite. `ENABLE_DEV_ROUTES` buida o sense definir activa
    les rutes de desenvolupament. Mai no llença.
    """
    source = os.environ if env is None else env

    origins = _parse_origins(source.get("FRONTEND_ORIGINS", ""))
    if not origins:
        origins = (DEFAULT_FRONTEND_ORIGIN,)

    dev_raw = source.get("ENABLE_DEV_ROUTES", "").strip()
    dev_routes_enabled = _parse_dev_routes(dev_raw) if dev_raw else True

    return AppSettings(frontend_origins=origins, dev_routes_enabled=dev_routes_enabled)
