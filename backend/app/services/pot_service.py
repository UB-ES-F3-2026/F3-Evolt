"""Guardioles: llistar i crear (T17.2 · US-17, docs/api.md §9.2 i §9.3).

Ordre de les validacions en crear (s'aturen al primer error):
  1. Format del cos (`name` string, `target` enter estricte o null, `color` de la
     llista tancada) → el router, VALIDATION_ERROR.
  2. Nom buit o només amb espais → aquí, INVALID_POT_NAME.
  3. `target ≤ 0` → aquí, INVALID_TARGET.
Tot o res: primer es valida tot i només al final s'escriu.
"""

from app.models import DEFAULT_POT_COLOR, Pot
from app.repositories import PotRepository
from app.services.errors import INVALID_POT_NAME, INVALID_TARGET, ApiError


def list_pots(user_id: int, pots: PotRepository) -> list[Pot]:
    """Guardioles de l'usuari, de la més antiga a la més nova (§9.2).

    Un usuari sense guardioles rep `[]`: és l'estat buit de US-17 (criteri 2).
    """
    return pots.list_by_user(user_id)


def create_pot(
    user_id: int,
    name: str,
    target: int | None,
    color: str | None,
    pots: PotRepository,
) -> Pot:
    """Crea una guardiola de l'usuari amb saldo 0 (§9.3).

    El nom es desa sense els espais del principi i del final, i es pot repetir.
    Sense `target` la guardiola no té objectiu; sense `color`, és `purple`.
    """
    clean_name = name.strip()
    if not clean_name:
        raise ApiError(INVALID_POT_NAME)
    if target is not None and target <= 0:
        raise ApiError(INVALID_TARGET)

    return pots.add(
        user_id=user_id,
        name=clean_name,
        balance=0,
        target=target,
        color=color or DEFAULT_POT_COLOR,
    )
