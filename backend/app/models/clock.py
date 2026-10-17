"""Hora de referència del contracte (docs/api.md §1).

"Avui" és el dia natural a Europe/Madrid, sigui quina sigui la zona del servidor,
i les dates es donen amb precisió de segons (P7). Ho fan servir el seed, els
repositoris i els serveis, per això viu aquí una sola vegada.
"""

from datetime import datetime
from zoneinfo import ZoneInfo

MADRID_TZ = ZoneInfo("Europe/Madrid")


def now_madrid() -> datetime:
    """Moment actual a Madrid, sense fraccions de segon."""
    return datetime.now(MADRID_TZ).replace(microsecond=0)
