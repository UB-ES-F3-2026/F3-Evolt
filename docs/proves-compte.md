# Proves d'acceptació · Dades del compte (US-12)

Proves d'acceptació de consultar l'IBAN i de rebre una transferència d'un altre banc, escrites a partir de la història (`docs/us/US-12.md`) i del contracte de l'[apartat 16 de `docs/api.md`](api.md#16-dades-del-compte-us-12). Tasca: T12.1 (issue #292).

## Índex

1. [Com fer servir aquest document](#com-fer-servir-aquest-document)
2. [Dades de partida](#dades-de-partida)
3. [US-12 · Dades del compte (IBAN)](#us-12--dades-del-compte-iban)
4. [Criteris d'acceptació i proves](#criteris-dacceptació-i-proves)

---

## Com fer servir aquest document

- **API:** proves del backend. Cada fila es converteix en un test de pytest a la tasca indicada, amb l'id de la prova al nom o al comentari del test (skill `qa-strategy`). Els esperats surten del seed, escrits tal qual.
- **Pantalla:** proves del frontend. Es comproven a mà amb l'app arrencada a 375 px i, quan es pugui, amb un test de Vitest del ViewModel.

L'usuari de cada petició és el de la sessió (`Authorization: Bearer`, [`api.md` §8.2](api.md#82-sessió)). Els tests de pytest el posen amb la capçalera `X-User-Id`, que §8.2 permet als tests (`ALLOW_X_USER_ID`); IB-07 prova la ruta sense aquesta capçalera. «Usuari 1» és `demo@evolt.test` i «usuari 2», `buit@evolt.test`; tots els usuaris del seed tenen la contrasenya `Evolt2026` (P13). La ruta `POST /api/dev/incoming-transfers` no demana sessió.

## Dades de partida

- Seed acabat de carregar (`POST /api/dev/reset` o un client nou de pytest), amb els vuit usuaris de [`api.md` §13.9](api.md#139-model-intern) i els IBAN de la taula de [§16.2](api.md#162-com-es-fa-liban).
- Usuari 1: saldo 3.795,21 € (`379521`) i 30 moviments; el següent és `mov-31`.
- Rutes de desenvolupament actives (`ENABLE_DEV_ROUTES` sense definir), excepte a IB-19.
- Rellotge fixat a **T0 = `2026-11-15T21:15:00+01:00`** a les proves que miren la data del moviment.

---

## US-12 · Dades del compte (IBAN)

### API (T12.2)

| Id | Situació inicial | Acció | Resultat esperat |
|---|---|---|---|
| **IB-01** | Seed | `GET /api/account` (usuari 1) | `200` `{ "iban": "ES9121000418450200051332", "bic": "EVOLESB1XXX", "holder": "Usuari demo" }`. |
| **IB-02** | Seed | Mirar la resposta d'IB-01 | Té exactament les claus `iban`, `bic` i `holder`. |
| **IB-03** | Seed | `GET /api/account` amb cadascun dels vuit usuaris | Els IBAN de la taula de §16.2, tots diferents. Cadascun té 24 caràcters, els dos dígits de control del CCC correctes i residu 1 entre 97. |
| **IB-04** | Seed | Demanar-lo dues vegades, i una altra després de `POST /api/dev/reset` | Sempre el mateix IBAN. |
| **IB-05** | Seed | Registrar i verificar un usuari nou (US-01) i demanar-ne les dades | El seu IBAN és el de `n = 9`: `ES9621000418430200051340`. |
| **IB-06** | IB-05 fet (usuari sense nom) | Mirar `holder` | `@` i el seu `username`. |
| **IB-07** | Seed | `GET /api/account` sense sessió (backend amb `ALLOW_X_USER_ID=false`) | `401 UNAUTHENTICATED`. |
| **IB-08** | Seed, T0 | `POST /api/dev/incoming-transfers` amb `{ "iban": "ES91 2100 0418 4502 0005 1332", "amount": 12000, "payer": "Maria Puig" }` | `201` amb `balance: 391521` i el `movement` de l'exemple de §16.3 (`mov-31`, «Transferència rebuda · Maria Puig», `income`, contrapart «Maria Puig»). |
| **IB-09** | IB-08 fet | `GET /api/home` i `GET /api/movements?type=income` (usuari 1) | `balance` `391521`, i el moviment d'IB-08 surt el primer a les dues llistes. |
| **IB-10** | IB-08 fet | `GET /api/dev/outbox?to=demo@evolt.test` | El primer missatge és `incoming_transfer`, «Has rebut 120,00 € de Maria Puig.», canal `email`, sense `code` ni `link`. |
| **IB-11** | Seed | El mateix que IB-08 amb l'IBAN `"es9121000418450200051332"` | `201`: s'accepta en minúscules i sense espais. |
| **IB-12** | Seed | IBAN `ES9621000418430200051340` (el de `n = 9`, que encara no existeix) i `ES0000000000000000000000` | `404 RECIPIENT_NOT_FOUND`. |
| **IB-13** | Un usuari registrat i pendent de verificar | Una transferència al seu IBAN | `404 RECIPIENT_NOT_FOUND`. |
| **IB-14** | Seed | `amount` `0` i `-100`; després `100000000` i `100000001` | `422 INVALID_AMOUNT` les dues primeres; `201` amb `100000000`; `422 AMOUNT_OVER_LIMIT` amb `100000001`. |
| **IB-15** | Seed | `payer` `""`, `"   "` i de 71 caràcters; després de 70 i `"  Maria Puig  "` | `422 VALIDATION_ERROR` les tres primeres; `201` les altres dues, i el segon ordenant es desa com a «Maria Puig». |
| **IB-16** | Seed | Cossos sense `iban`, amb `amount: "12000"` i amb `amount: 120.5` | `422 VALIDATION_ERROR`. |
| **IB-17** | IB-08 fet | `GET /api/transfers/limit` i l'XP de l'usuari 1 | `remainingToday: 100000` i l'XP sense canvis: rebre no compta per a cap límit. |
| **IB-18** | Seed. Test amb `monkeypatch`: falla el missatge de la bústia | IB-08 | `500 INTERNAL_ERROR`; el saldo i els moviments no canvien. |
| **IB-19** | Backend amb `ENABLE_DEV_ROUTES=false` | IB-08 | La ruta no existeix i respon com qualsevol ruta inexistent ([§4.4](api.md#44-post-apidevreset)). `GET /api/account` continua funcionant. |
| **IB-20** | IB-08 fet | `POST /api/dev/reset` | El saldo de l'usuari 1 torna a ser `379521` i el moviment d'IB-08 desapareix. |

### Pantalla (T12.3)

| Id | Què fas | Què has de veure |
|---|---|---|
| **IBP-01** | A Inici, obre el menú ☰ i toca «Dades del compte». | La pantalla amb la capçalera «← Inici» · «Dades del compte». |
| **IBP-02** | Mira la targeta amb l'usuari 1. | Una sota l'altra i amb l'etiqueta a l'esquerra: «IBAN» «ES91 2100 0418 4502 0005 1332», «BIC» «EVOLESB1XXX» i «Titular» «Usuari demo», com al mockup US-12-dades-compte. |
| **IBP-03** | Toca l'IBAN. | Es copia `ES9121000418450200051332` (sense espais) i a baix surt «IBAN copiat» durant 2 s. |
| **IBP-04** | Al mòbil, toca «Compartir». | S'obre el menú de compartir del mòbil amb «IBAN: ES91 2100 0418 4502 0005 1332 · BIC: EVOLESB1XXX · Titular: Usuari demo». |
| **IBP-05** | En un navegador d'ordinador sense compartir, toca «Compartir». | Es copia el mateix text i surt «Dades copiades». |
| **IBP-06** | Obre la pantalla amb l'usuari 2. | El seu IBAN, «ES21 2100 0418 4102 0005 1333», i «Titular» «Usuari nou». |
| **IBP-07** | Amb el backend a `SIMULATE_ERROR_RATE=100`, obre la pantalla. | «S'ha produït un error inesperat. Torna-ho a provar més tard.» amb «Reintentar». |
| **IBP-08** | Fes IB-08 i obre Inici i Moviments amb l'usuari 1. | Saldo 3.915,21 € i, el primer, «Transferència rebuda · Maria Puig» amb «+120,00 €» en verd, com al mockup US-12-transferencia-rebuda. |

---

## Criteris d'acceptació i proves

| Criteri de la US-12 | Proves |
|---|---|
| 1 · «Dades del compte» al menú ☰ | IBP-01 |
| 2 · IBAN en grups de 4, BIC i titular (sense nom, l'@usuari) | IB-01, IB-02, IB-06, IBP-02, IBP-06 |
| 3 · Cada usuari té el seu IBAN, sempre el mateix, amb el dígit de control correcte | IB-03, IB-04, IB-05 |
| 4 · En tocar l'IBAN es copia sense espais i surt «IBAN copiat» | IBP-03 |
| 5 · «Compartir», o copiar el text amb «Dades copiades» | IBP-04, IBP-05 |
| 6 · Una transferència d'un altre banc suma al saldo i surt a Inici i a Moviments | IB-08, IB-09, IB-11, IBP-08 |
| 7 · A la bústia arriba «Has rebut 120,00 € de <ordenant>» | IB-10 |
| 8 · Error amb «Reintentar» | IB-07, IBP-07 |
