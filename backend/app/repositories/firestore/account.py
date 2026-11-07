"""Comptes a Firestore (TR01.1). Mateixos mètodes que `repositories/account.py`.

Col·lecció `accounts`, un document per usuari amb l'id de l'usuari.
"""

from google.cloud import firestore

from app.models import Account
from app.repositories.firestore import _tx

ACCOUNTS = "accounts"


class FirestoreAccountRepository:
    def __init__(self, client: firestore.Client) -> None:
        self._accounts = client.collection(ACCOUNTS)

    def get_by_user(self, user_id: int) -> Account | None:
        snapshot = _tx.get(self._accounts.document(str(user_id)))
        if not snapshot.exists:
            return None
        data = snapshot.to_dict()
        return Account(id=data["id"], user_id=data["user_id"], balance=data["balance"])

    def set_balance(self, user_id: int, balance_cents: int) -> None:
        if not isinstance(balance_cents, int) or isinstance(balance_cents, bool):
            raise TypeError("balance_cents ha de ser un enter en cèntims")
        _tx.update(self._accounts.document(str(user_id)), {"balance": balance_cents})

    def create_for_user(self, user_id: int) -> Account:
        """Compte nou amb saldo 0. `create` falla si ja n'hi ha un, sense llegir abans."""
        account = Account(id=user_id, user_id=user_id, balance=0)
        _tx.create(self._accounts.document(str(user_id)), account_to_dict(account))
        return account


def account_to_dict(account: Account) -> dict:
    return {"id": account.id, "user_id": account.user_id, "balance": account.balance}
