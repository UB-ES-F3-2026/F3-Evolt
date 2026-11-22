"""Subcomptes en divisa a Firestore (T25.2). Mateixos mètodes que `repositories/subaccount.py`.

- Col·lecció `subaccounts`, un document per subcompte amb l'id `sub-NN`.
- El número surt del comptador `next_subaccount_number`.
- L'historial (T26.1, §12.6) va a la col·lecció `subaccount_movements`, amb ids
  `smov-NN` del comptador `next_subaccount_movement_number`. Eliminar un
  subcompte esborra el seu document, però no les entrades de l'historial.
- Dues creacions alhora van dins d'`atomic.run(...)`: totes dues transaccions
  llegeixen i escriuen el document dels comptadors, així que Firestore en fa
  repetir una, i la repetida ja veu el subcompte de l'altra.
"""

from datetime import datetime

from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

from app.data.seed import subaccount_id as make_subaccount_id
from app.data.seed import subaccount_movement_id
from app.models import Subaccount, SubaccountMovement
from app.repositories.firestore import _tx

SUBACCOUNTS = "subaccounts"
SUBACCOUNT_COUNTER = "next_subaccount_number"
SUBACCOUNT_MOVEMENTS = "subaccount_movements"
SUBACCOUNT_MOVEMENT_COUNTER = "next_subaccount_movement_number"


class FirestoreSubaccountRepository:
    def __init__(self, client: firestore.Client) -> None:
        self._client = client
        self._subaccounts = client.collection(SUBACCOUNTS)
        self._entries = client.collection(SUBACCOUNT_MOVEMENTS)

    def list_by_user(self, user_id: int) -> list[Subaccount]:
        """Per ordre de creació, com a la memòria. S'ordena aquí: com a molt n'hi ha quatre."""
        snapshots = _tx.query(self._subaccounts.where(filter=FieldFilter("user_id", "==", user_id)))
        subaccounts = [subaccount_from_dict(s.to_dict()) for s in snapshots]
        return sorted(subaccounts, key=lambda sub: sub.number)

    def get_by_user(self, user_id: int, subaccount_id: str) -> Subaccount | None:
        """None si no existeix o és d'un altre usuari, com a la memòria (§12.5)."""
        if not _tx.safe_doc_id(subaccount_id):
            return None
        snapshot = _tx.get(self._subaccounts.document(subaccount_id))
        if not snapshot.exists or snapshot.to_dict()["user_id"] != user_id:
            return None
        return subaccount_from_dict(snapshot.to_dict())

    def add(self, *, user_id: int, currency: str) -> Subaccount:
        # Es valida abans de gastar cap número del comptador, com a la memòria.
        subaccount = Subaccount(id=make_subaccount_id(0), user_id=user_id, currency=currency, balance=0, number=0)
        number = _tx.allocate(self._client, SUBACCOUNT_COUNTER)
        subaccount.id, subaccount.number = make_subaccount_id(number), number
        _tx.create(self._subaccounts.document(subaccount.id), subaccount_to_dict(subaccount))
        return subaccount

    def delete(self, subaccount_id: str) -> None:
        """Com a la memòria: només el subcompte; l'historial es queda (§12.5)."""
        _tx.delete(self._subaccounts.document(subaccount_id))

    def list_movements(self, subaccount_id: str) -> list[SubaccountMovement]:
        """De la més recent a la més antiga; amb la mateixa data, primer la creada més tard (P4)."""
        snapshots = _tx.query(self._entries.where(filter=FieldFilter("subaccount_id", "==", subaccount_id)))
        entries = [subaccount_movement_from_dict(s.id, s.to_dict()) for s in snapshots]
        return sorted(entries, key=SubaccountMovement.sort_key, reverse=True)

    def add_movement(
        self, *, subaccount_id: str, amount: int, concept: str, date: datetime, type: str
    ) -> SubaccountMovement:
        # Es valida abans de gastar cap número del comptador, com a la memòria.
        entry = SubaccountMovement(
            id=subaccount_movement_id(0),
            subaccount_id=subaccount_id,
            amount=amount,
            concept=concept,
            date=date,
            type=type,
            seq=0,
        )
        number = _tx.allocate(self._client, SUBACCOUNT_MOVEMENT_COUNTER)
        entry.id, entry.seq = subaccount_movement_id(number), number
        _tx.create(self._entries.document(entry.id), subaccount_movement_to_dict(entry))
        return entry


def subaccount_to_dict(subaccount: Subaccount) -> dict:
    return {
        "id": subaccount.id,
        "number": subaccount.number,
        "user_id": subaccount.user_id,
        "currency": subaccount.currency,
        "balance": subaccount.balance,
    }


def subaccount_from_dict(data: dict) -> Subaccount:
    return Subaccount(
        id=data["id"],
        user_id=data["user_id"],
        currency=data["currency"],
        balance=data["balance"],
        number=data["number"],
    )


def subaccount_movement_to_dict(entry: SubaccountMovement) -> dict:
    return {
        "subaccount_id": entry.subaccount_id,
        "amount": entry.amount,
        "concept": entry.concept,
        "date": entry.date,
        "type": entry.type,
        "seq": entry.seq,
    }


def subaccount_movement_from_dict(entry_id: str, data: dict) -> SubaccountMovement:
    return SubaccountMovement(
        id=entry_id,
        subaccount_id=data["subaccount_id"],
        amount=data["amount"],
        concept=data["concept"],
        date=_tx.to_madrid(data["date"]),
        type=data["type"],
        seq=data["seq"],
    )
