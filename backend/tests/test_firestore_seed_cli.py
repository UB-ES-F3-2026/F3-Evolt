"""Comanda que torna un projecte de Firestore al seed (docs/deploy.md, «Release with seed changes»).

Només es prova la guarda: amb un projecte mal confirmat no es connecta a cap Firestore.
"""

import pytest

# La comanda importa google-cloud-firestore (requirements.txt): sense el paquet, es salta.
pytest.importorskip("google.cloud.firestore")

from app.data import firestore_seed  # noqa: E402


def test_a_mismatched_confirmation_touches_nothing(monkeypatch: pytest.MonkeyPatch) -> None:
    def no_client(*args, **kwargs):
        raise AssertionError("no s'havia de connectar a Firestore")

    monkeypatch.setattr(firestore_seed.firestore, "Client", no_client)

    assert firestore_seed.main(["--project", "evolt-prod", "--confirm", "evolt-dev"]) == 2


def test_the_project_is_required() -> None:
    with pytest.raises(SystemExit):
        firestore_seed.main(["--confirm", "evolt-prod"])


def test_a_matching_confirmation_resets_that_project(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []
    monkeypatch.setattr(firestore_seed.firestore, "Client", lambda project: f"client:{project}")
    monkeypatch.setattr(firestore_seed, "reset", lambda client: calls.append(client))

    assert firestore_seed.main(["--project", "evolt-prod", "--confirm", "evolt-prod"]) == 0
    assert calls == ["client:evolt-prod"]
