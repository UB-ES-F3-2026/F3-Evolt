"""Hash de contrasenyes amb bcrypt (docs/api.md §8.4).

L'únic lloc del backend que importa `bcrypt`: el registre en fa el hash i el
login (T03.1) el comprova. La contrasenya en clar no surt mai d'aquí.
"""

import bcrypt


def hash_password(password: str) -> str:
    """Hash de bcrypt amb una sal nova, com a text per poder-lo desar.

    Qui crida ha de comprovar abans `fits_password_hash` (72 bytes com a màxim).
    """
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("ascii")


def verify_password(password: str, password_hash: str) -> bool:
    """Comprova una contrasenya contra el hash desat (en temps constant).

    Com `hash_password`, només accepta contrasenyes de 72 bytes com a màxim:
    bcrypt 5 llança `ValueError` amb una de més llarga.
    """
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("ascii"))
