"""Dependències de FastAPI que donen els repositoris als routers.

Els repositoris treballen sobre les dades en memòria de l'app (`app.state.seed`,
creades al `lifespan` de `main.py`). Quan hi hagi base de dades, només canviarà
aquest fitxer i `repositories/`.
"""

from fastapi import Request

from app.repositories import AccountRepository, MovementRepository, PotRepository


def account_repository(request: Request) -> AccountRepository:
    return AccountRepository(request.app.state.seed)


def pot_repository(request: Request) -> PotRepository:
    return PotRepository(request.app.state.seed)


def movement_repository(request: Request) -> MovementRepository:
    return MovementRepository(request.app.state.seed)
