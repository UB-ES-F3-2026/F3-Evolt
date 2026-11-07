"""Guardioles a Firestore (TR01.1). Mateixos mètodes que `repositories/pot.py`.

- Col·lecció `pots`, un document per guardiola amb l'id `pot-NN`.
- Col·lecció `pot_movements`, l'historial, amb l'id `pmov-NN`.
- Els números surten dels comptadors `next_pot_number` i `next_pot_movement_number`.
"""

from datetime import datetime

from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

from app.data.seed import pot_id as make_pot_id
from app.data.seed import pot_movement_id
from app.models import Pot, PotMovement
from app.repositories.firestore import _tx

POTS = "pots"
POT_MOVEMENTS = "pot_movements"
POT_COUNTER = "next_pot_number"
POT_MOVEMENT_COUNTER = "next_pot_movement_number"


class FirestorePotRepository:
    def __init__(self, client: firestore.Client) -> None:
        self._client = client
        self._pots = client.collection(POTS)
        self._entries = client.collection(POT_MOVEMENTS)

    def list_by_user(self, user_id: int) -> list[Pot]:
        """En ordre de creació, com a la memòria. S'ordena aquí: un usuari en té poques."""
        snapshots = _tx.query(self._pots.where(filter=FieldFilter("user_id", "==", user_id)))
        ordered = sorted(snapshots, key=lambda s: s.to_dict()["number"])
        return [pot_from_dict(s.to_dict()) for s in ordered]

    def add(self, *, user_id: int, name: str, balance: int, target: int | None, color: str) -> Pot:
        pot = Pot(id=make_pot_id(0), user_id=user_id, name=name, balance=balance, target=target, color=color)
        number = _tx.allocate(self._client, POT_COUNTER)
        pot.id = make_pot_id(number)
        _tx.create(self._pots.document(pot.id), pot_to_dict(pot, number))
        return pot

    def get_by_user(self, user_id: int, pot_id: str) -> Pot | None:
        """None si no existeix o és d'un altre usuari, com a la memòria (§9.4)."""
        if not _tx.safe_doc_id(pot_id):
            return None
        snapshot = _tx.get(self._pots.document(pot_id))
        if not snapshot.exists or snapshot.to_dict()["user_id"] != user_id:
            return None
        return pot_from_dict(snapshot.to_dict())

    def set_balance(self, pot_id: str, balance_cents: int) -> None:
        if not isinstance(balance_cents, int) or isinstance(balance_cents, bool):
            raise TypeError("balance_cents ha de ser un enter en cèntims")
        if balance_cents < 0:
            raise ValueError("una guardiola no pot tenir saldo negatiu")
        _tx.update(self._pots.document(pot_id), {"balance": balance_cents})

    def list_movements(self, pot_id: str) -> list[PotMovement]:
        """De la més recent a la més antiga; amb la mateixa data, primer la creada més tard (P4)."""
        snapshots = _tx.query(self._entries.where(filter=FieldFilter("pot_id", "==", pot_id)))
        entries = [pot_movement_from_dict(s.id, s.to_dict()) for s in snapshots]
        return sorted(entries, key=PotMovement.sort_key, reverse=True)

    def add_movement(self, *, pot_id: str, amount: int, concept: str, date: datetime, type: str) -> PotMovement:
        entry = PotMovement(
            id=pot_movement_id(0), pot_id=pot_id, amount=amount, concept=concept, date=date, type=type, seq=0
        )
        number = _tx.allocate(self._client, POT_MOVEMENT_COUNTER)
        entry.id, entry.seq = pot_movement_id(number), number
        _tx.create(self._entries.document(entry.id), pot_movement_to_dict(entry))
        return entry

    def remove_movement(self, entry: PotMovement) -> None:
        """Com `FirestoreMovementRepository.remove`: dins d'una transacció no cal."""
        if not _tx.in_transaction():
            _tx.delete(self._entries.document(entry.id))


def pot_to_dict(pot: Pot, number: int) -> dict:
    return {
        "id": pot.id,
        "number": number,
        "user_id": pot.user_id,
        "name": pot.name,
        "balance": pot.balance,
        "target": pot.target,
        "color": pot.color,
    }


def pot_from_dict(data: dict) -> Pot:
    return Pot(
        id=data["id"],
        user_id=data["user_id"],
        name=data["name"],
        balance=data["balance"],
        target=data.get("target"),
        color=data["color"],
    )


def pot_movement_to_dict(entry: PotMovement) -> dict:
    return {
        "pot_id": entry.pot_id,
        "amount": entry.amount,
        "concept": entry.concept,
        "date": entry.date,
        "type": entry.type,
        "seq": entry.seq,
    }


def pot_movement_from_dict(entry_id: str, data: dict) -> PotMovement:
    return PotMovement(
        id=entry_id,
        pot_id=data["pot_id"],
        amount=data["amount"],
        concept=data["concept"],
        date=_tx.to_madrid(data["date"]),
        type=data["type"],
        seq=data["seq"],
    )
