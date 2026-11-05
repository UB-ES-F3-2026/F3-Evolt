"""Dades hardcodeades de l'Sprint 0 (T07.3).

- Usuari 1: compte amb saldo, 3 guardioles i 30 moviments (ingressos i despeses).
- Usuari 2: compte sense moviments ni guardioles, saldo 0.
- Tots dos estan actius i tenen credencials fictícies per iniciar sessió (T01.2,
  docs/api.md §8.13).

Regles del contracte que es compleixen aquí:
- Dates relatives a avui (avui - N dies, N ≥ 1): el llistat sempre sembla recent
  i cap moviment, ni cap recàrrega, cau avui. Així el límit diari comença a zero.
- Dates a Europe/Madrid, amb precisió de segons.
- El saldo del compte és exactament la suma dels moviments, també del pendent
  (docs/api.md §10.1).

`build_seed()` retorna sempre una còpia nova i independent. Els repositoris (T07.4),
els tests (T09.5) i POST /api/dev/reset (T09.6) l'han de fer servir per reiniciar dades.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta

from app.models import (
    IDENTIFIER_EMAIL,
    KIND_OTHER,
    KIND_TOPUP,
    MADRID_TZ,
    MOVEMENT_STATUS_COMPLETED,
    MOVEMENT_STATUS_PENDING,
    POT_INITIAL_CONCEPT,
    STATUS_ACTIVE,
    TOPUP_CONCEPT,
    TOPUP_ICON,
    TYPE_EXPENSE,
    TYPE_INCOME,
    Account,
    Movement,
    MovementReport,
    OutboxMessage,
    Pot,
    PotMovement,
    Session,
    User,
    VerificationCode,
    now_madrid,
)

DEMO_USER_ID = 1
EMPTY_USER_ID = 2

# Credencials fictícies del seed (docs/api.md §8.13, P13). No són secretes: surten
# al contracte i serveixen per a la demo i les proves. El domini `.test` està
# reservat i no arriba a cap bústia real.
DEMO_IDENTIFIER = "demo@evolt.test"
EMPTY_IDENTIFIER = "buit@evolt.test"
SEED_PASSWORD = "Evolt2026"
# Hash de bcrypt de SEED_PASSWORD, calculat una vegada i escrit aquí: bcrypt és
# lent a propòsit (~0,25 s) i build_seed() es crida a cada test i a cada reinici.
# test_seed.py comprova que correspon a SEED_PASSWORD.
SEED_PASSWORD_HASH = "$2b$12$w0xKg70bzkJkEQXZoAeGn.1I05ZAySxhbb35VfvduDwxbsCM4uovq"

# Còpia al frontend: frontend/src/mocks/seed.ts. Si canvies aquestes dades, canvia-les també allà.
# (dies enrere, hora "HH:MM", concepte, type, icon, import en cèntims)
# Ordenat del més antic al més recent: l'ordre de la llista dona el `seq`.
# Les hores eviten la franja 02:00–03:00, que és ambigua el dia del canvi d'hora.
_USER1_MOVEMENTS: list[tuple[int, str, str, str, str, int]] = [
    (40, "10:00", "Ingrés inicial", TYPE_INCOME, "other", 100000),
    (38, "17:10", "Botiga de roba", TYPE_EXPENSE, "shopping", 3999),
    (36, "09:00", "Nòmina", TYPE_INCOME, "salary", 180000),
    (35, "08:05", "Abonament de transport", TYPE_EXPENSE, "transport", 2220),
    (34, "13:30", "Menú del dia", TYPE_EXPENSE, "food", 1350),
    (32, "18:42", "Supermercat", TYPE_EXPENSE, "shopping", 5230),
    (30, "20:15", TOPUP_CONCEPT, TYPE_INCOME, TOPUP_ICON, 20000),
    (29, "21:00", "Restaurant La Plaça", TYPE_EXPENSE, "food", 3480),
    (27, "13:20", "Transferència rebuda", TYPE_INCOME, "transfer", 5000),
    (26, "11:00", "Lloguer", TYPE_EXPENSE, "transfer", 65000),
    (24, "19:05", "Farmàcia", TYPE_EXPENSE, "other", 1475),
    (22, "08:30", "Bitllet de tren", TYPE_EXPENSE, "transport", 1200),
    (21, "18:10", "Supermercat", TYPE_EXPENSE, "shopping", 4590),
    (19, "14:00", "Cafeteria", TYPE_EXPENSE, "food", 420),
    (17, "12:45", "Llibreria", TYPE_EXPENSE, "shopping", 2495),
    (15, "10:30", TOPUP_CONCEPT, TYPE_INCOME, TOPUP_ICON, 15000),
    (13, "09:00", "Nòmina", TYPE_INCOME, "salary", 180000),
    (12, "16:20", "Transferència enviada", TYPE_EXPENSE, "transfer", 2500),
    (11, "21:30", "Sopar amb amics", TYPE_EXPENSE, "food", 2750),
    (10, "08:10", "Taxi", TYPE_EXPENSE, "transport", 1890),
    (9, "18:00", "Gimnàs", TYPE_EXPENSE, "other", 3990),
    (8, "13:15", "Menú del dia", TYPE_EXPENSE, "food", 1350),
    (7, "17:40", "Supermercat", TYPE_EXPENSE, "shopping", 6120),
    (6, "11:00", "Bizum rebut", TYPE_INCOME, "transfer", 1500),
    (5, "20:30", "Cinema", TYPE_EXPENSE, "other", 950),
    (4, "08:05", "Bitllet de tren", TYPE_EXPENSE, "transport", 1200),
    (3, "19:25", "Fruiteria", TYPE_EXPENSE, "food", 1830),
    # Dos moviments amb la mateixa data a propòsit, per provar el desempat (P4):
    # "Bizum enviat" té seq més gran i ha de sortir primer al llistat.
    (2, "18:42", "Supermercat", TYPE_EXPENSE, "shopping", 4590),
    (2, "18:42", "Bizum enviat", TYPE_EXPENSE, "transfer", 1000),
    (1, "21:15", "Restaurant La Plaça", TYPE_EXPENSE, "food", 2350),
]

# Contrapart dels moviments que en tenen, per número de moviment (docs/api.md §10.7).
# Noms inventats: el contacte a les transferències i els Bizum, l'empresa a les nòmines.
_USER1_COUNTERPARTIES: dict[int, str] = {
    3: "Empresa Demo SL",
    9: "Marta Puig",
    10: "Jordi Serra",
    17: "Empresa Demo SL",
    18: "Laia Vidal",
    24: "Pau Ferrer",
    29: "Núria Soler",
}

# L'únic moviment pendent del seed és el més recent (docs/api.md §10.7).
_USER1_PENDING_MOVEMENT = len(_USER1_MOVEMENTS)

# Guardioles de l'usuari 1 (docs/api.md §9.8). El nom i el saldo no canvien des de
# l'Sprint 0: els fan servir els tests i frontend/src/mocks/seed.ts.
# (nom, saldo en cèntims, objectiu en cèntims o None, color)
_USER1_POTS: list[tuple[str, int, int | None, str]] = [
    ("Vacances", 15000, 100000, "blue"),
    ("Emergències", 10000, None, "orange"),
    ("Regal d'aniversari", 5000, 8000, "pink"),
]


@dataclass
class SeedData:
    users: dict[int, User]
    accounts: dict[int, Account]  # clau: user_id (un compte principal per usuari)
    pots: list[Pot]
    movements: list[Movement]
    pot_movements: list[PotMovement]  # historial de totes les guardioles (T18.1)
    # Comptadors per crear moviments nous (recàrregues) sense repetir id ni seq.
    next_movement_number: int = field(default=1)
    next_movement_seq: int = field(default=1)
    # Comptador per als usuaris nous del registre (T01.2).
    next_user_id: int = field(default=1)
    # Sessions obertes, per token (T03.1). El seed no en té cap: reiniciar les
    # dades (arrencada o /api/dev/reset) tanca totes les sessions.
    sessions: dict[str, Session] = field(default_factory=dict)
    # Comptador per a les guardioles noves (T17.2): pot-04, pot-05…
    next_pot_number: int = field(default=1)
    # Codi de verificació vigent de cada usuari pendent, per user_id (T02.1).
    verification_codes: dict[int, VerificationCode] = field(default_factory=dict)
    # Bústia simulada: emails i SMS «enviats», en ordre d'enviament (T02.1, §8.12).
    outbox: list[OutboxMessage] = field(default_factory=list)
    # Comptador per a les entrades noves de l'historial (T18.1): pmov-04, pmov-05…
    next_pot_movement_number: int = field(default=1)
    # Informes de problema dels moviments (T11.1). El seed no en té cap: reiniciar les
    # dades els esborra (docs/api.md §10.4).
    movement_reports: list[MovementReport] = field(default_factory=list)
    next_report_number: int = field(default=1)


def _days_ago_at(now: datetime, days_ago: int, hhmm: str) -> datetime:
    """Data del dia (avui − days_ago) a Madrid, a l'hora indicada.

    Es construeix amb tzinfo=MADRID_TZ, de manera que el desplaçament (+02:00 o
    +01:00) és el correcte per a aquell dia, encara que hi hagi canvi d'hora pel mig.
    """
    day = (now.astimezone(MADRID_TZ) - timedelta(days=days_ago)).date()
    hour, minute = (int(part) for part in hhmm.split(":"))
    return datetime(day.year, day.month, day.day, hour, minute, tzinfo=MADRID_TZ)


def movement_id(number: int) -> str:
    """Id opac dels moviments (P1). El frontend no l'ha d'interpretar."""
    return f"mov-{number:02d}"


def movement_reference(number: int) -> str:
    """Referència opaca dels moviments (docs/api.md §10.1, P37). El frontend no l'ha d'interpretar."""
    return f"EVT-{number:06d}"


def report_id(number: int) -> str:
    """Id opac dels informes de problema (docs/api.md §10.4, P42). El frontend no l'ha d'interpretar."""
    return f"rep-{number:02d}"


def pot_id(number: int) -> str:
    """Id opac de les guardioles (docs/api.md §9.1, P21). El frontend no l'ha d'interpretar."""
    return f"pot-{number:02d}"


def pot_movement_id(number: int) -> str:
    """Id opac de les entrades de l'historial (docs/api.md §9.5). El frontend no l'ha d'interpretar."""
    return f"pmov-{number:02d}"


def build_seed(now: datetime | None = None) -> SeedData:
    """Crea les dades inicials. `now` permet fixar la data als tests."""
    now = now or now_madrid()

    users = {
        DEMO_USER_ID: User(
            id=DEMO_USER_ID,
            name="Usuari demo",
            identifier=DEMO_IDENTIFIER,
            identifier_type=IDENTIFIER_EMAIL,
            password_hash=SEED_PASSWORD_HASH,
            status=STATUS_ACTIVE,
            xp=120,
        ),
        EMPTY_USER_ID: User(
            id=EMPTY_USER_ID,
            name="Usuari nou",
            identifier=EMPTY_IDENTIFIER,
            identifier_type=IDENTIFIER_EMAIL,
            password_hash=SEED_PASSWORD_HASH,
            status=STATUS_ACTIVE,
            xp=0,
        ),
    }

    movements: list[Movement] = []
    for number, (days_ago, hhmm, concept, mov_type, icon, amount) in enumerate(
        _USER1_MOVEMENTS, start=1
    ):
        movements.append(
            Movement(
                id=movement_id(number),
                account_id=DEMO_USER_ID,
                amount=amount,
                concept=concept,
                date=_days_ago_at(now, days_ago, hhmm),
                type=mov_type,
                icon=icon,
                kind=KIND_TOPUP if icon == TOPUP_ICON else KIND_OTHER,
                seq=number,
                counterparty=_USER1_COUNTERPARTIES.get(number),
                status=(
                    MOVEMENT_STATUS_PENDING
                    if number == _USER1_PENDING_MOVEMENT
                    else MOVEMENT_STATUS_COMPLETED
                ),
                reference=movement_reference(number),
            )
        )

    # El saldo es calcula a partir dels moviments, així sempre és coherent.
    demo_balance = sum(m.signed_amount for m in movements)

    accounts = {
        DEMO_USER_ID: Account(id=DEMO_USER_ID, user_id=DEMO_USER_ID, balance=demo_balance),
        EMPTY_USER_ID: Account(id=EMPTY_USER_ID, user_id=EMPTY_USER_ID, balance=0),
    }

    pots = [
        Pot(
            id=pot_id(number),
            user_id=DEMO_USER_ID,
            name=name,
            balance=balance,
            target=target,
            color=color,
        )
        for number, (name, balance, target, color) in enumerate(_USER1_POTS, start=1)
    ]

    # El saldo de cada guardiola és la suma del seu historial: l'entrada inicial és tot
    # el saldo, amb una data anterior a avui (docs/api.md §9.8, P32).
    pot_movements = [
        PotMovement(
            id=pot_movement_id(number),
            pot_id=pot.id,
            amount=pot.balance,
            concept=POT_INITIAL_CONCEPT,
            date=_days_ago_at(now, 30, "10:00"),
            type=TYPE_INCOME,
            seq=number,
        )
        for number, pot in enumerate(pots, start=1)
    ]

    next_number = len(movements) + 1
    return SeedData(
        users=users,
        accounts=accounts,
        pots=pots,
        movements=movements,
        pot_movements=pot_movements,
        next_movement_number=next_number,
        next_movement_seq=next_number,
        next_user_id=max(users) + 1,
        next_pot_number=len(pots) + 1,
        next_pot_movement_number=len(pot_movements) + 1,
    )
