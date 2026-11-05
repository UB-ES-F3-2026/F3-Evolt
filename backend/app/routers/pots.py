"""Endpoints de les guardioles (US-17 i US-18, docs/api.md §9.2 a §9.5)."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, StrictInt, StrictStr, field_validator

from app.models import POT_COLORS, Pot, PotMovement
from app.repositories import AccountRepository, MovementRepository, PotRepository
from app.repositories.atomic import Atomic
from app.routers.current_user import current_user_id
from app.routers.dependencies import account_repository, atomic, movement_repository, pot_repository
from app.routers.schemas import MovementResponse
from app.services.pot_service import (
    ContributionResult,
    contribute,
    create_pot,
    list_pot_movements,
    list_pots,
)

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


class ContributionRequest(BaseModel):
    """Cos de la petició: `{ amount }` en cèntims (§9.4).

    `StrictInt` (P5): `"30"`, `30.0`, `30.5` o `true` són un `422 VALIDATION_ERROR`.
    """

    amount: StrictInt


class ContributionResponse(BaseModel):
    """Cos de la resposta `201`: `{ balance, pot, movement }` (§9.4)."""

    balance: int
    pot: PotResponse
    movement: MovementResponse

    @classmethod
    def from_result(cls, result: ContributionResult) -> "ContributionResponse":
        return cls(
            balance=result.balance,
            pot=PotResponse.from_pot(result.pot),
            movement=MovementResponse.from_movement(result.movement),
        )


class PotMovementResponse(BaseModel):
    """Entrada de l'historial (§9.5), sense els camps interns `pot_id` i `seq`."""

    id: str
    amount: int
    concept: str
    date: str
    type: str

    @classmethod
    def from_entry(cls, entry: PotMovement) -> "PotMovementResponse":
        return cls(
            id=entry.id,
            amount=entry.amount,
            concept=entry.concept,
            # isoformat() conserva el desplaçament de Madrid (+02:00 / +01:00) que demana §1.
            date=entry.date.isoformat(),
            type=entry.type,
        )


class PotMovementListResponse(BaseModel):
    """Cos de `GET /api/pots/{potId}/movements`: `{ items }`."""

    items: list[PotMovementResponse]


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
    run: Annotated[Atomic, Depends(atomic)],
) -> PotResponse:
    # Amb Firestore, el comptador dels ids i la guardiola nova van junts (TR01.1).
    pot = run.run(lambda: create_pot(user_id, body.name, body.target, body.color, pots))
    return PotResponse.from_pot(pot)


@router.post("/pots/{pot_id}/contributions", status_code=status.HTTP_201_CREATED)
def post_contribution(
    pot_id: str,
    body: ContributionRequest,
    user_id: Annotated[int, Depends(current_user_id)],
    accounts: Annotated[AccountRepository, Depends(account_repository)],
    pots: Annotated[PotRepository, Depends(pot_repository)],
    movements: Annotated[MovementRepository, Depends(movement_repository)],
    run: Annotated[Atomic, Depends(atomic)],
) -> ContributionResponse:
    # Les quatre escriptures de l'aportació, tot o res (TR01.1).
    result = run.run(lambda: contribute(user_id, pot_id, body.amount, accounts, pots, movements))
    return ContributionResponse.from_result(result)


@router.get("/pots/{pot_id}/movements")
def get_pot_movements(
    pot_id: str,
    user_id: Annotated[int, Depends(current_user_id)],
    pots: Annotated[PotRepository, Depends(pot_repository)],
) -> PotMovementListResponse:
    entries = list_pot_movements(user_id, pot_id, pots)
    return PotMovementListResponse(items=[PotMovementResponse.from_entry(entry) for entry in entries])
