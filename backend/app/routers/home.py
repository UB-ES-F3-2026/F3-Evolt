"""Endpoint del resum de la pantalla principal (T07.5, docs/api.md §4.1)."""

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from app.repositories import AccountRepository, MovementRepository, PotRepository
from app.routers.current_user import current_user_id
from app.routers.dependencies import account_repository, movement_repository, pot_repository
from app.routers.schemas import MovementResponse
from app.services.home_service import HomeSummary, get_home_summary

router = APIRouter(tags=["home"])


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


@router.get("/home")
def get_home(
    user_id: Annotated[int, Depends(current_user_id)],
    accounts: Annotated[AccountRepository, Depends(account_repository)],
    pots: Annotated[PotRepository, Depends(pot_repository)],
    movements: Annotated[MovementRepository, Depends(movement_repository)],
) -> HomeResponse:
    summary = get_home_summary(user_id, accounts, pots, movements)
    return HomeResponse.from_summary(summary)
