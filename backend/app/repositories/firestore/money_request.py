"""Sol·licituds de diners a Firestore (T15.2). Mateixos mètodes que `repositories/money_request.py`.

Col·lecció `money_requests`, un document per sol·licitud amb l'id `req-NN`. El número
surt del comptador `next_money_request_number` (§14.8: Firestore no té autoincrement).
"""

from datetime import datetime

from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

from app.data.seed import money_request_id
from app.models import REQUEST_PENDING, MoneyRequest
from app.repositories.firestore import _tx

MONEY_REQUESTS = "money_requests"
MONEY_REQUEST_COUNTER = "next_money_request_number"


class FirestoreMoneyRequestRepository:
    def __init__(self, client: firestore.Client) -> None:
        self._client = client
        self._requests = client.collection(MONEY_REQUESTS)

    def add(
        self,
        *,
        requester_id: int,
        recipient_id: int,
        amount: int,
        concept: str,
        created_at: datetime,
        split_id: str | None = None,
    ) -> MoneyRequest:
        """El model es valida abans de gastar cap número, com a la memòria."""
        request = MoneyRequest(
            id=money_request_id(0),
            requester_id=requester_id,
            recipient_id=recipient_id,
            amount=amount,
            concept=concept,
            created_at=created_at,
            status=REQUEST_PENDING,
            seq=0,
            split_id=split_id,
        )
        request.seq = _tx.allocate(self._client, MONEY_REQUEST_COUNTER)
        request.id = money_request_id(request.seq)
        _tx.create(self._requests.document(request.id), money_request_to_dict(request))
        return request

    def get(self, request_id: str) -> MoneyRequest | None:
        if not _tx.safe_doc_id(request_id):
            return None
        snapshot = _tx.get(self._requests.document(request_id))
        return money_request_from_dict(snapshot.id, snapshot.to_dict()) if snapshot.exists else None

    def list_by_requester(self, requester_id: int) -> list[MoneyRequest]:
        snapshots = _tx.query(self._requests.where(filter=FieldFilter("requester_id", "==", requester_id)))
        sent = [money_request_from_dict(snapshot.id, snapshot.to_dict()) for snapshot in snapshots]
        return sorted(sent, key=MoneyRequest.sort_key, reverse=True)

    def list_by_split(self, split_id: str) -> list[MoneyRequest]:
        snapshots = _tx.query(self._requests.where(filter=FieldFilter("split_id", "==", split_id)))
        return sorted((money_request_from_dict(s.id, s.to_dict()) for s in snapshots), key=lambda r: r.seq)

    def delete(self, request_id: str) -> None:
        _tx.delete(self._requests.document(request_id))

    def undo_add(self, request: MoneyRequest) -> None:
        """Dins d'una transacció no cal: un error inesperat ja no escriu res."""
        if not _tx.in_transaction():
            self.delete(request.id)


def money_request_to_dict(request: MoneyRequest) -> dict:
    return {
        "requester_id": request.requester_id,
        "recipient_id": request.recipient_id,
        "amount": request.amount,
        "concept": request.concept,
        "created_at": request.created_at,
        "status": request.status,
        "seq": request.seq,
        "split_id": request.split_id,
    }


def money_request_from_dict(request_id: str, data: dict) -> MoneyRequest:
    return MoneyRequest(
        id=request_id,
        requester_id=data["requester_id"],
        recipient_id=data["recipient_id"],
        amount=data["amount"],
        concept=data["concept"],
        created_at=_tx.to_madrid(data["created_at"]),
        status=data["status"],
        seq=data["seq"],
        # Les sol·licituds desades abans de la US-30 no tenen el camp.
        split_id=data.get("split_id"),
    )
