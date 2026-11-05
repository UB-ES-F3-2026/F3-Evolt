"""Operacions tot o res (TR01.1, docs/api.md §8.13).

Una recàrrega llegeix el límit diari i després escriu el moviment i el saldo;
un registre comprova el duplicat i després crea l'usuari, el compte i el codi;
una aportació escriu quatre coses. Si dues peticions ho fan alhora, o una
escriptura falla a mig camí, no pot quedar res a mitges. Els routers d'aquestes
operacions les executen amb `atomic.run(...)`, sense que el servei sàpiga on es
guarden les dades:

- **Memòria:** un pany. Dues operacions no s'encavalquen (és el pany que
  Alicia va demanar a la #128 per a la recàrrega).
- **Firestore:** una transacció. Totes les lectures i escriptures dels
  repositoris de dins hi van; si un altre client toca les mateixes dades,
  Firestore la torna a executar, i si hi ha un error inesperat no s'escriu res.
  Dins del mateix procés, a més, el mateix pany que la memòria: així les
  peticions del backend no es fan repetir entre elles (les transaccions toquen
  totes el document dels comptadors), i els reintents només calen si hi ha més
  d'un procés.

Un error de negoci (`ApiError`) no desfà res, igual que a la memòria: els serveis
ja validen abans d'escriure, i el que escriuen abans d'un `ApiError` ha de quedar
(p. ex. el codi de verificació incorrecte que compta com a intent, T02.1).

Una operació dins d'una altra fa servir la mateixa transacció (o el mateix pany).
"""

import threading
from collections.abc import Callable
from typing import Protocol, TypeVar

T = TypeVar("T")


class Atomic(Protocol):
    def run(self, operation: Callable[[], T]) -> T: ...


class MemoryAtomic:
    def __init__(self) -> None:
        # RLock: una operació atòmica en pot cridar una altra.
        self._lock = threading.RLock()

    def run(self, operation: Callable[[], T]) -> T:
        with self._lock:
            return operation()


# Reintents de Firestore si un altre procés toca les mateixes dades (per defecte, 5).
MAX_ATTEMPTS = 10


class FirestoreAtomic:
    def __init__(self, client) -> None:  # google.cloud.firestore.Client
        self._client = client
        self._lock = threading.RLock()

    def run(self, operation: Callable[[], T]) -> T:
        # Importats aquí: amb STORAGE=memory l'app no carrega Firestore.
        from google.cloud import firestore

        from app.repositories.firestore import _tx
        from app.services.errors import ApiError

        if _tx.in_transaction():
            return operation()

        counters = _tx.counters_ref(self._client)

        @firestore.transactional
        def in_transaction(transaction: firestore.Transaction) -> tuple[T | None, ApiError | None]:
            # Els comptadors es llegeixen primer: així els ids nous no trenquen la
            # regla «les lectures abans de les escriptures», i s'escriuen al final.
            state = _tx.CounterState(values=dict(counters.get(transaction=transaction).to_dict() or {}))
            transaction_token = _tx.current_transaction.set(transaction)
            counters_token = _tx.current_counters.set(state)
            try:
                result, error = operation(), None
            except ApiError as business_error:
                # Es fa el commit del que s'ha escrit i després es torna a llançar.
                result, error = None, business_error
            finally:
                _tx.current_counters.reset(counters_token)
                _tx.current_transaction.reset(transaction_token)
            if state.dirty:
                transaction.set(counters, state.values, merge=True)
            return result, error

        with self._lock:
            result, error = in_transaction(self._client.transaction(max_attempts=MAX_ATTEMPTS))
        if error is not None:
            raise error
        return result
