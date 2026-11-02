"""Endpoints de les guardioles (T17.2 · US-17, docs/api.md §9.2 i §9.3)."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, StrictInt, StrictStr, field_validator

from app.models import POT_COLORS, Pot
from app.repositories import PotRepository
from app.routers.current_user import current_user_id
from app.routers.dependencies import pot_repository
from app.services.pot_service import create_pot, list_pots

router = APIRouter(tags=["pots"])


class PotResponse(BaseModel):
    """Objecte `Pot` del contracte (§9.1), sense el camp intern `user_id`."""

    id: str
    name: str
    balance: int
    target: int | None
    color: str

    @classmethod
    def from_pot(cls, pot: Pot) -> "PotResponse":
        return cls(
            id=pot.id,
            name=pot.name,
            balance=pot.balance,
            target=pot.target,
            color=pot.color,
        )


class PotListResponse(BaseModel):
    """Cos de `GET /api/pots`: `{ items }`."""

    items: list[PotResponse]


class CreatePotRequest(BaseModel):
    """Cos de la petició: `{ name, target?, color? }` (§9.3).

    Tipus estrictes, com el `amount` de la recàrrega (P5): `"300"`, `300.0` o
    `300.5` a `target`, o un número a `name`, són un `422 VALIDATION_ERROR`.
    `target` i `color` poden faltar o valer `null`.
    """

    name: StrictStr
    target: StrictInt | None = None
    color: StrictStr | None = None

    @field_validator("color")
    @classmethod
    def _color_in_closed_list(cls, color: str | None) -> str | None:
        # Un color fora de la llista és un error de format (VALIDATION_ERROR), no de negoci.
        if color is not None and color not in POT_COLORS:
            raise ValueError("color fora de la llista tancada")
        return color


@router.get("/pots")
def get_pots(
    user_id: Annotated[int, Depends(current_user_id)],
    pots: Annotated[PotRepository, Depends(pot_repository)],
) -> PotListResponse:
    return PotListResponse(items=[PotResponse.from_pot(pot) for pot in list_pots(user_id, pots)])


@router.post("/pots", status_code=status.HTTP_201_CREATED)
def post_pot(
    body: CreatePotRequest,
    user_id: Annotated[int, Depends(current_user_id)],
    pots: Annotated[PotRepository, Depends(pot_repository)],
) -> PotResponse:
    pot = create_pot(user_id, body.name, body.target, body.color, pots)
    return PotResponse.from_pot(pot)
