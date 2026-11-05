"""Usuaris a Firestore (TR01.1). Mateixos mètodes que `repositories/user.py`.

- Col·lecció `users`, un document per usuari amb el seu id.
- Col·lecció `user_identifiers`: un document per email o telèfon, que apunta a
  l'usuari. Fa que un identificador no es pugui registrar dues vegades encara
  que arribin dos registres alhora: `create` falla si el document ja existeix.
  L'id del document és el hash de l'identificador, perquè un email pot tenir
  caràcters que Firestore no admet en un id (com `/`).
- L'id nou surt del comptador `next_user_id`.
"""

import hashlib
from datetime import datetime

from google.cloud import firestore

from app.models import USER_STATUSES, User
from app.repositories.firestore import _tx

USERS = "users"
USER_IDENTIFIERS = "user_identifiers"
USER_COUNTER = "next_user_id"


class FirestoreUserRepository:
    def __init__(self, client: firestore.Client) -> None:
        self._client = client
        self._users = client.collection(USERS)
        self._identifiers = client.collection(USER_IDENTIFIERS)

    def get(self, user_id: int) -> User | None:
        snapshot = _tx.get(self._users.document(str(user_id)))
        return user_from_dict(snapshot.to_dict()) if snapshot.exists else None

    def find_by_identifier(self, identifier: str) -> User | None:
        """Identificador **ja normalitzat**, com al repositori de memòria."""
        index = _tx.get(self._identifiers.document(identifier_key(identifier)))
        if not index.exists:
            return None
        return self.get(index.to_dict()["user_id"])

    def add(
        self,
        *,
        name: str,
        identifier: str,
        identifier_type: str,
        password_hash: str,
        status: str,
    ) -> User:
        user = User(
            id=0,  # provisional: el model valida els camps abans de gastar cap id
            name=name,
            identifier=identifier,
            identifier_type=identifier_type,
            password_hash=password_hash,
            status=status,
        )
        user.id = _tx.allocate(self._client, USER_COUNTER)
        _tx.create(self._identifiers.document(identifier_key(identifier)), {"user_id": user.id})
        _tx.create(self._users.document(str(user.id)), user_to_dict(user))
        return user

    def set_status(self, user_id: int, status: str) -> None:
        if status not in USER_STATUSES:
            raise ValueError(f"status desconegut: {status!r}")
        _tx.update(self._users.document(str(user_id)), {"status": status})

    def set_login_state(self, user_id: int, *, failed_logins: int, locked_until: datetime | None) -> None:
        _tx.update(
            self._users.document(str(user_id)),
            {"failed_logins": failed_logins, "locked_until": locked_until},
        )

    def set_password_hash(self, user_id: int, password_hash: str) -> None:
        if not password_hash:
            raise ValueError("password_hash no pot ser buit")
        _tx.update(self._users.document(str(user_id)), {"password_hash": password_hash})


def identifier_key(identifier: str) -> str:
    return hashlib.sha256(identifier.encode("utf-8")).hexdigest()


def user_to_dict(user: User) -> dict:
    return {
        "id": user.id,
        "name": user.name,
        "identifier": user.identifier,
        "identifier_type": user.identifier_type,
        "password_hash": user.password_hash,
        "status": user.status,
        "xp": user.xp,
        "failed_logins": user.failed_logins,
        "locked_until": user.locked_until,
    }


def user_from_dict(data: dict) -> User:
    return User(
        id=data["id"],
        name=data["name"],
        identifier=data["identifier"],
        identifier_type=data["identifier_type"],
        password_hash=data["password_hash"],
        status=data["status"],
        xp=data.get("xp", 0),
        failed_logins=data.get("failed_logins", 0),
        locked_until=_tx.to_madrid(data.get("locked_until")),
    )
