"""Client de Firestore (TR01.1, docs/api.md §8.13).

Només el backend parla amb Firestore. On es connecta ho decideix l'entorn:

- Amb `FIRESTORE_EMULATOR_HOST` (p. ex. `127.0.0.1:8080`), a l'emulador local:
  no cal cap credencial. És el que fan el desenvolupament i els tests.
- Sense, al projecte real, amb les credencials del compte de servei de
  `GOOGLE_APPLICATION_CREDENTIALS` (fitxer fora del repositori; a Render, un
  «secret file»).
"""

from google.cloud import firestore


def create_client(project_id: str) -> firestore.Client:
    return firestore.Client(project=project_id)
