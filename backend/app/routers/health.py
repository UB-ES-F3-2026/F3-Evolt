"""Endpoint de salut del backend (T07.2)."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    """L'èxit ha de ser JSON: un cos buit el tractaria el frontend com a
    INTERNAL_ERROR. No fa servir la capçalera X-User-Id: la prova de vida ha
    de funcionar també amb una capçalera incorrecta."""
    return {"status": "ok"}
