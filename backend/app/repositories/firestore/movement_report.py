"""Informes de problema a Firestore (TR01.1). Mateixos mètodes que `repositories/movement_report.py`.

Col·lecció `movement_reports`, un document per informe amb l'id `rep-NN`. El número
surt del comptador `next_report_number` (§10.7: Firestore no té autoincrement).
"""

from datetime import datetime

from google.cloud import firestore

from app.data.seed import report_id
from app.models import MovementReport
from app.repositories.firestore import _tx

MOVEMENT_REPORTS = "movement_reports"
REPORT_COUNTER = "next_report_number"


class FirestoreMovementReportRepository:
    def __init__(self, client: firestore.Client) -> None:
        self._client = client
        self._reports = client.collection(MOVEMENT_REPORTS)

    def add(self, *, movement_id: str, user_id: int, description: str, created_at: datetime) -> MovementReport:
        """El model es valida abans de gastar cap número, com a la memòria."""
        report = MovementReport(
            id=report_id(0),
            movement_id=movement_id,
            user_id=user_id,
            description=description,
            created_at=created_at,
        )
        report.id = report_id(_tx.allocate(self._client, REPORT_COUNTER))
        _tx.create(
            self._reports.document(report.id),
            {
                "movement_id": report.movement_id,
                "user_id": report.user_id,
                "description": report.description,
                "created_at": report.created_at,
            },
        )
        return report
