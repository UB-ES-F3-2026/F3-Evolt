"""Formes JSON del contracte compartides entre routers (docs/api.md §3).

`MovementResponse` és el mateix objecte a `GET /api/home`, `GET /api/movements` i
`POST /api/topups`: viu aquí una sola vegada perquè els tres routers l'importin.
"""

from pydantic import BaseModel

from app.models import Movement


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
