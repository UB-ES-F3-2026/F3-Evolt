"""Moviments a Firestore (TR01.1). Mateixos mètodes que `repositories/movement.py`.

- Col·lecció `movements`, un document per moviment amb l'id `mov-NN`.
- Firestore no té autoincrement: el número (id i `reference`) i el `seq` surten
  dels comptadors `next_movement_number` i `next_movement_seq`.
- Les dates es desen com a instants (UTC) i es tornen amb l'hora de Madrid.
- Es llegeixen els moviments del compte i els filtres, l'ordre i la paginació
  es fan aquí, amb les mateixes funcions que la memòria (`MovementFilters.matches`
  i `Movement.sort_key`). Un compte en té pocs, i així la cerca sense accents
  (§10.2) dona exactament el mateix resultat i no cal cap índex compost.
"""

from datetime import date, datetime

from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

from app.data.seed import movement_id, movement_reference
from app.models import KIND_TOPUP, MADRID_TZ, MOVEMENT_STATUS_COMPLETED, Movement, MovementFilters
from app.repositories.firestore import _tx

MOVEMENTS = "movements"
NUMBER_COUNTER = "next_movement_number"
SEQ_COUNTER = "next_movement_seq"


class FirestoreMovementRepository:
    def __init__(self, client: firestore.Client) -> None:
        self._client = client
        self._movements = client.collection(MOVEMENTS)

    def list_by_account(
        self,
        account_id: int,
        offset: int,
        limit: int,
        filters: MovementFilters | None = None,
    ) -> list[Movement]:
        """Del més recent al més antic; amb la mateixa data, primer el `seq` més gran (P4)."""
        if offset < 0 or limit < 1:
            raise ValueError("paginació invàlida: offset ha de ser ≥ 0 i limit ha de ser ≥ 1")
        ordered = sorted(self._filtered(account_id, filters), key=Movement.sort_key, reverse=True)
        return ordered[offset : offset + limit]

    def count_by_account(self, account_id: int, filters: MovementFilters | None = None) -> int:
        return len(self._filtered(account_id, filters))

    def add(
        self,
        *,
        account_id: int,
        amount: int,
        concept: str,
        date: datetime,
        type: str,
        icon: str,
        kind: str,
        counterparty: str | None = None,
        status: str = MOVEMENT_STATUS_COMPLETED,
    ) -> Movement:
        """Crea el moviment amb el següent número i `seq`.

        El model es valida abans de gastar cap número, com a la memòria.
        """
        draft = Movement(
            id=movement_id(0),
            account_id=account_id,
            amount=amount,
            concept=concept,
            date=date,
            type=type,
            icon=icon,
            kind=kind,
            seq=0,
            counterparty=counterparty,
            status=status,
            reference=movement_reference(0),
        )
        number = _tx.allocate(self._client, NUMBER_COUNTER)
        seq = _tx.allocate(self._client, SEQ_COUNTER)
        draft.id, draft.seq, draft.reference = movement_id(number), seq, movement_reference(number)
        _tx.create(self._movements.document(draft.id), movement_to_dict(draft))
        return draft

    def remove(self, movement: Movement) -> None:
        """Desfà un moviment acabat de crear (T18.1).

        Dins d'una transacció no cal: si l'operació falla, Firestore no n'escriu
        res. El número gastat no es torna: un forat a la numeració és inofensiu.
        """
        if not _tx.in_transaction():
            _tx.delete(self._movements.document(movement.id))

    def sum_topups_on_day(self, account_id: int, day: date) -> int:
        """Recàrregues del dia natural de Madrid, com a la memòria."""
        return sum(
            movement.amount
            for movement in self._by_account(account_id)
            if movement.kind == KIND_TOPUP and movement.date.astimezone(MADRID_TZ).date() == day
        )

    def _filtered(self, account_id: int, filters: MovementFilters | None) -> list[Movement]:
        movements = self._by_account(account_id)
        if filters is None:
            return movements
        return [movement for movement in movements if filters.matches(movement)]

    def _by_account(self, account_id: int) -> list[Movement]:
        query = self._movements.where(filter=FieldFilter("account_id", "==", account_id))
        return [movement_from_dict(s.id, s.to_dict()) for s in _tx.query(query)]


def movement_to_dict(movement: Movement) -> dict:
    return {
        "account_id": movement.account_id,
        "amount": movement.amount,
        "concept": movement.concept,
        "date": movement.date,
        "type": movement.type,
        "icon": movement.icon,
        "kind": movement.kind,
        "seq": movement.seq,
        "counterparty": movement.counterparty,
        "status": movement.status,
        "reference": movement.reference,
    }


def movement_from_dict(movement_id_: str, data: dict) -> Movement:
    return Movement(
        id=movement_id_,
        account_id=data["account_id"],
        amount=data["amount"],
        concept=data["concept"],
        date=_tx.to_madrid(data["date"]),
        type=data["type"],
        icon=data["icon"],
        kind=data["kind"],
        seq=data["seq"],
        counterparty=data.get("counterparty"),
        status=data["status"],
        reference=data["reference"],
    )
