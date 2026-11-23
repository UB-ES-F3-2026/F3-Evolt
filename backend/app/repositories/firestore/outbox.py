"""Bústia simulada a Firestore (TR01.1). Mateixos mètodes que `repositories/outbox.py`.

Col·lecció `outbox`. El comptador `next_outbox_seq` dona l'ordre d'enviament.
"""

from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

from app.models import OutboxMessage
from app.repositories.firestore import _tx

OUTBOX = "outbox"
OUTBOX_COUNTER = "next_outbox_seq"


class FirestoreOutboxRepository:
    def __init__(self, client: firestore.Client) -> None:
        self._client = client
        self._outbox = client.collection(OUTBOX)

    def add(self, message: OutboxMessage) -> None:
        seq = _tx.allocate(self._client, OUTBOX_COUNTER)
        _tx.create(
            self._outbox.document(f"msg-{seq:08d}"),
            {
                "seq": seq,
                "to": message.to,
                "channel": message.channel,
                "type": message.type,
                "text": message.text,
                "date": message.date,
                "code": message.code,
                "link": message.link,
            },
        )

    def remove(self, message: OutboxMessage) -> None:
        """Desfà un missatge acabat de desar (T14.1), com `FirestoreMovementRepository.remove`.

        Dins d'una transacció no cal: si l'operació falla, Firestore no n'escriu res.
        Fora, esborra el missatge igual més recent d'aquest destinatari.
        """
        if _tx.in_transaction():
            return
        query = self._outbox.where(filter=FieldFilter("to", "==", message.to))
        for snapshot in sorted(_tx.query(query), key=lambda s: s.to_dict()["seq"], reverse=True):
            if message_from_dict(snapshot.to_dict()) == message:
                _tx.delete(snapshot.reference)
                return

    def list(self, to: str | None = None) -> list[OutboxMessage]:
        """Del més recent al més antic; amb `to` (ja normalitzat), només els d'aquest destinatari."""
        query = self._outbox if to is None else self._outbox.where(filter=FieldFilter("to", "==", to))
        snapshots = sorted(_tx.query(query), key=lambda s: s.to_dict()["seq"], reverse=True)
        return [message_from_dict(s.to_dict()) for s in snapshots]


def message_from_dict(data: dict) -> OutboxMessage:
    return OutboxMessage(
        to=data["to"],
        channel=data["channel"],
        type=data["type"],
        text=data["text"],
        date=_tx.to_madrid(data["date"]),
        code=data.get("code"),
        link=data.get("link"),
    )
