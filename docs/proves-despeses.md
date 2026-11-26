# Proves d'acceptació · Despeses dividides (US-30 i US-31)

Proves d'acceptació de dividir una despesa i de seguir-la, escrites a partir de les històries (`docs/us/US-30.md` i `docs/us/US-31.md`) i del contracte de l'[apartat 17 de `docs/api.md`](api.md#17-despeses-dividides-us-30-i-us-31). Tasca: T30.1 (issue #326).

## Índex

1. [Com fer servir aquest document](#com-fer-servir-aquest-document)
2. [Dades de partida](#dades-de-partida)
3. [US-30 · Dividir una despesa](#us-30--dividir-una-despesa)
4. [US-31 · Seguiment d'una despesa dividida](#us-31--seguiment-duna-despesa-dividida)
5. [Criteris d'acceptació i proves](#criteris-dacceptació-i-proves)

---

## Com fer servir aquest document

- **API:** proves del backend. Cada fila es converteix en un test de pytest a la tasca indicada, amb l'id de la prova al nom o al comentari del test (skill `qa-strategy`).
- **Pantalla:** proves del frontend. Es comproven a mà amb l'app arrencada a 375 px i, quan es pugui, amb un test de Vitest del ViewModel.

L'usuari de cada petició és el de la sessió (`Authorization: Bearer`, [`api.md` §8.2](api.md#82-sessió)). «Usuari 1» és `demo@evolt.test`; tots els usuaris del seed tenen la contrasenya `Evolt2026` (P13).

## Dades de partida

- Seed acabat de carregar, amb els vuit usuaris de [`api.md` §13.9](api.md#139-model-intern). Cap despesa dividida.
- Rellotge fixat a **T0 = `2026-11-15T21:15:00+01:00`**.
- **La despesa de l'exemple** (D0): `POST /api/split-expenses` amb `{ "concept": "Sopar d'aniversari", "total": 6000, "myShare": 1500, "parts": [{ "toUserId": "usr-05", "amount": 1500 }, { "toUserId": "usr-03", "amount": 1500 }, { "toUserId": "usr-08", "amount": 1500 }] }` (Izan, Alicia i Martí).
- Els ids de les sol·licituds no s'escriuen tal qual: depenen de quantes en té el seed. Els tests fan servir els `requestId` de la resposta.
- Pagar i rebutjar una part són la US-39 i la US-40. Si encara no són a la branca, el test canvia l'estat de la sol·licitud al repositori.

---

## US-30 · Dividir una despesa

### API (T30.2)

| Id | Situació inicial | Acció | Resultat esperat |
|---|---|---|---|
| **DD-01** | Seed, T0 | D0 | `201` amb `id: "split-01"`, el concepte, `total: 6000`, `myShare: 1500`, `createdAt: T0`, `status: "pending"`, `people: 4`, `paidCount: 0`, `pendingAmount: 4500` i tres `parts` `pending` de 1500, en l'ordre d'Izan, Alicia i Martí. |
| **DD-02** | DD-01 fet | Mirar les sol·licituds desades (test del repositori) | Tres sol·licituds noves de l'usuari 1, `pending`, amb el concepte, la part de cadascú, la data T0 i `split_id: "split-01"`. |
| **DD-03** | DD-01 fet | `GET /api/dev/outbox` d'Izan, Alicia i Martí | Cadascú té `money_request` «Usuari demo et demana 15,00 €: Sopar d'aniversari.». |
| **DD-04** | DD-01 fet | `GET /api/home` i `GET /api/movements` dels quatre | Igual que abans: dividir no mou diners. |
| **DD-05** | DD-01 fet | `GET /api/money-requests` (usuari 1) | Només les sol·licituds normals del seed: les de la despesa no hi surten (P104). |
| **DD-06** | Seed | `total: 10000`, `myShare: 3334` i dues parts de `3333` | `201`: els cèntims que sobren són per a mi. |
| **DD-07** | Seed | `parts: []`, i 10 parts amb ids diferents | `422 VALIDATION_ERROR` les dues vegades. |
| **DD-08** | Seed | Dues parts amb el mateix `toUserId` | `422 VALIDATION_ERROR`. |
| **DD-09** | Seed | Una part a `usr-99`, i una altra a un usuari pendent de verificar | `404 RECIPIENT_NOT_FOUND`. No es desa res ni s'envia cap avís. |
| **DD-10** | Seed | Una part a `usr-01` (jo) | `422 SELF_REQUEST`. |
| **DD-11** | Seed | `total` `0` i `-100`; després `100000001`; després `100000000` amb parts que quadren | `INVALID_AMOUNT`, `AMOUNT_OVER_LIMIT` i `201`. |
| **DD-12** | Seed | Concepte `""`, `"   "` i de 141 caràcters | `422 INVALID_CONCEPT`. |
| **DD-13** | Seed | Una part de `0`; després `myShare: 0` | `422 INVALID_SHARE` les dues vegades (P101). |
| **DD-14** | Seed | `total: 6000`, `myShare: 1500` i parts de 1500, 1500 i 1000 | `422 SHARES_DO_NOT_MATCH`. |
| **DD-15** | Seed | Una part a `usr-01` i `total: 0` | `SELF_REQUEST`: l'ordre de 17.2. |
| **DD-16** | Seed | Cossos amb `total: "6000"`, sense `myShare` i amb `parts` que no és una llista | `422 VALIDATION_ERROR`. |
| **DD-17** | Seed. Test amb `monkeypatch`: falla l'avís del segon participant | D0 | `500 INTERNAL_ERROR`. No queda cap despesa, cap sol·licitud ni cap avís nou. |
| **DD-18** | DD-01 fet | Cancel·lar ([§14.4](api.md#144-post-apimoney-requestsrequestidcancel)) una de les sol·licituds de la despesa | `404 REQUEST_NOT_FOUND`, i continua `pending` (P105). |
| **DD-19** | DD-01 fet | `POST /api/dev/reset` | No queda cap despesa dividida. |
| **DD-20** | Seed | `POST /api/split-expenses` sense sessió (backend amb `ALLOW_X_USER_ID=false`) | `401 UNAUTHENTICATED`. |

### Pantalla (T30.3)

| Id | Què fas | Què has de veure |
|---|---|---|
| **DDP-01** | A «Demanar diners», toca «Dividir una despesa». | El formulari canvia a «Import total», «Concepte» i «Participants». «A una persona» és el que surt per defecte. |
| **DDP-02** | Afegeix Izan, Alicia i Martí amb la cerca. | Una fila per a cadascú amb la seva part i «×». Si tornes a cercar Izan, surt en gris amb «Ja hi és». |
| **DDP-03** | Escriu 60,00 € amb «Parts iguals». | 15,00 € per a cada participant i per a «Jo». Amb 100,00 € i dos participants, 33,33 € cadascun i 33,34 € per a «Jo». |
| **DDP-04** | Amb «Imports personalitzats», posa 20,00 €, 10,00 € i 10,00 € (i 15,00 € per a «Jo»). | «La suma de les parts ha de ser igual al total.» i «Enviar sol·licituds» desactivat. Amb una part a 0: «Cada part ha de ser més gran que 0.». |
| **DDP-05** | Torna a «Parts iguals». | Les parts es tornen a calcular i es perd el que havies escrit. |
| **DDP-06** | Afegeix 9 participants. | La cerca es desactiva i diu «Màxim 9 participants». |
| **DDP-07** | Envia la despesa de 60,00 €. | Tic verd, «Has enviat 3 sol·licituds» i «Pendent de cobrar: 45,00 €»; 1,5 s després, «Sol·licituds enviades» amb la despesa a dalt de tot. |
| **DDP-08** | Escriu alguna cosa i toca «← Inici». | Surts sense enviar res i sense cap pregunta. |
| **DDP-09** | Amb el backend a `SIMULATE_ERROR_RATE=100`, envia. | «S'ha produït un error inesperat. Torna-ho a provar més tard.» sota el botó, i el formulari continua omplert. |
| **DDP-10** | A «Dividir una despesa», escriu l'import i el concepte sense afegir cap participant. | Sota la cerca, en gris, «Afegeix almenys un participant.», i «Enviar sol·licituds» desactivat. |

---

## US-31 · Seguiment d'una despesa dividida

### API (T31.1)

| Id | Situació inicial | Acció | Resultat esperat |
|---|---|---|---|
| **SG-01** | DD-01 fet | `GET /api/split-expenses` (usuari 1) | `200` amb un sol element, igual que la resposta de DD-01. |
| **SG-02** | DD-01 fet i, després, una altra despesa | `GET /api/split-expenses` | Les dues, la més nova primer. |
| **SG-03** | DD-01 fet | `GET /api/split-expenses/split-01` | La mateixa `SplitExpense`. |
| **SG-04** | DD-01 fet | Izan paga la seva part | `paidCount: 1`, `pendingAmount: 3000`, `status: "pending"`; la part d'Izan, `paid`. |
| **SG-05** | SG-04 | Martí rebutja la seva | `pendingAmount: 1500`, `status: "pending"`; la part de Martí, `rejected`. |
| **SG-06** | SG-05 | Alicia paga la seva | `paidCount: 2`, `pendingAmount: 0`, `status: "closed"` («Tancada»). |
| **SG-07** | SG-06 | `POST /api/split-expenses/split-01/parts/usr-08/resend` | `201`. La part de Martí té un `requestId` nou i és `pending`; `pendingAmount: 1500`, `status: "pending"`. La sol·licitud rebutjada continua `rejected`, i a la bústia de Martí hi ha un altre `money_request`. |
| **SG-08** | SG-07 | Martí paga la nova | `paidCount: 3`, `pendingAmount: 0`, `status: "completed"`. |
| **SG-09** | DD-01 fet | Llegir la despesa el 22/11 a les 00:00 (rellotge fixat) | Les tres parts `expired`, `pendingAmount: 0`, `status: "closed"`. Es poden tornar a enviar. |
| **SG-10** | DD-01 fet (part pendent) i SG-04 (part pagada) | Tornar a enviar la part de Martí (pendent) i la d'Izan (pagada) | `422 PART_NOT_RESENDABLE` les dues vegades. |
| **SG-11** | DD-01 fet | Tornar a enviar a `usr-02` (no hi és); llegir i tornar a enviar a `split-99` | `404 PART_NOT_FOUND`, i `404 SPLIT_NOT_FOUND`. |
| **SG-12** | DD-01 fet | Alicia llegeix `split-01` i la seva llista | `404 SPLIT_NOT_FOUND`, i `items: []`. |
| **SG-13** | SG-05. Test amb dos fils | Dos «Tornar a enviar» alhora a Martí | Un `201` i un `422 PART_NOT_RESENDABLE`: només hi ha una sol·licitud nova. |
| **SG-14** | SG-05. Test amb `monkeypatch`: falla l'avís | Tornar a enviar a Martí | `500 INTERNAL_ERROR`; no hi ha cap sol·licitud nova i la part continua `rejected`. |
| **SG-15** | Seed | Les tres rutes sense sessió (backend amb `ALLOW_X_USER_ID=false`) | `401 UNAUTHENTICATED`. |

### Pantalla (T31.2)

| Id | Què fas | Què has de veure |
|---|---|---|
| **SGP-01** | Després de DDP-07, mira «Sol·licituds enviades». | Una sola targeta: «Sopar d'aniversari», «Despesa dividida · 4 persones», «0 de 3 han pagat», la data, 60,00 € i «Pendent»; a baix, «Pendent: 45,00 €». Les tres sol·licituds no surten soles. |
| **SGP-02** | Fes que Izan pagui i torna a la pantalla. | «1 de 3 han pagat» i «Pendent: 30,00 €». |
| **SGP-03** | Toca la targeta. | El detall («← Sol·licituds» · «Sopar d'aniversari»): el total, «1 de 3 han pagat · Pendent: 30,00 €» i una fila per participant amb la seva part i l'etiqueta. |
| **SGP-04** | Fes que Martí la rebutgi, i que Alicia pagui. | La fila de Martí, «Rebutjada» amb «Tornar a enviar»; la targeta, «Tancada» (gris). |
| **SGP-05** | Toca «Tornar a enviar» a Martí. | «Sol·licitud enviada a Martí.» i la fila passa a «Pendent». |
| **SGP-06** | Fes que Martí pagui. | La targeta passa a «Completada» (verd). |
| **SGP-07** | Amb el backend a `SIMULATE_ERROR_RATE=100`, obre el detall i, després, toca «Tornar a enviar». | En obrir: l'error amb «Reintentar». En tornar a enviar: l'error sota el botó, i la fila es queda com estava. |

---

## Criteris d'acceptació i proves

| Criteri | Proves |
|---|---|
| US-30 · 1 · «A una persona» o «Dividir una despesa» | DDP-01 |
| US-30 · 2 · Participants amb la cerca, «Ja hi és» i màxim 9 | DD-07, DD-08, DDP-02, DDP-06 |
| US-30 · 3 · Fila «Jo» i parts iguals amb els cèntims per a mi | DD-06, DDP-03 |
| US-30 · 4 · Imports personalitzats: la suma i les parts a 0 | DD-13, DD-14, DDP-04, DDP-05 |
| US-30 · 5 · «Enviar sol·licituds» desactivat fins que tot quadra; sense participants, «Afegeix almenys un participant.» | DD-07, DD-11, DD-12, DDP-04, DDP-10 |
| US-30 · 6 · Èxit: «Has enviat 3 sol·licituds» i «Pendent de cobrar» | DD-01, DDP-07 |
| US-30 · 7 · Avís a cada participant; no es mou cap diner | DD-02, DD-03, DD-04 |
| US-30 · 8 · Totes les sol·licituds o cap | DD-09, DD-17 |
| US-30 · 9 · «← Inici» surt sense enviar | DDP-08 |
| US-30 · 10 · Error del servidor o de xarxa | DD-17, DDP-09 |
| US-31 · 1 · Una sola targeta a «Sol·licituds enviades» | DD-05, SG-01, SG-02, SGP-01 |
| US-31 · 2 · «Pendent», «Completada» i «Tancada» | SG-04, SG-06, SG-08, SG-09, SGP-04, SGP-06 |
| US-31 · 3 · El detall amb una fila per participant | SG-03, SGP-03 |
| US-31 · 4 · «Tornar a enviar» a les rebutjades i caducades | SG-07, SG-09, SG-10, SG-13, SGP-05 |
| US-31 · 5 · El detall i la targeta s'actualitzen quan algú paga | SG-04, SGP-02 |
| US-31 · 6 · El pendent només suma les parts pendents | SG-05, SG-06 |
| US-31 · 7 · Error en carregar el detall, amb «Reintentar» | SG-11, SG-12, SGP-07 |
| US-31 · 8 · Error en «Tornar a enviar» | SG-14, SGP-07 |
