"""Configuració de desplegament llegida de l'entorn (TR06.1).

Decideix des de quins orígens es pot cridar l'API (CORS), si les eines de
desenvolupament (`/api/dev/*`) estan actives, si encara s'accepta la capçalera
`X-User-Id` sense sessió (T03.1, docs/api.md §8.2), si la bústia simulada és
visible i amb quina clau (T02.1, §8.12, P46) i la base de l'enllaç de
recuperació de la contrasenya (T04.1, §8.10), i on es guarden les dades
(memòria o Firestore, TR01.1, §8.13). Sense cap variable definida, el
backend es comporta exactament igual que en local: accepta el Vite dev server
i exposa `/api/dev/reset`. Al desplegament es fixen totes dues explícitament
(vegeu el README, secció «Deploy»).
"""

import logging
import os
from collections.abc import Mapping
from dataclasses import dataclass

logger = logging.getLogger("evolt")

# On es guarden les dades (TR01.1, docs/api.md §8.13). Sense res definit, en memòria,
# com a l'Sprint 0: els tests i el desenvolupament local no necessiten Firebase.
STORAGE_MEMORY = "memory"
STORAGE_FIRESTORE = "firestore"
_STORAGES = {STORAGE_MEMORY, STORAGE_FIRESTORE}
# Projecte de Firebase de desenvolupament de l'equip. No és un secret: les
# credencials van a GOOGLE_APPLICATION_CREDENTIALS, mai al repositori.
DEFAULT_FIRESTORE_PROJECT_ID = "evolt-dev-67e22"

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
    resoldre amb `X-User-Id` (docs/api.md §8.2): des de la T03.5, només si
    s'activa a propòsit (eines locals i tests);
    `dev_outbox_enabled` indica si es registra `GET /api/dev/outbox`, i
    `dev_outbox_key`, si n'hi ha, és la clau que ha de portar `X-Dev-Key`;
    `frontend_url` és la base de l'enllaç de recuperació (`FRONTEND_URL`, §8.10);
    `storage` és `memory` o `firestore`, i `firestore_project_id` el projecte.
    """

    frontend_origins: tuple[str, ...] = (DEFAULT_FRONTEND_ORIGIN,)
    dev_routes_enabled: bool = True
    allow_x_user_id: bool = False
    dev_outbox_enabled: bool = True
    dev_outbox_key: str | None = None
    frontend_url: str = DEFAULT_FRONTEND_ORIGIN
    storage: str = STORAGE_MEMORY
    firestore_project_id: str = DEFAULT_FIRESTORE_PROJECT_ID


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
    servir l'origen de Vite. `ENABLE_DEV_ROUTES` buida o sense definir queda
    activada. `ALLOW_X_USER_ID` buida o sense definir queda **desactivada** des de
    la T03.5 (§8.2): si a un desplegament s'oblida la variable, cap petició sense
    token no entra com l'usuari 1. Mai no llença.
    """
    source = os.environ if env is None else env

    origins = _parse_origins(source.get("FRONTEND_ORIGINS", ""))
    if not origins:
        origins = (DEFAULT_FRONTEND_ORIGIN,)

    storage = _parse_storage(source.get("STORAGE", ""))
    project_id = source.get("FIRESTORE_PROJECT_ID", "").strip() or DEFAULT_FIRESTORE_PROJECT_ID
    dev_routes_enabled = _dev_routes_enabled(
        source.get("ENABLE_DEV_ROUTES", ""), storage, source.get("FIRESTORE_EMULATOR_HOST", "")
    )
    allow_x_user_id = _parse_flag("ALLOW_X_USER_ID", source.get("ALLOW_X_USER_ID", ""), False)
    dev_outbox_key = source.get("DEV_OUTBOX_KEY", "").strip() or None
    dev_outbox_enabled = _outbox_enabled(
        source.get("ENABLE_DEV_OUTBOX", ""), dev_routes_enabled, dev_outbox_key
    )

    return AppSettings(
        frontend_url=_parse_frontend_url(source.get("FRONTEND_URL", "")),
        frontend_origins=origins,
        dev_routes_enabled=dev_routes_enabled,
        allow_x_user_id=allow_x_user_id,
        dev_outbox_enabled=dev_outbox_enabled,
        dev_outbox_key=dev_outbox_key,
        storage=storage,
        firestore_project_id=project_id,
    )


def _parse_frontend_url(raw: str) -> str:
    """`FRONTEND_URL`: sense barra final, perquè l'enllaç no surti amb `//nova-contrasenya`.

    Buida o sense `http(s)://` → la de Vite, amb un avís si n'hi havia una de mal escrita.
    """
    url = raw.strip().rstrip("/")
    if not url:
        return DEFAULT_FRONTEND_ORIGIN
    if not url.startswith(("http://", "https://")):
        logger.warning("FRONTEND_URL invàlida (%r): es fa servir %s", raw, DEFAULT_FRONTEND_ORIGIN)
        return DEFAULT_FRONTEND_ORIGIN
    return url


def _outbox_enabled(raw: str, dev_routes_enabled: bool, key: str | None) -> bool:
    """`ENABLE_DEV_OUTBOX`: per defecte, el mateix que `ENABLE_DEV_ROUTES` (§8.12).

    Al desplegament (`ENABLE_DEV_ROUTES=false`) la bústia només s'obre amb clau:
    conté codis i enllaços de recuperació de qualsevol compte, i sense clau
    qualsevol persona podria canviar la contrasenya de l'usuari de la demo. Si
    algú l'activa allà i s'oblida la clau, queda tancada i surt un avís.
    """
    enabled = _parse_flag("ENABLE_DEV_OUTBOX", raw, dev_routes_enabled)
    if enabled and not dev_routes_enabled and key is None:
        logger.warning(
            "ENABLE_DEV_OUTBOX=true sense DEV_OUTBOX_KEY al desplegament: la bústia queda desactivada"
        )
        return False
    return enabled


def _dev_routes_enabled(raw: str, storage: str, emulator_host: str) -> bool:
    """`ENABLE_DEV_ROUTES`, però mai amb el Firestore de veritat (revisió de la #137).

    `POST /api/dev/reset` esborra totes les col·leccions. Amb Firestore només
    s'activa contra l'emulador (`FIRESTORE_EMULATOR_HOST`): així, si a un
    desplegament amb Firestore s'oblida `ENABLE_DEV_ROUTES=false`, la ruta no hi és.
    """
    enabled = _parse_flag("ENABLE_DEV_ROUTES", raw, True)
    if enabled and storage == STORAGE_FIRESTORE and not emulator_host.strip():
        if raw.strip():
            logger.warning("ENABLE_DEV_ROUTES ignorada: amb Firestore real, /api/dev/reset no existeix")
        return False
    return enabled


def _parse_storage(raw: str) -> str:
    """`STORAGE`: `memory` (per defecte) o `firestore`.

    Un valor mal escrit es queda en memòria amb un avís: l'app arrenca igual,
    però el log diu clarament que les dades no es guardaran.
    """
    value = raw.strip().lower()
    if not value:
        return STORAGE_MEMORY
    if value not in _STORAGES:
        logger.warning("STORAGE invàlid (%r): les dades es guarden en memòria", raw)
        return STORAGE_MEMORY
    return value
