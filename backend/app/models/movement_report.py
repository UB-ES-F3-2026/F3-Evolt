from dataclasses import dataclass
from datetime import datetime

# Màxim de la descripció d'un informe, un cop trets els espais dels extrems (docs/api.md §10.4).
MAX_REPORT_DESCRIPTION = 500


@dataclass
class MovementReport:
    """Informe d'un problema amb un moviment (T11.1, docs/api.md §10.4 i §10.7).

    Camps de l'API: id, movement_id, description, created_at.
    Camp intern (mai a les respostes): user_id, qui l'ha enviat.
    """

    id: str
    movement_id: str
    user_id: int
    description: str
    created_at: datetime

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id:
            raise TypeError("id ha de ser un string no buit")
        if not isinstance(self.movement_id, str) or not self.movement_id:
            raise TypeError("movement_id ha de ser un string no buit")
        if not isinstance(self.description, str) or not self.description.strip():
            raise ValueError("description no pot ser buida")
        if len(self.description) > MAX_REPORT_DESCRIPTION:
            raise ValueError(f"description no pot passar de {MAX_REPORT_DESCRIPTION} caràcters")
        if self.created_at.tzinfo is None:
            raise ValueError("created_at ha de portar zona horària")
        if self.created_at.microsecond != 0:
            raise ValueError("created_at ha de tenir precisió de segons (P7)")
