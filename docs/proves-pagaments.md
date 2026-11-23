# Proves d'acceptació · Pagaments (US-13 a US-15)

Proves d'acceptació de cercar un usuari i d'enviar-li diners, escrites a partir de les històries (`docs/us/US-13.md` i `docs/us/US-14.md`) i del contracte de l'[apartat 13 de `docs/api.md`](api.md#13-pagaments-cercar-usuaris-i-enviar-diners-us-13-i-us-14). Tasca: T13.1 (issue #157).

Les de demanar diners (US-15) segueixen l'[apartat 14](api.md#14-sol·licituds-de-diners-us-15) i `docs/us/US-15.md`. Tasca: T15.1 (issue #153).

## Índex

1. [Com fer servir aquest document](#com-fer-servir-aquest-document)
2. [Dades de partida](#dades-de-partida)
3. [US-13 · Cercar un usuari](#us-13--cercar-un-usuari)
4. [US-14 · Enviar diners a usuaris](#us-14--enviar-diners-a-usuaris)
5. [US-15 · Sol·licitar diners](#us-15--sol·licitar-diners)
6. [Casos de les històries i proves](#casos-de-les-històries-i-proves)

---

## Com fer servir aquest document

Cada història té dues taules:

- **API:** proves del backend. Cada fila es converteix en un test de pytest a la tasca indicada, amb l'id de la prova al nom o al comentari del test (skill `qa-strategy`). Els esperats surten del seed, escrits tal qual.
- **Pantalla:** proves del frontend. Es comproven a mà amb l'app arrencada a 375 px i, quan es pugui, amb un test de Vitest del ViewModel.

L'usuari de cada petició és el de la sessió (`Authorization: Bearer`, [`api.md` §8.2](api.md#82-sessió)). «Usuari 1» és `demo@evolt.test` i «usuari 2», `buit@evolt.test`; tots els usuaris del seed tenen la contrasenya `Evolt2026` (P13).

## Dades de partida

- Seed acabat de carregar (`POST /api/dev/reset` o un client nou de pytest), amb els vuit usuaris de [`api.md` §13.9](api.md#139-model-intern):

  | `id` | Nom | `username` | Email | Telèfon | Saldo |
  |---|---|---|---|---|---|
  | `usr-01` | Usuari demo | `demo` | `demo@evolt.test` | `+34611223307` | 3.795,21 € (`379521`) |
  | `usr-02` | Usuari nou | `buit` | `buit@evolt.test` | `+34611223308` | 0,00 € |
  | `usr-03` | Alicia | `aliciaa415` | `alicia@evolt.test` | `+34611223301` | 0,00 € |
  | `usr-04` | Huabin | `123huabin123` | `huabin@evolt.test` | `+34611223302` | 0,00 € |
  | `usr-05` | Izan | `izanfarreny47` | `izan@evolt.test` | `+34611223303` | 0,00 € |
  | `usr-06` | Jiajun | `yayuuun` | `jiajun@evolt.test` | `+34611223304` | 0,00 € |
  | `usr-07` | Junhao | `junhaozhang` | `junhao@evolt.test` | `+34611223305` | 0,00 € |
  | `usr-08` | Martí | `sudo-itramplay` | `marti@evolt.test` | `+34611223306` | 0,00 € |

- Cap enviament fet avui: el límit diari d'enviament comença a 1.000,00 € (`100000`).
- Sol·licituds enviades per l'usuari 1 (US-15, [`api.md` §14.8](api.md#148-model-intern)): `req-01` a Huabin, 42,00 €, «Pizza del diumenge», fa 9 dies (caducada), i `req-02` a Alicia, 25,00 €, «El sopar de divendres», ahir a les 19:30 (pendent). La resta d'usuaris no n'han enviat cap.
- Rellotge fixat a **T0 = `2026-11-15T21:15:00+01:00`** a les proves que miren la data d'un enviament.

---

## US-13 · Cercar un usuari

### API (T13.2)

| Id | Situació inicial | Acció | Resultat esperat |
|---|---|---|---|
| **CU-01** | Seed (usuari 1) | `GET /api/users` | `200` amb 7 usuaris en aquest ordre: Alicia, Huabin, Izan, Jiajun, Junhao, Martí, Usuari nou. L'usuari 1 no hi surt. |
| **CU-02** | Seed | Mirar cada element de CU-01 | Té exactament les claus `id`, `name` i `username`: cap saldo, ni email, ni telèfon, ni XP. |
| **CU-03** | Seed | `GET /api/users?q=` i `GET /api/users?q=%20%20` | La mateixa llista que CU-01. |
| **CU-04** | Seed | `q=hua`, `q=@hua` i `q=@123HUABIN123` | `items` només amb Huabin (`usr-04`) les tres vegades: coincidència per `@usuari`. |
| **CU-05** | Seed | `q=marti` i `q=MARTÍ` | Només Martí: coincidència pel nom, sense majúscules ni accents. |
| **CU-06** | Seed | `q=huabin@evolt.test` i `q=  Huabin@Evolt.TEST  ` | Només Huabin: coincidència per l'email sencer. |
| **CU-07** | Seed | `q=evolt.test` i `q=huabin@` | `items: []`: una part de l'email no coincideix. |
| **CU-08** | Seed | `q=611 22 33 02`, `q=+34 611 22 33 02`, `q=611223302` i `q=0034611223302` | Només Huabin les quatre vegades: es comparen les 9 últimes xifres. |
| **CU-09** | Seed | `q=612 34 56 78` | `200` amb `items: []`. |
| **CU-10** | Seed | `q=11223302` (8 xifres) | `items: []`: amb menys de 9 xifres no es busca per telèfon, i cap nom ni `@usuari` hi coincideix. |
| **CU-11** | Seed (usuari 1) | `q=Usuari demo`, `q=@demo`, `q=demo@evolt.test` i `q=611 22 33 07` | `items: []` les quatre vegades: no surto als meus resultats. |
| **CU-12** | Seed (usuari 1) | `q=usuari` | Només Usuari nou: el nom de l'usuari 1 també hi coincideix, però no surt. |
| **CU-13** | Seed | `q=` amb 64 caràcters | `200`. |
| **CU-14** | Seed | `q=` amb 65 caràcters | `422 VALIDATION_ERROR`. |
| **CU-15** | Un usuari registrat i encara pendent (`anna@x.com`) | `GET /api/users?q=anna` i `GET /api/users?q=anna@x.com` | `items: []`: un compte pendent no surt mai. |
| **CU-16** | Un usuari registrat i verificat amb `anna@x.com` | `GET /api/users?q=anna` | Surt amb `name: null` i `username: "anna"`. |
| **CU-17** | Seed + 12 usuaris més verificats | `GET /api/users` | `200` amb 10 usuaris, els 10 primers pel nom visible. |
| **CU-18** | Seed | `GET /api/users/usr-04` | `200` `{ "id": "usr-04", "name": "Huabin", "username": "123huabin123" }`. |
| **CU-19** | Seed | `GET /api/users/usr-99`, `GET /api/users/4` i `GET /api/users/huabin` | `404 RECIPIENT_NOT_FOUND`. |
| **CU-20** | L'usuari pendent de CU-15 | `GET /api/users/<el seu id>` | `404 RECIPIENT_NOT_FOUND`. |
| **CU-21** | Seed | `GET /api/users` i `GET /api/users/usr-04` sense sessió (backend amb `ALLOW_X_USER_ID=false`) | `401 UNAUTHENTICATED` totes dues. |
| **CU-22** | Seed | Registrar `Anna.Puig+evolt@x.com`, després `anna.puigevolt@y.com`, i verificar tots dos | Els seus `username` són `anna.puigevolt` i `anna.puigevolt2`. |
| **CU-23** | Seed | Registrar el telèfon `600 11 22 33` i verificar-lo | El seu `username` és `usuari` seguit del seu id (p. ex. `usuari9`), i `GET /api/users?q=600112233` el troba. |

### Pantalla (T13.3)

| Id | Què fas | Què has de veure |
|---|---|---|
| **CUP-01** | A Inici, toca «Enviar diners». | S'obre «Enviar diners» (`/pagaments`) amb la barra «@usuari, telèfon o email» i la llista inicial: Alicia, Huabin, Izan, Jiajun, Junhao, Martí i Usuari nou. |
| **CUP-02** | Mira les files. | Cada fila té les inicials, el nom i l'`@usuari` en gris. Cap import ni cap saldo. |
| **CUP-03** | Escriu `611 22 33 02`. | Sense sortir de la pantalla, la llista es queda només amb Huabin. |
| **CUP-04** | Escriu `612 34 56 78`. | Surt «No hi ha resultats». |
| **CUP-05** | Esborra el text. | Torna la llista inicial, sense «No hi ha resultats». |
| **CUP-06** | Escriu `@demo`. | «No hi ha resultats»: no surts als teus resultats. |
| **CUP-07** | Escriu 65 caràcters. | «Les dades no són vàlides. Revisa-les i torna-ho a provar.» amb «Reintentar». |
| **CUP-08** | Toca la fila de Huabin. | S'obre `/pagaments/enviar?to=usr-04` amb Huabin com a destinatari. No surt cap finestra ni cap marca a la fila. |
| **CUP-09** | Recarrega `/pagaments/enviar?to=usr-04`. | Continua sortint Huabin com a destinatari. |
| **CUP-10** | Obre `/pagaments/enviar?to=usr-99`. | «No hem trobat aquest destinatari.» i «Torna a triar el destinatari». |
| **CUP-11** | Amb un usuari registrat sense nom, cerca'l. | La fila mostra el seu `@usuari` com a nom. |

---

## US-14 · Enviar diners a usuaris

### API (T14.1 i T14.2)

| Id | Situació inicial | Acció | Resultat esperat |
|---|---|---|---|
| **EN-01** | Seed, T0 | `POST /api/transfers` amb `{ "toUserId": "usr-02", "amount": 2000, "concept": "El sopar de divendres" }` | `201` `{ balance: 377521, movement: { amount: 2000, concept: "El sopar de divendres", date: T0, type: "expense", icon: "transfer", counterparty: "Usuari nou", status: "completed" }, recipient: { id: "usr-02", name: "Usuari nou", username: "buit" } }`. |
| **EN-02** | EN-01 fet | `GET /api/home` (usuari 1) | `balance` `377521`; el primer de `lastMovements` és el moviment d'EN-01. |
| **EN-03** | EN-01 fet | `GET /api/home` (usuari 2) | `balance` `2000`; el primer de `lastMovements` és «El sopar de divendres», `2000`, `type: "income"`, `icon: "transfer"`, `counterparty: "Usuari demo"`. |
| **EN-04** | Seed | Enviar `2000` a `usr-02` sense `concept`, i amb `"concept": "   "` | `201` les dues vegades. El moviment de l'usuari 1 diu «Transferència enviada» i el de l'usuari 2, «Transferència rebuda». |
| **EN-05** | EN-01 fet | `GET /api/dev/outbox?to=demo@evolt.test` i `?to=buit@evolt.test` | El primer missatge de cadascú: `transfer_sent` «Has enviat 20,00 € a Usuari nou.» i `transfer_received` «Usuari demo t'ha enviat 20,00 €: El sopar de divendres.». Canal `email`, sense `code` ni `link`. |
| **EN-06** | EN-01 fet | `GET /api/movements?type=expense` (usuari 1), `GET /api/movements?type=income` (usuari 2), i `GET /api/movements?q=usuari nou` (usuari 1) | El moviment d'EN-01 surt el primer a la primera i a la tercera; el de l'usuari 2 surt el primer a la segona. |
| **EN-07** | EN-01 fet | `GET /api/movements/<id>` dels dos moviments | `200` amb el detall de cadascun: `status: "completed"` i una `reference` diferent. |
| **EN-08** | EN-01 fet | Sumar els moviments de l'usuari 1 i els de l'usuari 2 | `377521` i `2000`: cada saldo continua sent la suma dels seus moviments. |
| **EN-09** | Seed | Enviar `379521` (tot el saldo) a `usr-02` | `422 TRANSFER_LIMIT_EXCEEDED` amb `remainingToday: 100000`: el límit es comprova encara que hi hagi saldo. |
| **EN-10** | Usuari 2 amb saldo `5000` (rebut de l'usuari 1) | L'usuari 2 envia `5000` a `usr-01` | `201`; el compte de l'usuari 2 queda a `0`. |
| **EN-11** | Usuari 2 amb saldo `0` | L'usuari 2 envia `100` a `usr-01` | `422 INSUFFICIENT_BALANCE`. No canvia res. |
| **EN-12** | Seed | Enviar `2000` i després `98000` a `usr-02` | `201` totes dues: arribar exactament a 1.000,00 € està permès. |
| **EN-13** | EN-12 fet | Enviar `1` més a `usr-03` | `422 TRANSFER_LIMIT_EXCEEDED` amb `details.remainingToday: 0`. |
| **EN-14** | Enviats `2000` avui | Enviar `98001` | `422 TRANSFER_LIMIT_EXCEEDED` amb `details.remainingToday: 98000`. No canvia res. |
| **EN-15** | Enviats `100000` ahir (rellotge fixat) | Enviar `2000` avui | `201`: el límit és per dia natural de Madrid. |
| **EN-16** | Seed | Recarregar `50000` i `50000`, i després enviar `100000` a `usr-02` | `201` les tres: el límit de recàrrega i el d'enviament són independents. |
| **EN-17** | EN-12 fet | Recarregar `50000` | `201`: enviar no gasta límit de recàrrega. |
| **EN-18** | Usuari 2 ha rebut `100000` avui | L'usuari 2 envia `50000` | `201`: els diners rebuts no compten per al límit. |
| **EN-19** | Seed | Enviar `2000` a `usr-01` (a mi mateix) | `422 SELF_TRANSFER`. No canvia res. |
| **EN-20** | Seed | Enviar `2000` a `usr-99`, a `"4"` i a `"huabin"` | `404 RECIPIENT_NOT_FOUND`. |
| **EN-21** | L'usuari pendent de CU-15 | Enviar-li `2000` | `404 RECIPIENT_NOT_FOUND`. |
| **EN-22** | Seed | Enviar `0`, i després `-100`, a `usr-02` | `422 INVALID_AMOUNT` totes dues vegades. |
| **EN-23** | Seed | Cossos `{ "toUserId": "usr-02", "amount": "2000" }`, `amount: 20.0`, sense `amount`, sense `toUserId`, `toUserId: 2`, i `concept` de 141 caràcters | `422 VALIDATION_ERROR`. Amb `concept` de 140 caràcters, `201`. |
| **EN-24** | Seed | Enviar `0` a `usr-99`; `0` a `usr-01`; i `500000` a `usr-01` | `RECIPIENT_NOT_FOUND`, `SELF_TRANSFER` i `SELF_TRANSFER`: l'ordre de 13.4. |
| **EN-25** | Usuari 2 amb saldo `0` | L'usuari 2 envia `0` a `usr-01` | `422 INVALID_AMOUNT`: l'import es comprova abans que el saldo. |
| **EN-26** | Seed | Qualsevol error d'EN-11 a EN-25 | No canvien els saldos, ni el nombre de moviments, ni la bústia. |
| **EN-27** | Seed. Test amb `monkeypatch`: falla una escriptura que no és la primera | Enviar `2000` a `usr-02` | `500 INTERNAL_ERROR`. No canvia res: es desfà el que ja s'havia escrit. |
| **EN-28** | Seed, backend amb `SIMULATE_ERROR_RATE=100` | Enviar `2000` a `usr-02` | `500 INTERNAL_ERROR` i, sense la simulació, els saldos de partida. |
| **EN-29** | Usuari 1 amb `60000` enviats avui | Dos enviaments de `30000` alhora | Un `201` i l'altre `422 TRANSFER_LIMIT_EXCEEDED`: el límit no es pot passar. |
| **EN-30** | EN-01 fet | Mirar l'XP dels dos usuaris | No ha canviat. |
| **EN-31** | EN-01 fet | `POST /api/dev/reset` | Els dos saldos, els moviments i la bústia tornen al seed. |
| **EN-32** | Seed | `POST /api/transfers` sense sessió (backend amb `ALLOW_X_USER_ID=false`) | `401 UNAUTHENTICATED`. |
| **EN-33** | Seed | `GET /api/transfers/limit` (usuari 1) | `200` `{ "dailyLimit": 100000, "remainingToday": 100000 }`. |
| **EN-34** | EN-01 fet | `GET /api/transfers/limit` (usuari 1 i usuari 2) | Usuari 1: `remainingToday: 98000`. Usuari 2: `100000`, perquè els diners rebuts no compten. |
| **EN-35** | EN-12 fet (1.000,00 € enviats avui) | `GET /api/transfers/limit` | `remainingToday: 0`. L'endemà a les 00:00 (rellotge fixat), `100000`. |
| **EN-36** | Seed | `GET /api/transfers/limit` sense sessió | `401 UNAUTHENTICATED`. |

### Pantalla (T14.3 i T14.4)

| Id | Què fas | Què has de veure |
|---|---|---|
| **ENP-01** | A «Enviar diners», toca «Usuari nou». | S'obre «Enviar» amb Usuari nou i `@buit`, la casella «Import», el teclat numèric, «Concepte» i «Continuar». |
| **ENP-02** | Escriu `4.000,00`. | «No tens prou saldo.» en vermell i «Continuar» desactivat. No s'envia cap petició. |
| **ENP-03** | Amb 20,00 € enviats avui, escriu `981`. | Sense tocar «Continuar»: exactament «Has superat el límit diari de 1.000,00 €.» en vermell i «Continuar» desactivat. «Enviar» ho sap per `GET /api/transfers/limit`. |
| **ENP-04** | Escriu `20`, el concepte «El sopar de divendres» i toca «Continuar». | «Confirmar» amb el destinatari, l'import, el concepte i el saldo disponible. |
| **ENP-05** | Toca «Confirmar enviament». | Tic verd «Has enviat 20,00 € a Usuari nou» i «Saldo disponible: 3.775,21 €». 1,5 s després torna sol a Inici. |
| **ENP-06** | Mira Inici. | Saldo 3.775,21 € i, el primer moviment, «−20,00 €» en vermell. Recarregar no ho canvia. |
| **ENP-07** | Inicia sessió com a `buit@evolt.test`. | Saldo 20,00 € i el primer moviment, «+20,00 €» en verd. |
| **ENP-08** | Entre «Continuar» i «Confirmar enviament», gasta el saldo des d'una altra pestanya i confirma. | Surt el mateix missatge vermell i no s'envia res. |
| **ENP-09** | Obre «Enviar» amb el teu propi id (`?to=usr-01`) i confirma un enviament. | «No et pots enviar diners a tu mateix.» i no es mou res. |
| **ENP-10** | Envia sense concepte. | A Inici, «Transferència enviada»; a la sessió de qui rep, «Transferència rebuda». |
| **ENP-11** | Amb el backend a `SIMULATE_ERROR_RATE=100`, confirma un enviament. | «S'ha produït un error inesperat. Torna-ho a provar més tard.» en vermell i el saldo no canvia. |

---

## US-15 · Sol·licitar diners

### API (T15.2)

| Id | Situació inicial | Acció | Resultat esperat |
|---|---|---|---|
| **SO-01** | Seed, T0 | `POST /api/money-requests` amb `{ "toUserId": "usr-03", "amount": 2500, "concept": "El sopar de divendres" }` | `201` `{ id: "req-03", to: { id: "usr-03", name: "Alicia", username: "aliciaa415" }, amount: 2500, concept: "El sopar de divendres", status: "pending", createdAt: T0, expiresAt: "2026-11-22T00:00:00+01:00" }`. |
| **SO-02** | SO-01 fet | `GET /api/money-requests` (usuari 1) | `200` amb `req-03`, `req-02` i `req-01`, en aquest ordre. `req-01` és `expired` i les altres dues, `pending`. |
| **SO-03** | SO-01 fet | Mirar cada element de SO-02 | Té exactament les claus `id`, `to`, `amount`, `concept`, `status`, `createdAt` i `expiresAt`; `to` només té `id`, `name` i `username`. |
| **SO-04** | SO-01 fet | `GET /api/home`, `GET /api/movements`, `GET /api/pots` (usuaris 1 i 3) | Igual que abans de SO-01: una sol·licitud no mou diners. |
| **SO-05** | SO-01 fet | `GET /api/dev/outbox?to=alicia@evolt.test` | El primer missatge és `money_request`, «Usuari demo et demana 25,00 €: El sopar de divendres.», canal `email`, sense `code` ni `link`. |
| **SO-06** | Seed | `GET /api/money-requests` com a usuari 2 | `200` amb `items: []`. |
| **SO-07** | Seed | Demanar `2500` a `usr-01` (a mi mateix) | `422 SELF_REQUEST`. No es desa res ni hi ha cap missatge nou. |
| **SO-08** | Seed | Demanar a `usr-99`, a `"3"` i a l'usuari pendent de CU-15 | `404 RECIPIENT_NOT_FOUND`. |
| **SO-09** | Seed | Demanar `0` i després `-100` | `422 INVALID_AMOUNT`. |
| **SO-10** | Seed | Demanar `100000000` (1.000.000,00 €) i després `100000001` | Primer `201`; després `422 AMOUNT_OVER_LIMIT`. |
| **SO-11** | Seed | Concepte `""`, `"   "` i de 141 caràcters | `422 INVALID_CONCEPT`. Amb 140 caràcters, `201`, i amb `"  Sopar  "`, el concepte es desa com a «Sopar». |
| **SO-12** | Seed | Cossos sense `concept`, amb `amount: "2500"`, amb `toUserId: 3` i sense `toUserId` | `422 VALIDATION_ERROR`. |
| **SO-13** | Seed | Demanar `0` a `usr-01` i `0` a `usr-99` | `SELF_REQUEST` i `RECIPIENT_NOT_FOUND`: l'ordre de 14.2. |
| **SO-14** | Una sol·licitud creada el 14/11 a les 19:30 | `GET /api/money-requests` el 20/11 a les 23:59:59 i el 21/11 a les 00:00 (rellotge fixat) | `pending` i després `expired`, amb `expiresAt` `2026-11-21T00:00:00+01:00` totes dues vegades. |
| **SO-15** | SO-14 | Mirar la sol·licitud desada | Continua desada com a pendent: `expired` no es desa mai. |
| **SO-16** | Seed | `POST /api/money-requests/req-02/cancel` (usuari 1) | `200` `{ "status": "ok" }`. `GET /api/money-requests` ja no té `req-02`. |
| **SO-17** | SO-16 fet | Tornar a cancel·lar `req-02` | `404 REQUEST_NOT_FOUND`. |
| **SO-18** | Seed | Cancel·lar `req-01` (caducada) | `422 REQUEST_NOT_PENDING`, i `req-01` continua a la llista. |
| **SO-19** | Seed | Cancel·lar `req-02` com a usuari 3 (Alicia, la destinatària) | `404 REQUEST_NOT_FOUND`, amb el mateix cos que SO-17; `req-02` continua pendent. |
| **SO-20** | Seed | Cancel·lar `req-99` i `abc` | `404 REQUEST_NOT_FOUND`. |
| **SO-21** | Seed | Cancel·lar `req-02` el dia que caduca a les 00:00 (rellotge fixat) | `422 REQUEST_NOT_PENDING`: l'estat es calcula en el moment de la petició. |
| **SO-22** | SO-16 fet | Crear una sol·licitud nova | Té l'id `req-03`: l'id d'una cancel·lada no es torna a fer servir. |
| **SO-23** | Seed. Test amb `monkeypatch`: falla el missatge de la bústia | Crear una sol·licitud | `500 INTERNAL_ERROR`; no es desa cap sol·licitud. |
| **SO-24** | SO-01 fet | `POST /api/dev/reset` | Les sol·licituds tornen a ser `req-01` i `req-02`. |
| **SO-25** | Seed | Les tres rutes sense sessió (backend amb `ALLOW_X_USER_ID=false`) | `401 UNAUTHENTICATED`. |

### Pantalla (T15.3)

| Id | Què fas | Què has de veure |
|---|---|---|
| **SOP-01** | Obre «Sol·licituds enviades» (`/requests`) amb l'usuari 1. | La pendent a Alicia (25,00 €, «El sopar de divendres», etiqueta «Pendent» i «Cancel·lar») i la caducada a Huabin (42,00 €, «Pizza del diumenge», «Caducada», sense «Cancel·lar»). |
| **SOP-02** | Obre `/requests` amb l'usuari 2. | «Encara no has enviat cap sol·licitud.» i «Demanar diners». |
| **SOP-03** | A «Demanar diners», sense destinatari, import ni concepte. | «Enviar sol·licitud» desactivat. |
| **SOP-04** | Tria Alicia, escriu `25` i el concepte «El sopar de divendres», i envia. | «Sol·licitud enviada a Alicia.» i, 1,5 s després, `/requests` amb la fila nova la primera. |
| **SOP-05** | A la cerca de destinatari, escriu el teu nom. | No surts als resultats. |
| **SOP-06** | Amb el backend a `SIMULATE_ERROR_RATE=100`, envia una sol·licitud. | Error en vermell, i el destinatari, l'import i el concepte continuen escrits. |
| **SOP-07** | A la fila pendent, toca «Cancel·lar». | Diàleg «Cancel·lar sol·licitud» amb «Segur que vols cancel·lar aquesta sol·licitud?», «Cancel·lar» i «Confirmar». |
| **SOP-08** | Tanca el diàleg amb «Cancel·lar», amb `Esc` i fent clic fora. | Es tanca sense cap petició; la fila continua igual. |
| **SOP-09** | Torna a obrir-lo i toca «Confirmar». | «Sol·licitud cancel·lada.» a dalt i la fila desapareix; recarregant, no torna. |
| **SOP-10** | Cancel·la una sol·licitud que ha caducat mentre tenies la pantalla oberta. | «Només es poden cancel·lar les sol·licituds pendents.» i la llista es torna a carregar. |
| **SOP-11** | Comprova Inici després d'enviar una sol·licitud. | El saldo i els moviments no han canviat. |

---

## Casos de les històries i proves

| Cas de la història | Proves |
|---|---|
| US-13 · Cerca per @usuari, telèfon o email | CU-04, CU-05, CU-06, CU-08, CUP-03 |
| US-13 · Telèfon amb i sense +34 dona la mateixa fila (9 últimes xifres) | CU-08, CU-10, CUP-03 |
| US-13 · Mai es mostren dades financeres als resultats | CU-02, CUP-02 |
| US-13 · No apareixo als meus propis resultats | CU-01, CU-11, CU-12, CUP-06 |
| US-13 · Sense coincidències surt «No hi ha resultats»; amb el camp buit torna la llista inicial | CU-03, CU-09, CUP-04, CUP-05 |
| US-13 · Tocar una fila obre «Enviar» amb el destinatari, que es manté en recarregar | CU-18, CU-19, CUP-08, CUP-09, CUP-10 |
| US-13 · Un usuari sense nom mostra l'@usuari | CU-16, CUP-11 |
| US-13 · Més de 64 caràcters: «Les dades no són vàlides…» amb «Reintentar» | CU-13, CU-14, CUP-07 |
| US-13 · `User` porta `username` i `phone`; el seed té 8 usuaris | CU-01, CU-22, CU-23 |
| US-14 · Import més gran que 0 i per sota del límit diari | EN-12, EN-13, EN-14, EN-22, ENP-03 |
| US-14 · Concepte opcional | EN-01, EN-04, EN-23, ENP-10 |
| US-14 · Sense prou saldo: «No tens prou saldo.» i no s'envia res | EN-11, EN-26, ENP-02 |
| US-14 · El límit és 1.000,00 €/dia i la igualtat està permesa; el missatge surt a «Enviar», abans de confirmar | EN-12, EN-13, EN-15, EN-33, EN-34, EN-35, ENP-03 |
| US-14 · El servidor torna a comprovar saldo i límit en confirmar | EN-11, EN-14, EN-29, ENP-08 |
| US-14 · Enviar-me diners a mi mateix dona «No et pots enviar diners a tu mateix.» | EN-19, EN-24, ENP-09 |
| US-14 · Èxit: tic verd amb l'import, el destinatari i el saldo disponible | EN-01, ENP-05 |
| US-14 · A Inici surt «−» a qui envia i «+» a qui rep, i recarregar no ho perd | EN-02, EN-03, ENP-06, ENP-07 |
| US-14 · Notificació a qui envia i a qui rep, a la bústia simulada | EN-05 |
| US-14 · Sense concepte, «Transferència enviada» i «Transferència rebuda» | EN-04, ENP-10 |
| US-14 · Destinatari inexistent: «No hem trobat aquest destinatari.» | EN-20, EN-21, CUP-10 |
| US-15 · Quatre estats, sense «Cancel·lada»; a l'Sprint 2 només Pendent i Caducada | SO-01, SO-02, SOP-01 |
| US-15 · «Caducada» es deriva en llegir, pel dia natural de Madrid (7 dies) | SO-14, SO-15, SO-21 |
| US-15 · Una sol·licitud no mou diners; només deixa l'avís a la bústia simulada | SO-04, SO-05, SOP-11 |
| US-15 · «Enviar sol·licitud» desactivat sense destinatari, import vàlid (fins a 1.000.000,00 €) i concepte d'1 a 140 caràcters | SO-09, SO-10, SO-11, SOP-03 |
| US-15 · La cerca no et retorna mai a tu, i el servidor respon «No et pots demanar diners a tu mateix.» | SO-07, SO-13, SOP-05 |
| US-15 · «Cancel·lar» només a les pendents; el diàleg es tanca sense cap crida | SO-18, SOP-01, SOP-07, SOP-08 |
| US-15 · En confirmar, s'esborra i desapareix per sempre | SO-16, SO-17, SO-22, SOP-09 |
| US-15 · Si ja no és pendent, «Només es poden cancel·lar…»; si no és teva, «Aquesta sol·licitud ja no existeix.» | SO-18, SO-19, SO-20, SOP-10 |
| US-15 · Èxit: «Sol·licitud enviada a Alicia.» i la fila nova la primera; un error deixa el formulari intacte | SO-01, SO-02, SOP-04, SOP-06 |

Proves que no surten d'un cas de la història, sinó del contracte: CU-15, CU-17, CU-20 i CU-21 (comptes pendents, màxim de 10 i sessió); EN-06 a EN-08 (llistat, detall i invariants), EN-09 i EN-16 a EN-18 (límits independents), EN-23 a EN-25 (format i ordre de les validacions), EN-27 a EN-32 i EN-36 (tot o res, concurrència, XP, reinici i sessió); SO-03, SO-06, SO-08, SO-12, SO-23 a SO-25 (forma, llista buida, format, tot o res, reinici i sessió).
