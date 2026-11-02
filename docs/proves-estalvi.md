# Proves d'acceptació · Estalvi (US-17 i US-18)

Proves d'acceptació de les històries d'estalvi, escrites a partir dels criteris de [`docs/P1/trello-backlog.md`](P1/trello-backlog.md) i del contracte de l'[apartat 9 de `docs/api.md`](api.md#9-guardioles-us-17-i-us-18). Tasca: T17.1 (issue #71).

## Índex

1. [Com fer servir aquest document](#com-fer-servir-aquest-document)
2. [Dades de partida](#dades-de-partida)
3. [US-17 · Crear guardiola](#us-17--crear-guardiola)
4. [US-18 · Aportar diners a una guardiola](#us-18--aportar-diners-a-una-guardiola)
5. [Criteris d'acceptació i proves](#criteris-dacceptació-i-proves)

---

## Com fer servir aquest document

Cada història té dues taules:

- **API:** proves del backend. Cada fila es converteix en un test de pytest a la tasca indicada. Els esperats es calculen a partir del seed, com als tests de l'Sprint 0.
- **Pantalla:** proves del frontend. Es comproven a mà amb l'app arrencada (com a [`docs/prueba-sprint0.md`](prueba-sprint0.md)) i, quan es pugui, amb un test de Vitest del ViewModel.

L'usuari de cada petició es tria com a la resta de l'API ([`api.md` §2](api.md#2-usuari-actual-i-estat-del-servei)): amb `X-User-Id` mentre estigui permès, o amb la sessió quan arribi la T03.1. «Usuari 2» vol dir una petició feta com a usuari 2.

## Dades de partida

- Seed acabat de carregar (`POST /api/dev/reset` o un client nou de pytest).
- **Usuari 1:**
  - Saldo del compte principal: **3.795,21 €** (`379521`), la suma dels seus 30 moviments.
  - Tres guardioles, que sumen **300,00 €** (`30000`):

    | `id` | Nom | Saldo | Objectiu | Color |
    |---|---|---|---|---|
    | `pot-01` | Vacances | 150,00 € (`15000`) | 1.000,00 € (`100000`) | `blue` |
    | `pot-02` | Emergències | 100,00 € (`10000`) | — (`null`) | `orange` |
    | `pot-03` | Regal d'aniversari | 50,00 € (`5000`) | 80,00 € (`8000`) | `pink` |

  - Cada guardiola té una sola entrada a l'historial: «Saldo inicial», pel seu saldo.
- **Usuari 2:** saldo 0,00 € i cap guardiola.
- Rellotge fixat a **T0 = `2026-11-03T10:00:00+01:00`** a les proves que miren la data d'una aportació.
- Els objectius i els colors de les guardioles del seed són una proposta del contracte (P32). Si a la revisió canvien, s'actualitzen aquí.

---

## US-17 · Crear guardiola

### API (T17.2)

| Id | Situació inicial | Acció | Resultat esperat |
|---|---|---|---|
| **P-01** | Seed | `GET /api/pots` (usuari 1) | `200` `{ items }` amb les 3 guardioles de les dades de partida, en aquest ordre: `pot-01`, `pot-02`, `pot-03`. |
| **P-02** | Seed | `GET /api/pots` (usuari 2) | `200` `{ "items": [] }`. |
| **P-03** | Seed | `POST /api/pots` amb `{ "name": "Viatge", "target": 30000 }` | `201` `{ id: "pot-04", name: "Viatge", balance: 0, target: 30000, color: "purple" }`: sense color, és el de per defecte. |
| **P-04** | P-03 fet | `GET /api/pots` | 4 guardioles. L'última és «Viatge», amb saldo `0`. |
| **P-05** | Seed | `POST /api/pots` amb `{ "name": "Fons" }` | `201` amb `target: null`: l'objectiu és opcional. |
| **P-06** | Seed | `POST /api/pots` amb `{ "name": "Viatge", "target": 30000, "color": "teal" }` | `201` amb `color: "teal"`. |
| **P-07** | Seed | `POST /api/pots` amb `{ "name": "" }` | `422 INVALID_POT_NAME`. `GET /api/pots` continua tornant 3 guardioles. |
| **P-08** | Seed | `POST /api/pots` amb `{ "name": "   " }` | `422 INVALID_POT_NAME`. |
| **P-09** | Seed | `POST /api/pots` amb `{ "name": "Viatge", "target": 0 }` | `422 INVALID_TARGET`. |
| **P-10** | Seed | `POST /api/pots` amb `{ "name": "Viatge", "target": -500 }` | `422 INVALID_TARGET`. |
| **P-11** | Seed | `POST /api/pots` amb `{ "name": "", "target": 0 }` | `422 INVALID_POT_NAME`: el nom es comprova abans que l'objectiu. |
| **P-12** | Seed | `POST /api/pots` amb `target` `"300"`, `300.5` o `300.0` | `422 VALIDATION_ERROR`. |
| **P-13** | Seed | `POST /api/pots` sense `name`, o amb `"name": 123` | `422 VALIDATION_ERROR`. |
| **P-14** | Seed | `POST /api/pots` amb `{ "name": "Viatge", "color": "red" }` | `422 VALIDATION_ERROR`: el color no és de la llista. |
| **P-15** | Seed | `POST /api/pots` amb `{ "name": "Viatge", "target": "300" }` i, després, una creació correcta | El primer, `422 VALIDATION_ERROR`; el segon, `201` amb `id: "pot-04"`: l'error no ha creat res ni ha gastat cap id. |
| **P-16** | Seed | `POST /api/pots` amb `{ "name": "  Viatge  " }` | `201` amb `name: "Viatge"`. |
| **P-17** | Seed | `POST /api/pots` amb `{ "name": "Primera" }` (usuari 2), i després `GET /api/pots` dels dos usuaris | `201`. L'usuari 2 té 1 guardiola; l'usuari 1 continua amb 3. |
| **P-18** | P-03 fet | `GET /api/home` (usuari 1) | `balance` `379521` i `totalSaved` `30000`, igual que abans: crear una guardiola no mou diners. |
| **P-19** | P-03 fet | Mirar la resposta de P-03 | Té exactament les claus `id`, `name`, `balance`, `target` i `color`. |

### Pantalla (T17.3 i T17.4)

| Id | Què fas | Què has de veure |
|---|---|---|
| **PP-01** | A «Inici», toca l'accés «Guardioles». | S'obre la pantalla «Guardioles». |
| **PP-02** | Amb l'usuari 2, obre «Guardioles». | El missatge gris «Encara no tens cap guardiola» i el botó lila «Crear guardiola». |
| **PP-03** | Amb l'usuari 1, obre «Guardioles». | La llista amb el nom i el saldo de cadascuna: Vacances 150,00 €, Emergències 100,00 € i Regal d'aniversari 50,00 €. |
| **PP-04** | Toca «Crear guardiola». | Un formulari amb les caselles «Nom» i «Objectiu (opcional)» i una fila de colors per triar. |
| **PP-05** | Deixa el nom buit, o escriu-hi només espais. | La casella «Nom» es posa vermella, surt el motiu en vermell a sota i el botó «Crear» queda desactivat. |
| **PP-06** | Escriu un nom i, a l'objectiu, `0`. Després, `-5`. | La casella «Objectiu (opcional)» es posa vermella, surt el motiu en vermell a sota i el botó «Crear» queda desactivat. |
| **PP-07** | Escriu «Viatge», objectiu `300`, tria un color i toca «Crear». | La guardiola «Viatge» surt a la llista amb saldo 0,00 €. |
| **PP-08** | Crea «Fons» sense objectiu. | Es crea i surt a la llista amb saldo 0,00 €. |
| **PP-09** | (T18.4) Amb el backend real, crea una guardiola i torna a «Inici». | El total estalviat no ha canviat: la guardiola nova té 0,00 €. |

---

## US-18 · Aportar diners a una guardiola

### API (T18.1)

| Id | Situació inicial | Acció | Resultat esperat |
|---|---|---|---|
| **A-01** | Seed, T0 | `POST /api/pots/pot-01/contributions` amb `{ "amount": 3000 }` | `201` `{ balance: 376521, pot: { id: "pot-01", name: "Vacances", balance: 18000, … }, movement: { amount: 3000, concept: "Aportació a Vacances", date: "2026-11-03T10:00:00+01:00", type: "expense", icon: "savings" } }`. |
| **A-02** | A-01 fet | `GET /api/home` | `balance` `376521` i `totalSaved` `33000`. `balance + totalSaved` és `409521`, igual que abans de l'aportació. |
| **A-03** | A-01 fet | `GET /api/home` i `GET /api/movements` | El primer de `lastMovements` i el primer del llistat són el moviment d'A-01. |
| **A-04** | A-01 fet | `GET /api/pots/pot-01/movements` | `200` amb 2 entrades: primer l'aportació (`3000`, `"Aportació"`, `type: "income"`, data T0) i després «Saldo inicial» (`15000`). Sumen `18000`, el saldo de la guardiola. |
| **A-05** | Seed | `GET /api/pots/pot-02/movements` | Una sola entrada: «Saldo inicial», `10000`. |
| **A-06** | Seed | Aportar `379521` (tot el saldo) a `pot-01` | `201` amb `balance: 0`. La guardiola queda a `394521`. |
| **A-07** | Seed | Aportar `379522` (1 cèntim més que el saldo) a `pot-01` | `422 INSUFFICIENT_BALANCE`. No canvien el saldo del compte, el saldo de la guardiola, el nombre de moviments ni l'historial. |
| **A-08** | Seed | Aportar `0`, i després `-100` | `422 INVALID_AMOUNT` totes dues vegades. No canvia res. |
| **A-09** | Seed | Aportar `"30"`, `30.0`, o sense `amount` | `422 VALIDATION_ERROR`. |
| **A-10** | Seed | Aportar `3000` a `pot-99` | `404 POT_NOT_FOUND`. |
| **A-11** | Seed | Aportar `3000` a `pot-01` com a usuari 2 | `404 POT_NOT_FOUND`, amb **el mateix cos** que A-10. La guardiola de l'usuari 1 no canvia. |
| **A-12** | Seed | `GET /api/pots/pot-01/movements` com a usuari 2, i `GET /api/pots/pot-99/movements` | `404 POT_NOT_FOUND` tots dos. |
| **A-13** | Seed | Aportar `0` a `pot-99` | `404 POT_NOT_FOUND`: la guardiola es comprova abans que l'import. |
| **A-14** | L'usuari 2 ha creat una guardiola (saldo del compte `0`) | Aportar-hi `0`, i després `100` | Primer `422 INVALID_AMOUNT` (l'import es comprova abans que el saldo); després `422 INSUFFICIENT_BALANCE`. |
| **A-15** | P-03 fet («Viatge», objectiu `30000`) | Aportar-hi `30000` i, després, `1000` més | `201` totes dues vegades: es pot aportar a una guardiola que ja ha arribat a l'objectiu. Queda a `31000`. |
| **A-16** | Seed, backend amb `SIMULATE_ERROR_RATE=100` | Aportar `3000` a `pot-01` | `500 INTERNAL_ERROR`. Sense la simulació, `GET /api/home` i `GET /api/pots` mostren els saldos de partida. |
| **A-17** | Seed. Test amb `monkeypatch`: falla una escriptura que no és la primera (p. ex. la de l'historial) | Aportar `3000` a `pot-01` | `500 INTERNAL_ERROR`. No canvien el saldo del compte, el de la guardiola, els moviments ni l'historial: es desfà el que ja s'havia escrit. |
| **A-18** | Seed | Dues aportacions de `300000` a `pot-01` alhora | Una `201` i l'altra `422 INSUFFICIENT_BALANCE`. El saldo del compte queda a `79521`, mai negatiu. |
| **A-19** | A-01 fet | Sumar els moviments del compte de l'usuari 1 | La suma és `376521`: el saldo continua sent la suma dels seus moviments. |
| **A-20** | A-01 fet | Mirar l'XP de l'usuari 1 a les dades en memòria | No ha canviat: en aquest sprint, aportar no dona XP. |
| **A-21** | A-01 fet | Recarregar `50000` i `50000` el mateix dia | `201` totes dues: l'aportació no compta per al límit diari de recàrrega. |
| **A-22** | A-01 fet | `POST /api/dev/reset` i `GET /api/pots` | Les guardioles tornen al seed: Vacances té `15000` i una sola entrada a l'historial. |

### Pantalla (T18.2 i T18.4)

| Id | Què fas | Què has de veure |
|---|---|---|
| **AP-01** | A «Guardioles», obre «Vacances». | La pantalla de la guardiola, amb el saldo, l'historial i el botó lila «Aportar». |
| **AP-02** | Toca «Aportar». | S'obre «Aportar a Vacances». A dalt, el saldo principal disponible (3.795,21 €) i el nom i el saldo de la guardiola (Vacances, 150,00 €). |
| **AP-03** | Escriu `0`. Després, un import més gran que el saldo principal (p. ex. `4000`). | La casella es posa vermella, surt el motiu en vermell i el botó «Confirmar» queda desactivat. |
| **AP-04** | Escriu `30` i toca «Confirmar». | Surt un tic verd amb «Has aportat 30,00 € a Vacances». El saldo principal és 3.765,21 € i Vacances té 180,00 €. |
| **AP-05** | Mira l'historial de Vacances. | A dalt de tot, l'aportació en verd amb «+30,00 €» i el concepte «Aportació». |
| **AP-06** | (T18.4) Torna a «Inici». | Saldo 3.765,21 € i total estalviat 330,00 €. A «Últims moviments», el primer és «Aportació a Vacances», −30,00 € en vermell. |
| **AP-07** | Amb el backend a `SIMULATE_ERROR_RATE=100`, aporta `10`. | Surt el missatge d'error en vermell. Quan el backend torna a funcionar, cap dels dos saldos ha canviat. |
| **AP-08** | Aporta exactament tot el saldo principal. | Es fa l'aportació i el saldo principal queda a 0,00 €. |

---

## Criteris d'acceptació i proves

| Criteri d'acceptació | Proves |
|---|---|
| US-17 · A «Inici» hi ha l'accés «Guardioles», que obre la pantalla «Guardioles» | PP-01 |
| US-17 · Si no en tinc cap, surt el missatge gris «Encara no tens cap guardiola» i el botó lila «Crear guardiola»; si en tinc, surt la llista amb el nom i el saldo de cadascuna | P-01, P-02, PP-02, PP-03 |
| US-17 · El botó «Crear guardiola» obre un formulari amb les caselles «Nom» i «Objectiu (opcional)» i una fila de colors per triar | P-05, P-06, P-14, PP-04 |
| US-17 · Si el nom està buit o l'objectiu és 0 o negatiu, la casella es posa vermella, surt el motiu en vermell a sota i el botó «Crear» queda desactivat | P-07, P-08, P-09, P-10, P-11, P-15, PP-05, PP-06 |
| US-17 · En tocar «Crear», la guardiola nova surt a la llista amb saldo 0,00 € | P-03, P-04, P-16, P-17, P-18, P-19, PP-07, PP-08, PP-09 |
| US-18 · A la pantalla d'una guardiola hi ha el botó lila «Aportar», que obre la pantalla «Aportar a <nom de la guardiola>» | AP-01, AP-02 |
| US-18 · A dalt es veu el saldo principal disponible i el nom i el saldo de la guardiola | P-01, AP-02 |
| US-18 · L'import ha de ser més gran que 0 i no més gran que el saldo principal; si no, la casella es posa vermella, surt el motiu en vermell i el botó «Confirmar» queda desactivat | A-06, A-07, A-08, A-09, A-14, AP-03, AP-08 |
| US-18 · En confirmar, el saldo principal baixa i el de la guardiola puja exactament el mateix import | A-01, A-02, A-03, A-19, AP-04, AP-06 |
| US-18 · Surt un tic verd amb «Has aportat X € a <nom>» | A-01, AP-04 |
| US-18 · A l'historial de la guardiola surt l'aportació en verd amb «+» i el concepte «Aportació» | A-04, A-05, AP-05 |
| US-18 · Si el servidor falla, surt el missatge d'error en vermell i cap dels dos saldos canvia | A-16, AP-07 |
| US-18 · Mai es queda a mitges: o canvien els dos saldos o no en canvia cap | A-07, A-17, A-18 |

Proves que no surten d'un criteri, sinó del contracte: P-12 i P-13 (format del cos), A-10 a A-13 (guardioles inexistents o d'altres usuaris), A-15 (aportar per sobre de l'objectiu), A-20 (sense XP), A-21 (límit diari) i A-22 (reinici de dades).
