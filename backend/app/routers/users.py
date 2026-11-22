"""Endpoints de la cerca d'usuaris (US-13, docs/api.md §13.2 i §13.3)."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from app.repositories import UserRepository
from app.routers.current_user import current_user_id
from app.routers.dependencies import user_repository
from app.services.user_search import UserSummary, get_user, public_user_id, search_users

router = APIRouter(tags=["users"])


class UserSummaryResponse(BaseModel):
    """Objecte `UserSummary` del contracte (§13.1): mai email, telèfon ni dades financeres."""

    id: str
    name: str | None
    username: str

    @classmethod
    def from_summary(cls, summary: UserSummary) -> "UserSummaryResponse":
        return cls(id=public_user_id(summary.id), name=summary.name, username=summary.username)


class UserListResponse(BaseModel):
    """Cos de `GET /api/users`: `{ items }`."""

    items: list[UserSummaryResponse]


@router.get("/users")
def get_users(
    user_id: Annotated[int, Depends(current_user_id)],
    users: Annotated[UserRepository, Depends(user_repository)],
    q: Annotated[str | None, Query()] = None,
) -> UserListResponse:
    found = search_users(user_id, q, users)
    return UserListResponse(items=[UserSummaryResponse.from_summary(summary) for summary in found])


@router.get("/users/{public_id}")
def get_user_by_id(
    public_id: str,
    user_id: Annotated[int, Depends(current_user_id)],
    users: Annotated[UserRepository, Depends(user_repository)],
) -> UserSummaryResponse:
    # La sessió no canvia la resposta, però la ruta és protegida (§13).
    del user_id
    return UserSummaryResponse.from_summary(get_user(public_id, users))
