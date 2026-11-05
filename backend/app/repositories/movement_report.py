"""Repositori dels informes de problema (T11.1, docs/api.md §10.4 i §10.7).

Llegeix i escriu les dades en memòria del SeedData. No decideix regles de
negoci: això és feina dels serveis.
"""

import threading
from datetime import datetime

from app.data.seed import SeedData, report_id
from app.models import MovementReport

# Les rutes síncrones de FastAPI corren en un pool de fils: sense aquest pany, dos
# informes alhora podrien llegir el mateix comptador i rebre el mateix id. Amb
# Firestore (#106) el comptador anirà dins d'una transacció.
_ADD_LOCK = threading.Lock()


class MovementReportRepository:
    """Informes de problema dels moviments (T11.1)."""

    def __init__(self, seed: SeedData) -> None:
        self._seed = seed

    def add(
        self,
        *,
        movement_id: str,
        user_id: int,
        description: str,
        created_at: datetime,
    ) -> MovementReport:
        """Crea i desa un informe amb un id nou, i el retorna.

        Tot o res: si la construcció de l'informe falla (__post_init__), no es
        desa res i el comptador no avança.
        """
        with _ADD_LOCK:
            number = self._seed.next_report_number
            report = MovementReport(
                id=report_id(number),
                movement_id=movement_id,
                user_id=user_id,
                description=description,
                created_at=created_at,
            )
            self._seed.next_report_number = number + 1
            self._seed.movement_reports.append(report)
        return report
