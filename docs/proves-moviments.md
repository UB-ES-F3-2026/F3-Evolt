# Proves d'acceptació · Moviments (US-10 i US-11)

Proves d'acceptació de les històries de filtres i detall de moviments, escrites a partir dels criteris de [`docs/P1/trello-backlog.md`](P1/trello-backlog.md) i del contracte de l'[apartat 10 de `docs/api.md`](api.md#10-moviments-filtres-detall-i-informe-us-10-i-us-11). Tasca: T10.1 (issue #80).

## Índex

1. [Com fer servir aquest document](#com-fer-servir-aquest-document)
2. [Dades de partida](#dades-de-partida)
3. [Camps nous del moviment](#camps-nous-del-moviment)
4. [US-10 · Filtres i cerca de moviments](#us-10--filtres-i-cerca-de-moviments)
5. [US-11 · Detall d'un moviment](#us-11--detall-dun-moviment)
6. [Criteris d'acceptació i proves](#criteris-dacceptació-i-proves)

---

## Com fer servir aquest document

Cada bloc té dues taules:

- **API:** proves del backend. Cada fila es converteix en un test de pytest a la tasca indicada. Els esperats es calculen a partir del seed, com als tests de l'Sprint 0.
- **Pantalla:** proves del frontend. Es comproven a mà amb l'app arrencada (com a [`docs/prueba-sprint0.md`](prueba-sprint0.md)) i, quan es pugui, amb un test de Vitest del ViewModel.

L'usuari de cada petició es tria com a la resta de l'API ([`api.md` §2](api.md#2-usuari-actual-i-estat-del-servei)): amb `X-User-Id` mentre estigui permès, o amb la sessió quan arribi la T03.1. «Usuari 2» vol dir una petició feta com a usuari 2.

## Dades de partida

- Seed acabat de carregar (`POST /api/dev/reset` o un client nou de pytest), amb el rellotge fixat a **T0 = `2026-11-03T10:00:00+01:00`**. Les dates del seed són relatives a avui, així que a pytest el seed es construeix amb aquesta data.
- **Usuari 1:** 30 moviments, de `mov-01` (el més antic) a `mov-30` (el més recent).
  - 7 ingressos (`mov-01`, `mov-03`, `mov-07`, `mov-09`, `mov-16`, `mov-17` i `mov-24`) i 23 despeses.
  - 4 «Supermercat»: `mov-06` (2/10), `mov-13` (13/10), `mov-23` (27/10) i `mov-28` (1/11).
  - 2 «Recàrrega»: `mov-07` i `mov-16`.
  - El 2/11 hi ha `mov-30`. L'1/11 hi ha `mov-28` i `mov-29`, a la mateixa hora.
  - Contraparts i estat, segons la proposta de [`api.md` §10.7](api.md#107-model-intern-dels-moviments):

    | Moviment | Concepte | `counterparty` | `status` |
    |---|---|---|---|
    | `mov-03` | Nòmina | Empresa Demo SL | `completed` |
    | `mov-09` | Transferència rebuda | Marta Puig | `completed` |
    | `mov-10` | Lloguer | Jordi Serra | `completed` |
    | `mov-17` | Nòmina | Empresa Demo SL | `completed` |
    | `mov-18` | Transferència enviada | Laia Vidal | `completed` |
    | `mov-24` | Bizum rebut | Pau Ferrer | `completed` |
    | `mov-29` | Bizum enviat | Núria Soler | `completed` |
    | `mov-30` | Restaurant La Plaça | `null` | `pending` |
    | La resta | | `null` | `completed` |

  - Referències: `EVT-000001` a `EVT-000030`, amb el mateix número que l'id.
- **Usuari 2:** cap moviment.
- Els noms de les contraparts, l'estat pendent de `mov-30` i el format de les referències són propostes del contracte (P35, P37 i P45). Si a la revisió canvien, s'actualitzen aquí.

---

## Camps nous del moviment

### API (T10.2)

| Id | Situació inicial | Acció | Resultat esperat |
|---|---|---|---|
| **F-01** | Seed | `GET /api/movements?limit=50` (usuari 1) | Els 30 moviments tenen la clau `counterparty`, un `status` de la llista (`completed` o `pending`) i una `reference` no buida. Les 30 referències són diferents. |
| **F-02** | Seed | Mirar les contraparts de F-01 | `mov-09`, `mov-10`, `mov-18`, `mov-24` i `mov-29` (transferències i Bizum) tenen el nom del contacte de les dades de partida; `mov-03` i `mov-17` (nòmines), «Empresa Demo SL». |
| **F-03** | Seed | Mirar les recàrregues `mov-07` i `mov-16` | `counterparty: null`. |
| **F-04** | Seed | Mirar l'estat dels moviments | `mov-30` és `pending`; els altres 29, `completed`. |
| **F-05** | Seed | `GET /api/home` i `POST /api/topups` amb `{ "amount": 1000 }` | Els moviments de les dues respostes tenen exactament les claus `id`, `amount`, `concept`, `date`, `type`, `icon`, `counterparty`, `status` i `reference`. |
| **F-06** | Seed | `POST /api/topups` amb `{ "amount": 1000 }` | El moviment nou té `status: "completed"`, `counterparty: null` i `reference: "EVT-000031"`, que no té cap altre moviment. |
| **F-07** | Seed | `GET /api/home` | `balance` és `379521`, la suma de tots els moviments, també el pendent: un moviment pendent ja compta al saldo. |

---

## US-10 · Filtres i cerca de moviments

### API (T10.3)

Totes les peticions són de l'usuari 1, llevat que es digui el contrari.

| Id | Situació inicial | Acció | Resultat esperat |
|---|---|---|---|
| **M-01** | Seed | `GET /api/movements?type=expense&q=super` | Exactament `mov-28`, `mov-23`, `mov-13` i `mov-06`, en aquest ordre, i `nextOffset: null`. |
| **M-02** | Seed | `q=recarrega` | `mov-16` i `mov-07`: el text sense accent troba «Recàrrega». |
| **M-03** | Seed | `q=SUPER` i `q=super` | El mateix resultat totes dues vegades. |
| **M-04** | Seed | `type=expense&limit=50` | 23 moviments, i cap té `type: "income"`. |
| **M-05** | Seed | `type=income&limit=50` | Els 7 ingressos, i cap té `type: "expense"`. |
| **M-06** | Seed | `q=marta` | `mov-09`: el text també busca per la contrapart. |
| **M-07** | Seed | `q=nuria` | `mov-29` («Núria Soler»): tampoc distingeix accents a la contrapart. |
| **M-08** | Seed | `dateFrom=2026-11-01&dateTo=2026-11-02` | `mov-30`, `mov-29` i `mov-28`: els dos extrems són inclosos. |
| **M-09** | Seed | `dateFrom=2026-11-01&dateTo=2026-11-01` | `mov-29` i `mov-28`: un sol dia. |
| **M-10** | Seed | `dateFrom=2026-11-02&dateTo=2026-11-01` | `422 VALIDATION_ERROR`. |
| **M-11** | Seed | `dateFrom=2026-13-01`, i després `dateFrom=01/11/2026` | `422 VALIDATION_ERROR` totes dues vegades. |
| **M-12** | Seed | `type=refund` | `422 VALIDATION_ERROR`. |
| **M-13** | Seed | `type=expense&q=super&limit=2`, i després el mateix amb `offset=2` | Primer `mov-28` i `mov-23` amb `nextOffset: 2`; després `mov-13` i `mov-06` amb `nextOffset: null`. Entre les dues pàgines, el resultat de M-01 sense repeticions. |
| **M-14** | Seed | `type=expense&limit=2`, seguint `nextOffset` fins al final | 12 pàgines amb els 23 moviments de M-04, en el mateix ordre i sense cap repetit. L'última porta `nextOffset: null`. |
| **M-15** | Seed | `q=xyz` | `200` `{ "items": [], "nextOffset": null }`. |
| **M-16** | Seed | `q=` i `q=%20%20` (només espais) | El mateix que sense filtre: 20 moviments i `nextOffset: 20`. |
| **M-17** | Seed | `q=super` (usuari 2) | `200` `{ "items": [], "nextOffset": null }`. |
| **M-18** | Seed | `dateFrom=2026-10-01&type=income&q=nomina` | Només `mov-17` (21/10). `mov-03` també és una nòmina, però és del 28/9. |
| **M-19** | Seed | `type=expense&q=super&offset=4` | `200` `{ "items": [], "nextOffset": null }`: un `offset` més enllà del resultat filtrat no és un error. |
| **M-20** | Seed | `GET /api/home?q=super` | Els mateixos 5 `lastMovements` que sense paràmetre: la Home no té filtres. |

### Pantalla (T10.4)

| Id | Què fas | Què has de veure |
|---|---|---|
| **MP-01** | A «Moviments», toca «Filtres» i tria de l'1/11/2026 al 2/11/2026. | La llista només mostra els 3 moviments d'aquests dos dies: Restaurant La Plaça, Bizum enviat i Supermercat. |
| **MP-02** | Als filtres, tria «Ingressos» i després «Despeses». | Les opcions «Tots», «Ingressos» (en verd) i «Despeses» (en vermell). La llista només mostra el tipus triat. |
| **MP-03** | A la barra de cerca, amb el text gris «Cerca per concepte o contacte», escriu `super`. Després, `marta`. | Mentre escrius, la llista es redueix: amb `super`, els 4 «Supermercat»; amb `marta`, «Transferència rebuda». |
| **MP-04** | Combina dates, «Despeses» i la cerca `super`, i després toca «Esborrar filtres». | Primer es veuen només els moviments que compleixen les tres coses. Després de «Esborrar filtres», torna la llista completa. |
| **MP-05** | Cerca `xyz`. | El missatge gris «No hi ha resultats» i el botó «Esborrar filtres», que torna la llista completa. |
| **MP-06** | Amb «Despeses», fes scroll fins al final. | Es carreguen més moviments, sense cap repetit, fins als 23. |
| **MP-07** | Fes scroll, i després canvia un filtre. | La llista torna a començar per la primera pàgina, sense moviments duplicats. |

---

## US-11 · Detall d'un moviment

### API (T11.1)

| Id | Situació inicial | Acció | Resultat esperat |
|---|---|---|---|
| **D-01** | Seed | `GET /api/movements/mov-29` | `200` amb el moviment sencer: `date` `"2026-11-01T18:42:00+01:00"`, `amount` `1000` i `type: "expense"`, `status: "completed"`, `counterparty: "Núria Soler"` i `reference: "EVT-000029"`. |
| **D-02** | Seed | `GET /api/movements/mov-30` | `status: "pending"` i `counterparty: null`. |
| **D-03** | Seed | `GET /api/movements/mov-99` | `404 MOVEMENT_NOT_FOUND`. |
| **D-04** | Seed | `GET /api/movements/mov-29` (usuari 2) | `404 MOVEMENT_NOT_FOUND`, amb **el mateix cos** que D-03. |
| **D-05** | Seed | `GET /api/movements/abc` | `404 MOVEMENT_NOT_FOUND`. |
| **D-06** | Seed | Comparar D-01 amb `mov-29` a `GET /api/movements` | És el mateix objecte, camp per camp. |
| **D-07** | F-06 fet | `GET /api/movements/mov-31` | La recàrrega nova, amb `status: "completed"`, `counterparty: null` i `reference: "EVT-000031"`. |
| **I-01** | Seed, T0 | `POST /api/movements/mov-30/reports` amb `{ "description": "No reconec aquest pagament" }` | `201` `{ id: "rep-01", movementId: "mov-30", description: "No reconec aquest pagament", createdAt: "2026-11-03T10:00:00+01:00" }`. |
| **I-02** | I-01 fet | Mirar els informes a les dades en memòria | N'hi ha un, vinculat a `mov-30` i a l'usuari 1. |
| **I-03** | Seed | Informe sobre `mov-30` amb `description` `""`, i després `"   "` | `422 INVALID_DESCRIPTION` totes dues vegades. No es desa res. |
| **I-04** | Seed | Informe amb una descripció de 501 caràcters, i després una de 500 | Primer `422 INVALID_DESCRIPTION`; després `201`. |
| **I-05** | Seed | Informe sense `description`, o amb `"description": 123` | `422 VALIDATION_ERROR`. |
| **I-06** | Seed | Informe sobre `mov-29` (usuari 2) | `404 MOVEMENT_NOT_FOUND`. No es desa res. |
| **I-07** | Seed | Informe sobre `mov-99` amb `description` `""` | `404 MOVEMENT_NOT_FOUND`: el moviment es comprova abans que la descripció. |
| **I-08** | Seed | Dos informes sobre `mov-30` | `201` tots dos, amb `id` `rep-01` i `rep-02`. |
| **I-09** | Seed | Informe amb `"  No el reconec  "` | `201` amb `description: "No el reconec"`. |
| **I-10** | I-01 fet | `POST /api/dev/reset` i un informe nou | Els informes anteriors s'han esborrat, i el nou torna a ser `rep-01`. |

### Pantalla (T11.2 i T11.3)

| Id | Què fas | Què has de veure |
|---|---|---|
| **DP-01** | A «Moviments», toca «Bizum enviat» (1/11). | S'obre «Detall del moviment»: a dalt, en gran i en vermell, «−10,00 €»; a sota, en files, la data i l'hora (1/11/2026, 18:42), l'estat «Completat», la contrapart «Núria Soler» i la referència «EVT-000029». |
| **DP-02** | Obre «Restaurant La Plaça» (2/11). | L'estat diu «Pendent» i la contrapart surt buida («—»). |
| **DP-03** | Obre «Bizum rebut». | L'import en verd amb «+15,00 €» i la contrapart «Pau Ferrer». |
| **DP-04** | Al detall de «Bizum enviat», toca «Descarregar justificant». | Es baixa un PDF amb les mateixes dades. L'import i la referència són exactament els del detall. |
| **DP-05** | Toca l'enllaç «Reportar un problema». | S'obre un formulari amb el moviment ja indicat i una casella per explicar què passa. |
| **DP-06** | Intenta enviar-lo amb la casella buida. | No s'envia: surt el motiu en vermell. |
| **DP-07** | Escriu què passa i envia'l. | Surt una confirmació que l'informe s'ha enviat. |

---

## Criteris d'acceptació i proves

| Criteri d'acceptació | Proves |
|---|---|
| US-10 · A dalt de la pantalla «Moviments» hi ha el botó «Filtres», que permet triar una data d'inici i una de final; la llista només mostra els moviments entre aquestes dues dates | M-08, M-09, M-10, M-11, MP-01 |
| US-10 · Als filtres hi ha tres opcions: «Tots», «Ingressos» (en verd) i «Despeses» (en vermell); en triar-ne una, la llista només mostra aquest tipus | M-04, M-05, M-12, MP-02 |
| US-10 · A dalt de tot hi ha una barra de cerca amb el text gris «Cerca per concepte o contacte»; mentre escric, la llista només mostra els moviments que contenen aquest text | M-01, M-02, M-03, M-06, M-07, M-16, MP-03 |
| US-10 · Les dates, el tipus i la cerca es poden fer servir alhora, i el botó «Esborrar filtres» els treu tots i torna a mostrar la llista completa | M-13, M-14, M-18, MP-04, MP-06, MP-07 |
| US-10 · Si cap moviment compleix els filtres, surt el missatge gris «No hi ha resultats» amb el botó «Esborrar filtres» | M-15, M-17, M-19, MP-05 |
| US-11 · En tocar un moviment de la llista s'obre la pantalla «Detall del moviment»: a dalt l'import en gran (en verd amb «+» si és un ingrés, en vermell amb «−» si és una despesa) i a sota, en files, la data i l'hora, l'estat («Completat» o «Pendent»), la contrapart (qui paga o qui cobra) i la referència | F-01, F-02, F-03, F-04, D-01, D-02, D-06, DP-01, DP-02, DP-03 |
| US-11 · Hi ha el botó «Descarregar justificant», que baixa un PDF amb aquestes mateixes dades | D-01, DP-04 |
| US-11 · Hi ha l'enllaç «Reportar un problema», que obre un formulari amb el moviment ja indicat i una casella per explicar què passa | I-01, I-02, I-03, I-04, I-08, DP-05, DP-06, DP-07 |

Proves que no surten d'un criteri, sinó del contracte: F-05 a F-07 (els camps nous a totes les respostes i el saldo amb pendents), M-20 (la Home sense filtres), D-03 a D-05 i D-07 (moviments inexistents, d'altres usuaris i nous), i I-05 a I-07, I-09 i I-10 (format, ordre de les validacions i reinici).
