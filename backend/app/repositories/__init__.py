"""Repositoris en memòria (T07.4). Única capa que llegeix i escriu les dades del seed; els serveis no accedeixen mai a seed.py directament."""

from app.repositories.account import AccountRepository
from app.repositories.movement import MovementRepository
from app.repositories.pot import PotRepository

__all__ = ["AccountRepository", "MovementRepository", "PotRepository"]
