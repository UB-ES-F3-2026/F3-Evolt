"""Repositori de moviments (T07.4).

Llegeix i escriu les dades en memòria del SeedData. No decideix regles de
negoci: això és feina dels serveis.
"""

from datetime import date, datetime

from app.data.seed import MADRID_TZ, SeedData, movement_id, movement_reference
from app.models import KIND_TOPUP, MOVEMENT_STATUS_COMPLETED, Movement, MovementFilters


class MovementRepository:
    """Moviments del compte principal (T07.4)."""

    def __init__(self, seed: SeedData) -> None:
        self._seed = seed

    def list_by_account(
        self,
        account_id: int,
        offset: int,
        limit: int,
        filters: MovementFilters | None = None,
    ) -> list[Movement]:
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
        Amb `filters`, s'apliquen abans de paginar (T10.3, §10.2).
        """
        if offset < 0 or limit < 1:
            raise ValueError("paginació invàlida: offset ha de ser ≥ 0 i limit ha de ser ≥ 1")
        ordered = sorted(self._filtered(account_id, filters), key=Movement.sort_key, reverse=True)
        return ordered[offset : offset + limit]

    def count_by_account(self, account_id: int, filters: MovementFilters | None = None) -> int:
        """Nombre de moviments d'un compte (T07.4).

        Existeix perquè T08.1 pugui calcular `nextOffset` (§4.2) sense
        carregar tots els moviments. Amb `filters`, només compta els que els
        compleixen: `nextOffset` es calcula sobre el resultat filtrat (T10.3, §10.2).
        """
        return len(self._filtered(account_id, filters))

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
        counterparty: str | None = None,
        status: str = MOVEMENT_STATUS_COMPLETED,
    ) -> Movement:
        """Crea i desa un moviment, i retorna l'objecte desat (T07.4).

        No toca el saldo: l'invariant financer balance == suma dels
        signed_amount el manté el servei, que canvia el compte i afegeix el
        moviment. Tot o res: si la construcció del Movement falla
        (__post_init__), no s'emmagatzema res i els comptadors no avancen.
        Els moviments nous neixen completats i sense contrapart (§10.1, P38).
        """
        number = self._seed.next_movement_number
        seq = self._seed.next_movement_seq
        # id, seq i reference són mecànica d'emmagatzematge (com un autoincrement), no
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
            counterparty=counterparty,
            status=status,
            reference=movement_reference(number),
        )
        # Només després de construir-lo correctament es consumeixen els
        # comptadors i es desa: així una entrada invàlida no deixa forats.
        self._seed.next_movement_number = number + 1
        self._seed.next_movement_seq = seq + 1
        self._seed.movements.append(movement)
        return movement

    def remove(self, movement: Movement) -> None:
        """Treu un moviment acabat de crear, per desfer una operació que ha fallat (T18.1).

        Si és l'últim que s'ha creat, els comptadors tornen enrere i no queda cap
        forat a la numeració. No toca el saldo: això també ho desfà el servei.
        """
        self._seed.movements.remove(movement)
        if movement.seq == self._seed.next_movement_seq - 1:
            self._seed.next_movement_seq = movement.seq
            self._seed.next_movement_number -= 1

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

    def _filtered(self, account_id: int, filters: MovementFilters | None) -> list[Movement]:
        """Moviments d'un compte que compleixen els filtres (ajudant intern) (T10.3)."""
        movements = self._by_account(account_id)
        if filters is None:
            return movements
        return [movement for movement in movements if filters.matches(movement)]

    def _by_account(self, account_id: int) -> list[Movement]:
        """Còpia filtrada dels moviments d'un compte (ajudant intern) (T07.4)."""
        return [movement for movement in self._seed.movements if movement.account_id == account_id]
