"""Repositori de moviments (T07.4).

Llegeix i escriu les dades en memòria del SeedData. No decideix regles de
negoci: això és feina dels serveis.
"""

from datetime import date, datetime

from app.data.seed import MADRID_TZ, SeedData, movement_id
from app.models import KIND_TOPUP, Movement


class MovementRepository:
    """Moviments del compte principal (T07.4)."""

    def __init__(self, seed: SeedData) -> None:
        self._seed = seed

    def list_by_account(self, account_id: int, offset: int, limit: int) -> list[Movement]:
        """Moviments d'un compte en pàgina, del més recent al més antic (T07.4).

        Ordena per `date` descendent i, si dues dates coincideixen, va primer
        el creat més tard (seq més gran) (P4, §4.2). Un `offset` ≥ total no és
        error: retorna `[]` (P3, §4.2). Els moviments que torna són objectes
        vius del seed: les escriptures s'han de fer a través del repositori.

        El desordre d'`offset`/`limit` és error de programació i es rebutja amb
        ValueError: la validació que el contracte converteix en
        422 VALIDATION_ERROR (offset ≥ 0, limit 1–50) la fa el router/servei
        (T08.1, §4.2). S'ordenen els moviments en llegir, no en escriure.
        El filtre és l'`account_id` (els moviments el porten): resoldre
        usuari → compte és feina d'AccountRepository.
        """
        if offset < 0 or limit < 1:
            raise ValueError("paginació invàlida: offset ha de ser ≥ 0 i limit ha de ser ≥ 1")
        ordered = sorted(self._by_account(account_id), key=Movement.sort_key, reverse=True)
        return ordered[offset : offset + limit]

    def count_by_account(self, account_id: int) -> int:
        """Nombre de moviments d'un compte (T07.4).

        Existeix perquè T08.1 pugui calcular `nextOffset` (§4.2) sense
        carregar tots els moviments.
        """
        return len(self._by_account(account_id))

    def add(
        self,
        *,
        account_id: int,
        amount: int,
        concept: str,
        date: datetime,
        type: str,
        icon: str,
        kind: str,
    ) -> Movement:
        """Crea i desa un moviment, i retorna l'objecte desat (T07.4).

        No toca el saldo: l'invariant financer balance == suma dels
        signed_amount el manté el servei, que canvia el compte i afegeix el
        moviment. Tot o res: si la construcció del Movement falla
        (__post_init__), no s'emmagatzema res i els comptadors no avancen.
        """
        number = self._seed.next_movement_number
        seq = self._seed.next_movement_seq
        # id i seq són mecànica d'emmagatzematge (com un autoincrement), no
        # una regla de negoci: els decideix el repositori.
        movement = Movement(
            id=movement_id(number),
            account_id=account_id,
            amount=amount,
            concept=concept,
            date=date,
            type=type,
            icon=icon,
            kind=kind,
            seq=seq,
        )
        # Només després de construir-lo correctament es consumeixen els
        # comptadors i es desa: així una entrada invàlida no deixa forats.
        self._seed.next_movement_number = number + 1
        self._seed.next_movement_seq = seq + 1
        self._seed.movements.append(movement)
        return movement

    def sum_topups_on_day(self, account_id: int, day: date) -> int:
        """Suma de les recàrregues d'un compte en un dia natural de Madrid (T07.4).

        Filtra per `kind == "topup"` i per la `date` dins del dia natural a
        Europe/Madrid (§6, §1), mai pel text del concepte. `kind == topup`
        implica `type == income`, de manera que `amount` ja és positiu.
        Quin dia és "avui" el tria el servei: el repositori no crida
        `datetime.now()`. `astimezone(MADRID_TZ)` fa el càlcul segur amb el
        canvi d'hora (DST), igual que el frontend.
        """
        return sum(
            movement.amount
            for movement in self._by_account(account_id)
            if movement.kind == KIND_TOPUP
            and movement.date.astimezone(MADRID_TZ).date() == day
        )

    def _by_account(self, account_id: int) -> list[Movement]:
        """Còpia filtrada dels moviments d'un compte (ajudant intern) (T07.4)."""
        return [movement for movement in self._seed.movements if movement.account_id == account_id]
