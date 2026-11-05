"""Tests de T11.1: detall del moviment i informe de problema (docs/api.md §10.3 i §10.4).

Proves D-01 a D-07 i I-01 a I-10 de docs/proves-moviments.md, més el model
`MovementReport` i els repositoris.

Executar des de backend/:  python -m pytest tests/test_movement_detail.py
"""

from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from app.data.seed import DEMO_USER_ID, EMPTY_USER_ID, SeedData, build_seed
from app.main import create_app
from app.models import MADRID_TZ, MAX_REPORT_DESCRIPTION, MovementReport
from app.repositories import AccountRepository, MovementReportRepository, MovementRepository
from app.services.errors import MOVEMENT_NOT_FOUND, ApiError
from app.services.movement_service import report_movement

# T0 de docs/proves-moviments.md: les dates del seed són relatives a aquest dia.
T0 = datetime(2026, 11, 3, 10, 0, 0, tzinfo=MADRID_TZ)
EMPTY_USER = {"X-User-Id": str(EMPTY_USER_ID)}
NOT_FOUND_BODY = {"code": "MOVEMENT_NOT_FOUND", "message": "No s'ha trobat el moviment."}
INVALID_BODY = {
    "code": "INVALID_DESCRIPTION",
    "message": "Explica què passa amb el moviment (com a màxim 500 caràcters).",
}
REPORT_KEYS = {"id", "movementId", "description", "createdAt"}


@pytest.fixture
def seed(client: TestClient) -> SeedData:
    """Seed de les proves, amb el rellotge a T0. Els repositoris el llegeixen a cada petició."""
    fixed = build_seed(now=T0)
    client.app.state.seed = fixed
    return fixed


def _report(client: TestClient, movement_id: str, description, headers: dict[str, str] | None = None):
    return client.post(f"/api/movements/{movement_id}/reports", json={"description": description}, headers=headers)


def _state(seed: SeedData):
    """Estat que un informe rebutjat no pot canviar."""
    return (list(seed.movement_reports), seed.next_report_number)


# --- Detall (§10.3) ---------------------------------------------------------------------


def test_detail_is_the_whole_movement(client: TestClient, seed: SeedData) -> None:
    # D-01
    response = client.get("/api/movements/mov-29")

    assert response.status_code == 200
    assert response.json() == {
        "id": "mov-29",
        "amount": 1000,
        "concept": "Bizum enviat",
        "date": "2026-11-01T18:42:00+01:00",
        "type": "expense",
        "icon": "transfer",
        "counterparty": "Núria Soler",
        "status": "completed",
        "reference": "EVT-000029",
    }


def test_detail_of_the_pending_movement(client: TestClient, seed: SeedData) -> None:
    # D-02
    body = client.get("/api/movements/mov-30").json()

    assert body["status"] == "pending"
    assert body["counterparty"] is None


@pytest.mark.parametrize("movement_id", ["mov-99", "abc", "rep-01", "EVT-000029"])
def test_unknown_movement_is_not_found(client: TestClient, seed: SeedData, movement_id: str) -> None:
    # D-03 i D-05: també un id amb un format qualsevol.
    response = client.get(f"/api/movements/{movement_id}")

    assert response.status_code == 404
    assert response.json() == NOT_FOUND_BODY


def test_movement_of_another_user_looks_like_an_unknown_one(client: TestClient, seed: SeedData) -> None:
    # D-04: el mateix cos que D-03.
    response = client.get("/api/movements/mov-29", headers=EMPTY_USER)

    assert response.status_code == 404
    assert response.json() == NOT_FOUND_BODY


def test_detail_is_the_same_object_as_in_the_list(client: TestClient, seed: SeedData) -> None:
    # D-06, amb tots els moviments del seed.
    listed = client.get("/api/movements", params={"limit": 50}).json()["items"]

    assert len(listed) == 30
    for item in listed:
        assert client.get(f"/api/movements/{item['id']}").json() == item


def test_detail_of_a_new_topup(client: TestClient, seed: SeedData) -> None:
    # D-07
    created = client.post("/api/topups", json={"amount": 1000}).json()["movement"]

    body = client.get(f"/api/movements/{created['id']}").json()

    assert body == created
    assert (body["id"], body["status"], body["counterparty"]) == ("mov-31", "completed", None)
    assert body["reference"] == "EVT-000031"


def test_detail_of_a_new_contribution(client: TestClient, seed: SeedData) -> None:
    created = client.post("/api/pots/pot-01/contributions", json={"amount": 1000}).json()["movement"]

    assert client.get(f"/api/movements/{created['id']}").json() == created


# --- Informe (§10.4) --------------------------------------------------------------------


def test_report_is_saved_and_follows_the_contract(client: TestClient, seed: SeedData) -> None:
    # I-01
    response = _report(client, "mov-30", "No reconec aquest pagament")

    assert response.status_code == 201
    body = response.json()
    assert set(body) == REPORT_KEYS
    assert body["id"] == "rep-01"
    assert body["movementId"] == "mov-30"
    assert body["description"] == "No reconec aquest pagament"
    # 2026-11-03T10:00:00+01:00: desplaçament de Madrid i precisió de segons (P7).
    assert body["createdAt"][-6:] in {"+02:00", "+01:00"}
    assert len(body["createdAt"]) == len("2026-11-03T10:00:00+01:00")


def test_report_uses_the_given_moment() -> None:
    # I-01: el `createdAt` de les proves, amb el rellotge fixat.
    seed = build_seed(now=T0)

    report = report_movement(
        DEMO_USER_ID,
        "mov-30",
        "No reconec aquest pagament",
        AccountRepository(seed),
        MovementRepository(seed),
        MovementReportRepository(seed),
        now=T0,
    )

    assert report.created_at.isoformat() == "2026-11-03T10:00:00+01:00"


def test_report_is_linked_to_the_movement_and_the_user(client: TestClient, seed: SeedData) -> None:
    # I-02
    _report(client, "mov-30", "No reconec aquest pagament")

    assert [(r.movement_id, r.user_id, r.description) for r in seed.movement_reports] == [
        ("mov-30", DEMO_USER_ID, "No reconec aquest pagament")
    ]


@pytest.mark.parametrize("description", ["", "   ", "\t\n", " " * 600])
def test_empty_description_saves_nothing(client: TestClient, seed: SeedData, description: str) -> None:
    # I-03
    before = _state(seed)

    response = _report(client, "mov-30", description)

    assert response.status_code == 422
    assert response.json() == INVALID_BODY
    assert _state(seed) == before


def test_description_over_the_limit_saves_nothing(client: TestClient, seed: SeedData) -> None:
    # I-04
    before = _state(seed)

    response = _report(client, "mov-30", "a" * (MAX_REPORT_DESCRIPTION + 1))

    assert response.status_code == 422
    assert response.json() == INVALID_BODY
    assert _state(seed) == before


def test_description_at_the_limit_is_accepted(client: TestClient, seed: SeedData) -> None:
    # I-04
    response = _report(client, "mov-30", "a" * MAX_REPORT_DESCRIPTION)

    assert response.status_code == 201


def test_the_limit_counts_after_taking_the_spaces_out(client: TestClient, seed: SeedData) -> None:
    # §10.4: 500 caràcters un cop trets els espais dels extrems.
    description = "  " + "a" * MAX_REPORT_DESCRIPTION + "  "

    response = _report(client, "mov-30", description)

    assert response.status_code == 201
    assert response.json()["description"] == "a" * MAX_REPORT_DESCRIPTION


@pytest.mark.parametrize("body", [{}, {"description": 123}, {"description": None}, {"description": ["a"]}])
def test_badly_formed_body_is_a_validation_error(client: TestClient, seed: SeedData, body: dict[str, object]) -> None:
    # I-05
    before = _state(seed)

    response = client.post("/api/movements/mov-30/reports", json=body)

    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"
    assert _state(seed) == before


def test_report_on_a_movement_of_another_user_saves_nothing(client: TestClient, seed: SeedData) -> None:
    # I-06
    before = _state(seed)

    response = _report(client, "mov-29", "No el reconec", headers=EMPTY_USER)

    assert response.status_code == 404
    assert response.json() == NOT_FOUND_BODY
    assert _state(seed) == before


def test_movement_is_checked_before_the_description(client: TestClient, seed: SeedData) -> None:
    # I-07
    response = _report(client, "mov-99", "")

    assert response.status_code == 404
    assert response.json() == NOT_FOUND_BODY


def test_format_is_checked_before_the_movement(client: TestClient, seed: SeedData) -> None:
    # Ordre del §10.4: el format va primer.
    response = client.post("/api/movements/mov-99/reports", json={"description": 123})

    assert response.json()["code"] == "VALIDATION_ERROR"


def test_a_movement_can_have_several_reports(client: TestClient, seed: SeedData) -> None:
    # I-08
    first = _report(client, "mov-30", "Primer")
    second = _report(client, "mov-30", "Segon")

    assert (first.status_code, second.status_code) == (201, 201)
    assert (first.json()["id"], second.json()["id"]) == ("rep-01", "rep-02")


def test_description_is_saved_without_the_spaces_at_the_ends(client: TestClient, seed: SeedData) -> None:
    # I-09
    response = _report(client, "mov-30", "  No el reconec  ")

    assert response.status_code == 201
    assert response.json()["description"] == "No el reconec"
    assert seed.movement_reports[0].description == "No el reconec"


def test_rejected_report_does_not_spend_an_id(client: TestClient, seed: SeedData) -> None:
    assert _report(client, "mov-30", "").status_code == 422
    assert _report(client, "mov-99", "No el reconec").status_code == 404

    assert _report(client, "mov-30", "No el reconec").json()["id"] == "rep-01"


def test_reset_deletes_the_reports(client: TestClient) -> None:
    # I-10
    _report(client, "mov-30", "No reconec aquest pagament")

    client.post("/api/dev/reset")

    assert client.app.state.seed.movement_reports == []
    assert _report(client, "mov-30", "Un altre").json()["id"] == "rep-01"


def test_report_does_not_change_the_movement_or_the_money(client: TestClient, seed: SeedData) -> None:
    movement = client.get("/api/movements/mov-30").json()
    home = client.get("/api/home").json()

    _report(client, "mov-30", "No reconec aquest pagament")

    assert client.get("/api/movements/mov-30").json() == movement
    assert client.get("/api/home").json() == home


# --- Rutes protegides -------------------------------------------------------------------


def test_routes_need_a_session_without_x_user_id(monkeypatch: pytest.MonkeyPatch) -> None:
    # §8.2: són rutes protegides, com la resta de dades de l'usuari.
    monkeypatch.setenv("ALLOW_X_USER_ID", "false")

    with TestClient(create_app()) as client:
        detail = client.get("/api/movements/mov-29")
        report = _report(client, "mov-29", "No el reconec")
        assert client.app.state.seed.movement_reports == []

        login = client.post("/api/auth/login", json={"identifier": "demo@evolt.test", "password": "Evolt2026"})
        auth = {"Authorization": f"Bearer {login.json()['token']}"}
        with_token = client.get("/api/movements/mov-29", headers=auth)
        report_with_token = _report(client, "mov-29", "No el reconec", headers=auth)

    assert (detail.status_code, report.status_code) == (401, 401)
    assert detail.json()["code"] == report.json()["code"] == "UNAUTHENTICATED"
    assert (with_token.status_code, report_with_token.status_code) == (200, 201)


# --- Model i repositoris ----------------------------------------------------------------


def _report_kwargs(**overrides):
    """Arguments per defecte d'un informe vàlid."""
    kwargs = {
        "id": "rep-99",
        "movement_id": "mov-30",
        "user_id": DEMO_USER_ID,
        "description": "No el reconec",
        "created_at": T0,
    }
    kwargs.update(overrides)
    return kwargs


@pytest.mark.parametrize(
    "overrides, error",
    [
        ({"id": ""}, TypeError),
        ({"id": 1}, TypeError),
        ({"movement_id": ""}, TypeError),
        ({"description": "   "}, ValueError),
        ({"description": 5}, ValueError),
        ({"description": "a" * (MAX_REPORT_DESCRIPTION + 1)}, ValueError),
        ({"created_at": datetime(2026, 11, 3, 10, 0, 0)}, ValueError),
        ({"created_at": T0.replace(microsecond=1)}, ValueError),
    ],
)
def test_report_model_rejects_invalid_values(overrides, error) -> None:
    with pytest.raises(error):
        MovementReport(**_report_kwargs(**overrides))


def test_repository_add_with_invalid_values_stores_nothing() -> None:
    seed = build_seed(now=T0)

    with pytest.raises(ValueError):
        MovementReportRepository(seed).add(movement_id="mov-30", user_id=DEMO_USER_ID, description=" ", created_at=T0)

    assert seed.movement_reports == []
    assert seed.next_report_number == 1


def test_get_by_account_only_finds_the_movements_of_that_account() -> None:
    seed = build_seed(now=T0)
    movements = MovementRepository(seed)

    assert movements.get_by_account(seed.accounts[DEMO_USER_ID].id, "mov-29").concept == "Bizum enviat"
    assert movements.get_by_account(seed.accounts[EMPTY_USER_ID].id, "mov-29") is None
    assert movements.get_by_account(seed.accounts[DEMO_USER_ID].id, "mov-99") is None


def test_service_raises_not_found_for_a_movement_of_another_user() -> None:
    seed = build_seed(now=T0)

    with pytest.raises(ApiError) as error:
        report_movement(
            EMPTY_USER_ID,
            "mov-29",
            "No el reconec",
            AccountRepository(seed),
            MovementRepository(seed),
            MovementReportRepository(seed),
        )

    assert error.value.code == MOVEMENT_NOT_FOUND
    assert seed.movement_reports == []
