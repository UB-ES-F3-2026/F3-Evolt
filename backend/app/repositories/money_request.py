"""Repositori de sol·licituds de diners (T15.2, docs/api.md §14.8).

Llegeix i escriu les dades en memòria del SeedData. No decideix regles de
negoci (qui pot cancel·lar, quan caduca): això és feina del servei.
"""

from datetime import datetime

from app.data.seed import SeedData, money_request_id
from app.models import REQUEST_PENDING, MoneyRequest


class MoneyRequestRepository:
    """Sol·licituds de diners (T15.2)."""

    def __init__(self, seed: SeedData) -> None:
        self._seed = seed

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
        """Crea i desa una sol·licitud pendent amb un id nou, i la retorna.

        Tot o res: si la construcció falla (__post_init__), no es desa res i el
        comptador no avança.
        """
        number = self._seed.next_money_request_number
        request = MoneyRequest(
            id=money_request_id(number),
            requester_id=requester_id,
            recipient_id=recipient_id,
            amount=amount,
            concept=concept,
            created_at=created_at,
            status=REQUEST_PENDING,
            seq=number,
            split_id=split_id,
        )
        self._seed.next_money_request_number = number + 1
        self._seed.money_requests.append(request)
        return request

    def get(self, request_id: str) -> MoneyRequest | None:
        """La sol·licitud amb aquest id, de qualsevol usuari, o None."""
        return next((request for request in self._seed.money_requests if request.id == request_id), None)

    def list_by_requester(self, requester_id: int) -> list[MoneyRequest]:
        """Les enviades per un usuari, de la més recent a la més antiga (§14.3, P4)."""
        sent = [request for request in self._seed.money_requests if request.requester_id == requester_id]
        return sorted(sent, key=MoneyRequest.sort_key, reverse=True)

    def list_by_split(self, split_id: str) -> list[MoneyRequest]:
        """Les sol·licituds d'una despesa dividida, en l'ordre de creació (§17.9)."""
        return sorted((r for r in self._seed.money_requests if r.split_id == split_id), key=lambda r: r.seq)

    def delete(self, request_id: str) -> None:
        """Esborra una sol·licitud cancel·lada (§14.4). El seu id no es torna a fer servir."""
        self._seed.money_requests = [r for r in self._seed.money_requests if r.id != request_id]

    def undo_add(self, request: MoneyRequest) -> None:
        """Treu una sol·licitud acabada de crear, si l'avís ha fallat (tot o res, §14.2).

        Si és l'última que s'ha creat, el comptador torna enrere i no queda cap forat.
        """
        self.delete(request.id)
        if request.seq == self._seed.next_money_request_number - 1:
            self._seed.next_money_request_number = request.seq
