"""Repositori de la bústia simulada (T02.1, docs/api.md §8.12)."""

from app.data.seed import SeedData
from app.models import OutboxMessage


class OutboxRepository:
    """Emails i SMS «enviats» pel backend."""

    def __init__(self, seed: SeedData) -> None:
        self._seed = seed

    def add(self, message: OutboxMessage) -> None:
        self._seed.outbox.append(message)

    def remove(self, message: OutboxMessage) -> None:
        """Treu un missatge acabat de desar, per desfer una operació que ha fallat (T14.1).

        Busca aquest mateix objecte des del final: un missatge igual d'abans no es toca.
        """
        for index in range(len(self._seed.outbox) - 1, -1, -1):
            if self._seed.outbox[index] is message:
                del self._seed.outbox[index]
                return

    def list(self, to: str | None = None) -> list[OutboxMessage]:
        """Missatges del més recent al més antic; amb `to`, només els d'aquest destinatari.

        `to` ha d'estar ja normalitzat, com a `UserRepository.find_by_identifier`.
        """
        messages = [m for m in self._seed.outbox if to is None or m.to == to]
        return list(reversed(messages))


class ClosedOutboxRepository:
    """Bústia tancada (`ENABLE_DEV_OUTBOX` desactivada): no desa res (revisió de la #137).

    Els missatges porten el codi de verificació i l'enllaç de recuperació en clar.
    Si ningú no els pot llegir per la ruta, tampoc no s'han de quedar a les dades,
    on qui llegís la base de dades podria fer-los servir.
    """

    def add(self, message: OutboxMessage) -> None:
        return None

    def remove(self, message: OutboxMessage) -> None:
        return None

    def list(self, to: str | None = None) -> list[OutboxMessage]:
        return []
