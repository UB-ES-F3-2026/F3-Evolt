"""Endpoint del resum de la pantalla principal (T07.5, docs/api.md §4.1)."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from app.models import Movement
from app.repositories import AccountRepository, MovementRepository, PotRepository
from app.routers.current_user import current_user_id
from app.services.home_service import HomeSummary, get_home_summary

router = APIRouter(tags=["home"])


class MovementResponse(BaseModel):
    """Objecte `Movement` del contracte (§3): sense els camps interns (`kind`, `seq`, `account_id`)."""

    id: str
    amount: int
    concept: str
    date: str
    type: str
    icon: str

    @classmethod
    def from_movement(cls, movement: Movement) -> "MovementResponse":
        return cls(
            id=movement.id,
            amount=movement.amount,
            concept=movement.concept,
            # isoformat() conserva el desplaçament de Madrid (+02:00 / +01:00) que demana §1.
            date=movement.date.isoformat(),
            type=movement.type,
            icon=movement.icon,
        )


class HomeResponse(BaseModel):
    """Cos de `GET /api/home`, amb les claus en camelCase (§1)."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    balance: int
    total_saved: int
    last_movements: list[MovementResponse]

    @classmethod
    def from_summary(cls, summary: HomeSummary) -> "HomeResponse":
        return cls(
            balance=summary.balance,
            total_saved=summary.total_saved,
            last_movements=[
                MovementResponse.from_movement(movement) for movement in summary.last_movements
            ],
        )


# Interí: encara no hi ha dependències compartides dels repositoris (queden
# pendents de T07.2, vegeu la revisió de la #39), així que aquest router els
# construeix sobre el seed de l'app. Quan hi siguin, aquestes tres funcions
# s'han de substituir per les compartides.
def _account_repository(request: Request) -> AccountRepository:
    return AccountRepository(request.app.state.seed)


def _pot_repository(request: Request) -> PotRepository:
    return PotRepository(request.app.state.seed)


def _movement_repository(request: Request) -> MovementRepository:
    return MovementRepository(request.app.state.seed)


@router.get("/home")
def get_home(
    user_id: Annotated[int, Depends(current_user_id)],
    accounts: Annotated[AccountRepository, Depends(_account_repository)],
    pots: Annotated[PotRepository, Depends(_pot_repository)],
    movements: Annotated[MovementRepository, Depends(_movement_repository)],
) -> HomeResponse:
    summary = get_home_summary(user_id, accounts, pots, movements)
    return HomeResponse.from_summary(summary)
