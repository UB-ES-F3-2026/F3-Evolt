"""Eina de desenvolupament: reinici de dades (T09.6, docs/api.md §4.4).

L'Sprint 0 manté les dades **en memòria**: el `lifespan` de `app.main` les
construeix amb `build_seed()` a cada arrencada. Aquest endpoint replica
exactament aquesta operació sense reiniciar el servidor, perquè les seqüències
amb estat (p. ex. el límit diari de recàrrega) es puguin reproduir a demanda.

No és una regla de negoci ni toca cap servei ni repositori: és una eina de
desenvolupament (com la capçalera `X-User-Id`) i per això viu només al router.
"""

from fastapi import APIRouter, Request

from app.data.seed import build_seed

router = APIRouter(tags=["dev"])


@router.post("/dev/reset", status_code=200)
def reset_seed(request: Request) -> dict[str, str]:
    request.app.state.seed = build_seed()
    return {"status": "ok"}
