"""Seed i reinici a Firestore (TR01.1, docs/api.md §4.4 i §8.13).

Les dades són les mateixes de `build_seed()`: usuaris, comptes, guardioles amb el
seu historial, moviments, subcomptes en divisa i el seu historial (cap, T25.2 i T26.1), i
els comptadors per als ids nous.

- `ensure_seeded`: a l'arrencada, només si la base de dades és buida. Les dades
  es conserven entre reinicis del backend.
- `reset`: per a `POST /api/dev/reset`. Esborra **totes** les col·leccions i hi
  torna a escriure el seed: només amb l'emulador o el projecte de desenvolupament.
- `main`: el mateix `reset` a mà, per a una release que canvia el seed
  (docs/deploy.md, «Release with seed changes»). Demana el projecte dues vegades.
"""

import argparse
import sys

from google.cloud import firestore

from app.data.seed import SeedData, build_seed
from app.repositories.firestore import _tx
from app.repositories.firestore.account import ACCOUNTS, account_to_dict
from app.repositories.firestore.movement import MOVEMENTS, NUMBER_COUNTER, SEQ_COUNTER, movement_to_dict
from app.repositories.firestore.movement_report import MOVEMENT_REPORTS, REPORT_COUNTER
from app.repositories.firestore.outbox import OUTBOX, OUTBOX_COUNTER
from app.repositories.firestore.password_reset import PASSWORD_RESET_TOKENS
from app.repositories.firestore.pot import (
    POT_COUNTER,
    POT_MOVEMENT_COUNTER,
    POT_MOVEMENTS,
    POTS,
    pot_movement_to_dict,
    pot_to_dict,
)
from app.repositories.firestore.session import SESSIONS
from app.repositories.firestore.subaccount import (
    SUBACCOUNT_COUNTER,
    SUBACCOUNT_MOVEMENT_COUNTER,
    SUBACCOUNT_MOVEMENTS,
    SUBACCOUNTS,
    subaccount_movement_to_dict,
    subaccount_to_dict,
)
from app.repositories.firestore.user import (
    USER_COUNTER,
    USER_IDENTIFIERS,
    USERNAMES,
    USERS,
    identifier_key,
    user_to_dict,
)
from app.repositories.firestore.verification_code import VERIFICATION_CODES

COLLECTIONS = (
    USERS,
    USER_IDENTIFIERS,
    USERNAMES,
    ACCOUNTS,
    POTS,
    POT_MOVEMENTS,
    MOVEMENTS,
    MOVEMENT_REPORTS,
    SESSIONS,
    VERIFICATION_CODES,
    OUTBOX,
    PASSWORD_RESET_TOKENS,
    SUBACCOUNTS,
    SUBACCOUNT_MOVEMENTS,
    _tx.COUNTERS,
)


def is_seeded(client: firestore.Client) -> bool:
    """Els comptadors només existeixen si ja s'ha escrit el seed."""
    return _tx.counters_ref(client).get().exists


def ensure_seeded(client: firestore.Client) -> None:
    if not is_seeded(client):
        write_seed(client, build_seed())


def reset(client: firestore.Client) -> None:
    for name in COLLECTIONS:
        for document in client.collection(name).list_documents():
            document.delete()
    write_seed(client, build_seed())


def write_seed(client: firestore.Client, seed: SeedData) -> None:
    """Escriu tot el seed en un sol lot: o hi és tot, o no hi és res.

    El seed no té sessions, codis, missatges, enllaços ni informes: neixen buits.
    """
    batch = client.batch()
    for user in seed.users.values():
        batch.set(client.collection(USERS).document(str(user.id)), user_to_dict(user))
        batch.set(
            client.collection(USER_IDENTIFIERS).document(identifier_key(user.identifier)),
            {"user_id": user.id},
        )
        if user.username:
            batch.set(client.collection(USERNAMES).document(user.username), {"user_id": user.id})
    for user_id, account in seed.accounts.items():
        batch.set(client.collection(ACCOUNTS).document(str(user_id)), account_to_dict(account))
    for number, pot in enumerate(seed.pots, start=1):
        batch.set(client.collection(POTS).document(pot.id), pot_to_dict(pot, number))
    for entry in seed.pot_movements:
        batch.set(client.collection(POT_MOVEMENTS).document(entry.id), pot_movement_to_dict(entry))
    for movement in seed.movements:
        batch.set(client.collection(MOVEMENTS).document(movement.id), movement_to_dict(movement))
    for subaccount in seed.subaccounts:
        batch.set(client.collection(SUBACCOUNTS).document(subaccount.id), subaccount_to_dict(subaccount))
    for entry in seed.subaccount_movements:
        batch.set(client.collection(SUBACCOUNT_MOVEMENTS).document(entry.id), subaccount_movement_to_dict(entry))
    batch.set(
        _tx.counters_ref(client),
        {
            USER_COUNTER: seed.next_user_id,
            NUMBER_COUNTER: seed.next_movement_number,
            SEQ_COUNTER: seed.next_movement_seq,
            POT_COUNTER: seed.next_pot_number,
            POT_MOVEMENT_COUNTER: seed.next_pot_movement_number,
            OUTBOX_COUNTER: 1,
            REPORT_COUNTER: seed.next_report_number,
            SUBACCOUNT_COUNTER: seed.next_subaccount_number,
            SUBACCOUNT_MOVEMENT_COUNTER: seed.next_subaccount_movement_number,
        },
    )
    batch.commit()


def main(argv: list[str] | None = None) -> int:
    """Torna un projecte de Firestore al seed: esborra **totes** les dades.

    Només per a una release que canvia el seed (docs/deploy.md). El projecte s'ha
    d'escriure dues vegades: si no coincideixen, no es connecta ni s'esborra res.
    """
    parser = argparse.ArgumentParser(prog="python -m app.data.firestore_seed")
    parser.add_argument("--project", required=True, help="id del projecte de Firestore")
    parser.add_argument("--confirm", required=True, help="el mateix id, una altra vegada")
    args = parser.parse_args(argv)
    if args.confirm != args.project:
        print("--project i --confirm no coincideixen: no s'esborra res.", file=sys.stderr)
        return 2
    reset(firestore.Client(project=args.project))
    print(f"Seed escrit de nou a {args.project}: totes les dades anteriors s'han esborrat.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
