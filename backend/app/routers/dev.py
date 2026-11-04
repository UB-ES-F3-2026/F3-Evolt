"""Eines de desenvolupament: reinici de dades (T09.6, docs/api.md §4.4) i bústia
simulada (T02.1, §8.12).

L'Sprint 0 manté les dades **en memòria**: el `lifespan` de `app.main` les
construeix amb `build_seed()` a cada arrencada. Aquest endpoint replica
exactament aquesta operació sense reiniciar el servidor, perquè les seqüències
amb estat (p. ex. el límit diari de recàrrega) es puguin reproduir a demanda.

No és una regla de negoci ni toca cap servei ni repositori: és una eina de
desenvolupament (com la capçalera `X-User-Id`) i per això viu només al router.
"""

import secrets
from typing import Annotated

from fastapi import APIRouter, Depends, Header, Request

from app.data.seed import build_seed
from app.models import OutboxMessage
from app.repositories import OutboxRepository
from app.routers.dependencies import outbox_repository
from app.services.errors import UNAUTHENTICATED, ApiError
from app.services.notifications import messages_for

router = APIRouter(tags=["dev"])
# Router a part: la bústia es pot activar sense el reinici (ENABLE_DEV_OUTBOX, §8.12).
outbox_router = APIRouter(tags=["dev"])


@router.post("/dev/reset", status_code=200)
def reset_seed(request: Request) -> dict[str, str]:
    request.app.state.seed = build_seed()
    return {"status": "ok"}


def require_outbox_key(
    request: Request,
    x_dev_key: Annotated[str | None, Header()] = None,
) -> None:
    """Amb `DEV_OUTBOX_KEY` definida, cal `X-Dev-Key` amb aquest valor (P46).

    `compare_digest` i no `==`: triga el mateix encara que la clau sigui
    incorrecta, i així no es pot endevinar caràcter a caràcter.
    """
    key = request.app.state.settings.dev_outbox_key
    if key is None:
        return
    if x_dev_key is None or not secrets.compare_digest(x_dev_key.encode(), key.encode()):
        raise ApiError(UNAUTHENTICATED)


def _message_json(message: OutboxMessage) -> dict[str, str]:
    """Missatge del contracte (§8.12): `code` i `link` només quan en té (com P6)."""
    body = {
        "to": message.to,
        "channel": message.channel,
        "type": message.type,
        "text": message.text,
        "date": message.date.isoformat(),
    }
    if message.code is not None:
        body["code"] = message.code
    if message.link is not None:
        body["link"] = message.link
    return body


@outbox_router.get("/dev/outbox", dependencies=[Depends(require_outbox_key)])
def read_outbox(
    outbox: Annotated[OutboxRepository, Depends(outbox_repository)],
    to: str | None = None,
) -> dict[str, list[dict[str, str]]]:
    """Missatges «enviats», del més recent al més antic. Amb `to`, només els d'aquest destinatari."""
    return {"messages": [_message_json(m) for m in messages_for(to, outbox)]}
