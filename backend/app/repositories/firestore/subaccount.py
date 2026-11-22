"""Subcomptes en divisa a Firestore (T25.2). Mateixos mètodes que `repositories/subaccount.py`.

- Col·lecció `subaccounts`, un document per subcompte amb l'id `sub-NN`.
- El número surt del comptador `next_subaccount_number`.
- Dues creacions alhora van dins d'`atomic.run(...)`: totes dues transaccions
  llegeixen i escriuen el document dels comptadors, així que Firestore en fa
  repetir una, i la repetida ja veu el subcompte de l'altra.
"""

from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

from app.data.seed import subaccount_id as make_subaccount_id
from app.models import Subaccount
from app.repositories.firestore import _tx

SUBACCOUNTS = "subaccounts"
SUBACCOUNT_COUNTER = "next_subaccount_number"


class FirestoreSubaccountRepository:
    def __init__(self, client: firestore.Client) -> None:
        self._client = client
        self._subaccounts = client.collection(SUBACCOUNTS)

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
