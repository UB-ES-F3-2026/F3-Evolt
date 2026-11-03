"""Configuració de desplegament llegida de l'entorn (TR06.1).

Decideix des de quins orígens es pot cridar l'API (CORS), si les eines de
desenvolupament (`/api/dev/*`) estan actives i si encara s'accepta la capçalera
`X-User-Id` sense sessió (T03.1, docs/api.md §8.2). Sense cap variable definida, el
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
    `dev_routes_enabled` indica si es registra el router `/api/dev`;
    `allow_x_user_id` indica si una ruta protegida sense token encara es pot
    resoldre amb `X-User-Id` (docs/api.md §8.2, transició fins a la T03.5).
    """

    frontend_origins: tuple[str, ...] = (DEFAULT_FRONTEND_ORIGIN,)
    dev_routes_enabled: bool = True
    allow_x_user_id: bool = True


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


def _parse_flag(name: str, raw: str, default: bool) -> bool:
    """Llegeix un interruptor `true`/`false`. Buit o sense definir → `default`.

    Un valor mal escrit es tracta com a desactivat: és més segur no exposar
    una eina de desenvolupament (el reinici de dades, o entrar sense sessió
    amb `X-User-Id`) que exposar-la per error.
    """
    value = raw.strip().lower()
    if not value:
        return default
    if value in _TRUE_VALUES:
        return True
    if value not in _FALSE_VALUES:
        logger.warning("%s invàlid (%r): queda desactivada", name, raw)
    return False


def load_app_settings(env: Mapping[str, str] | None = None) -> AppSettings:
    """Llegeix `FRONTEND_ORIGINS`, `ENABLE_DEV_ROUTES` i `ALLOW_X_USER_ID` de l'entorn.

    `FRONTEND_ORIGINS` és una llista separada per comes; si queda buida, es fa
    servir l'origen de Vite. `ENABLE_DEV_ROUTES` i `ALLOW_X_USER_ID` buides o
    sense definir queden activades (la segona, fins a la T03.5). Mai no llença.
    """
    source = os.environ if env is None else env

    origins = _parse_origins(source.get("FRONTEND_ORIGINS", ""))
    if not origins:
        origins = (DEFAULT_FRONTEND_ORIGIN,)

    dev_routes_enabled = _parse_flag("ENABLE_DEV_ROUTES", source.get("ENABLE_DEV_ROUTES", ""), True)
    allow_x_user_id = _parse_flag("ALLOW_X_USER_ID", source.get("ALLOW_X_USER_ID", ""), True)

    return AppSettings(
        frontend_origins=origins,
        dev_routes_enabled=dev_routes_enabled,
        allow_x_user_id=allow_x_user_id,
    )
