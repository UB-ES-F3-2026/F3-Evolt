"""Lectures i escriptures de Firestore, dins o fora d'una transacció (TR01.1).

Els repositoris de Firestore no reben la transacció com a paràmetre: així tenen
els mateixos mètodes que els de memòria i els serveis no canvien.
`FirestoreAtomic` (a `app/repositories/atomic.py`) guarda la transacció en curs
en aquesta ContextVar, i aquestes funcions la fan servir si n'hi ha.

Regla de Firestore: dins d'una transacció, totes les lectures han d'anar abans
de la primera escriptura. Els serveis ja ho fan així (primer validen i al final
escriuen), i els comptadors no la trenquen: es llegeixen un sol cop a l'inici de
la transacció i s'escriuen al final (vegeu `allocate`).
"""

from contextvars import ContextVar
from dataclasses import dataclass, field
from datetime import UTC, datetime

from google.cloud import firestore

from app.models import MADRID_TZ

COUNTERS = "counters"
# Tots els comptadors en un sol document: una transacció el llegeix una vegada.
COUNTERS_DOC = "main"


@dataclass
class CounterState:
    """Els comptadors d'una transacció: llegits a l'inici, escrits en acabar."""

    values: dict[str, int] = field(default_factory=dict)
    dirty: bool = False


current_transaction: ContextVar[firestore.Transaction | None] = ContextVar("current_transaction", default=None)
current_counters: ContextVar[CounterState | None] = ContextVar("current_counters", default=None)


def counters_ref(client: firestore.Client) -> firestore.DocumentReference:
    return client.collection(COUNTERS).document(COUNTERS_DOC)


def get(ref: firestore.DocumentReference) -> firestore.DocumentSnapshot:
    return ref.get(transaction=current_transaction.get())


def query(query: firestore.Query) -> list[firestore.DocumentSnapshot]:
    return list(query.get(transaction=current_transaction.get()))


def set_doc(ref: firestore.DocumentReference, data: dict) -> None:
    transaction = current_transaction.get()
    if transaction is None:
        ref.set(data)
    else:
        transaction.set(ref, data)


def create(ref: firestore.DocumentReference, data: dict) -> None:
    """Crea el document; falla si ja existeix (en una transacció, en fer el commit)."""
    transaction = current_transaction.get()
    if transaction is None:
        ref.create(data)
    else:
        transaction.create(ref, data)


def update(ref: firestore.DocumentReference, data: dict) -> None:
    transaction = current_transaction.get()
    if transaction is None:
        ref.update(data)
    else:
        transaction.update(ref, data)


def delete(ref: firestore.DocumentReference) -> None:
    transaction = current_transaction.get()
    if transaction is None:
        ref.delete()
    else:
        transaction.delete(ref)


def in_transaction() -> bool:
    return current_transaction.get() is not None


def allocate(client: firestore.Client, name: str) -> int:
    """El següent número del comptador `name` (Firestore no té autoincrement).

    - Dins d'una transacció: surt dels comptadors llegits a l'inici, i
      `FirestoreAtomic` els escriu al final. Si la transacció es repeteix o falla,
      no es gasta cap número.
    - Fora: una transacció petita només per al comptador, perquè dues peticions
      alhora no rebin el mateix número.
    Tots els comptadors comencen per 1.
    """
    state = current_counters.get()
    if state is not None:
        value = state.values.get(name, 1)
        state.values[name] = value + 1
        state.dirty = True
        return value

    ref = counters_ref(client)

    @firestore.transactional
    def bump(transaction: firestore.Transaction) -> int:
        snapshot = ref.get(transaction=transaction)
        value = (snapshot.to_dict() or {}).get(name, 1)
        transaction.set(ref, {name: value + 1}, merge=True)
        return value

    return bump(client.transaction())


# Firestore admet ids de document de com a màxim 1.500 bytes.
_MAX_DOC_ID_BYTES = 1500


def safe_doc_id(value: str) -> bool:
    """Un id que ve de l'URL només és un id de document vàlid si no té `/`, no és
    `.`/`..`, no comença per `__` i no passa de 1.500 bytes.

    Si no, Firestore el llegiria com un altre camí o donaria un error (un 500):
    aquests ids no existeixen mai, i es responen com un id desconegut.
    """
    return (
        bool(value)
        and len(value.encode("utf-8")) <= _MAX_DOC_ID_BYTES
        and "/" not in value
        and value not in {".", ".."}
        and not value.startswith("__")
    )


def to_madrid(value: datetime | None) -> datetime | None:
    """Firestore desa els instants en UTC; l'API els dona amb l'hora de Madrid (§1).

    Es reconstrueix camp a camp per conservar els microsegons tal com eren en
    memòria i no tornar el tipus propi de la llibreria.
    """
    if value is None:
        return None
    utc = value.astimezone(UTC)
    plain = datetime(utc.year, utc.month, utc.day, utc.hour, utc.minute, utc.second, utc.microsecond, tzinfo=UTC)
    return plain.astimezone(MADRID_TZ)
