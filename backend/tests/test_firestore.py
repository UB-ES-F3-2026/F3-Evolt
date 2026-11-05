"""Tests de TR01.1: repositoris de Firestore i l'app amb STORAGE=firestore.

Necessiten l'emulador de Firestore; sense, se salten (la CI i el desenvolupament
normal continuen en memòria). Des de backend/, amb l'emulador engegat:

    FIRESTORE_EMULATOR_HOST=127.0.0.1:8080 python -m pytest tests/test_firestore.py

A més, `TEST_STORAGE=firestore` passa tota la resta de tests de l'API per
l'emulador (vegeu `conftest.py`). Aquí hi ha el que només té sentit amb Firestore:
les dades que sobreviuen als reinicis, les transaccions, els comptadors i les
proves amb dades que la resta de tests llegeixen directament de la memòria.

Cada test fa servir un projecte nou de l'emulador: les dades no es barregen.
"""

import os
import threading
import uuid
from collections.abc import Iterator
from datetime import datetime, timedelta

import pytest

if not os.environ.get("FIRESTORE_EMULATOR_HOST"):
    pytest.skip("cal l'emulador de Firestore (FIRESTORE_EMULATOR_HOST)", allow_module_level=True)

from fastapi.testclient import TestClient  # noqa: E402
from google.cloud import firestore  # noqa: E402

from app.data.firestore_seed import is_seeded, write_seed  # noqa: E402
from app.data.seed import (  # noqa: E402
    DEMO_IDENTIFIER,
    DEMO_USER_ID,
    EMPTY_USER_ID,
    MADRID_TZ,
    SEED_PASSWORD,
    build_seed,
)
from app.main import create_app  # noqa: E402
from app.models import KIND_TOPUP, TYPE_INCOME, MovementFilters, OutboxMessage  # noqa: E402
from app.repositories import (  # noqa: E402
    AccountRepository,
    MovementRepository,
    OutboxRepository,
    PotRepository,
    UserRepository,
)
from app.repositories.atomic import FirestoreAtomic  # noqa: E402
from app.repositories.firestore import (  # noqa: E402
    FirestoreAccountRepository,
    FirestoreMovementReportRepository,
    FirestoreMovementRepository,
    FirestoreOutboxRepository,
    FirestorePasswordResetTokenRepository,
    FirestorePotRepository,
    FirestoreSessionRepository,
    FirestoreUserRepository,
    FirestoreVerificationCodeRepository,
)
from app.services.errors import INVALID_AMOUNT, ApiError  # noqa: E402
from app.services.topup_service import top_up  # noqa: E402

NOW = datetime(2026, 11, 3, 10, 0, 0, tzinfo=MADRID_TZ)


def _project() -> str:
    return f"test-{uuid.uuid4().hex[:12]}"


@pytest.fixture
def seed():
    return build_seed(now=NOW)


@pytest.fixture
def db(seed) -> firestore.Client:
    """Projecte buit de l'emulador amb el mateix seed que la memòria."""
    client = firestore.Client(project=_project())
    write_seed(client, seed)
    return client


@pytest.fixture
def project(monkeypatch) -> str:
    """Projecte de l'emulador per a l'app, amb STORAGE=firestore."""
    name = _project()
    monkeypatch.setenv("STORAGE", "firestore")
    monkeypatch.setenv("FIRESTORE_PROJECT_ID", name)
    return name


@pytest.fixture
def app_client(project) -> Iterator[TestClient]:
    with TestClient(create_app()) as client:
        yield client


def _login(client: TestClient) -> dict[str, str]:
    token = client.post("/api/auth/login", json={"identifier": DEMO_IDENTIFIER, "password": SEED_PASSWORD}).json()[
        "token"
    ]
    return {"Authorization": f"Bearer {token}"}


# --- Paritat amb la memòria: mateix seed, mateixes respostes ------------------------


def test_seed_is_written_once(db) -> None:
    assert is_seeded(db)
    assert not is_seeded(firestore.Client(project=_project()))


def test_users_and_accounts_match_memory(db, seed) -> None:
    users, memory_users = FirestoreUserRepository(db), UserRepository(seed)
    accounts, memory_accounts = FirestoreAccountRepository(db), AccountRepository(seed)

    for user_id in (DEMO_USER_ID, EMPTY_USER_ID, 999):
        assert users.get(user_id) == memory_users.get(user_id)
        assert accounts.get_by_user(user_id) == memory_accounts.get_by_user(user_id)
    assert users.find_by_identifier(DEMO_IDENTIFIER) == memory_users.find_by_identifier(DEMO_IDENTIFIER)
    assert users.find_by_identifier("ningu@x.com") is None


def test_movements_match_memory_with_filters(db, seed) -> None:
    movements, memory = FirestoreMovementRepository(db), MovementRepository(seed)
    cases = [
        None,
        MovementFilters(type="expense"),
        MovementFilters(text="bizum"),
        MovementFilters(date_from=NOW.date() - timedelta(days=7), date_to=NOW.date()),
    ]
    for filters in cases:
        for offset, limit in ((0, 20), (20, 20), (5, 3)):
            assert movements.list_by_account(DEMO_USER_ID, offset, limit, filters) == memory.list_by_account(
                DEMO_USER_ID, offset, limit, filters
            )
        assert movements.count_by_account(DEMO_USER_ID, filters) == memory.count_by_account(DEMO_USER_ID, filters)
    assert movements.sum_topups_on_day(DEMO_USER_ID, NOW.date()) == memory.sum_topups_on_day(DEMO_USER_ID, NOW.date())


def test_pots_and_history_match_memory(db, seed) -> None:
    pots, memory = FirestorePotRepository(db), PotRepository(seed)

    assert pots.list_by_user(DEMO_USER_ID) == memory.list_by_user(DEMO_USER_ID)
    assert pots.list_by_user(EMPTY_USER_ID) == []
    assert pots.get_by_user(DEMO_USER_ID, "pot-01") == memory.get_by_user(DEMO_USER_ID, "pot-01")
    assert pots.get_by_user(EMPTY_USER_ID, "pot-01") is None
    assert pots.list_movements("pot-01") == memory.list_movements("pot-01")


@pytest.mark.parametrize("pot_id", ["pot-99", "a/b", "..", "__x__", "", "x" * 1501, "é" * 751])
def test_unknown_or_unsafe_pot_id_is_not_found(db, pot_id: str) -> None:
    # Un id de l'URL amb `/` no pot convertir-se en un altre camí de Firestore.
    assert FirestorePotRepository(db).get_by_user(DEMO_USER_ID, pot_id) is None


def test_dates_keep_the_madrid_offset(db) -> None:
    [newest] = FirestoreMovementRepository(db).list_by_account(DEMO_USER_ID, 0, 1)
    assert newest.date.tzinfo is not None
    assert newest.date.utcoffset() == newest.date.astimezone(MADRID_TZ).utcoffset()


# --- Comptadors i transaccions ------------------------------------------------------


def test_new_ids_continue_the_seed(db) -> None:
    atomic = FirestoreAtomic(db)
    movements, pots = FirestoreMovementRepository(db), FirestorePotRepository(db)

    movement = atomic.run(
        lambda: movements.add(
            account_id=DEMO_USER_ID,
            amount=100,
            concept="Recàrrega",
            date=NOW,
            type=TYPE_INCOME,
            icon="topup",
            kind=KIND_TOPUP,
        )
    )
    pot = atomic.run(lambda: pots.add(user_id=DEMO_USER_ID, name="Viatge", balance=0, target=None, color="blue"))

    assert (movement.id, movement.seq, movement.reference) == ("mov-31", 31, "EVT-000031")
    assert pot.id == "pot-04"


def test_unexpected_error_writes_nothing_and_spends_no_number(db) -> None:
    atomic = FirestoreAtomic(db)
    movements = FirestoreMovementRepository(db)

    def fails_after_writing():
        movements.add(
            account_id=DEMO_USER_ID,
            amount=100,
            concept="Recàrrega",
            date=NOW,
            type=TYPE_INCOME,
            icon="topup",
            kind=KIND_TOPUP,
        )
        raise RuntimeError("escriptura fallida")

    with pytest.raises(RuntimeError):
        atomic.run(fails_after_writing)

    assert movements.count_by_account(DEMO_USER_ID) == 30
    after = atomic.run(lambda: top_up(DEMO_USER_ID, 100, FirestoreAccountRepository(db), movements, now=NOW))
    assert after.movement.id == "mov-31"


def test_business_error_keeps_what_was_written(db) -> None:
    # Com a la memòria: el que el servei escriu abans d'un ApiError queda (p. ex. un intent fallit).
    atomic = FirestoreAtomic(db)
    outbox = FirestoreOutboxRepository(db)

    def writes_then_rejects():
        outbox.add(OutboxMessage(to="a@x.com", channel="email", type="verification_code", text="t", date=NOW))
        raise ApiError(INVALID_AMOUNT)

    with pytest.raises(ApiError):
        atomic.run(writes_then_rejects)

    assert len(outbox.list("a@x.com")) == 1


def test_simultaneous_topups_are_all_counted(db) -> None:
    # El cas de la #128: sense transacció, dues recàrregues alhora es podien menjar una.
    atomic = FirestoreAtomic(db)
    accounts, movements = FirestoreAccountRepository(db), FirestoreMovementRepository(db)
    before = accounts.get_by_user(EMPTY_USER_ID).balance
    threads_count = 5
    barrier = threading.Barrier(threads_count)
    errors: list[Exception] = []

    def attempt() -> None:
        barrier.wait()
        try:
            atomic.run(lambda: top_up(EMPTY_USER_ID, 1000, accounts, movements, now=NOW))
        except Exception as error:  # noqa: BLE001
            errors.append(error)

    threads = [threading.Thread(target=attempt) for _ in range(threads_count)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert errors == []
    assert accounts.get_by_user(EMPTY_USER_ID).balance == before + threads_count * 1000
    ids = [m.id for m in movements.list_by_account(EMPTY_USER_ID, 0, 50)]
    assert len(ids) == len(set(ids)) == threads_count


def test_outbox_keeps_the_order(db) -> None:
    outbox, memory = FirestoreOutboxRepository(db), OutboxRepository(build_seed(now=NOW))
    for to in ("a@x.com", "b@x.com", "a@x.com"):
        message = OutboxMessage(to=to, channel="email", type="verification_code", text=to, date=NOW, code="012345")
        outbox.add(message)
        memory.add(message)

    assert outbox.list() == memory.list()
    assert outbox.list("a@x.com") == memory.list("a@x.com")


def test_tokens_are_stored_only_as_hashes(db) -> None:
    session = FirestoreSessionRepository(db).create(DEMO_USER_ID, NOW)
    reset = FirestorePasswordResetTokenRepository(db).replace(DEMO_USER_ID, NOW)

    stored = [d.id for name in ("sessions", "password_reset_tokens") for d in db.collection(name).list_documents()]
    assert session.token not in stored
    assert reset.token not in stored
    assert FirestoreSessionRepository(db).get(session.token).user_id == DEMO_USER_ID
    assert FirestorePasswordResetTokenRepository(db).get(reset.token).user_id == DEMO_USER_ID


def test_new_reset_link_replaces_the_old_one(db) -> None:
    tokens = FirestorePasswordResetTokenRepository(db)
    first = tokens.replace(DEMO_USER_ID, NOW)
    second = tokens.replace(DEMO_USER_ID, NOW)

    assert tokens.get(first.token) is None
    assert tokens.get(second.token) is not None


def test_sessions_of_one_user_close_together(db) -> None:
    sessions = FirestoreSessionRepository(db)
    mine = [sessions.create(DEMO_USER_ID, NOW).token for _ in range(2)]
    other = sessions.create(EMPTY_USER_ID, NOW).token

    sessions.delete_for_user(DEMO_USER_ID)

    assert [sessions.get(t) for t in mine] == [None, None]
    assert sessions.get(other) is not None


def test_verification_failures_are_counted(db) -> None:
    codes = FirestoreVerificationCodeRepository(db)
    codes.replace(EMPTY_USER_ID, "012345", NOW)

    assert [codes.record_failure(EMPTY_USER_ID) for _ in range(3)] == [1, 2, 3]
    assert codes.get(EMPTY_USER_ID).code == "012345"
    codes.delete(EMPTY_USER_ID)
    assert codes.get(EMPTY_USER_ID) is None


def test_movement_detail_matches_memory(db, seed) -> None:
    movements, memory = FirestoreMovementRepository(db), MovementRepository(seed)

    for movement_id in ("mov-29", "mov-30", "mov-99", "a/b", ".."):
        assert movements.get_by_account(DEMO_USER_ID, movement_id) == memory.get_by_account(DEMO_USER_ID, movement_id)
    assert movements.get_by_account(EMPTY_USER_ID, "mov-29") is None


def test_report_ids_continue_from_the_counter(db) -> None:
    atomic, reports = FirestoreAtomic(db), FirestoreMovementReportRepository(db)

    first, second = (
        atomic.run(
            lambda: reports.add(movement_id="mov-30", user_id=DEMO_USER_ID, description="No el reconec", created_at=NOW)
        )
        for _ in range(2)
    )

    assert (first.id, second.id) == ("rep-01", "rep-02")
    assert db.collection("movement_reports").document("rep-01").get().to_dict()["user_id"] == DEMO_USER_ID


# --- L'app sencera amb STORAGE=firestore --------------------------------------------


def test_data_survives_a_restart(project) -> None:
    with TestClient(create_app()) as client:
        headers = _login(client)
        balance = client.post("/api/topups", json={"amount": 1000}, headers=headers).json()["balance"]

    with TestClient(create_app()) as client:
        # La sessió també sobreviu (§8.2): el mateix token encara serveix.
        response = client.get("/api/home", headers=headers)

    assert response.status_code == 200
    assert response.json()["balance"] == balance


def test_dev_reset_writes_the_seed_again(app_client) -> None:
    headers = _login(app_client)
    seed_balance = app_client.get("/api/home", headers=headers).json()["balance"]
    app_client.post("/api/topups", json={"amount": 1000}, headers=headers)

    app_client.post("/api/dev/reset")

    assert app_client.get("/api/home", headers=headers).json()["code"] == "UNAUTHENTICATED"
    assert app_client.get("/api/home", headers=_login(app_client)).json()["balance"] == seed_balance


def test_contribution_moves_the_money_and_keeps_the_history(app_client) -> None:
    headers = _login(app_client)
    before = app_client.get("/api/home", headers=headers).json()
    [pot] = [p for p in app_client.get("/api/pots", headers=headers).json()["items"] if p["id"] == "pot-01"]

    response = app_client.post("/api/pots/pot-01/contributions", json={"amount": 3000}, headers=headers)

    assert response.status_code == 201
    body = response.json()
    assert body["balance"] == before["balance"] - 3000
    assert body["pot"]["balance"] == pot["balance"] + 3000
    history = app_client.get("/api/pots/pot-01/movements", headers=headers).json()["items"]
    assert history[0]["amount"] == 3000
    home = app_client.get("/api/home", headers=headers).json()
    assert home["balance"] == body["balance"]
    assert home["lastMovements"][0]["id"] == body["movement"]["id"]


def test_simultaneous_contributions_never_leave_a_negative_balance(app_client) -> None:
    headers = _login(app_client)
    balance = app_client.get("/api/home", headers=headers).json()["balance"]
    amount = balance // 2 + 1  # dues alhora no hi caben
    barrier = threading.Barrier(2)
    codes: list[int] = []

    def attempt() -> None:
        barrier.wait()
        codes.append(
            app_client.post("/api/pots/pot-01/contributions", json={"amount": amount}, headers=headers).status_code
        )

    threads = [threading.Thread(target=attempt) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert sorted(codes) == [201, 422]
    assert app_client.get("/api/home", headers=headers).json()["balance"] == balance - amount


def test_register_verify_and_reset_password(app_client) -> None:
    body = {"identifier": "ana@x.com", "password": "Platja2026", "acceptedTerms": True}
    assert app_client.post("/api/auth/register", json=body).status_code == 201
    assert app_client.post("/api/auth/register", json=body).json()["code"] == "ALREADY_REGISTERED"

    [message] = app_client.get("/api/dev/outbox", params={"to": "ana@x.com"}).json()["messages"]
    verified = app_client.post("/api/auth/verify", json={"identifier": "ana@x.com", "code": message["code"]})
    assert verified.status_code == 200
    headers = {"Authorization": f"Bearer {verified.json()['token']}"}
    assert app_client.get("/api/home", headers=headers).json()["balance"] == 0

    app_client.post("/api/auth/forgot-password", json={"identifier": "ana@x.com"})
    link = app_client.get("/api/dev/outbox", params={"to": "ana@x.com"}).json()["messages"][0]["link"]
    token = link.split("token=")[1]
    assert (
        app_client.post("/api/auth/reset-password", json={"token": token, "password": "NovaClau2026"}).status_code
        == 200
    )

    assert app_client.get("/api/home", headers=headers).json()["code"] == "UNAUTHENTICATED"
    login = app_client.post("/api/auth/login", json={"identifier": "ana@x.com", "password": "NovaClau2026"})
    assert login.status_code == 200


def test_movement_detail_and_report(app_client) -> None:
    headers = _login(app_client)

    detail = app_client.get("/api/movements/mov-29", headers=headers).json()
    report = app_client.post(
        "/api/movements/mov-30/reports", json={"description": "  No el reconec  "}, headers=headers
    )

    assert (detail["counterparty"], detail["reference"]) == ("Núria Soler", "EVT-000029")
    assert report.status_code == 201
    assert (report.json()["id"], report.json()["description"]) == ("rep-01", "No el reconec")
    assert app_client.get("/api/movements/mov-99", headers=headers).json()["code"] == "MOVEMENT_NOT_FOUND"


def test_lockout_is_stored(app_client) -> None:
    for _ in range(5):
        last = app_client.post("/api/auth/login", json={"identifier": DEMO_IDENTIFIER, "password": "Dolenta2026"})

    assert last.status_code == 423
    assert "lockedUntil" in last.json()["details"]
    again = app_client.post("/api/auth/login", json={"identifier": DEMO_IDENTIFIER, "password": SEED_PASSWORD})
    assert again.status_code == 423


def test_closed_outbox_writes_nothing_to_firestore(project, monkeypatch) -> None:
    # Revisió de la #137: amb la bústia tancada, el codi i l'enllaç no queden a la base de dades.
    monkeypatch.setenv("ENABLE_DEV_OUTBOX", "false")
    with TestClient(create_app()) as client:
        body = {"identifier": "ana@x.com", "password": "Platja2026", "acceptedTerms": True}
        assert client.post("/api/auth/register", json=body).status_code == 201
        client.post("/api/auth/forgot-password", json={"identifier": DEMO_IDENTIFIER})

    assert list(firestore.Client(project=project).collection("outbox").list_documents()) == []
