"""Despeses dividides a Firestore (T30.2). Mateixos mètodes que `repositories/split_expense.py`.

Col·lecció `split_expenses`, un document per despesa amb l'id `split-NN`. El número surt
del comptador `next_split_expense_number` (§17.9).
"""

from datetime import datetime

from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

from app.data.seed import split_expense_id
from app.models import SplitExpense, SplitPart
from app.repositories.firestore import _tx

SPLIT_EXPENSES = "split_expenses"
SPLIT_EXPENSE_COUNTER = "next_split_expense_number"


class FirestoreSplitExpenseRepository:
    def __init__(self, client: firestore.Client) -> None:
        self._client = client
        self._splits = client.collection(SPLIT_EXPENSES)

    def add(
        self,
        *,
        requester_id: int,
        concept: str,
        total: int,
        my_share: int,
        created_at: datetime,
        parts: list[SplitPart],
    ) -> SplitExpense:
        """El model es valida abans de gastar cap número, com a la memòria."""
        split = SplitExpense(
            id=split_expense_id(0),
            requester_id=requester_id,
            concept=concept,
            total=total,
            my_share=my_share,
            created_at=created_at,
            seq=0,
            parts=list(parts),
        )
        split.seq = _tx.allocate(self._client, SPLIT_EXPENSE_COUNTER)
        split.id = split_expense_id(split.seq)
        _tx.create(self._splits.document(split.id), split_expense_to_dict(split))
        return split

    def get(self, split_id: str) -> SplitExpense | None:
        if not _tx.safe_doc_id(split_id):
            return None
        snapshot = _tx.get(self._splits.document(split_id))
        return split_expense_from_dict(snapshot.id, snapshot.to_dict()) if snapshot.exists else None

    def list_by_requester(self, requester_id: int) -> list[SplitExpense]:
        snapshots = _tx.query(self._splits.where(filter=FieldFilter("requester_id", "==", requester_id)))
        mine = [split_expense_from_dict(snapshot.id, snapshot.to_dict()) for snapshot in snapshots]
        return sorted(mine, key=SplitExpense.sort_key, reverse=True)

    def undo_add(self, split: SplitExpense) -> None:
        """Dins d'una transacció no cal: un error inesperat ja no escriu res."""
        if not _tx.in_transaction():
            _tx.delete(self._splits.document(split.id))


def split_expense_to_dict(split: SplitExpense) -> dict:
    return {
        "requester_id": split.requester_id,
        "concept": split.concept,
        "total": split.total,
        "my_share": split.my_share,
        "created_at": split.created_at,
        "seq": split.seq,
        "parts": [{"user_id": part.user_id, "amount": part.amount} for part in split.parts],
    }


def split_expense_from_dict(split_id: str, data: dict) -> SplitExpense:
    return SplitExpense(
        id=split_id,
        requester_id=data["requester_id"],
        concept=data["concept"],
        total=data["total"],
        my_share=data["my_share"],
        created_at=_tx.to_madrid(data["created_at"]),
        seq=data["seq"],
        parts=[SplitPart(user_id=part["user_id"], amount=part["amount"]) for part in data["parts"]],
    )
