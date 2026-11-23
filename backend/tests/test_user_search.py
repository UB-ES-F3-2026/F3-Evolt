"""Tests de T13.2: l'@usuari, el seed de 8 usuaris i la cerca (docs/api.md §13.1 a §13.3 i §13.9).

Proves CU-01 a CU-23 de docs/proves-pagaments.md (la CU-21, sense sessió, és a
test_session_auth.py), més les regles pures de l'@usuari.

Executar des de backend/:  python -m pytest tests/test_user_search.py
"""

import pytest
from fastapi.testclient import TestClient

from app.data.seed import EMPTY_USER_ID, SEED_PASSWORD_HASH, SeedData
from app.models import IDENTIFIER_EMAIL, IDENTIFIER_PHONE, STATUS_ACTIVE
from app.repositories import UserRepository
from app.services.user_search import parse_public_user_id, public_user_id
from app.services.username import email_username_base, first_free, username_from_email

EMPTY_USER = {"X-User-Id": str(EMPTY_USER_ID)}
SUMMARY_KEYS = {"id", "name", "username"}
PASSWORD = "Platja2026"
# Llista inicial de l'usuari 1 (CU-01): tots els altres, pel nom visible.
INITIAL_LIST = ["Alicia", "Huabin", "Izan", "Jiajun", "Junhao", "Martí", "Usuari nou"]
HUABIN = {"id": "usr-04", "name": "Huabin", "username": "123huabin123"}
NOT_FOUND_BODY = {"code": "RECIPIENT_NOT_FOUND", "message": "No hem trobat aquest destinatari."}


def _seed(client: TestClient) -> SeedData:
    return client.app.state.seed


def _search(client: TestClient, q: str | None = None, headers: dict[str, str] | None = None) -> list[dict]:
    response = client.get("/api/users", params={} if q is None else {"q": q}, headers=headers)
    assert response.status_code == 200
    return response.json()["items"]


def _names(items: list[dict]) -> list[str | None]:
    return [item["name"] for item in items]


def _register(client: TestClient, identifier: str) -> None:
    response = client.post(
        "/api/auth/register",
        json={"identifier": identifier, "password": PASSWORD, "acceptedTerms": True},
    )
    assert response.status_code == 201


def _register_and_verify(client: TestClient, identifier: str) -> None:
    _register(client, identifier)
    code = client.get("/api/dev/outbox", params={"to": identifier}).json()["messages"][0]["code"]
    response = client.post("/api/auth/verify", json={"identifier": identifier, "code": code})
    assert response.status_code == 200


def _user_by_identifier(client: TestClient, identifier: str):
    # Pel repositori, no pel seed: així també funciona amb TEST_STORAGE=firestore,
    # on `app.state.seed` no existeix (CU-20 es prova als dos emmagatzematges).
    firestore = getattr(client.app.state, "firestore", None)
    if firestore is not None:
        from app.repositories.firestore import FirestoreUserRepository

        return FirestoreUserRepository(firestore).find_by_identifier(identifier)
    return UserRepository(_seed(client)).find_by_identifier(identifier)


# --- Llista inicial (§13.2) ---------------------------------------------------------------


def test_initial_list_is_everybody_else_by_name(client: TestClient) -> None:
    # CU-01: l'usuari 1 no hi surt.
    assert _names(_search(client)) == INITIAL_LIST


def test_results_only_have_id_name_and_username(client: TestClient) -> None:
    # CU-02: cap saldo, ni email, ni telèfon, ni XP.
    assert all(set(item) == SUMMARY_KEYS for item in _search(client))


@pytest.mark.parametrize("q", ["", "   "])
def test_empty_query_gives_the_initial_list(client: TestClient, q: str) -> None:
    # CU-03
    assert _names(_search(client, q)) == INITIAL_LIST


@pytest.mark.parametrize("q", ["@", "  @  "])
def test_a_bare_at_sign_is_not_a_search(client: TestClient, q: str) -> None:
    # §13.2 (#212b): un `@` sol no és cap text, així que no hi ha cap coincidència.
    # abans deia la llista inicial perquè `@` no té text després i buit coincideix amb tot.
    assert _search(client, q) == []


# --- Les quatre vies (§13.2) ----------------------------------------------------------------


@pytest.mark.parametrize("q", ["hua", "@hua", "@123HUABIN123"])
def test_search_by_username(client: TestClient, q: str) -> None:
    # CU-04
    assert _search(client, q) == [HUABIN]


@pytest.mark.parametrize("q", ["marti", "MARTÍ"])
def test_search_by_name_ignores_case_and_accents(client: TestClient, q: str) -> None:
    # CU-05
    assert _names(_search(client, q)) == ["Martí"]


@pytest.mark.parametrize("q", ["huabin@evolt.test", "  Huabin@Evolt.TEST  "])
def test_search_by_the_whole_email(client: TestClient, q: str) -> None:
    # CU-06
    assert _search(client, q) == [HUABIN]


@pytest.mark.parametrize("q", ["evolt.test", "huabin@"])
def test_part_of_an_email_finds_nobody(client: TestClient, q: str) -> None:
    # CU-07: la cerca no serveix per endevinar emails.
    assert _search(client, q) == []


@pytest.mark.parametrize("q", ["611 22 33 02", "+34 611 22 33 02", "611223302", "0034611223302"])
def test_search_by_phone_compares_the_last_9_digits(client: TestClient, q: str) -> None:
    # CU-08: amb i sense +34, i amb 0034.
    assert _search(client, q) == [HUABIN]


def test_unknown_phone_gives_no_results(client: TestClient) -> None:
    # CU-09: «No hi ha resultats» a la pantalla.
    assert _search(client, "612 34 56 78") == []


def test_fewer_than_9_digits_is_not_a_phone(client: TestClient) -> None:
    # CU-10
    assert _search(client, "11223302") == []


@pytest.mark.parametrize("q", ["Usuari demo", "@demo", "demo@evolt.test", "611 22 33 07"])
def test_i_never_appear_in_my_results(client: TestClient, q: str) -> None:
    # CU-11: el meu nom, el meu @usuari, el meu email i el meu telèfon.
    assert _search(client, q) == []


def test_my_name_matches_but_i_do_not_appear(client: TestClient) -> None:
    # CU-12: «Usuari demo» i «Usuari nou» hi coincideixen; només surt l'altre.
    assert _names(_search(client, "usuari")) == ["Usuari nou"]


def test_another_user_also_does_not_find_himself(client: TestClient) -> None:
    # CU-11, des de l'usuari 2: ell no hi surt, i l'usuari 1 sí.
    items = _search(client, headers=EMPTY_USER)

    assert "Usuari nou" not in _names(items)
    assert "Usuari demo" in _names(items)


# --- Límits (§13.2) -----------------------------------------------------------------------


def test_64_characters_is_still_a_search(client: TestClient) -> None:
    # CU-13
    assert client.get("/api/users", params={"q": "a" * 64}).status_code == 200


def test_65_characters_is_a_validation_error(client: TestClient) -> None:
    # CU-14
    response = client.get("/api/users", params={"q": "a" * 65})

    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"


@pytest.mark.memory_only
def test_at_most_10_results_by_name(client: TestClient) -> None:
    # CU-17: amb 12 usuaris més, la llista inicial es queda amb els 10 primers.
    users = UserRepository(_seed(client))
    for number in range(12):
        users.add(
            name=f"Zoe {number:02d}",
            identifier=f"zoe{number}@x.com",
            identifier_type=IDENTIFIER_EMAIL,
            password_hash=SEED_PASSWORD_HASH,
            status=STATUS_ACTIVE,
            username=f"zoe{number}",
        )

    names = _names(_search(client))

    assert names == INITIAL_LIST + ["Zoe 00", "Zoe 01", "Zoe 02"]


# --- Comptes pendents i usuaris sense nom ---------------------------------------------------


def test_a_pending_account_never_appears(client: TestClient) -> None:
    # CU-15
    _register(client, "anna@x.com")

    assert _search(client, "anna") == []
    assert _search(client, "anna@x.com") == []
    assert "anna" not in [item["username"] for item in _search(client)]


def test_a_verified_user_without_name_has_null_name(client: TestClient) -> None:
    # CU-16: la pantalla mostra l'@usuari com a nom.
    _register_and_verify(client, "anna@x.com")

    assert _search(client, "anna") == [{"id": "usr-09", "name": None, "username": "anna"}]


def test_usernames_come_from_the_email_and_never_repeat(client: TestClient) -> None:
    # CU-22
    _register_and_verify(client, "Anna.Puig+evolt@x.com")
    _register_and_verify(client, "anna.puigevolt@y.com")

    usernames = [item["username"] for item in _search(client, "anna.puigevolt")]

    assert usernames == ["anna.puigevolt", "anna.puigevolt2"]


def test_a_phone_user_is_usuari_and_its_id(client: TestClient) -> None:
    # CU-23: no es fa servir el telèfon per a l'@usuari.
    _register_and_verify(client, "600 11 22 33")

    assert _search(client, "600112233") == [{"id": "usr-09", "name": None, "username": "usuari9"}]


def test_no_two_users_can_share_a_username(client: TestClient) -> None:
    # §13.9 (#212c): l'@usuari és únic, també amb la forma de reserva `usuari<id>`
    # i amb el número que afegeix `first_free`.
    _register_and_verify(client, "600 11 22 33")  # usr-09: sense @usuari desat → usuari9
    _register_and_verify(client, "usuari9@x.com")  # usr-10 → usuari9_, mai usuari9
    _register_and_verify(client, "usuari9_@x.com")  # usr-11 → usuari9_2, perquè usuari9_ ja hi és

    usernames = [client.get(f"/api/users/usr-{user_id:02d}").json()["username"] for user_id in range(1, 12)]

    assert usernames[8:] == ["usuari9", "usuari9_", "usuari9_2"]
    assert len(set(usernames)) == len(usernames)


# --- GET /api/users/{userId} (§13.3) ---------------------------------------------------------


def test_get_one_user(client: TestClient) -> None:
    # CU-18
    response = client.get("/api/users/usr-04")

    assert response.status_code == 200
    assert response.json() == HUABIN


def test_get_yourself_also_works(client: TestClient) -> None:
    # §13.3: no és cap dada nova; qui impedeix enviar-se diners és l'enviament.
    assert client.get("/api/users/usr-01").json()["username"] == "demo"


@pytest.mark.parametrize("public_id", ["usr-99", "4", "huabin", "usr-4", "usr-004"])
def test_unknown_or_badly_formed_id_is_not_found(client: TestClient, public_id: str) -> None:
    # CU-19
    response = client.get(f"/api/users/{public_id}")

    assert response.status_code == 404
    assert response.json() == NOT_FOUND_BODY


def test_a_pending_user_is_not_found(client: TestClient) -> None:
    # CU-20
    _register(client, "anna@x.com")
    pending_id = public_user_id(_user_by_identifier(client, "anna@x.com").id)

    assert client.get(f"/api/users/{pending_id}").json() == NOT_FOUND_BODY


# --- Seed (§13.9) -------------------------------------------------------------------------


@pytest.mark.memory_only
def test_seed_users_have_their_team_alias_and_phone(client: TestClient) -> None:
    # CU-01 i §13.9: vuit usuaris actius, i el telèfon del mockup de US-13 és Huabin.
    users = {user.id: (user.name, user.username, user.phone) for user in _seed(client).users.values()}

    assert users == {
        1: ("Usuari demo", "demo", "+34611223307"),
        2: ("Usuari nou", "buit", "+34611223308"),
        3: ("Alicia", "aliciaa415", "+34611223301"),
        4: ("Huabin", "123huabin123", "+34611223302"),
        5: ("Izan", "izanfarreny47", "+34611223303"),
        6: ("Jiajun", "yayuuun", "+34611223304"),
        7: ("Junhao", "junhaozhang", "+34611223305"),
        8: ("Martí", "sudo-itramplay", "+34611223306"),
    }
    assert all(user.status == STATUS_ACTIVE for user in _seed(client).users.values())


@pytest.mark.memory_only
def test_team_users_can_log_in_and_start_at_zero(client: TestClient) -> None:
    # §13.9: la contrasenya del seed i el compte principal a 0.
    response = client.post("/api/auth/login", json={"identifier": "huabin@evolt.test", "password": "Evolt2026"})

    assert response.status_code == 200
    assert _seed(client).accounts[4].balance == 0


# --- Regles pures de l'@usuari (§13.9) -------------------------------------------------------


@pytest.mark.parametrize(
    ("email", "username"),
    [
        ("anna@x.com", "anna"),
        ("Anna.Puig+evolt@x.com", "anna.puigevolt"),
        ("joan_garcia-1@x.com", "joan_garcia-1"),
        ("àlex@x.com", "lex"),
        ("+++@x.com", ""),
    ],
)
def test_username_is_the_cleaned_local_part(email: str, username: str) -> None:
    assert username_from_email(email) == username


def test_phone_registrations_have_no_base() -> None:
    # Sense base, es mostra com a `usuari<id>`.
    assert email_username_base("+34600112233", IDENTIFIER_PHONE) == ""


def test_the_reserved_form_gets_an_underscore() -> None:
    # `usuari9` és el de l'usuari 9: un correu no se'l pot quedar.
    assert email_username_base("usuari9@x.com", IDENTIFIER_EMAIL) == "usuari9_"


@pytest.mark.parametrize("local", ["usuari9", "usuari123", "Usuari7", "usuari0"])
def test_the_reserved_form_is_never_a_registration_base(local: str) -> None:
    # §13.9 (#212c): com que la forma `usuari<xifres>` queda reservada, cap registre pot
    # fer-la servir d'`@usuari`, així que `is_username_taken` només ha de mirar els
    # `@usuari` desats (a Firestore, la col·lecció `usernames`): no hi pot haver xoc.
    assert email_username_base(f"{local}@x.com", IDENTIFIER_EMAIL) == f"{local.lower()}_"


def test_first_free_adds_the_first_free_number() -> None:
    taken = {"anna", "anna2"}

    assert first_free("anna", taken.__contains__) == "anna3"
    assert first_free("pau", taken.__contains__) == "pau"


@pytest.mark.parametrize(("raw", "user_id"), [("usr-04", 4), ("usr-123", 123), ("usr-4", None), ("4", None), ("", None)])
def test_public_ids_have_one_exact_form(raw: str, user_id: int | None) -> None:
    # P64
    assert parse_public_user_id(raw) == user_id
