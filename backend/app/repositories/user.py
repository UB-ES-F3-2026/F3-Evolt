"""Repositori d'usuaris (T01.2).

Llegeix i escriu les dades en memòria del SeedData. No decideix regles de
negoci: normalitzar l'identificador, validar la contrasenya o rebutjar un
duplicat és feina del servei.
"""

from datetime import datetime

from app.data.seed import SeedData
from app.models import USER_STATUSES, User


class UserRepository:
    """Usuaris i les seves credencials (T01.2)."""

    def __init__(self, seed: SeedData) -> None:
        self._seed = seed

    def get(self, user_id: int) -> User | None:
        """Usuari amb aquest id, o None si no existeix."""
        return self._seed.users.get(user_id)

    def find_by_identifier(self, identifier: str) -> User | None:
        """Usuari amb aquest identificador **ja normalitzat**, o None.

        La comparació és exacta: qui crida ha de normalitzar abans
        (`services/identifier.py`), perquè `ANA@x.com` trobi `ana@x.com`.
        """
        return next(
            (user for user in self._seed.users.values() if user.identifier == identifier),
            None,
        )

    def add(
        self,
        *,
        name: str,
        identifier: str,
        identifier_type: str,
        password_hash: str,
        status: str,
    ) -> User:
        """Crea un usuari amb un id nou i el retorna.

        L'id surt del comptador del seed, així que no es repeteix ni després
        d'esborrar dades. Els camps els valida el model (`User.__post_init__`).
        """
        user = User(
            id=self._seed.next_user_id,
            name=name,
            identifier=identifier,
            identifier_type=identifier_type,
            password_hash=password_hash,
            status=status,
        )
        self._seed.users[user.id] = user
        self._seed.next_user_id += 1
        return user

    def set_status(self, user_id: int, status: str) -> None:
        """Canvia l'estat del compte (p. ex. `pending` → `active` en verificar, T02.1).

        L'usuari ha d'existir (KeyError) i l'estat ha de ser de la llista (ValueError).
        """
        if status not in USER_STATUSES:
            raise ValueError(f"status desconegut: {status!r}")
        self._seed.users[user_id].status = status

    def set_login_state(self, user_id: int, *, failed_logins: int, locked_until: datetime | None) -> None:
        """Desa els errors de login seguits i el bloqueig (T03.2).

        És un SET: quan sumar, bloquejar o tornar a zero ho decideix el servei.
        L'usuari ha d'existir (KeyError).
        """
        user = self._seed.users[user_id]
        user.failed_logins = failed_logins
        user.locked_until = locked_until
