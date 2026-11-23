# Contracte de l'API

Contracte compartit entre el backend (FastAPI) i el frontend per a les històries **US-07** (saldo a la pantalla principal), **US-08** (llistat de moviments) i **US-09** (recàrrega de prova) de l'Sprint 0, i **US-01 a US-04** (accés: registre, verificació, inici de sessió i recuperació de contrasenya) de l'Sprint 1.

- Tasques: T07.1 (issue #4) per a l'Sprint 0 i T01.1 (issue #56) per a l'[apartat 8](#8-accés-us-01-a-us-04).
- Qualsevol canvi en aquest contracte es fa amb una PR sobre aquest fitxer, revisada per almenys una persona de backend i una de frontend.
- Els punts nous es marquen amb **[PROPOSTA — pendent de validar]** i s'han de confirmar a la revisió de la PR que els proposa. Quan s'aprova, la marca es treu i el punt queda a l'[apartat 7](#7-propostes-del-contracte).

## Índex

1. [Convencions generals](#1-convencions-generals)
2. [Usuari actual i estat del servei](#2-usuari-actual-i-estat-del-servei)
3. [Objecte `Movement`](#3-objecte-movement)
4. [Endpoints](#4-endpoints)
5. [Errors](#5-errors)
6. [Model intern (no exposat a l'API)](#6-model-intern-no-exposat-a-lapi)
7. [Propostes del contracte](#7-propostes-del-contracte)
8. [Accés (US-01 a US-04)](#8-accés-us-01-a-us-04)
9. [Guardioles (US-17 i US-18)](#9-guardioles-us-17-i-us-18)
10. [Moviments: filtres, detall i informe (US-10 i US-11)](#10-moviments-filtres-detall-i-informe-us-10-i-us-11)
12. [Multidivisa: subcomptes i canvi (US-25, US-26 i US-27)](#12-multidivisa-subcomptes-i-canvi-us-25-us-26-i-us-27)
13. [Pagaments: cercar usuaris i enviar diners (US-13 i US-14)](#13-pagaments-cercar-usuaris-i-enviar-diners-us-13-i-us-14)

---

## 1. Convencions generals

### Rutes i format

- Totes les rutes comencen per `/api`.
- Les peticions i les respostes són JSON en UTF-8 (`Content-Type: application/json`).
- Les claus JSON van en **camelCase** (`totalSaved`, `lastMovements`, `nextOffset`, `remainingToday`).

### Imports

- Tots els imports són **enters en cèntims**. Exemple: 500 € = `50000`; 1.250,50 € = `125050`.
- L'`amount` d'un moviment és **sempre positiu**. El sentit (entrada o sortida de diners) el dona el camp `type` (`income` / `expense`), mai el signe.
- El frontend és qui converteix els cèntims a euros per mostrar-los (p. ex. `125050` → «1.250,50 €»).

### Dates

- Format ISO 8601 **amb desplaçament horari**. Exemple: `2026-10-12T22:14:00+02:00`.
- El desplaçament és el de la zona `Europe/Madrid`: `+02:00` a l'horari d'estiu i `+01:00` a l'horari d'hivern.
- Precisió de segons, sense fraccions de segon.

### Què vol dir "avui"

"Avui" és el **dia natural a la zona `Europe/Madrid`**: de les 00:00:00 a les 23:59:59 hora de Madrid, sigui quina sigui la zona horària del servidor o del client.

### Límits de recàrrega (US-09)

| Límit | Valor | Equivalent |
|---|---|---|
| Màxim per recàrrega | `50000` | 500,00 € |
| Màxim per dia natural (suma de recàrregues d'avui) | `100000` | 1.000,00 € |

Recarregar **exactament** el màxim (500 € en una recàrrega o 1.000 € en un dia) està permès.

---

## 2. Usuari actual i estat del servei

### Capçalera `X-User-Id`

> **Sprint 1.** Amb el login, l'usuari surt del token de sessió (`Authorization: Bearer`, [apartat 8.2](#82-sessió)). Aquesta capçalera només es manté com a eina de desenvolupament i de tests mentre la variable `ALLOW_X_USER_ID` estigui activada; l'[apartat 8.2](#transició-des-dx-user-id) explica l'ordre en què es resol l'usuari. Les regles següents descriuen el comportament amb la capçalera activada.

A l'Sprint 0 no hi ha login. L'usuari de cada petició es resol així:

- `X-User-Id` és **opcional**.
- Sense la capçalera, el backend fa servir l'**usuari 1**.
- Amb `X-User-Id: 2`, el backend fa servir l'**usuari 2**, que té un compte **sense moviments ni guardioles**. Serveix per provar els estats buits.
- Amb un valor **no vàlid** (no numèric, buit, o número d'un usuari que no existeix), qualsevol endpoint que resolgui l'usuari retorna `422 VALIDATION_ERROR` sense `details`. Exemples: `X-User-Id: abc`, `X-User-Id: 99`. `GET /api/health` no resol l'usuari i continua tornant `200`.

```http
GET /api/home HTTP/1.1
X-User-Id: 2
```

> Aquesta capçalera és una eina de desenvolupament, **no** un mecanisme d'autenticació. Quan hi hagi login, l'usuari sortirà de la sessió i la capçalera desapareixerà.

### `GET /api/health`

Comprova que el backend està en marxa. No fa servir la capçalera `X-User-Id`.

**Resposta `200`:** `{ status }`

| Camp | Tipus | Descripció |
|---|---|---|
| `status` | string | Sempre `"ok"` quan el backend respon. |

**Resposta:**

```json
{
  "status": "ok"
}
```

---

## 3. Objecte `Movement`

Representa un moviment del compte principal. És el mateix objecte a `GET /api/home`, `GET /api/movements`, `POST /api/topups`, `POST /api/pots/{potId}/contributions` ([apartat 9.4](#94-post-apipotspotidcontributions)) i `POST /api/transfers` ([apartat 13.4](#134-post-apitransfers)).

| Camp | Tipus | Notes |
|---|---|---|
| `id` | string | Identificador opac. El frontend no l'ha d'interpretar. És un string, per no dependre de l'emmagatzematge. |
| `amount` | integer | Cèntims, sempre `> 0`. |
| `concept` | string | Text que es mostra a l'usuari. A les recàrregues val `"Recàrrega"`. |
| `date` | string | ISO 8601 amb desplaçament (vegeu l'[apartat 1](#dates)). |
| `type` | `"income"` \| `"expense"` | `income`: entren diners. `expense`: surten diners. |
| `icon` | string | Un dels valors de la llista tancada següent. |
| `counterparty` | string \| `null` | Qui paga o qui cobra. La clau sempre hi és; val `null` quan no n'hi ha. Vegeu l'[apartat 10.1](#101-camps-nous-de-movement). |
| `status` | `"completed"` \| `"pending"` | La pantalla mostra «Completat» o «Pendent». Vegeu l'[apartat 10.1](#101-camps-nous-de-movement). |
| `reference` | string | Referència única i opaca, generada pel backend. Vegeu l'[apartat 10.1](#101-camps-nous-de-movement). |

Valors d'`icon` (llista tancada):

| Valor | Ús |
|---|---|
| `topup` | Recàrrega de prova |
| `salary` | Nòmina |
| `transfer` | Transferència |
| `shopping` | Compres |
| `food` | Menjar i restaurants |
| `transport` | Transport |
| `savings` | Aportació a una guardiola ([apartat 9.4](#94-post-apipotspotidcontributions)) |
| `other` | Qualsevol altre moviment |

Exemple:

```json
{
  "id": "mov-20",
  "amount": 2350,
  "concept": "Restaurant La Plaça",
  "date": "2026-10-11T21:15:00+02:00",
  "type": "expense",
  "icon": "food",
  "counterparty": null,
  "status": "completed",
  "reference": "EVT-000020"
}
```

> El camp intern `kind` **no forma part de l'API**: cap resposta l'inclou. Vegeu l'[apartat 6](#6-model-intern-no-exposat-a-lapi).

---

## 4. Endpoints

| Mètode i ruta | Èxit | Història |
|---|---|---|
| `GET /api/home` | `200` | US-07 |
| `GET /api/movements` | `200` | US-08 |
| `POST /api/topups` | `201` | US-09 |
| `POST /api/dev/reset` | `200` | T09.6 |
| `POST /api/auth/register` | `201` | US-01 · [8.5](#85-post-apiauthregister) |
| `POST /api/auth/verify` | `200` | US-02 · [8.6](#86-post-apiauthverify) |
| `POST /api/auth/resend-code` | `200` | US-02 · [8.7](#87-post-apiauthresend-code) |
| `POST /api/auth/login` | `200` | US-03 · [8.8](#88-post-apiauthlogin) |
| `POST /api/auth/logout` | `200` | US-03 · [8.9](#89-post-apiauthlogout) |
| `POST /api/auth/forgot-password` | `200` | US-04 · [8.10](#810-post-apiauthforgot-password) |
| `POST /api/auth/reset-password` | `200` | US-04 · [8.11](#811-post-apiauthreset-password) |
| `GET /api/dev/outbox` | `200` | US-02 a US-04 · [8.12](#812-get-apidevoutbox) |
| `GET /api/pots` | `200` | US-17 · [9.2](#92-get-apipots) |
| `POST /api/pots` | `201` | US-17 · [9.3](#93-post-apipots) |
| `POST /api/pots/{potId}/contributions` | `201` | US-18 · [9.4](#94-post-apipotspotidcontributions) |
| `GET /api/pots/{potId}/movements` | `200` | US-18 · [9.5](#95-get-apipotspotidmovements) |
| `GET /api/movements/{movementId}` | `200` | US-11 · [10.3](#103-get-apimovementsmovementid) |
| `POST /api/movements/{movementId}/reports` | `201` | US-11 · [10.4](#104-post-apimovementsmovementidreports) |
| `GET /api/subaccounts` | `200` | US-25 · [12.3](#123-get-apisubaccounts) |
| `POST /api/subaccounts` | `201` | US-25 · [12.4](#124-post-apisubaccounts) |
| `POST /api/subaccounts/{subaccountId}/delete` | `200` | US-26 · [12.5](#125-post-apisubaccountssubaccountiddelete) |
| `GET /api/subaccounts/{subaccountId}/movements` | `200` | US-26 · [12.6](#126-get-apisubaccountssubaccountidmovements) |
| `POST /api/exchanges` | `201` | US-27 · [12.7](#127-post-apiexchanges) |
| `GET /api/users` | `200` | US-13 · [13.2](#132-get-apiusers) |
| `GET /api/users/{userId}` | `200` | US-13 · [13.3](#133-get-apiusersuserid) |
| `POST /api/transfers` | `201` | US-14 · [13.4](#134-post-apitransfers) |
| `GET /api/transfers/limit` | `200` | US-14 · [13.5](#get-apitransferslimit) |

A partir de la T03.1, `GET /api/home`, `GET /api/movements` i `POST /api/topups` són **rutes protegides**: necessiten una sessió ([apartat 8.2](#82-sessió)).

`GET /api/movements` accepta també els filtres de US-10 ([apartat 10.2](#102-filtres-de-get-apimovements)).

Els exemples d'aquest apartat fan servir les mateixes dades fictícies de l'usuari 1. Les dades reals són les del seed (T07.3).

### 4.1 `GET /api/home`

Resum de la pantalla principal (US-07).

**Resposta `200`:** `{ balance, totalSaved, lastMovements }`

| Camp | Tipus | Descripció |
|---|---|---|
| `balance` | integer | Saldo del compte principal, en cèntims. |
| `totalSaved` | integer | Suma dels saldos de **totes** les guardioles de l'usuari, en cèntims. `0` si no en té. |
| `lastMovements` | `Movement[]` | Els **5 moviments més recents**, del més recent al més antic. Pot tenir menys de 5 elements o ser una llista buida. Coincideix amb els 5 primers de `GET /api/movements`. |

**Petició:**

```http
GET /api/home HTTP/1.1
```

**Resposta:**

```json
{
  "balance": 125050,
  "totalSaved": 30000,
  "lastMovements": [
    {
      "id": "mov-20",
      "amount": 2350,
      "concept": "Restaurant La Plaça",
      "date": "2026-10-11T21:15:00+02:00",
      "type": "expense",
      "icon": "food",
      "counterparty": null,
      "status": "completed",
      "reference": "EVT-000020"
    },
    {
      "id": "mov-19",
      "amount": 4590,
      "concept": "Supermercat",
      "date": "2026-10-10T18:42:00+02:00",
      "type": "expense",
      "icon": "shopping",
      "counterparty": null,
      "status": "completed",
      "reference": "EVT-000019"
    },
    {
      "id": "mov-18",
      "amount": 1200,
      "concept": "Bitllet de tren",
      "date": "2026-10-09T08:05:00+02:00",
      "type": "expense",
      "icon": "transport",
      "counterparty": null,
      "status": "completed",
      "reference": "EVT-000018"
    },
    {
      "id": "mov-17",
      "amount": 180000,
      "concept": "Nòmina d'octubre",
      "date": "2026-10-01T09:00:00+02:00",
      "type": "income",
      "icon": "salary",
      "counterparty": "Empresa Demo SL",
      "status": "completed",
      "reference": "EVT-000017"
    },
    {
      "id": "mov-16",
      "amount": 5000,
      "concept": "Transferència rebuda",
      "date": "2026-09-28T13:20:00+02:00",
      "type": "income",
      "icon": "transfer",
      "counterparty": "Marta Puig",
      "status": "completed",
      "reference": "EVT-000016"
    }
  ]
}
```

Amb l'usuari 2 (`X-User-Id: 2`), `totalSaved` és `0` i `lastMovements` és `[]`. El valor de `balance` és el que fixi el seed.

### 4.2 `GET /api/movements`

Llistat paginat de tots els moviments de l'usuari (US-08), pensat per a l'scroll infinit.

**Paràmetres de consulta:**

| Paràmetre | Tipus | Per defecte | Rang vàlid |
|---|---|---|---|
| `offset` | integer | `0` | `≥ 0` |
| `limit` | integer | `20` | `1`–`50` |
| `dateFrom`, `dateTo`, `type`, `q` | — | Sense filtre | Filtres opcionals de US-10. Vegeu l'[apartat 10.2](#102-filtres-de-get-apimovements). |

- Un `offset` negatiu, un `limit` fora de rang o un valor que no sigui enter retorna `422 VALIDATION_ERROR`.
- Un `offset` igual o més gran que el nombre total de moviments **no** és un error: retorna `200` amb `items: []` i `nextOffset: null`.

**Resposta `200`:** `{ items, nextOffset }`

| Camp | Tipus | Descripció |
|---|---|---|
| `items` | `Movement[]` | Com a màxim `limit` moviments, del més recent al més antic. |
| `nextOffset` | integer \| `null` | `offset + items.length` si encara queden moviments després d'aquesta pàgina. `null` si s'ha arribat al final. |

- El frontend continua demanant pàgines amb `offset = nextOffset` fins que rep `null`.
- Ordre: per `date` descendent. Si dos moviments tenen la mateixa `date`, va primer el que s'ha creat més tard, perquè l'ordre sigui estable entre pàgines.

**Petició (primera pàgina):**

```http
GET /api/movements?offset=0&limit=3 HTTP/1.1
```

**Resposta:**

```json
{
  "items": [
    {
      "id": "mov-20",
      "amount": 2350,
      "concept": "Restaurant La Plaça",
      "date": "2026-10-11T21:15:00+02:00",
      "type": "expense",
      "icon": "food",
      "counterparty": null,
      "status": "completed",
      "reference": "EVT-000020"
    },
    {
      "id": "mov-19",
      "amount": 4590,
      "concept": "Supermercat",
      "date": "2026-10-10T18:42:00+02:00",
      "type": "expense",
      "icon": "shopping",
      "counterparty": null,
      "status": "completed",
      "reference": "EVT-000019"
    },
    {
      "id": "mov-18",
      "amount": 1200,
      "concept": "Bitllet de tren",
      "date": "2026-10-09T08:05:00+02:00",
      "type": "expense",
      "icon": "transport",
      "counterparty": null,
      "status": "completed",
      "reference": "EVT-000018"
    }
  ],
  "nextOffset": 3
}
```

**Petició (última pàgina, suposant que l'usuari té 20 moviments en total):**

```http
GET /api/movements?offset=18&limit=20 HTTP/1.1
```

**Resposta:**

```json
{
  "items": [
    {
      "id": "mov-02",
      "amount": 3999,
      "concept": "Botiga de roba",
      "date": "2026-09-03T17:10:00+02:00",
      "type": "expense",
      "icon": "shopping",
      "counterparty": null,
      "status": "completed",
      "reference": "EVT-000002"
    },
    {
      "id": "mov-01",
      "amount": 100000,
      "concept": "Ingrés inicial",
      "date": "2026-09-01T10:00:00+02:00",
      "type": "income",
      "icon": "other",
      "counterparty": null,
      "status": "completed",
      "reference": "EVT-000001"
    }
  ],
  "nextOffset": null
}
```

**Usuari sense moviments** (`X-User-Id: 2`), estat buit de US-08:

```json
{
  "items": [],
  "nextOffset": null
}
```

### 4.3 `POST /api/topups`

Recàrrega de prova simulada (US-09). No demana dades de targeta i s'aprova automàticament si compleix els límits.

**Cos de la petició:** `{ amount }`

| Camp | Tipus | Descripció |
|---|---|---|
| `amount` | integer | Import de la recàrrega en cèntims. Obligatori. |

`amount` ha de ser un **enter JSON**. Valors com `"500"` (string) o `500.5` (decimal) retornen `422 VALIDATION_ERROR`. També `500.0` es considera no vàlid.

**Resposta `201`:** `{ balance, movement }`

| Camp | Tipus | Descripció |
|---|---|---|
| `balance` | integer | Saldo **nou** del compte principal, en cèntims. |
| `movement` | `Movement` | El moviment creat, amb `type: "income"`, `concept: "Recàrrega"`, `icon: "topup"`, `amount` igual a l'import recarregat i `date` igual al moment de la recàrrega. |

El frontend pot fer servir aquest `balance` per actualitzar la pantalla principal sense tornar a demanar `GET /api/home` (US-07, criteri 4).

**Ordre de les validacions.** S'aturen al primer error:

1. Format del cos: falta `amount` o no és un enter → `VALIDATION_ERROR`.
2. Límits per recàrrega: `amount ≤ 0` → `INVALID_AMOUNT`; `amount > 50000` → `AMOUNT_OVER_LIMIT`.
3. Límit diari: recàrregues d'avui + `amount > 100000` → `DAILY_LIMIT_EXCEEDED`, amb `details.remainingToday = max(0, 100000 − recàrregues d'avui)`.

Per exemple, una recàrrega de `60000` sempre retorna `AMOUNT_OVER_LIMIT`, encara que també superi el límit diari.

**Regles:**

- Si hi ha un error, **no es modifica res**: ni el saldo ni els moviments.
- Les recàrregues **no modifiquen l'XP** de l'usuari (US-09, criteri 6).

**Petició:**

```http
POST /api/topups HTTP/1.1
Content-Type: application/json

{
  "amount": 50000
}
```

**Resposta `201`** (saldo anterior: `125050`):

```json
{
  "balance": 175050,
  "movement": {
    "id": "mov-21",
    "amount": 50000,
    "concept": "Recàrrega",
    "date": "2026-10-12T22:14:00+02:00",
    "type": "income",
    "icon": "topup",
    "counterparty": null,
    "status": "completed",
    "reference": "EVT-000021"
  }
}
```

**Exemple de límit diari.** Avui l'usuari ja ha recarregat `90000` (900,00 €), per exemple amb una recàrrega de `50000` i una de `40000`:

| Petició | Resultat |
|---|---|
| `{ "amount": 10000 }` | `201`. El total d'avui arriba just a `100000`, que està permès. |
| `{ "amount": 10001 }` | `422 DAILY_LIMIT_EXCEEDED` amb `details.remainingToday = 10000`. |

```json
{
  "code": "DAILY_LIMIT_EXCEEDED",
  "message": "Has superat el límit diari de recàrrega. Avui encara pots recarregar 100,00 €.",
  "details": { "remainingToday": 10000 }
}
```

### 4.4 `POST /api/dev/reset`

Eina de **desenvolupament** (T09.6), com la capçalera `X-User-Id`. **No l'usa el frontend**: serveix per provar l'API manualment, p. ex. amb la col·lecció [`docs/api.http`](api.http).

L'Sprint 0 manté les dades **en memòria** i les carrega del seed a l'arrencada. Aquest endpoint **restaura les dades inicials sense reiniciar el servidor**, de manera que es puguin reproduir seqüències amb estat (p. ex. el límit diari de recàrrega) des de zero.

Només existeix si la variable d'entorn `ENABLE_DEV_ROUTES` no és `false` (per defecte, sí). Al desplegament (TR06.1) està desactivada: la ruta no es registra i respon com qualsevol ruta inexistent, `500 INTERNAL_ERROR` (§5).

> **Sprint 1.** Amb `STORAGE=firestore` (P20, [apartat 8.13](#813-model-intern-de-laccés)), aquest endpoint esborra les col·leccions de Firestore i hi torna a escriure el seed. Per això només es pot fer servir amb l'**emulador de Firebase** o el projecte de desenvolupament, **mai** amb les dades del desplegament.

- **Cos de la petició:** cap.
- **Resposta `200`:** `{ status }`

| Camp | Tipus | Descripció |
|---|---|---|
| `status` | string | Sempre `"ok"` quan el reinici s'ha fet. |

**Petició:**

```http
POST /api/dev/reset HTTP/1.1
```

**Resposta:**

```json
{
  "status": "ok"
}
```

---

## 5. Errors

### Format

Totes les respostes d'error tenen aquest format:

```json
{
  "code": "CODI_ESTABLE",
  "message": "Text en català pensat per a persones.",
  "details": {}
}
```

| Camp | Tipus | Descripció |
|---|---|---|
| `code` | string | Codi estable de la taula següent. |
| `message` | string | Text en català per mostrar a l'usuari. |
| `details` | object | **Opcional.** Dades addicionals de l'error. Quan un error no en té, la clau `details` no apareix a la resposta. |

> El frontend decideix què fa a partir del **`code`** (i de `details`), **mai** a partir del text de `message`. Els textos de `message` d'aquest document són orientatius i el backend els pot ajustar sense trencar el contracte.

### Taula de codis

| `code` | HTTP | Quan | `details` |
|---|---|---|---|
| `INVALID_AMOUNT` | 422 | `amount ≤ 0`, a una recàrrega o a una aportació a una guardiola ([9.4](#94-post-apipotspotidcontributions)) | — |
| `AMOUNT_OVER_LIMIT` | 422 | `amount > 50000` | — |
| `DAILY_LIMIT_EXCEEDED` | 422 | Recàrregues d'avui + `amount > 100000` | `{ remainingToday }` (cèntims) |
| `VALIDATION_ERROR` | 422 | Paràmetres o cos mal formats: falta `amount`, no és un enter, `offset`/`limit` fora de rang, o filtres del llistat no vàlids (data mal formada, `type` desconegut o `dateFrom` posterior a `dateTo`, [10.2](#102-filtres-de-get-apimovements)) | — |
| `INTERNAL_ERROR` | 500 | Error inesperat, inclosos els que simula T08.2 | — |

Codis de l'accés (Sprint 1, [apartat 8](#8-accés-us-01-a-us-04)):

| `code` | HTTP | Quan | `details` |
|---|---|---|---|
| `UNAUTHENTICATED` | 401 | Ruta protegida sense token, o amb un token desconegut o ja tancat. També `GET /api/dev/outbox` sense la clau correcta quan `DEV_OUTBOX_KEY` està definida ([8.12](#812-get-apidevoutbox)) | — |
| `SESSION_EXPIRED` | 401 | La sessió ha passat 5 minuts sense activitat | — |
| `WEAK_PASSWORD` | 422 | La contrasenya no compleix la política ([8.4](#84-política-de-contrasenya)) | — |
| `ALREADY_REGISTERED` | 409 | L'email o el telèfon ja té un compte | — |
| `INVALID_CODE` | 422 | Codi de verificació incorrecte | — |
| `CODE_EXPIRED` | 422 | Codi de verificació caducat (10 minuts) | — |
| `TOO_MANY_ATTEMPTS` | 429 | 5 codis de verificació incorrectes: cal demanar-ne un de nou | — |
| `INVALID_CREDENTIALS` | 401 | Login amb dades incorrectes, sense dir quina falla | — |
| `ACCOUNT_LOCKED` | 423 | Compte bloquejat 15 minuts després de 5 errors de login seguits | `{ lockedUntil }` (data ISO 8601) |
| `ACCOUNT_NOT_VERIFIED` | 403 | Login correcte d'un compte encara pendent de verificació | — |
| `RESET_LINK_EXPIRED` | 422 | Enllaç de recuperació caducat, ja usat o desconegut | — |

> Fins a l'Sprint 0 tots els errors eren `422` o `500`. Els codis d'accés fan servir també `401`, `403`, `409`, `423` i `429`, i els recursos que no existeixen (p. ex. una guardiola) fan servir `404`. El frontend continua decidint només amb el `code`: l'`apiClient` ja propaga qualsevol cos d'error del contracte, sigui quin sigui l'estat HTTP.

> Qualsevol ruta o mètode no definit es tracta com a error inesperat i retorna `500 INTERNAL_ERROR` (mateix cos que `INTERNAL_ERROR`).

Codis de l'estalvi (Sprint 1, [apartat 9](#9-guardioles-us-17-i-us-18)):

| `code` | HTTP | Quan | `details` |
|---|---|---|---|
| `INVALID_POT_NAME` | 422 | El nom de la guardiola és buit o només té espais | — |
| `INVALID_TARGET` | 422 | L'objectiu de la guardiola és `≤ 0` | — |
| `INSUFFICIENT_BALANCE` | 422 | L'aportació supera el saldo del compte principal | — |
| `POT_NOT_FOUND` | 404 | La guardiola no existeix o és d'un altre usuari | — |

Codis dels moviments (Sprint 1, [apartat 10](#10-moviments-filtres-detall-i-informe-us-10-i-us-11)):

| `code` | HTTP | Quan | `details` |
|---|---|---|---|
| `MOVEMENT_NOT_FOUND` | 404 | El moviment no existeix o és d'un altre usuari | — |
| `INVALID_DESCRIPTION` | 422 | La descripció de l'informe és buida, només té espais o passa de 500 caràcters | — |

Codis de multidivisa (Sprint 2, [apartat 12](#12-multidivisa-subcomptes-i-canvi-us-25-us-26-i-us-27)):

| `code` | HTTP | Quan | `details` |
|---|---|---|---|
| `CURRENCY_NOT_SUPPORTED` | 422 | La divisa d'un subcompte nou no és a la llista ([12.1](#121-divises-i-tipus-de-canvi)) | — |
| `CURRENCY_EXISTS` | 422 | L'usuari ja té un compte en aquesta divisa | — |
| `SUBACCOUNT_NOT_FOUND` | 404 | El subcompte no existeix o és d'un altre usuari, o el canvi fa servir una divisa que no és un compte de l'usuari | — |
| `MAIN_ACCOUNT_NOT_DELETABLE` | 422 | Es vol eliminar el compte en euros | — |
| `SUBACCOUNT_NOT_EMPTY` | 422 | Es vol eliminar un subcompte amb el saldo diferent de 0 | — |
| `SAME_CURRENCY` | 422 | L'origen i el destí d'un canvi són la mateixa divisa | — |
| `AMOUNT_TOO_SMALL` | 422 | L'import d'un canvi, convertit, no arriba a una unitat menor del destí | — |

- `INVALID_AMOUNT` i `INSUFFICIENT_BALANCE` també valen per al canvi ([12.7](#127-post-apiexchanges)): `amount ≤ 0`, o l'import més la comissió supera el saldo de l'origen.

Codis dels pagaments (Sprint 2, [apartat 13](#13-pagaments-cercar-usuaris-i-enviar-diners-us-13-i-us-14)):

| `code` | HTTP | Quan | `details` |
|---|---|---|---|
| `RECIPIENT_NOT_FOUND` | 404 | El destinatari no existeix o està pendent de verificar ([13.3](#133-get-apiusersuserid), [13.4](#134-post-apitransfers)) | — |
| `SELF_TRANSFER` | 422 | Enviar-se diners a un mateix | — |
| `TRANSFER_LIMIT_EXCEEDED` | 422 | Enviat avui + `amount > 100000` ([13.5](#135-límit-diari-denviament)) | `{ remainingToday }` (cèntims) |

`INSUFFICIENT_BALANCE` i `INVALID_AMOUNT` també surten a `POST /api/transfers`, amb el mateix significat.

### Exemples

`INVALID_AMOUNT`:

```json
{
  "code": "INVALID_AMOUNT",
  "message": "L'import ha de ser més gran que 0."
}
```

`AMOUNT_OVER_LIMIT`:

```json
{
  "code": "AMOUNT_OVER_LIMIT",
  "message": "L'import màxim per recàrrega és de 500,00 €."
}
```

`DAILY_LIMIT_EXCEEDED` (avui ja s'han recarregat `100000`):

```json
{
  "code": "DAILY_LIMIT_EXCEEDED",
  "message": "Has superat el límit diari de recàrrega. Avui encara pots recarregar 0,00 €.",
  "details": { "remainingToday": 0 }
}
```

`VALIDATION_ERROR` (p. ex. `GET /api/movements?limit=0`):

```json
{
  "code": "VALIDATION_ERROR",
  "message": "Les dades de la petició no són vàlides."
}
```

`INTERNAL_ERROR`:

```json
{
  "code": "INTERNAL_ERROR",
  "message": "S'ha produït un error inesperat. Torna-ho a provar més tard."
}
```

---

## 6. Model intern (no exposat a l'API)

Aquest apartat és per al backend. El frontend no en depèn.

### `Movement.kind`

- El model intern `Movement` té un camp `kind`:
  - `"topup"` a les recàrregues;
  - `"other"` a la resta de moviments.
- Serveix per sumar les recàrregues d'un dia (mètode del repositori de T07.4 i comprovació del límit diari de T09.2) **sense dependre del text del concepte**.
- La suma de les recàrregues d'avui filtra per `kind == "topup"` i per la `date` dins del dia natural d'avui a `Europe/Madrid` (vegeu l'[apartat 1](#què-vol-dir-avui)).
- `kind` **no s'exposa** a cap resposta. Per mostrar una recàrrega, el frontend ja té `icon: "topup"`.
- Des de l'Sprint 2, els enviaments fan servir `"transfer_out"` i `"transfer_in"` per al seu límit diari ([13.9](#139-model-intern)).

### Seed

- El seed (T07.3) **no pot tenir cap recàrrega amb data d'avui**. Si en tingués, el límit diari no començaria a zero i les proves i la demo de US-09 no serien reproduïbles.
- A partir de la T01.2, els dos usuaris del seed tenen credencials fictícies per poder iniciar sessió ([apartat 8.13](#813-model-intern-de-laccés)).

---

## 7. Propostes del contracte

Totes les propostes d'aquesta llista estan acceptades: es van validar en aprovar-se la PR que les proposava. Les noves continuen a partir de la P86 i porten la marca fins que s'aproven.

Propostes de l'Sprint 0 (PR #29):

| # | Apartat | Proposta |
|---|---|---|
| P1 | [3](#3-objecte-movement) | `Movement.id` és un string opac, per no dependre de l'emmagatzematge. |
| P2 | [4.2](#42-get-apimovements) | El rang vàlid de `limit` és `1`–`50`. |
| P3 | [4.2](#42-get-apimovements) | Un `offset` més gran o igual que el total retorna `200` amb `items: []` i `nextOffset: null`, no un error. |
| P4 | [4.2](#42-get-apimovements) | Si dues `date` coincideixen, va primer el moviment creat més tard. |
| P5 | [4.3](#43-post-apitopups) | `amount` ha de ser un enter JSON estricte: `"500"`, `500.5` i `500.0` retornen `VALIDATION_ERROR`. |
| P6 | [5](#5-errors) | Quan un error no té `details`, la clau no apareix a la resposta (en lloc de `"details": null`). |
| P7 | [1](#dates) | Les dates es donen amb precisió de segons, sense fraccions de segon. |

Propostes de l'accés (T01.1, PR #105):

| # | Apartat | Proposta |
|---|---|---|
| P8 | [8.8](#88-post-apiauthlogin) | Un compte «pendent» **no** pot iniciar sessió. Amb la contrasenya correcta rep `ACCOUNT_NOT_VERIFIED`; amb una d'incorrecta, el mateix `INVALID_CREDENTIALS` que la resta. |
| P9 | [8.6](#86-post-apiauthverify) | Verificar el codi obre la sessió directament i retorna un `token`, perquè l'app passi a «Inici» sense tornar a demanar la contrasenya (US-02). |
| P10 | [8.10](#810-post-apiauthforgot-password) | La recuperació accepta email **o** telèfon, perquè qui s'ha registrat amb telèfon també pugui recuperar el compte (l'enllaç li arriba per SMS). |
| P11 | [5](#taula-de-codis) | Els errors d'accés fan servir `401`, `403`, `409`, `423` i `429`, a més de `422` i `500`. Els recursos que no existeixen fan servir `404`. |
| P12 | [8.2](#transició-des-dx-user-id) | `X-User-Id` queda darrere de la variable `ALLOW_X_USER_ID`: activada per defecte fins a la T03.5 i desactivada després, excepte als tests. |
| P13 | [8.13](#813-model-intern-de-laccés) | Credencials fictícies del seed: `demo@evolt.test` (usuari 1) i `buit@evolt.test` (usuari 2), totes dues amb la contrasenya `Evolt2026`. |
| P14 | [8.9](#89-post-apiauthlogout) | `logout` sempre respon `200`, encara que el token ja no sigui vàlid. |
| P15 | [8.11](#811-post-apiauthreset-password) | Canviar la contrasenya amb l'enllaç també desbloqueja el compte i posa a zero els errors de login. |
| P16 | [8.4](#84-política-de-contrasenya) | Una contrasenya de més de 72 bytes és `VALIDATION_ERROR` (límit de bcrypt). |
| P17 | [8.10](#810-post-apiauthforgot-password) | L'enllaç de recuperació és `<FRONTEND_URL>/nova-contrasenya?token=<token>`, amb `FRONTEND_URL` per defecte `http://localhost:5173` i, a Render, l'URL del frontend desplegat. |
| P18 | [8.7](#87-post-apiauthresend-code), [8.10](#810-post-apiauthforgot-password) | Demanar un codi o un enllaç nou invalida l'anterior. |
| P19 | [8.5](#85-post-apiauthregister) | El registre crea també el compte principal amb saldo `0`, sense moviments ni guardioles. |
| P20 | [8.13](#813-model-intern-de-laccés) | **Acceptada** (TR01.1, #106). Les dades es guarden a Cloud Firestore des del backend. El login és propi (no Firebase Auth) i el frontend no parla amb Firebase. |
| P46 | [8.12](#812-get-apidevoutbox) | La bústia simulada es pot activar al desplegament amb `ENABLE_DEV_OUTBOX`, independent d'`ENABLE_DEV_ROUTES`, però protegida amb la clau `DEV_OUTBOX_KEY` (capçalera `X-Dev-Key`). El número salta a P46 perquè P21–P33 són del contracte de guardioles (§9) i P34–P45, del de moviments (§10). |

Propostes de l'estalvi (T17.1, PR #119):

| # | Apartat | Proposta |
|---|---|---|
| P21 | [9.1](#91-objecte-pot) | `Pot.id` és un string opac amb el format `pot-01`, `pot-02`…, com `Movement.id` (P1). |
| P22 | [9.1](#91-objecte-pot) | Llista tancada de colors: `purple` (el valor per defecte), `blue`, `teal`, `orange`, `pink` i `yellow`. No hi ha verd ni vermell, perquè la guia d'estil els reserva per als ingressos, les despeses i els errors. S'ha de validar amb la Jiajun. |
| P23 | [9.2](#92-get-apipots) | `GET /api/pots` respon `{ items }`, amb les guardioles en ordre de creació (la més antiga primer). |
| P24 | [9.3](#93-post-apipots) | `POST /api/pots` respon `201` amb l'objecte `Pot` sol, sense embolcall. |
| P25 | [9.3](#93-post-apipots) | El nom es desa sense els espais del principi i del final, i es poden repetir noms. |
| P26 | [9.3](#93-post-apipots) | Ordre de les validacions en crear: format (`VALIDATION_ERROR`) → `INVALID_POT_NAME` → `INVALID_TARGET`. |
| P27 | [9.4](#94-post-apipotspotidcontributions) | L'aportació respon `201` amb `{ balance, pot, movement }`. |
| P28 | [9.4](#94-post-apipotspotidcontributions) | Ordre de les validacions en aportar: format (`VALIDATION_ERROR`) → `POT_NOT_FOUND` → `INVALID_AMOUNT` → `INSUFFICIENT_BALANCE`. |
| P29 | [3](#3-objecte-movement), [9.4](#94-post-apipotspotidcontributions) | El moviment del compte principal d'una aportació té el concepte `"Aportació a <nom de la guardiola>"` i la icona nova `savings`. |
| P30 | [9.4](#94-post-apipotspotidcontributions) | Es pot aportar a una guardiola que ja ha arribat a l'objectiu. Dues aportacions alhora s'apliquen una darrere l'altra. |
| P31 | [9.5](#95-get-apipotspotidmovements) | L'historial respon `{ items }`, del més recent al més antic i sense paginació. Cada entrada té `id` (`pmov-01`, `pmov-02`…), `amount`, `concept`, `date` i `type`. |
| P32 | [9.8](#98-model-intern-de-lestalvi) | Cada guardiola del seed té una entrada inicial «Saldo inicial» pel seu saldo, i el seed dona un color a cada guardiola i un objectiu a dues. |
| P33 | [9.7](#97-errors) | `POT_NOT_FOUND` respon `404`, seguint la P11 de l'accés. |

Propostes dels moviments (T10.1, PR #120):

| # | Apartat | Proposta |
|---|---|---|
| P34 | [10.1](#101-camps-nous-de-movement) | El camp de la contrapart es diu `counterparty`. La clau sempre hi és i val `null` quan no n'hi ha. |
| P35 | [10.1](#101-camps-nous-de-movement) | Regla de `counterparty`: el nom del contacte a les transferències i els Bizum, l'empresa que paga a les nòmines, i `null` a la resta (recàrregues, aportacions, compres i altres pagaments, on el concepte ja diu de què es tracta). L'alternativa és posar-hi el nom del comerç. |
| P36 | [10.1](#101-camps-nous-de-movement) | Un moviment pendent ja compta al saldo (el saldo continua sent la suma de tots els moviments): `status` només canvia l'etiqueta. |
| P37 | [10.1](#101-camps-nous-de-movement) | Format de `reference`: `EVT-` seguit de 6 xifres per ordre de creació, p. ex. `EVT-000031`. |
| P38 | [10.1](#101-camps-nous-de-movement) | Els moviments nous (recàrregues i aportacions) neixen amb `status: "completed"`, una `reference` nova i `counterparty: null`. |
| P39 | [10.2](#102-filtres-de-get-apimovements) | Noms dels filtres: `dateFrom`, `dateTo`, `type` i `q`. |
| P40 | [10.2](#102-filtres-de-get-apimovements) | La cerca troba el text com a part del concepte o de la contrapart. S'ignoren els espais dels extrems, i un `q` buit o només amb espais no filtra. |
| P41 | [10.3](#103-get-apimovementsmovementid), [10.4](#104-post-apimovementsmovementidreports) | `MOVEMENT_NOT_FOUND` respon `404`, seguint la P11 de l'accés (com `POT_NOT_FOUND` a l'estalvi). |
| P42 | [10.4](#104-post-apimovementsmovementidreports) | L'informe respon `201` amb `{ id, movementId, description, createdAt }`, amb ids `rep-01`, `rep-02`… Es poden enviar diversos informes sobre el mateix moviment. |
| P43 | [10.4](#104-post-apimovementsmovementidreports) | Codi propi `INVALID_DESCRIPTION` (`422`) per a una descripció buida, només amb espais o de més de 500 caràcters. La descripció es desa sense els espais dels extrems. |
| P44 | [10.5](#105-justificant-pdf) | El justificant PDF es genera al navegador amb jsPDF (llicència MIT), sense Cloud Function ni cap ruta (decisió de PO). |
| P45 | [10.7](#107-model-intern-dels-moviments) | Seed: els noms fictius de la contrapart de la taula de 10.7, i el moviment més recent de l'usuari 1 (`mov-30`) en estat `pending`. |

Propostes de multidivisa (T25.1, PR #193):

| # | Apartat | Proposta |
|---|---|---|
| P50 | [12.1](#121-divises-i-tipus-de-canvi) | Tipus fixos i format `rateBps` de la pantalla de la US-25 (`models/currency.ts`): `EUR` 10000, `USD` 9123, `GBP` 11680, `CHF` 10355 i `JPY` 5700. |
| P51 | [12.1](#121-divises-i-tipus-de-canvi) | Conversió amb enters i arrodoniment mig cap amunt. El total en euros arrodoneix cada compte per separat i després els suma. |
| P52 | [12.2](#122-objecte-subaccount) | Objecte `Subaccount` `{ id, currency, balance, isMain, rateBps }`. El compte en euros és el compte principal, amb l'`id` `"main"`; els subcomptes en divisa són `sub-01`, `sub-02`… |
| P53 | [12.3](#123-get-apisubaccounts) | `GET /api/subaccounts` respon `{ items, totalInEuros }`: l'EUR primer i després per ordre de creació. El total el calcula el servidor. |
| P54 | [12.4](#124-post-apisubaccounts) | Ordre de les validacions en crear: format → `CURRENCY_NOT_SUPPORTED` → `CURRENCY_EXISTS`. Els codis distingeixen majúscules. |
| P55 | [12.5](#125-post-apisubaccountssubaccountiddelete) | Eliminar respon `200` `{ status: "ok" }`, amb l'ordre `SUBACCOUNT_NOT_FOUND` → `MAIN_ACCOUNT_NOT_DELETABLE` → `SUBACCOUNT_NOT_EMPTY`. |
| P56 | [12.6](#126-get-apisubaccountssubaccountidmovements) | Historial d'un subcompte en divisa a `GET /api/subaccounts/{subaccountId}/movements`, amb entrades `{ id, amount, concept, date, type }` i ids `smov-01`, `smov-02`…. El compte en euros fa servir `GET /api/movements`. La ruta la fa la T26.1, i les entrades, la T27.1. |
| P57 | [12.7](#127-post-apiexchanges) | El canvi rep `{ fromCurrency, toCurrency, amount }` i respon `201` amb `{ from, to, amount, commission, received }`, sense els moviments. |
| P58 | [12.7](#127-post-apiexchanges) | La comissió es calcula en la divisa d'origen: `max(arrodonir(amount × 1,5 %), mínim)`, amb el mínim de 0,50 € convertit arrodonint cap amunt. |
| P59 | [12.7](#127-post-apiexchanges) | Ordre de les validacions del canvi: format → `SAME_CURRENCY` → `SUBACCOUNT_NOT_FOUND` → `INVALID_AMOUNT` → `AMOUNT_TOO_SMALL` → `INSUFFICIENT_BALANCE`. |
| P60 | [12.8](#128-moviments-dun-canvi-i-efecte-sobre-altres-rutes) | Dos moviments per canvi, un a cada compte, tots dos amb el concepte «Canvi <origen> → <destí>» (p. ex. «Canvi EUR → USD»). El del compte en euros és un `Movement` normal (`icon: "transfer"`); el d'un subcompte en divisa només surt al seu historial. |
| P61 | [12.5](#125-post-apisubaccountssubaccountiddelete) | En eliminar un subcompte, el seu historial es queda desat, però ja no es pot consultar. |
| P62 | [12.10](#1210-errors) | `SUBACCOUNT_NOT_FOUND` diu «No s'ha trobat el subcompte.», i `SAME_CURRENCY`, el text de la pantalla (PR #180): «Origen i destí no poden ser el mateix subcompte.». |
| P63 | [12.11](#1211-model-intern-de-multidivisa) | El compte en euros és l'`Account` actual, sense duplicar-ne el saldo, i el seed no té subcomptes en divisa. |

Propostes dels pagaments (T13.1, US-13 i US-14, PR #196). Comencen a la P64 perquè les P47–P49 són de la retirada i el progrés (T19.1, PR #177) i les P50–P63, de la multidivisa (T25.1, PR #193):

| # | Apartat | Proposta |
|---|---|---|
| P64 | [13.1](#131-objecte-usersummary) | L'`id` d'un usuari a l'API és un string opac amb el format `usr-03`, com `Movement.id` (P1). |
| P65 | [13.1](#131-objecte-usersummary) | `UserSummary` només té `id`, `name` (o `null` si no en té) i `username` (sense `@`): mai email, telèfon, estat ni cap dada financera. |
| P66 | [13.2](#132-get-apiusers) | La cerca troba el text com a part de l'`username` o del nom (sense majúscules ni accents), l'email només si és igual, i el telèfon per les 9 últimes xifres. Mai l'usuari de la sessió ni els pendents. Com a màxim 10, ordenats pel nom visible. `q` de més de 64 caràcters és `VALIDATION_ERROR`. |
| P67 | [13.2](#132-get-apiusers) | Sense `q`, o amb `q` buit, la llista inicial són tots els altres usuaris actius (els 10 primers pel nom visible). |
| P68 | [13.3](#133-get-apiusersuserid) | `GET /api/users/{userId}` per tornar a validar el destinatari en recarregar «Enviar». Un usuari que no existeix o pendent és `404 RECIPIENT_NOT_FOUND`. |
| P69 | [13.4](#134-post-apitransfers) | `POST /api/transfers` amb `{ toUserId, amount, concept? }`, que respon `201` amb `{ balance, movement, recipient }`. |
| P70 | [13.4](#134-post-apitransfers) | Ordre de les validacions: format → `RECIPIENT_NOT_FOUND` → `SELF_TRANSFER` → `INVALID_AMOUNT` → `INSUFFICIENT_BALANCE` → `TRANSFER_LIMIT_EXCEEDED`. |
| P71 | [13.5](#135-límit-diari-denviament) | El límit d'enviament (1.000,00 € al dia, decisió de PO) és independent del de recàrrega i té el seu propi codi, `TRANSFER_LIMIT_EXCEEDED`, amb `details.remainingToday`. |
| P72 | [13.4](#134-post-apitransfers) | El concepte és opcional (fins a 140 caràcters). Sense concepte, els moviments diuen «Transferència enviada» i «Transferència rebuda». Tots dos fan servir `icon: "transfer"` i, a `counterparty`, el nom visible de l'altra persona. |
| P73 | [13.7](#137-avisos-a-la-bústia-simulada) | Els avisos d'enviament són missatges `transfer_sent` i `transfer_received` a la bústia simulada, amb els textos de 13.7. |
| P74 | [13.9](#139-model-intern) | L'`@usuari` d'un registre amb email és la part local netejada, amb un número si ja existeix; amb telèfon, `usuari` i l'id. |
| P75 | [13.9](#139-model-intern) | Seed de vuit usuaris: els dos d'abans i un per a cada membre de l'equip, amb el seu àlies de GitHub com a `@usuari` i telèfons fictius `+34 611 22 33 0N`. |
| P84 | [13.5](#get-apitransferslimit) | `GET /api/transfers/limit` → `{ dailyLimit, remainingToday }`, perquè «Enviar» pugui avisar del límit abans de confirmar (revisió de l'Izan a la #196). La numeració salta a P84 perquè les P76–P83 són de la #198. |
| P85 | [13.8](#138-errors) | `INSUFFICIENT_BALANCE` té un sol text, «No tens prou saldo.», a l'aportació, a l'enviament i al canvi de divises (revisió del Huabin a la #196). |

---

## 8. Accés (US-01 a US-04)

Registre, verificació del codi, inici i tancament de sessió i recuperació de contrasenya. Tasca: T01.1 (issue #56).

| Tasca | Què implementa d'aquest apartat |
|---|---|
| T01.2 (backend) | [8.3](#83-identificador-email-o-telèfon), [8.4](#84-política-de-contrasenya), [8.5](#85-post-apiauthregister) i el seed de [8.13](#813-model-intern-de-laccés) |
| T02.1 (backend) | [8.6](#86-post-apiauthverify), [8.7](#87-post-apiauthresend-code) i [8.12](#812-get-apidevoutbox) |
| T03.1 (backend) | [8.2](#82-sessió), [8.8](#88-post-apiauthlogin) (sense el bloqueig) i [8.9](#89-post-apiauthlogout) |
| T03.2 (backend) | El bloqueig de [8.8](#88-post-apiauthlogin) i la caducitat per inactivitat de [8.2](#82-sessió) |
| T04.1 (backend) | [8.10](#810-post-apiauthforgot-password) i [8.11](#811-post-apiauthreset-password) |
| T01.3, T02.2, T03.3, T03.5, T04.2 (frontend) | Les pantalles que criden aquestes rutes |

Les proves d'acceptació de US-01 a US-04 són a [`docs/proves-acces.md`](proves-acces.md).

### 8.1 Límits de temps i d'intents

| Regla | Valor | Quan s'aplica |
|---|---|---|
| Caducitat del codi de verificació | 10 minuts | El codi ja no serveix quan han passat **600 segons o més** des que s'ha generat. |
| Codis de verificació incorrectes | 5 | El 5è codi incorrecte bloqueja el codi: cal demanar-ne un de nou. |
| Errors de login seguits | 5 | El 5è error seguit bloqueja el compte. Un login correcte posa el comptador a zero. |
| Bloqueig del compte | 15 minuts | El compte es desbloqueja quan arriba l'hora de `lockedUntil`. |
| Inactivitat de la sessió | 5 minuts | La sessió es tanca quan han passat **300 segons o més** des de l'última petició amb aquell token. |
| Caducitat de l'enllaç de recuperació | 30 minuts | L'enllaç ja no serveix quan han passat **1.800 segons o més** des que s'ha generat, o si ja s'ha fet servir. |

Tots aquests temps es calculen amb el rellotge del backend (`models/clock.py`), que els tests poden fixar.

#### Variables d'entorn de l'accés

Es llegeixen amb la resta de la configuració del backend (`ENABLE_DEV_ROUTES`, `FRONTEND_ORIGINS`...). Un valor booleà mal escrit es tracta com a `false`.

| Variable | Per defecte | Què fa | Apartat |
|---|---|---|---|
| `ALLOW_X_USER_ID` | `0` (des de la T03.5; abans, `1`) | Accepta la capçalera `X-User-Id` quan no hi ha token. Només per als tests i les eines locals. | [8.2](#transició-des-dx-user-id) |
| `FRONTEND_URL` | `http://localhost:5173` | Base de l'enllaç de recuperació. A Render, `https://f3-evolt.onrender.com`. | [8.10](#810-post-apiauthforgot-password) |
| `ENABLE_DEV_OUTBOX` | El mateix valor que `ENABLE_DEV_ROUTES` | Activa `GET /api/dev/outbox` encara que les altres rutes `/api/dev` estiguin desactivades. | [8.12](#812-get-apidevoutbox) |
| `DEV_OUTBOX_KEY` | Sense definir | Si està definida, `GET /api/dev/outbox` demana la capçalera `X-Dev-Key` amb aquest valor. A Render va com a secret. | [8.12](#812-get-apidevoutbox) |

### 8.2 Sessió

- El login ([8.8](#88-post-apiauthlogin)) i la verificació del codi ([8.6](#86-post-apiauthverify)) retornen un **`token`**: un string opac que el frontend no ha d'interpretar.
- A cada petició a una ruta protegida, el frontend l'envia a la capçalera:

```http
GET /api/home HTTP/1.1
Authorization: Bearer 9fJx2sQ0b7Wm4LrT1vYc8NnK3pZa6HdE5gUiOeRkXwA
```

- **Rutes protegides:** `GET /api/home`, `GET /api/movements`, `POST /api/topups` i totes les rutes noves de dades de l'usuari.
- **Rutes públiques:** `GET /api/health`, totes les de `/api/auth/*` i les eines `/api/dev/*`.
- **Inactivitat:** cada petició a una ruta protegida amb un token vàlid compta com a activitat, encara que acabi en error de negoci (p. ex. `AMOUNT_OVER_LIMIT`). Si han passat 5 minuts o més des de l'última activitat, la petició respon `401 SESSION_EXPIRED` i el token deixa de ser vàlid.
- Sense capçalera `Authorization`, o amb un token desconegut o ja tancat → `401 UNAUTHENTICATED`.
- Un usuari pot tenir **diverses sessions** obertes alhora (un dispositiu per sessió). El logout tanca només la seva; canviar la contrasenya les tanca totes ([8.11](#811-post-apiauthreset-password)).
- Les sessions es guarden on diu `STORAGE` ([8.13](#813-model-intern-de-laccés)): en memòria, reiniciar el backend les tanca totes; a Firestore, **sobreviuen als reinicis**. En tots dos casos, `POST /api/dev/reset` les tanca totes.
- Com guarda el token el frontend i si també té un temporitzador propi d'inactivitat ho decideix la T03.3. La referència sempre és la resposta del backend.

#### Transició des d'`X-User-Id`

Perquè la resta de blocs (guardioles, filtres, detall) no quedessin bloquejats mentre es feia el login, `X-User-Id` es va mantenir darrere de la variable d'entorn **`ALLOW_X_USER_ID`** (`1` activada, `0` desactivada). Des de la T03.5 és **desactivada per defecte**: només s'activa a propòsit, per als tests i les eines locals.

El backend resol l'usuari de cada ruta protegida en aquest ordre:

1. Si hi ha `Authorization: Bearer <token>`, fa servir el token, i els seus errors (`UNAUTHENTICATED`, `SESSION_EXPIRED`). `X-User-Id` s'ignora.
2. Si no hi ha token i `ALLOW_X_USER_ID=1`, aplica les regles de l'[apartat 2](#capçalera-x-user-id): sense capçalera, usuari 1.
3. Si no hi ha token i `ALLOW_X_USER_ID=0` → `401 UNAUTHENTICATED`.

| Moment | Valor per defecte d'`ALLOW_X_USER_ID` |
|---|---|
| Des de la T03.1 fins a la T03.5 | `1`: el frontend actual continua funcionant sense login. |
| Des de la T03.5 (actual) | `0`: el frontend ja no envia `X-User-Id`. Els tests de pytest l'activen a `tests/conftest.py`, i els que proven el comportament sense la capçalera la desactiven. |

El CORS ha d'acceptar la capçalera `Authorization` (T03.1).

### 8.3 Identificador (email o telèfon)

Les rutes d'accés reben un sol camp, **`identifier`**, que pot ser un email o un telèfon. Abans de comparar-lo o desar-lo, el backend el **normalitza**:

| Tipus | Com es reconeix | Normalització | Vàlid si | Exemple |
|---|---|---|---|---|
| Email | Conté `@` | Treu els espais del principi i del final i el passa a minúscules. | Té exactament una `@`, alguna cosa abans, i un domini amb almenys un punt amb text a banda i banda (`x.com`; no `x.` ni `.com`), sense espais. | `" Ana@X.com "` → `"ana@x.com"` |
| Telèfon | No conté `@` | Treu espais, `-`, `.`, `(` i `)`. Un `00` inicial passa a ser `+`. Un número de 9 xifres sense prefix rep `+34`. | És `+` seguit de 8 a 15 xifres, i la primera no és `0`. | `"612 34 56 78"` → `"+34612345678"` |

- Un `identifier` que no és vàlid retorna `422 VALIDATION_ERROR`, excepte al login, que respon `INVALID_CREDENTIALS` per no dir quina casella falla ([8.8](#88-post-apiauthlogin)).
- Les respostes que retornen l'`identifier` el donen **normalitzat**.
- Els missatges a un email surten pel canal `email` de la bústia simulada; els d'un telèfon, pel canal `sms` ([8.12](#812-get-apidevoutbox)).

### 8.4 Política de contrasenya

- **Mínim 8 caràcters, almenys una lletra majúscula i almenys un número** (`0`–`9`). Qualsevol majúscula compta, també les accentuades (`À`, `É`...).
- És la mateixa regla al registre (US-01) i a la contrasenya nova (US-04). El backend la defineix en **un sol lloc** (T01.2) i la reutilitza la T04.1.
- Si no la compleix → `422 WEAK_PASSWORD`.
- Una contrasenya de més de 72 bytes en UTF-8 → `422 VALIDATION_ERROR`, perquè bcrypt no en fa servir més.
- El frontend també la valida per mostrar l'error en vermell sense esperar, però la comprovació que mana és la del backend.
- La contrasenya **mai** es guarda en clar (es desa el hash amb bcrypt) i **mai** surt a cap resposta, log ni missatge de la bústia.

### 8.5 `POST /api/auth/register`

Crea un compte nou en estat **«pendent de verificació»** (US-01). **No obre cap sessió.**

**Cos de la petició:** `{ identifier, password, acceptedTerms }`

| Camp | Tipus | Descripció |
|---|---|---|
| `identifier` | string | Email o telèfon ([8.3](#83-identificador-email-o-telèfon)). |
| `password` | string | Contrasenya en clar; només viatja en aquesta petició ([8.4](#84-política-de-contrasenya)). |
| `acceptedTerms` | boolean | Ha de ser `true`: la casella «Accepto els termes i la política de privacitat». |

«Repeteix la contrasenya» només existeix a la pantalla: el frontend comprova que coincideixen i **no** l'envia.

**Ordre de les validacions.** S'aturen al primer error:

1. Format: falta un camp, un tipus no és correcte, `acceptedTerms` no és `true`, l'`identifier` no és vàlid o la contrasenya passa de 72 bytes → `VALIDATION_ERROR`.
2. Política de contrasenya → `WEAK_PASSWORD`.
3. L'`identifier` normalitzat ja existeix, tant si el compte és pendent com si és actiu → `409 ALREADY_REGISTERED`. Per exemple, si existeix `ana@x.com`, registrar `ANA@x.com` també falla.

**Resposta `201`:** `{ identifier, status }`

| Camp | Tipus | Descripció |
|---|---|---|
| `identifier` | string | L'identificador normalitzat. El frontend el fa servir a la pantalla «Verifica el teu compte». |
| `status` | `"pending"` | Sempre `"pending"` en registrar-se. |

**Efectes:**

- Es crea l'usuari en estat `pending`, amb el seu compte principal amb saldo `0`, sense moviments ni guardioles i amb XP `0`.
- Es genera un codi de verificació i es deixa a la bústia simulada ([8.12](#812-get-apidevoutbox)).

**Petició:**

```http
POST /api/auth/register HTTP/1.1
Content-Type: application/json

{
  "identifier": "Ana@X.com",
  "password": "Platja2026",
  "acceptedTerms": true
}
```

**Resposta `201`:**

```json
{
  "identifier": "ana@x.com",
  "status": "pending"
}
```

### 8.6 `POST /api/auth/verify`

Comprova el codi de 6 xifres, activa el compte i **obre la sessió** (US-02).

**Cos de la petició:** `{ identifier, code }`

| Camp | Tipus | Descripció |
|---|---|---|
| `identifier` | string | El mateix que al registre (es normalitza igual). |
| `code` | string | Exactament 6 xifres, p. ex. `"048213"`. És un string perquè no es perdin els zeros de l'esquerra. |

**Ordre de les validacions.** S'aturen al primer error:

1. Format: falta un camp, o `code` no són exactament 6 xifres → `VALIDATION_ERROR`. No compta com a intent.
2. No hi ha cap compte **pendent** amb aquest `identifier` (no existeix o ja està actiu) → `INVALID_CODE`. No compta com a intent i no revela si el compte existeix.
3. El codi actual ja ha rebut 5 codis incorrectes → `429 TOO_MANY_ATTEMPTS`, **encara que ara el codi sigui correcte**.
4. El codi ha caducat → `CODE_EXPIRED`. No compta com a intent.
5. El codi no és correcte → suma un intent fallit. Si és el 5è → `429 TOO_MANY_ATTEMPTS`; si no → `INVALID_CODE`.

Un codi antic que s'ha substituït amb «Envia'm un codi nou» ja no és el codi actual: es tracta com un codi incorrecte (pas 5).

**Resposta `200`:** `{ token }`, la mateixa que el login ([8.8](#88-post-apiauthlogin)). El compte passa a `active`, el codi deixa de servir i el frontend obre «Inici» amb aquest token.

**Petició:**

```http
POST /api/auth/verify HTTP/1.1
Content-Type: application/json

{
  "identifier": "ana@x.com",
  "code": "048213"
}
```

**Resposta `200`:**

```json
{
  "token": "9fJx2sQ0b7Wm4LrT1vYc8NnK3pZa6HdE5gUiOeRkXwA"
}
```

`INVALID_CODE` i `CODE_EXPIRED` porten el mateix text, perquè la US-02 mostra el mateix missatge en tots dos casos:

```json
{
  "code": "CODE_EXPIRED",
  "message": "El codi no és correcte o ha caducat."
}
```

### 8.7 `POST /api/auth/resend-code`

Envia un codi de verificació nou («Envia'm un codi nou», US-02).

**Cos de la petició:** `{ identifier }`

- `identifier` mal format → `VALIDATION_ERROR`.
- **Resposta `200`:** `{ status }`, amb `status` sempre `"ok"`. La resposta és la mateixa existeixi o no el compte, per no revelar quins comptes hi ha.
- Si hi ha un compte **pendent** amb aquest `identifier`: es genera un codi nou, l'anterior **deixa de servir**, el comptador d'intents torna a zero i els 10 minuts tornen a començar.
- Si el compte no existeix o ja està actiu, no s'envia res.
- A l'Sprint 1 no hi ha límit de reenviaments.

### 8.8 `POST /api/auth/login`

Inicia la sessió amb l'email o el telèfon i la contrasenya (US-03).

**Cos de la petició:** `{ identifier, password }`

**Ordre de les validacions.** S'aturen al primer error:

1. Format: falta un camp o un tipus no és correcte → `VALIDATION_ERROR`. **No** es valida la política de contrasenya.
2. L'`identifier` no és vàlid o no hi ha cap compte amb aquest `identifier` → `401 INVALID_CREDENTIALS`.
3. El compte està bloquejat → `423 ACCOUNT_LOCKED`, **encara que la contrasenya sigui correcta**. No compta com a error.
4. La contrasenya no és correcta → suma un error seguit. Si és el 5è: el compte queda bloquejat 15 minuts, el comptador torna a zero, s'envia un avís a la bústia simulada i la resposta és `423 ACCOUNT_LOCKED`. Si no, `401 INVALID_CREDENTIALS`.
5. La contrasenya és correcta però el compte és pendent → `403 ACCOUNT_NOT_VERIFIED`. El comptador d'errors torna a zero. El frontend pot portar l'usuari a «Verifica el teu compte» i demanar un codi nou ([8.7](#87-post-apiauthresend-code)).
6. Tot correcte: el comptador d'errors torna a zero i s'obre una sessió nova.

`INVALID_CREDENTIALS` és **idèntic** (estat, `code` i `message`) tant si el compte no existeix com si la contrasenya és errònia.

**Resposta `200`:** `{ token }`

| Camp | Tipus | Descripció |
|---|---|---|
| `token` | string | Token de sessió opac ([8.2](#82-sessió)). |

**Petició:**

```http
POST /api/auth/login HTTP/1.1
Content-Type: application/json

{
  "identifier": "demo@evolt.test",
  "password": "Evolt2026"
}
```

**Resposta `200`:**

```json
{
  "token": "9fJx2sQ0b7Wm4LrT1vYc8NnK3pZa6HdE5gUiOeRkXwA"
}
```

**Errors:**

```json
{
  "code": "INVALID_CREDENTIALS",
  "message": "L'email, el telèfon o la contrasenya no són correctes."
}
```

```json
{
  "code": "ACCOUNT_LOCKED",
  "message": "Compte bloquejat durant 15 minuts.",
  "details": { "lockedUntil": "2026-11-03T10:15:00+01:00" }
}
```

### 8.9 `POST /api/auth/logout`

Tanca la sessió actual («Tancar sessió», US-03).

- **Capçalera:** `Authorization: Bearer <token>`.
- **Cos de la petició:** cap.
- **Resposta `200`:** `{ status }`, amb `status` sempre `"ok"`.
- Si el token és vàlid, la sessió es tanca i el token deixa de servir.
- Respon `200` **sempre**, també sense capçalera o amb un token ja caducat o tancat: l'usuari vol sortir i no té sentit mostrar-li un error.
- La resposta porta cos JSON (no `204`), perquè l'`apiClient` del frontend espera JSON a totes les respostes.

### 8.10 `POST /api/auth/forgot-password`

Demana un enllaç per canviar la contrasenya («He oblidat la contrasenya», US-04).

**Cos de la petició:** `{ identifier }`

- Accepta email **o** telèfon. La US-04 parla d'email, però així qui s'ha registrat amb telèfon també pot recuperar el compte, i l'enllaç li arriba per SMS.
- `identifier` mal format → `VALIDATION_ERROR`.
- **Resposta `200`:** `{ status }`, amb `status` sempre `"ok"`, **existeixi o no el compte**. El frontend mostra sempre «Si l'email és correcte, rebràs un enllaç per canviar la contrasenya».
- Si el compte existeix (pendent, actiu o bloquejat): es genera un enllaç d'**un sol ús** que caduca als 30 minuts, l'enllaç anterior **deixa de servir** i es deixa a la bústia simulada.
- L'enllaç és `<FRONTEND_URL>/nova-contrasenya?token=<token>`. `FRONTEND_URL` és una variable d'entorn ([8.1](#variables-dentorn-de-laccés)): en local val `http://localhost:5173` i a Render, l'URL del frontend desplegat. La T04.2 crea aquesta ruta del frontend, que llegeix el `token` de l'URL.

### 8.11 `POST /api/auth/reset-password`

Canvia la contrasenya amb el token de l'enllaç («Nova contrasenya», US-04).

**Cos de la petició:** `{ token, password }`

| Camp | Tipus | Descripció |
|---|---|---|
| `token` | string | El `token` de l'URL de l'enllaç. |
| `password` | string | Contrasenya nova ([8.4](#84-política-de-contrasenya)). |

**Ordre de les validacions.** S'aturen al primer error:

1. Format → `VALIDATION_ERROR`.
2. El token no existeix, ja s'ha fet servir, s'ha substituït per un de més nou o ha caducat → `422 RESET_LINK_EXPIRED`. El frontend mostra «Aquest enllaç ha caducat» i el botó «Demanar-ne un de nou».
3. Política de contrasenya → `WEAK_PASSWORD`. El token **no** es gasta: l'usuari pot tornar-ho a provar amb el mateix enllaç.

**Resposta `200`:** `{ status }`, amb `status` sempre `"ok"`.

**Efectes:**

- La contrasenya canvia i el token queda gastat.
- **Totes les sessions** de l'usuari es tanquen (US-04: es tanquen les sessions dels altres dispositius). No s'obre cap sessió nova: l'usuari ha d'iniciar sessió amb la contrasenya nova.
- El compte es desbloqueja i el comptador d'errors de login torna a zero.
- L'estat del compte (pendent o actiu) no canvia.

### 8.12 `GET /api/dev/outbox`

Bústia simulada: eina de **desenvolupament**, com `POST /api/dev/reset`. En lloc d'enviar emails o SMS de veritat, el backend desa aquí els missatges. **No l'usa l'app**: serveix per llegir el codi o l'enllaç a les proves manuals, a la demo i als tests.

**Disponibilitat i protecció** (P46):

- La ruta existeix si `ENABLE_DEV_OUTBOX` és `true`. Per defecte pren el valor d'`ENABLE_DEV_ROUTES`, així que en local està activa i al desplegament no, tret que s'activi expressament ([8.1](#variables-dentorn-de-laccés)). Si no existeix, respon com qualsevol ruta no definida ([apartat 5](#5-errors)).
- Si `DEV_OUTBOX_KEY` està definida, la petició ha de portar la capçalera `X-Dev-Key` amb aquest valor; si falta o no coincideix → `401 UNAUTHENTICATED`. En local no es defineix i no cal cap capçalera.
- **Per què cal la clau:** la bústia conté codis i enllaços de recuperació de qualsevol compte. Oberta a l'URL pública, qualsevol persona podria demanar «He oblidat la contrasenya» per a `demo@evolt.test`, llegir-ne l'enllaç i canviar-li la contrasenya. Per tant, **al desplegament la bústia només s'activa amb `DEV_OUTBOX_KEY` definida**.
- La clau va com a secret a Render i es comparteix només dins de l'equip; **mai** al repositori ni a l'URL (`?key=`), perquè quedaria a l'historial del navegador i als logs. A la demo es llegeix la bústia amb `docs/api.http` o `curl`.

**Paràmetre de consulta opcional:** `to`, un `identifier`. Es normalitza i només es retornen els missatges per a aquell destinatari.

**Resposta `200`:** `{ messages }`, del més recent al més antic.

| Camp | Tipus | Descripció |
|---|---|---|
| `to` | string | Destinatari, normalitzat. |
| `channel` | `"email"` \| `"sms"` | Segons si el destinatari és un email o un telèfon. |
| `type` | `"verification_code"` \| `"account_locked"` \| `"password_reset"` | Per què s'ha enviat. |
| `text` | string | Text del missatge, en català. |
| `date` | string | Data ISO 8601, com a la resta de l'API. |
| `code` | string | **Només** a `verification_code`: el codi de 6 xifres. |
| `link` | string | **Només** a `password_reset`: l'enllaç complet. |

Com als errors (P6), les claus `code` i `link` no apareixen als missatges que no en tenen.

**Petició:**

```http
GET /api/dev/outbox?to=ana@x.com HTTP/1.1
```

Al desplegament, amb la clau:

```http
GET /api/dev/outbox?to=ana@x.com HTTP/1.1
X-Dev-Key: <DEV_OUTBOX_KEY>
```

**Resposta:**

```json
{
  "messages": [
    {
      "to": "ana@x.com",
      "channel": "email",
      "type": "verification_code",
      "text": "El teu codi d'Evolt és 048213. Caduca en 10 minuts.",
      "date": "2026-11-03T10:00:00+01:00",
      "code": "048213"
    }
  ]
}
```

Textos dels altres dos tipus (els avisos d'enviament, `transfer_sent` i `transfer_received`, són a [13.7](#137-avisos-a-la-bústia-simulada)):

- `account_locked`: «Hem bloquejat el teu compte d'Evolt durant 15 minuts després de 5 intents fallits. Si no has estat tu, canvia la contrasenya.»
- `password_reset`: «Per canviar la contrasenya d'Evolt, obre aquest enllaç. Caduca en 30 minuts: <enllaç>»

`POST /api/dev/reset` buida la bústia.

### 8.13 Model intern de l'accés

Aquest apartat és per al backend. El frontend no en depèn.

**Emmagatzematge** (P20, acceptada). Amb `STORAGE=firestore`, les dades es guarden a **Cloud Firestore** (TR01.1, #106); sense, en memòria com a l'Sprint 0:

- Només el backend parla amb Firestore, amb la llibreria de Google `google-cloud-firestore` (la mateixa que fa servir l'Admin SDK, `firebase-admin`). El frontend **no** usa Firebase: continua cridant només aquesta API.
- El login el fa el nostre backend tal com descriu aquest apartat. **No** es fa servir Firebase Auth.
- Les credencials del compte de servei es llegeixen d'una variable d'entorn i **mai** es pugen al repositori.
- En local i als tests s'usa l'**emulador de Firestore** o els repositoris en memòria; una variable d'entorn tria quin. Els serveis no canvien: només canvien els repositoris.
- El contracte de les rutes és el mateix en tots dos casos. Les sessions es desen pel hash del token, no pel token.

| Col·lecció | Contingut |
|---|---|
| `users`, `accounts`, `pots`, `pot_movements`, `movements`, `movement_reports` | Les dades de l'Sprint 0, l'estalvi i els informes (seed, saldos, historials, moviments). |
| `user_identifiers` | Un document per email o telèfon (amb el hash com a id): impedeix dos registres amb el mateix identificador encara que arribin alhora. |
| `sessions`, `verification_codes`, `password_reset_tokens` | Les dades de l'accés (taula següent). Les sessions i els enllaços es desen pel **hash** del token. |
| `outbox` | La bústia simulada ([8.12](#812-get-apidevoutbox)). |
| `counters` | Un sol document amb els comptadors dels ids nous (`mov-NN`, `EVT-NNNNNN`, `pot-NN`, `pmov-NN`, `rep-NN`, usuaris i bústia): Firestore no té autoincrement. |

Les dates es desen com a `Timestamp` de Firestore (UTC) i el backend les converteix a `Europe/Madrid` en llegir-les, de manera que l'API continua donant-les com a l'[apartat 1](#dates). Les operacions que escriuen més d'una cosa es fan dins d'una **transacció** de Firestore, perquè siguin tot o res: el registre, la verificació, la recàrrega, crear una guardiola, l'aportació, l'informe d'un moviment, «He oblidat la contrasenya» i la contrasenya nova. En memòria, el mateix codi les fa amb un pany. Un error de negoci (p. ex. un codi incorrecte que compta com a intent) no desfà el que el servei ja ha escrit, igual que en memòria.

| Model | Camps nous | Notes |
|---|---|---|
| `User` | `identifier`, `identifier_type` (`email` / `phone`), `password_hash`, `status` (`pending` / `active`), `failed_logins`, `locked_until` | `password_hash` amb bcrypt. `locked_until` és `None` si no està bloquejat. |
| `VerificationCode` | `user_id`, `code`, `created_at`, `failed_attempts` | Com a màxim un codi vàlid per usuari. |
| `PasswordResetToken` | `token`, `user_id`, `created_at`, `used` | Com a màxim un enllaç vàlid per usuari. |
| `Session` | `token`, `user_id`, `last_activity` | Diverses per usuari. |
| `OutboxMessage` | Els camps de [8.12](#812-get-apidevoutbox) | Només per a desenvolupament. |

- Els codis de 6 xifres i els tokens es generen amb el mòdul `secrets` de Python (p. ex. `secrets.token_urlsafe`), **no** amb `random`.
- Tots els temps fan servir el rellotge injectable de `models/clock.py`, perquè els tests puguin fixar l'hora.
- Les noves dades s'afegeixen al seed i es reinicien amb `POST /api/dev/reset`, com la resta.

**Credencials del seed**. Són fictícies i serveixen per a la demo i les proves:

| Usuari | `identifier` | Contrasenya | Estat |
|---|---|---|---|
| 1 (compte amb moviments) | `demo@evolt.test` | `Evolt2026` | `active` |
| 2 (compte buit) | `buit@evolt.test` | `Evolt2026` | `active` |

El domini `.test` està reservat i no pot arribar a cap bústia real. Els mocks del frontend han de fer servir les mateixes credencials. Des de la T13.2 el seed té vuit usuaris, tots amb aquesta contrasenya ([13.9](#139-model-intern)).

### 8.14 Textos dels errors d'accés

Textos orientatius de `message` ([apartat 5](#5-errors)). Surten dels criteris d'acceptació de les US, perquè el frontend els pugui mostrar tal qual si vol.

| `code` | `message` |
|---|---|
| `UNAUTHENTICATED` | «Cal iniciar sessió.» |
| `SESSION_EXPIRED` | «La sessió s'ha tancat per inactivitat.» |
| `WEAK_PASSWORD` | «La contrasenya ha de tenir 8 caràcters, una majúscula i un número.» |
| `ALREADY_REGISTERED` | «Aquest email o telèfon ja té un compte.» |
| `INVALID_CODE` | «El codi no és correcte o ha caducat.» |
| `CODE_EXPIRED` | «El codi no és correcte o ha caducat.» |
| `TOO_MANY_ATTEMPTS` | «Has fet massa intents. Demana un codi nou.» |
| `INVALID_CREDENTIALS` | «L'email, el telèfon o la contrasenya no són correctes.» |
| `ACCOUNT_LOCKED` | «Compte bloquejat durant 15 minuts.» |
| `ACCOUNT_NOT_VERIFIED` | «Has de verificar el compte abans d'iniciar sessió.» |
| `RESET_LINK_EXPIRED` | «Aquest enllaç ha caducat.» |

---

## 9. Guardioles (US-17 i US-18)

Crear guardioles, llistar-les, aportar-hi diners del compte principal i consultar-ne l'historial. Tasca: T17.1 (issue #71).

| Tasca | Què implementa d'aquest apartat |
|---|---|
| T17.2 (backend) | [9.1](#91-objecte-pot), [9.2](#92-get-apipots), [9.3](#93-post-apipots) i les guardioles del seed de [9.8](#98-model-intern-de-lestalvi) |
| T18.1 (backend) | [9.4](#94-post-apipotspotidcontributions), [9.5](#95-get-apipotspotidmovements), [9.6](#96-efecte-sobre-altres-rutes) i l'historial de [9.8](#98-model-intern-de-lestalvi) |
| T17.3, T17.4, T18.2, T18.4 (frontend) | Les pantalles que criden aquestes rutes |

Totes les rutes d'aquest apartat són **rutes protegides** i resolen l'usuari igual que la resta: amb `X-User-Id` ([apartat 2](#2-usuari-actual-i-estat-del-servei)) mentre estigui permesa, i a partir de la T03.1 amb la sessió ([apartat 8.2](#82-sessió)). Cada usuari només veu i modifica les seves guardioles. Segueixen les convencions de l'[apartat 1](#1-convencions-generals): imports en cèntims enters, dates ISO 8601 amb el desplaçament de Madrid i claus en camelCase.

Els exemples d'aquest apartat fan servir les dades de l'usuari 1 del seed: compte principal amb `379521` (3.795,21 €) i tres guardioles que sumen `30000` (300,00 €). Les dates d'exemple són del 3/11/2026 (`+01:00`, horari d'hivern).

### 9.1 Objecte `Pot`

Una guardiola de l'usuari. És el mateix objecte a totes les respostes d'aquest apartat.

| Camp | Tipus | Notes |
|---|---|---|
| `id` | string | Identificador opac, com `Movement.id` (P1). El frontend no l'ha d'interpretar. Format `pot-01`, `pot-02`… |
| `name` | string | Mai buit: té almenys un caràcter que no és un espai. |
| `balance` | integer | Cèntims, `≥ 0`. Una guardiola nova té `0`. |
| `target` | integer \| `null` | Objectiu en cèntims, `> 0`. Val `null` si la guardiola no en té, perquè és opcional. |
| `color` | string | Un dels valors de la llista tancada següent. |

Valors de `color` (llista tancada):

| Valor | Notes |
|---|---|
| `purple` | Valor per defecte si no se n'envia cap. És el lila de la guia d'estil. |
| `blue` | |
| `teal` | |
| `orange` | |
| `pink` | |
| `yellow` | |

- No hi ha verd ni vermell: la guia d'estil els reserva per als ingressos, les despeses i els errors.
- El backend només guarda el nom del color. Quin to exacte es pinta el decideix el frontend.

Exemple:

```json
{
  "id": "pot-01",
  "name": "Vacances",
  "balance": 15000,
  "target": 100000,
  "color": "blue"
}
```

### 9.2 `GET /api/pots`

Les guardioles de l'usuari (US-17).

**Resposta `200`:** `{ items }`

| Camp | Tipus | Descripció |
|---|---|---|
| `items` | `Pot[]` | Totes les guardioles de l'usuari, en ordre de creació, de la més antiga a la més nova. Pot ser una llista buida. |

- No té paginació: a la demo, un usuari té poques guardioles.
- Un usuari sense guardioles rep `{ "items": [] }`. És l'estat buit de US-17 (criteri 2): el frontend mostra «Encara no tens cap guardiola».

**Petició:**

```http
GET /api/pots HTTP/1.1
```

**Resposta:**

```json
{
  "items": [
    {
      "id": "pot-01",
      "name": "Vacances",
      "balance": 15000,
      "target": 100000,
      "color": "blue"
    },
    {
      "id": "pot-02",
      "name": "Emergències",
      "balance": 10000,
      "target": null,
      "color": "orange"
    },
    {
      "id": "pot-03",
      "name": "Regal d'aniversari",
      "balance": 5000,
      "target": 8000,
      "color": "pink"
    }
  ]
}
```

**Usuari sense guardioles** (`X-User-Id: 2`):

```json
{
  "items": []
}
```

### 9.3 `POST /api/pots`

Crea una guardiola (US-17).

**Cos de la petició:** `{ name, target?, color? }`

| Camp | Tipus | Descripció |
|---|---|---|
| `name` | string | Obligatori. Es desa sense els espais del principi i del final. |
| `target` | integer \| `null` | Opcional. Objectiu en cèntims. Si no s'envia, o val `null`, la guardiola no té objectiu. |
| `color` | string | Opcional. Un dels valors de [9.1](#91-objecte-pot). Si no s'envia, o val `null`, és `purple`. |

**Resposta `201`:** l'objecte `Pot` creat, sol.

- La guardiola neix amb `balance: 0`.
- Es retorna l'objecte sol perquè només hi ha una cosa a retornar, i és exactament el mateix objecte que surt a `GET /api/pots`. La recàrrega i l'aportació retornen un objecte amb diverses claus perquè canvien més d'una cosa (el saldo i el moviment).

**Ordre de les validacions.** S'aturen al primer error:

1. Format del cos → `VALIDATION_ERROR`:
   - falta `name` o no és un string;
   - `target` no és un enter JSON estricte, com a P5 (`"300"`, `300.5` i `300.0` no valen);
   - `color` no és de la llista tancada.
2. `name` buit o només amb espais → `INVALID_POT_NAME`.
3. `target ≤ 0` → `INVALID_TARGET`.

**Regles:**

- Si hi ha un error, no es crea res.
- No hi ha límit de guardioles (assumpte de US-17).
- Es poden repetir noms.
- Fora de l'abast d'aquest sprint: editar i esborrar guardioles, que no són als criteris de US-17.

**Petició:**

```http
POST /api/pots HTTP/1.1
Content-Type: application/json

{
  "name": "Viatge",
  "target": 30000,
  "color": "teal"
}
```

**Resposta `201`:**

```json
{
  "id": "pot-04",
  "name": "Viatge",
  "balance": 0,
  "target": 30000,
  "color": "teal"
}
```

### 9.4 `POST /api/pots/{potId}/contributions`

Aporta diners del compte principal a una guardiola (US-18).

**Cos de la petició:** `{ amount }`

| Camp | Tipus | Descripció |
|---|---|---|
| `amount` | integer | Import de l'aportació en cèntims. Obligatori. Enter JSON estricte, com a P5. |

**Resposta `201`:** `{ balance, pot, movement }`

| Camp | Tipus | Descripció |
|---|---|---|
| `balance` | integer | Saldo **nou** del compte principal, en cèntims. |
| `pot` | `Pot` | La guardiola amb el saldo nou. |
| `movement` | `Movement` | El moviment que s'ha creat al compte principal. |

Amb aquesta resposta, el frontend pot pintar el tic verd «Has aportat X € a <nom>» i actualitzar els dos saldos sense tornar a demanar res.

**Ordre de les validacions.** S'aturen al primer error:

1. Format del cos: `amount` falta o no és un enter JSON estricte → `VALIDATION_ERROR`.
2. La guardiola no existeix o és d'un altre usuari → `POT_NOT_FOUND`. La resposta és la mateixa en tots dos casos, perquè no es pugui saber si una guardiola d'un altre usuari existeix. Un `potId` amb un format qualsevol (p. ex. `abc`) també dona `POT_NOT_FOUND`.
3. `amount ≤ 0` → `INVALID_AMOUNT`, el mateix codi que a la recàrrega.
4. `amount` més gran que el saldo del compte principal → `INSUFFICIENT_BALANCE`.

**Regles:**

- Aportar **exactament** tot el saldo del compte principal està permès, perquè el criteri diu «no més gran que el saldo principal». El compte es queda a `0`.
- **Tot o res** (US-18, criteris 4, 7 i 8). Una aportació fa quatre canvis: el saldo del compte, el saldo de la guardiola, un moviment nou al compte i una entrada nova a l'historial de la guardiola. O es fan tots quatre, o no se'n fa cap. Si hi ha un error, no canvia res.
- **Moviment del compte principal.** Cada aportació crea, en la mateixa operació, un moviment del compte principal (decisió de l'equip: així el saldo del compte continua sent la suma dels seus moviments):
  - `type: "expense"`;
  - `amount` igual a l'aportació;
  - `concept: "Aportació a <nom de la guardiola>"`, p. ex. `"Aportació a Vacances"`;
  - `icon: "savings"`, un valor nou de la llista de l'[apartat 3](#3-objecte-movement). Si el frontend rep una icona que no coneix, mostra `other` (`frontend/src/models/movement.ts`), així que la icona nova no trenca res;
  - `date`: el moment de l'aportació;
  - `counterparty: null`, `status: "completed"` i una `reference` nova, com tots els moviments nous ([10.1](#101-camps-nous-de-movement), P38);
  - `kind` intern `"other"`, perquè no compti per al límit diari de recàrrega.
- **Casos límit**:
  - Es pot aportar a una guardiola que ja ha arribat a l'objectiu, o que el passaria: els criteris no ho prohibeixen, i l'objectiu és una meta, no un límit.
  - Dues aportacions alhora s'apliquen una darrere l'altra. La segona es valida amb el saldo que ha deixat la primera: si ja no n'hi ha prou, rep `INSUFFICIENT_BALANCE`. El saldo del compte mai pot quedar negatiu.
- En aquest sprint, aportar no dona XP: la gamificació no és a l'abast.

**Petició:**

```http
POST /api/pots/pot-01/contributions HTTP/1.1
Content-Type: application/json

{
  "amount": 3000
}
```

**Resposta `201`** (saldo anterior del compte: `379521`; saldo anterior de la guardiola: `15000`):

```json
{
  "balance": 376521,
  "pot": {
    "id": "pot-01",
    "name": "Vacances",
    "balance": 18000,
    "target": 100000,
    "color": "blue"
  },
  "movement": {
    "id": "mov-31",
    "amount": 3000,
    "concept": "Aportació a Vacances",
    "date": "2026-11-03T10:00:00+01:00",
    "type": "expense",
    "icon": "savings",
    "counterparty": null,
    "status": "completed",
    "reference": "EVT-000031"
  }
}
```

### 9.5 `GET /api/pots/{potId}/movements`

L'historial d'una guardiola (US-18, criteri 6).

**Resposta `200`:** `{ items }`

| Camp | Tipus | Descripció |
|---|---|---|
| `items` | Entrada[] | Les entrades de l'historial, de la més recent a la més antiga, sense paginació. |

Cada entrada de l'historial:

| Camp | Tipus | Notes |
|---|---|---|
| `id` | string | Identificador opac. Format `pmov-01`, `pmov-02`… |
| `amount` | integer | Cèntims, sempre `> 0`. |
| `concept` | string | `"Aportació"` a les aportacions. `"Saldo inicial"` a l'entrada inicial de les guardioles del seed ([9.8](#98-model-intern-de-lestalvi)). |
| `date` | string | ISO 8601 amb desplaçament. |
| `type` | `"income"` \| `"expense"` | Des del punt de vista de la **guardiola**: una aportació hi fa entrar diners, i per tant és `income`. El frontend la mostra en verd i amb «+». |

- L'historial és de la guardiola, no del compte. Per això l'aportació hi surt com a `income` amb el concepte «Aportació», mentre que al compte principal surt com a `expense` amb el concepte «Aportació a <nom>».
- El saldo d'una guardiola és sempre la suma del seu historial.
- Si dues entrades tenen la mateixa data, va primer la creada més tard, com a P4.
- La guardiola no existeix o és d'un altre usuari → `POT_NOT_FOUND`.

**Petició** (després de l'aportació de l'exemple de 9.4):

```http
GET /api/pots/pot-01/movements HTTP/1.1
```

**Resposta:**

```json
{
  "items": [
    {
      "id": "pmov-04",
      "amount": 3000,
      "concept": "Aportació",
      "date": "2026-11-03T10:00:00+01:00",
      "type": "income"
    },
    {
      "id": "pmov-01",
      "amount": 15000,
      "concept": "Saldo inicial",
      "date": "2026-10-04T10:00:00+02:00",
      "type": "income"
    }
  ]
}
```

### 9.6 Efecte sobre altres rutes

Després d'una aportació (US-18, criteri 4):

- `GET /api/home`: el `balance` baixa i el `totalSaved` puja exactament el mateix import. La suma `balance + totalSaved` no canvia.
- El moviment del compte principal surt el primer a `lastMovements` i a `GET /api/movements`.
- El límit diari de recàrrega no canvia: l'aportació no és una recàrrega.

Exemple amb l'aportació de 9.4:

| | `balance` | `totalSaved` | `balance + totalSaved` |
|---|---|---|---|
| Abans | `379521` | `30000` | `409521` |
| Després | `376521` | `33000` | `409521` |

Crear una guardiola no canvia res a `GET /api/home`: neix amb saldo `0`.

### 9.7 Errors

Els codis són a la taula de l'[apartat 5](#taula-de-codis). Els missatges són orientatius: el frontend decideix a partir del `code`.

| `code` | HTTP | Ruta | Quan |
|---|---|---|---|
| `VALIDATION_ERROR` | 422 | Totes les de `POST` | El cos està mal format ([9.3](#93-post-apipots), [9.4](#94-post-apipotspotidcontributions)) |
| `INVALID_POT_NAME` | 422 | `POST /api/pots` | El nom és buit o només té espais |
| `INVALID_TARGET` | 422 | `POST /api/pots` | `target ≤ 0` |
| `POT_NOT_FOUND` | 404 | Les de `/api/pots/{potId}/…` | La guardiola no existeix o és d'un altre usuari |
| `INVALID_AMOUNT` | 422 | `POST /api/pots/{potId}/contributions` | `amount ≤ 0` |
| `INSUFFICIENT_BALANCE` | 422 | `POST /api/pots/{potId}/contributions` | L'aportació supera el saldo del compte principal |

- El `404` segueix la P11 ([apartat 7](#7-propostes-del-contracte)), que el preveu per als recursos que no existeixen.
- Un `POT_NOT_FOUND` és un error de negoci amb el seu `code`. No té res a veure amb el `500 INTERNAL_ERROR` de les rutes que no existeixen ([apartat 5](#taula-de-codis)).

`INVALID_POT_NAME`:

```json
{
  "code": "INVALID_POT_NAME",
  "message": "El nom de la guardiola no pot estar buit."
}
```

`INVALID_TARGET`:

```json
{
  "code": "INVALID_TARGET",
  "message": "L'objectiu ha de ser més gran que 0."
}
```

`INSUFFICIENT_BALANCE`:

```json
{
  "code": "INSUFFICIENT_BALANCE",
  "message": "No tens prou saldo."
}
```

`POT_NOT_FOUND`:

```json
{
  "code": "POT_NOT_FOUND",
  "message": "No s'ha trobat la guardiola."
}
```

### 9.8 Model intern de l'estalvi

Aquest apartat és per al backend. El frontend no en depèn.

- **`Pot`** guanya `target` (enter o `None`) i `color`, i el seu `id` passa a ser un string (P21). Continua tenint `user_id`, que no s'exposa.
- **Historial.** Cada entrada de l'historial pertany a una guardiola i té els camps de [9.5](#95-get-apipotspotidmovements). Com es desa ho proposa la T18.1.
- **Una aportació escriu quatre coses alhora:** el saldo del compte, el saldo de la guardiola, el moviment del compte i l'entrada de l'historial. Es valida tot abans d'escriure. Si una escriptura falla a mig camí, es desfan les anteriors abans de deixar sortir l'error.
- **Invariants:**
  - el saldo del compte és la suma dels `signed_amount` dels seus moviments;
  - el saldo d'una guardiola és la suma del seu historial;
  - `balance + totalSaved` és igual abans i després d'aportar.
- **Amb Firestore** (TR01.1, #106): les guardioles i el seu historial són les col·leccions `pots` i `pot_movements`, els ids surten dels comptadors i l'aportació va dins d'una **transacció**, com la recàrrega ([8.13](#813-model-intern-de-laccés)).
- **Seed**. Les tres guardioles de l'usuari 1 no canvien de nom ni de saldo, perquè en depenen els tests i els mocks del frontend. Guanyen:

  | `id` | `name` | `balance` | `target` | `color` | Entrada inicial de l'historial |
  |---|---|---|---|---|---|
  | `pot-01` | Vacances | `15000` | `100000` | `blue` | `pmov-01`, «Saldo inicial», `15000` |
  | `pot-02` | Emergències | `10000` | `null` | `orange` | `pmov-02`, «Saldo inicial», `10000` |
  | `pot-03` | Regal d'aniversari | `5000` | `8000` | `pink` | `pmov-03`, «Saldo inicial», `5000` |

  - Les entrades inicials tenen una data anterior a avui, com la resta del seed.
  - Les guardioles i les entrades noves continuen la numeració (`pot-04`, `pmov-04`…). Els comptadors es reinicien amb el seed (`POST /api/dev/reset`).
  - L'usuari 2 continua sense guardioles.

---

## 10. Moviments: filtres, detall i informe (US-10 i US-11)

Camps nous del moviment, filtres i cerca al llistat, detall d'un moviment, informe de problema i justificant. Tasca: T10.1 (issue #80).

| Tasca | Què implementa d'aquest apartat |
|---|---|
| T10.2 (backend) | [10.1](#101-camps-nous-de-movement) i el seed de [10.7](#107-model-intern-dels-moviments) |
| T10.3 (backend) | [10.2](#102-filtres-de-get-apimovements) |
| T11.1 (backend) | [10.3](#103-get-apimovementsmovementid) i [10.4](#104-post-apimovementsmovementidreports) |
| T10.4, T11.2 (frontend) | Les pantalles que fan servir aquestes rutes |
| T11.3 (frontend) | El justificant de [10.5](#105-justificant-pdf): el botó i la generació del PDF al navegador |

Totes les rutes d'aquest apartat són **rutes protegides** i resolen l'usuari igual que la resta: amb `X-User-Id` ([apartat 2](#2-usuari-actual-i-estat-del-servei)) mentre estigui permesa, i a partir de la T03.1 amb la sessió ([apartat 8.2](#82-sessió)). Cada usuari només veu els seus moviments. Segueixen les convencions de l'[apartat 1](#1-convencions-generals).

Els exemples fan servir les dades de l'usuari 1 del seed, suposant que avui és el **3/11/2026**. Els ids són els del seed (`mov-01` és el més antic i `mov-30`, el més recent). En canvi, els exemples de l'[apartat 4](#4-endpoints) són fictius i els seus ids no coincideixen amb el seed: per exemple, allà `mov-16` és una transferència i al seed és una recàrrega.

### 10.1 Camps nous de `Movement`

L'objecte `Movement` de l'[apartat 3](#3-objecte-movement) guanya tres camps. Com que l'objecte és el mateix a totes les respostes, els camps nous surten a la Home, al llistat, a la recàrrega, a l'aportació a una guardiola i al detall.

| Camp | Tipus | Notes |
|---|---|---|
| `counterparty` | string \| `null` | Qui paga o qui cobra (US-11). Mai és un text buit. La clau sempre hi és, amb `null` quan no n'hi ha. |
| `status` | `"completed"` \| `"pending"` | Llista tancada. La pantalla mostra «Completat» o «Pendent». |
| `reference` | string | Única entre tots els moviments i opaca: el frontend no l'ha d'interpretar. La genera el backend en crear el moviment, com l'`id`. Format `EVT-000031`. |

**Regla de `counterparty`**:

| Moviment | `counterparty` |
|---|---|
| Transferència o Bizum (`icon: "transfer"`) | El nom del contacte |
| Nòmina (`icon: "salary"`) | L'empresa que paga |
| Recàrrega i aportació a una guardiola | `null` |
| Compres, menjar, transport i altres pagaments | `null`: el concepte ja diu de què es tracta |

- L'alternativa, si es vol una contrapart a tots els pagaments, és posar-hi el nom del comerç. Caldria inventar un nom per a cada moviment del seed.
- Els noms són sempre inventats: cap dada personal real.

**Estat**:

- Un moviment pendent **ja compta al saldo**. El saldo continua sent la suma de tots els moviments, pendents o no: `status` només canvia l'etiqueta.
- Els moviments nous (recàrregues i aportacions) neixen amb `status: "completed"`, una `reference` nova i `counterparty: null`.

Exemple (un Bizum del seed):

```json
{
  "id": "mov-29",
  "amount": 1000,
  "concept": "Bizum enviat",
  "date": "2026-11-01T18:42:00+01:00",
  "type": "expense",
  "icon": "transfer",
  "counterparty": "Núria Soler",
  "status": "completed",
  "reference": "EVT-000029"
}
```

### 10.2 Filtres de `GET /api/movements`

Paràmetres de consulta nous (US-10), opcionals i combinables. Funcionen junt amb `offset` i `limit` ([4.2](#42-get-apimovements)). Noms:

| Paràmetre | Tipus | Què fa |
|---|---|---|
| `dateFrom` | string `YYYY-MM-DD` | Només moviments d'aquest dia o posteriors. |
| `dateTo` | string `YYYY-MM-DD` | Només moviments d'aquest dia o anteriors. |
| `type` | `"income"` \| `"expense"` | Només els moviments d'aquest tipus. Sense el paràmetre surten tots («Tots»). |
| `q` | string | Només els moviments que contenen aquest text al concepte o a la contrapart. |

**Regles:**

- **Dates:** dies naturals a `Europe/Madrid` ([apartat 1](#què-vol-dir-avui)), amb **els dos extrems inclosos**. El dia d'un moviment és el de la seva `date` a Madrid. Es pot fer servir només un dels dos extrems.
- **Text**:
  - El moviment surt si el text apareix com a part del concepte o de la contrapart (`super` troba «Supermercat»).
  - No es distingeixen majúscules ni accents: `recarrega` troba «Recàrrega», i `SUPER` troba el mateix que `super`.
  - S'ignoren els espais dels extrems. Un `q` buit o només amb espais no filtra.
- **Paginació:** els filtres s'apliquen **abans** de paginar. `nextOffset` es calcula sobre el resultat filtrat. L'ordre no canvia: data descendent i, si dues dates coincideixen, primer el creat més tard (P4).
- **Errors:** una data mal formada (p. ex. `2026-13-01` o `01/11/2026`), un `type` que no és `income` ni `expense`, o un `dateFrom` posterior a `dateTo` → `422 VALIDATION_ERROR`.
- **Sense resultats:** `200` amb `{ "items": [], "nextOffset": null }`. El frontend mostra «No hi ha resultats» (US-10, criteri 5).
- `GET /api/home` no té filtres: els `lastMovements` són sempre els 5 últims.

**Petició** (despeses que contenen «super», de dues en dues):

```http
GET /api/movements?type=expense&q=super&limit=2 HTTP/1.1
```

**Resposta:**

```json
{
  "items": [
    {
      "id": "mov-28",
      "amount": 4590,
      "concept": "Supermercat",
      "date": "2026-11-01T18:42:00+01:00",
      "type": "expense",
      "icon": "shopping",
      "counterparty": null,
      "status": "completed",
      "reference": "EVT-000028"
    },
    {
      "id": "mov-23",
      "amount": 6120,
      "concept": "Supermercat",
      "date": "2026-10-27T17:40:00+01:00",
      "type": "expense",
      "icon": "shopping",
      "counterparty": null,
      "status": "completed",
      "reference": "EVT-000023"
    }
  ],
  "nextOffset": 2
}
```

La pàgina següent (`offset=2`) retorna `mov-13` i `mov-06`, amb `nextOffset: null`: en total hi ha 4 «Supermercat».

**Petició** (rang de dates, amb els dos extrems inclosos):

```http
GET /api/movements?dateFrom=2026-11-01&dateTo=2026-11-02 HTTP/1.1
```

Retorna `mov-30` (del 2/11) i `mov-29` i `mov-28` (de l'1/11), amb `nextOffset: null`.

**Error** (`dateFrom` posterior a `dateTo`):

```http
GET /api/movements?dateFrom=2026-11-02&dateTo=2026-11-01 HTTP/1.1
```

```json
{
  "code": "VALIDATION_ERROR",
  "message": "Les dades de la petició no són vàlides."
}
```

### 10.3 `GET /api/movements/{movementId}`

El detall d'un moviment (US-11, criteri 1).

**Resposta `200`:** l'objecte `Movement` sencer ([apartat 3](#3-objecte-movement) i [10.1](#101-camps-nous-de-movement)): l'import i el tipus, la data i l'hora, l'estat, la contrapart i la referència.

- Si el moviment no existeix o és d'un altre usuari → `MOVEMENT_NOT_FOUND`. La resposta és la mateixa en tots dos casos, perquè no es pugui saber si un moviment d'un altre usuari existeix. Un `movementId` amb un format qualsevol (p. ex. `abc`) també dona `MOVEMENT_NOT_FOUND`.

**Petició:**

```http
GET /api/movements/mov-30 HTTP/1.1
```

**Resposta `200`:**

```json
{
  "id": "mov-30",
  "amount": 2350,
  "concept": "Restaurant La Plaça",
  "date": "2026-11-02T21:15:00+01:00",
  "type": "expense",
  "icon": "food",
  "counterparty": null,
  "status": "pending",
  "reference": "EVT-000030"
}
```

### 10.4 `POST /api/movements/{movementId}/reports`

Informe d'un problema amb un moviment (US-11, criteri 3).

**Cos de la petició:** `{ description }`

| Camp | Tipus | Descripció |
|---|---|---|
| `description` | string | Obligatori. Què passa amb el moviment, explicat per l'usuari. |

**Resposta `201`:** `{ id, movementId, description, createdAt }`

| Camp | Tipus | Descripció |
|---|---|---|
| `id` | string | Identificador opac de l'informe. Format `rep-01`, `rep-02`… |
| `movementId` | string | El moviment al qual està vinculat. |
| `description` | string | La descripció desada, sense els espais dels extrems. |
| `createdAt` | string | Data ISO 8601 amb el desplaçament de Madrid. |

**Ordre de les validacions.** S'aturen al primer error:

1. Format del cos: falta `description` o no és un string → `VALIDATION_ERROR`.
2. El moviment no existeix o és d'un altre usuari → `MOVEMENT_NOT_FOUND`.
3. La descripció és buida, només té espais o passa de **500 caràcters** (un cop trets els espais dels extrems) → `INVALID_DESCRIPTION`.

**Regles:**

- Si hi ha un error, no es desa res.
- Es poden enviar diversos informes sobre el mateix moviment.
- L'informe es desa on diu `STORAGE`, com la resta de dades: en memòria, o a la col·lecció `movement_reports` de Firestore (TR01.1, [8.13](#813-model-intern-de-laccés)). **No s'envia enlloc**. `POST /api/dev/reset` l'esborra.
- En aquest sprint no hi ha cap ruta per consultar els informes: el frontend mostra la confirmació a partir de la resposta `201`.

**Petició:**

```http
POST /api/movements/mov-30/reports HTTP/1.1
Content-Type: application/json

{
  "description": "No reconec aquest pagament: aquell dia no vaig anar a aquest restaurant."
}
```

**Resposta `201`:**

```json
{
  "id": "rep-01",
  "movementId": "mov-30",
  "description": "No reconec aquest pagament: aquell dia no vaig anar a aquest restaurant.",
  "createdAt": "2026-11-03T10:00:00+01:00"
}
```

### 10.5 Justificant PDF

El justificant (US-11, criteri 2) es genera **al navegador**, amb **jsPDF** (llicència MIT), a partir de les dades que la pantalla «Detall del moviment» ja ha rebut de [10.3](#103-get-apimovementsmovementid). El botó és «Descarregar justificant». No hi ha cap ruta ni cap servei extern, així que funciona igual amb les dades en memòria, amb Firestore i amb els mocks.

La Cloud Function que s'havia decidit abans demanava el pla Blaze de Firebase, amb una targeta, i el PO la va descartar.

- El PDF és una còpia del que mostra la pantalla: el servidor no el guarda ni el signa.
- La font DejaVu Sans va dins del fitxer, perquè les fonts bàsiques de PDF no tenen el signe «−». jsPDF i la font es carreguen només en tocar el botó.
- Si no es poden carregar (per exemple, sense connexió), surt un error propi de la pantalla, sense cap `code`, i el detall continua visible. El navegador recorda la càrrega fallida, així que per tornar-ho a provar cal recarregar la pàgina, i el missatge ho diu.
- El PDF porta les mateixes dades que la pantalla «Detall del moviment» ([10.3](#103-get-apimovementsmovementid)): el concepte, l'import amb el signe, la data i l'hora, l'estat, la contrapart (o «—» si és `null`) i la referència. L'import i la referència han de coincidir exactament amb els del detall.
- Amb l'ull d'amagar els imports actiu (US-07), la pantalla mostra «••••», però el PDF porta igualment l'import: el justificant es demana expressament, i sense l'import no serviria (decisió del PO).

### 10.6 Errors

Els codis són a la taula de l'[apartat 5](#taula-de-codis). Els missatges són orientatius: el frontend decideix a partir del `code`.

| `code` | HTTP | Ruta | Quan |
|---|---|---|---|
| `VALIDATION_ERROR` | 422 | `GET /api/movements` | Filtres no vàlids ([10.2](#102-filtres-de-get-apimovements)) |
| `VALIDATION_ERROR` | 422 | `POST /api/movements/{movementId}/reports` | Falta `description` o no és un string |
| `MOVEMENT_NOT_FOUND` | 404 | Les de `/api/movements/{movementId}…` | El moviment no existeix o és d'un altre usuari |
| `INVALID_DESCRIPTION` | 422 | `POST /api/movements/{movementId}/reports` | La descripció és buida, només té espais o passa de 500 caràcters |

- El `404` segueix la P11 ([apartat 7](#7-propostes-del-contracte)), que el preveu per als recursos que no existeixen, igual que el `POT_NOT_FOUND` de l'estalvi (PR #119).
- Un `MOVEMENT_NOT_FOUND` és un error de negoci amb el seu `code`. No té res a veure amb el `500 INTERNAL_ERROR` de les rutes que no existeixen ([apartat 5](#taula-de-codis)).

`MOVEMENT_NOT_FOUND`:

```json
{
  "code": "MOVEMENT_NOT_FOUND",
  "message": "No s'ha trobat el moviment."
}
```

`INVALID_DESCRIPTION`:

```json
{
  "code": "INVALID_DESCRIPTION",
  "message": "Explica què passa amb el moviment (com a màxim 500 caràcters)."
}
```

### 10.7 Model intern dels moviments

Aquest apartat és per al backend. El frontend no en depèn.

- **`Movement`** guanya `counterparty` (string o `None`), `status` i `reference`, amb les validacions del model: `status` de la llista tancada, `reference` no buida i `counterparty` `None` o un text no buit.
- **`reference`** la genera el repositori en crear el moviment, igual que l'`id` i el `seq`.
- **Cerca de text:** la regla «sense distingir majúscules ni accents» viu en un sol lloc, una funció pura amb tests propis, que fan servir el servei o el repositori.
- **Informes:** cada informe té `id`, el moviment, l'usuari, la descripció i la data de creació. Es desen en una col·lecció nova del seed, així que `POST /api/dev/reset` els esborra.
- **Amb Firestore** (TR01.1, #106): els informes són la col·lecció `movement_reports`, i la `reference` dels moviments i l'`id` dels informes surten dels comptadors, perquè Firestore no té autoincrement. Crear un informe va dins d'una transacció.
- **Seed**. Els 30 moviments de l'usuari 1 no canvien d'import, de data, de concepte ni d'ordre, perquè en depenen els tests i els mocks del frontend. Guanyen:
  - `reference`: `EVT-000001` a `EVT-000030`, en l'ordre de creació (el mateix número que l'`id`);
  - `status`: `completed` a tots, excepte el més recent (`mov-30`, «Restaurant La Plaça»), que és `pending`;
  - `counterparty`: `null`, excepte aquests (noms inventats):

    | Moviment | Concepte | `counterparty` |
    |---|---|---|
    | `mov-03` | Nòmina | Empresa Demo SL |
    | `mov-09` | Transferència rebuda | Marta Puig |
    | `mov-10` | Lloguer | Jordi Serra |
    | `mov-17` | Nòmina | Empresa Demo SL |
    | `mov-18` | Transferència enviada | Laia Vidal |
    | `mov-24` | Bizum rebut | Pau Ferrer |
    | `mov-29` | Bizum enviat | Núria Soler |

---

## 12. Multidivisa: subcomptes i canvi (US-25, US-26 i US-27)

Subcomptes en altres divises: llistar-los, crear-ne, eliminar-los, veure'n l'historial i canviar diners entre ells. Tasca: T25.1 (issue #166). Històries: `docs/us/US-25.md`, `US-26.md` i `US-27.md`.

| Tasca | Què implementa d'aquest apartat |
|---|---|
| T25.2 (backend) | [12.1](#121-divises-i-tipus-de-canvi), [12.2](#122-objecte-subaccount), [12.3](#123-get-apisubaccounts), [12.4](#124-post-apisubaccounts) i el seed de [12.11](#1211-model-intern-de-multidivisa) |
| T26.1 (backend) | [12.5](#125-post-apisubaccountssubaccountiddelete) i la ruta de [12.6](#126-get-apisubaccountssubaccountidmovements), que llegeix l'historial |
| T27.1 (backend) | [12.7](#127-post-apiexchanges) i [12.8](#128-moviments-dun-canvi-i-efecte-sobre-altres-rutes): el canvi crea els moviments i les entrades de l'historial de 12.6 |
| T25.3, T26.2, T27.2 (frontend) | Les pantalles que criden aquestes rutes |

Totes les rutes d'aquest apartat són **rutes protegides**: necessiten la sessió ([apartat 8.2](#82-sessió)), i sense sessió responen `401 UNAUTHENTICATED`. Cada usuari només veu i modifica els seus comptes. Segueixen les convencions de l'[apartat 1](#1-convencions-generals), amb una diferència: els imports d'un subcompte són enters en la **unitat menor de la seva divisa** (cèntims, o iens sencers al JPY), no sempre en cèntims d'euro.

Els exemples d'aquest apartat fan servir les xifres de les històries: el compte en euros amb `125050` (1.250,50 €, US-25) i un subcompte en dòlars amb `31755` (317,55 $, US-26). Les proves d'acceptació ([`docs/proves-multidivisa.md`](proves-multidivisa.md)) parteixen del seed. Les dates d'exemple són del 19/11/2026 (`+01:00`, horari d'hivern).

### 12.1 Divises i tipus de canvi

La llista de divises és **tancada** i els tipus són fixos: no es consulta cap API de tipus de canvi (US-25).

| Codi | Nom | Símbol | Decimals | `rateBps` | Equivalència |
|---|---|---|---|---|---|
| `EUR` | Euro | € | 2 | `10000` | 1 € = 1 € |
| `USD` | Dòlar nord-americà | $ | 2 | `9123` | 1 $ = 0,9123 € |
| `GBP` | Lliura esterlina | £ | 2 | `11680` | 1 £ = 1,1680 € |
| `CHF` | Franc suís | CHF | 2 | `10355` | 1 CHF = 1,0355 € |
| `JPY` | Ien japonès | ¥ | 0 | `5700` | 1 ¥ = 0,0057 € |

Els valors i el format són els de la pantalla que ja hi ha a la branca de la US-25 (`frontend/src/models/currency.ts`, T25.3).

- **Unitat menor:** el cèntim a les divises amb 2 decimals, i el ien sencer al JPY, que no té decimals. `1234` en JPY és «1.234 ¥» (US-25).
- **`rateBps`:** quants cèntims d'euro val una unitat menor de la divisa, multiplicat per 10.000. Per això el JPY és `5700`: 1 ¥ val 0,57 cèntims d'euro.
- **Conversió** d'`amount` unitats menors de la divisa `A` a la divisa `B`:

  ```
  convertit = arrodonir(amount × rateBps[A] / rateBps[B])
  ```

  - Tot es calcula amb enters, mai amb decimals. `arrodonir(n / d)` és `⌊(2n + d) / (2d)⌋`: la meitat, cap amunt.
  - Exemple: 100,00 € en dòlars és `10000 × 10000 / 9123 = 10961,30…`, que s'arrodoneix a `10961` (109,61 $).
- **Total aproximat en euros** («Total ≈ … €», US-25): cada compte es converteix a cèntims d'euro i s'arrodoneix per separat (`arrodonir(balance × rateBps / 10000)`), i després se sumen. Exemple: `125050` € i `31755` $ donen `125050 + 28970 = 154020` («Total ≈ 1.540,20 €»).

### 12.2 Objecte `Subaccount`

Un compte de l'usuari en una divisa. És el mateix objecte a totes les respostes d'aquest apartat.

| Camp | Tipus | Notes |
|---|---|---|
| `id` | string | Identificador opac. El compte principal en euros és `"main"`. Els subcomptes en divisa són `sub-01`, `sub-02`…, per ordre de creació i únics a tot el sistema, com les guardioles. |
| `currency` | string | Un codi de la llista de [12.1](#121-divises-i-tipus-de-canvi). |
| `balance` | integer | Saldo en la unitat menor de la divisa, `≥ 0`. Un subcompte nou té `0`. |
| `isMain` | boolean | `true` només al compte principal en euros, que no s'elimina mai (US-25 i US-26). |
| `rateBps` | integer | El tipus fix de la divisa ([12.1](#121-divises-i-tipus-de-canvi)). El resum del canvi el fa servir per al «Rebràs exactament» (US-27). |

- **El compte en euros és el compte principal**, no un compte a part. El seu `balance` és el mateix que el de `GET /api/home`, i els seus moviments són els de `GET /api/movements`. Tots els usuaris el tenen des del registre.
- Com a molt hi ha cinc comptes: l'EUR i les quatre altres divises. La llista tancada ja és el topall (US-25).

Exemples:

```json
{ "id": "main", "currency": "EUR", "balance": 125050, "isMain": true, "rateBps": 10000 }
```

```json
{ "id": "sub-01", "currency": "USD", "balance": 31755, "isMain": false, "rateBps": 9123 }
```

### 12.3 `GET /api/subaccounts`

Els comptes de l'usuari: la card «Divises» d'Inici i la pantalla `/divises` (US-25).

**Resposta `200`:** `{ items, totalInEuros }`

| Camp | Tipus | Descripció |
|---|---|---|
| `items` | `Subaccount[]` | Tots els comptes de l'usuari. El primer és sempre el compte principal en euros; després, els subcomptes en divisa per ordre de creació. Mai és buida. |
| `totalInEuros` | integer | El total aproximat, en cèntims d'euro, calculat com diu [12.1](#121-divises-i-tipus-de-canvi). |

- El total el calcula el servidor amb la taula de tipus fixa (T25.2), perquè cap pantalla el calculi diferent.
- Un subcompte nou, a `0`, no canvia el total (US-25).

**Resposta** (xifres de les històries):

```json
{
  "items": [
    { "id": "main", "currency": "EUR", "balance": 125050, "isMain": true, "rateBps": 10000 },
    { "id": "sub-01", "currency": "USD", "balance": 31755, "isMain": false, "rateBps": 9123 }
  ],
  "totalInEuros": 154020
}
```

### 12.4 `POST /api/subaccounts`

Crea un subcompte en una divisa nova («Afegir divisa», US-25).

**Cos de la petició:** `{ currency }`

| Camp | Tipus | Descripció |
|---|---|---|
| `currency` | string | Codi de la divisa. Obligatori. Distingeix majúscules: `"usd"` no és a la llista. |

**Resposta `201`:** el `Subaccount` creat, sol, amb `balance: 0`.

**Ordre de les validacions**, el que ja fa servir la pantalla (`frontend/src/mocks/currencies.ts`). S'aturen al primer error:

1. Format del cos: falta `currency` o no és un string → `VALIDATION_ERROR`.
2. El codi no és a la llista de [12.1](#121-divises-i-tipus-de-canvi) → `CURRENCY_NOT_SUPPORTED`.
3. L'usuari ja té un compte en aquesta divisa, també si és l'`EUR` principal → `CURRENCY_EXISTS`. El servidor ho valida encara que la pantalla ja mostri la fila en gris (US-25).

**Regles:**

- Un sol subcompte per divisa i usuari. Si arriben dues peticions alhora per a la mateixa divisa, només en guanya una, i l'altra rep `CURRENCY_EXISTS`.
- Un error no crea res ni gasta cap `id`.

**Petició:**

```http
POST /api/subaccounts HTTP/1.1
Content-Type: application/json

{
  "currency": "USD"
}
```

**Resposta `201`:**

```json
{ "id": "sub-01", "currency": "USD", "balance": 0, "isMain": false, "rateBps": 9123 }
```

### 12.5 `POST /api/subaccounts/{subaccountId}/delete`

Elimina un subcompte en divisa que té saldo 0 («Eliminar subcompte», US-26). És `POST` i no `DELETE` perquè el CORS i l'`apiClient` només admeten `GET` i `POST`.

- **Cos de la petició:** cap.
- **Resposta `200`:** `{ status }`, amb `status` sempre `"ok"`, com a [8.9](#89-post-apiauthlogout).

**Ordre de les validacions**. S'aturen al primer error:

1. El subcompte no existeix o és d'un altre usuari → `SUBACCOUNT_NOT_FOUND`. La resposta és la mateixa en tots dos casos, com a `POT_NOT_FOUND`.
2. És el compte principal (`main`) → `MAIN_ACCOUNT_NOT_DELETABLE`. Es comprova abans que el saldo: l'EUR no s'elimina mai, tingui el saldo que tingui.
3. El saldo no és exactament 0 → `SUBACCOUNT_NOT_EMPTY`. N'hi ha prou amb `1` (0,01 $).

**Regles:**

- Només s'esborra el subcompte. Els moviments del compte principal que han fet els seus canvis es queden a `GET /api/movements`, amb el seu import (US-26).
- Les entrades de l'historial del subcompte ([12.6](#126-get-apisubaccountssubaccountidmovements)) es queden desades, però ja no es poden consultar: la ruta de l'historial respon `SUBACCOUNT_NOT_FOUND`.
- La divisa torna a estar disponible. Un `POST /api/subaccounts` amb la mateixa divisa en crea un de nou, amb un `id` nou, saldo `0` i l'historial buit.
- El total de [12.3](#123-get-apisubaccounts) no canvia, perquè el saldo era 0.

### 12.6 `GET /api/subaccounts/{subaccountId}/movements`

L'historial d'un subcompte en divisa: «Últims moviments» al detall del subcompte (mockup `US-26-detall-subcompte`).

**Resposta `200`:** `{ items }`, de l'entrada més recent a la més antiga, sense paginació.

Cada entrada:

| Camp | Tipus | Notes |
|---|---|---|
| `id` | string | Identificador opac. Format `smov-01`, `smov-02`… |
| `amount` | integer | En la unitat menor de la divisa del subcompte, sempre `> 0`. |
| `concept` | string | El de [12.8](#128-moviments-dun-canvi-i-efecte-sobre-altres-rutes). |
| `date` | string | ISO 8601 amb desplaçament. |
| `type` | `"income"` \| `"expense"` | Des del punt de vista del subcompte: entren o surten diners. |

- Un subcompte nou té l'historial buit (`{ "items": [] }`). La pantalla mostra «Encara no tens moviments» (mockup).
- El saldo d'un subcompte és sempre la suma del seu historial.
- Si dues entrades tenen la mateixa data, va primer la creada més tard, com a P4.
- Només és per als subcomptes en divisa. L'historial del compte en euros és `GET /api/movements` ([4.2](#42-get-apimovements)), que ja existeix, i amb `main` aquesta ruta respon `SUBACCOUNT_NOT_FOUND` (decisió del PO).
- El subcompte no existeix, és d'un altre usuari o s'ha eliminat → `SUBACCOUNT_NOT_FOUND`.

**Resposta** (`sub-01`, després del canvi de [12.7](#127-post-apiexchanges)):

```json
{
  "items": [
    {
      "id": "smov-01",
      "amount": 10961,
      "concept": "Canvi EUR → USD",
      "date": "2026-11-19T10:00:00+01:00",
      "type": "income"
    }
  ]
}
```

### 12.7 `POST /api/exchanges`

Canvia diners d'un compte de l'usuari a un altre de la mateixa persona en una altra divisa («Confirmar canvi», US-27). El nom de la ruta és el que ja fa servir la pantalla (PR #180).

**Cos de la petició:** `{ fromCurrency, toCurrency, amount }`

| Camp | Tipus | Descripció |
|---|---|---|
| `fromCurrency` | string | Divisa del compte d'origen. Obligatori. |
| `toCurrency` | string | Divisa del compte de destí. Obligatori. |
| `amount` | integer | Import a canviar, en la unitat menor de la divisa d'origen. Obligatori. Enter JSON estricte, com a P5. |

**Càlcul**:

| Valor | Fórmula | 100,00 € a dòlars |
|---|---|---|
| Import convertit (`received`) | `arrodonir(amount × rateBps[origen] / rateBps[destí])` | `10961` (109,61 $) |
| Comissió (`commission`) | `max(arrodonir(amount × 150 / 10000), mínim[origen])` | `150` (1,50 €) |
| Càrrec a l'origen | `amount + commission` | `10150` (101,50 €) |

- **La comissió** és de l'1,5 % amb un mínim de 0,50 €, **sempre**: aquest sprint no hi ha canvis sense comissió (decisió del PO, issues #166 i #173). Es calcula en la divisa d'origen, arrodonida a la unitat menor. La paga l'origen i es queda al sistema: no l'ingressa cap compte.
- **El mínim de 0,50 €** es converteix a la divisa d'origen arrodonint **cap amunt**, perquè mai valgui menys de 0,50 €: `mínim[origen] = ⌈50 × 10000 / rateBps[origen]⌉`.

  | Divisa d'origen | `EUR` | `USD` | `GBP` | `CHF` | `JPY` |
  |---|---|---|---|---|---|
  | Comissió mínima | `50` (0,50 €) | `55` (0,55 $) | `43` (0,43 £) | `49` (0,49 CHF) | `88` (88 ¥) |

- **Exemples de les històries**, que quadren amb aquest càlcul:
  - **US-27:** 100,00 € a dòlars, amb 1.250,50 € i 317,55 $. La comissió és d'1,50 €, l'EUR queda a 1.149,00 € (`114900`), el USD a 427,16 $ (`42716`) i el total a 1.538,70 € (`153870`).
  - **US-26:** 312,86 $ a euros. La comissió és `arrodonir(31286 × 150 / 10000) = 469` (4,69 $), més gran que el mínim de 0,55 $. El càrrec és `31755`, tot el saldo, i el subcompte queda a 0,00 $. L'EUR rep `28542` (285,42 €).
  - **El mínim:** 10,00 € a dòlars. L'1,5 % són 0,15 €, així que la comissió és de 0,50 € i el càrrec, de 10,50 €.

**Ordre de les validacions**, el de la pantalla (PR #180) amb els codis de l'API. S'aturen al primer error:

1. Format del cos: falta un camp, les divises no són strings o `amount` no és un enter JSON estricte → `VALIDATION_ERROR`.
2. `fromCurrency` i `toCurrency` són la mateixa → `SAME_CURRENCY`.
3. Alguna de les dues divises no és un compte de l'usuari, també si el codi no és a la llista → `SUBACCOUNT_NOT_FOUND`.
4. `amount ≤ 0` → `INVALID_AMOUNT`, el mateix codi que a la recàrrega i a l'aportació.
5. `amount × rateBps[origen] < rateBps[destí]` → `AMOUNT_TOO_SMALL`: l'import convertit, **exacte i abans d'arrodonir**, no arriba a una unitat menor del destí. És la regla literal de la US-27 i la que fa la pantalla (PR #180). Exemple: 0,01 $ són 0,9123 cèntims d'euro, que no arriben a 1 cèntim, i per tant és massa petit, encara que arrodonit donaria 1. Si l'import passa aquesta comprovació, el convertit exacte és com a mínim 1, i `received` mai no és 0.
6. `amount + commission` és més gran que el saldo de l'origen → `INSUFFICIENT_BALANCE`. Exemple: canviar tot el saldo, sense marge per a la comissió.

**Regles:**

- **Tot o res** (US-27). Un canvi fa quatre escriptures: el saldo de l'origen, el del destí i un moviment a cadascun ([12.8](#128-moviments-dun-canvi-i-efecte-sobre-altres-rutes)). O es fan totes, o no se'n fa cap. Si hi ha un error, no canvia res.
- Dos canvis alhora des del mateix compte s'apliquen un darrere l'altre. El segon es valida amb el saldo que ha deixat el primer: cap saldo pot quedar negatiu.
- Canviar exactament tot el saldo (l'import més la comissió) està permès. L'origen queda a `0`.
- No hi ha cap límit diari de canvi, i un canvi no compta per al límit diari de recàrrega.

**Resposta `201`:** `{ from, to, amount, commission, received }`

| Camp | Tipus | Descripció |
|---|---|---|
| `from` | `Subaccount` | El compte d'origen, amb el saldo nou. |
| `to` | `Subaccount` | El compte de destí, amb el saldo nou. |
| `amount` | integer | L'import canviat, en la unitat menor de l'origen. |
| `commission` | integer | La comissió aplicada, en la unitat menor de l'origen. |
| `received` | integer | El que ha rebut el destí, en la seva unitat menor. |

- Els tipus aplicats són el `rateBps` de `from` i el de `to`.
- La resposta no porta els moviments: després del tic «Canvi fet», l'app torna a Inici i hi torna a demanar les dades (US-27).

**Petició** (exemple de la US-27):

```http
POST /api/exchanges HTTP/1.1
Content-Type: application/json

{
  "fromCurrency": "EUR",
  "toCurrency": "USD",
  "amount": 10000
}
```

**Resposta `201`:**

```json
{
  "from": { "id": "main", "currency": "EUR", "balance": 114900, "isMain": true, "rateBps": 10000 },
  "to": { "id": "sub-01", "currency": "USD", "balance": 42716, "isMain": false, "rateBps": 9123 },
  "amount": 10000,
  "commission": 150,
  "received": 10961
}
```

### 12.8 Moviments d'un canvi i efecte sobre altres rutes

Cada canvi crea **dos moviments**, un a cada compte i en la seva divisa (US-27):

| Compte | `type` | `amount` |
|---|---|---|
| Origen | `expense` | L'import més la comissió |
| Destí | `income` | L'import convertit |

- **Concepte:** el mateix als dos moviments, «Canvi <codi d'origen> → <codi de destí>», p. ex. «Canvi EUR → USD» (decisió del PO).

- **Compte principal en euros.** Si l'EUR és l'origen o el destí, el seu moviment és un `Movement` normal ([apartat 3](#3-objecte-movement)) i surt a `GET /api/home` i a `GET /api/movements`, com al mockup `US-27-inici-despres-canvi` (−101,50 €). Porta `icon: "transfer"`, `counterparty: null`, `status: "completed"`, una `reference` nova i el `kind` intern `"other"`.
- **Subcompte en divisa.** El seu moviment només surt al seu historial ([12.6](#126-get-apisubaccountssubaccountidmovements)). `GET /api/movements` continua tenint només moviments en euros, i l'objecte `Movement` no canvia.
- Un canvi entre dues divises sense l'EUR (p. ex. de dòlars a lliures) no crea cap moviment al compte principal.
- La comissió va dins del moviment d'origen. Així cada saldo continua sent la suma dels seus moviments.

Després d'un canvi:

- `GET /api/home`: el `balance` canvia si l'EUR és l'origen o el destí.
- `GET /api/subaccounts`: canvien els dos saldos, i el `totalInEuros` baixa més o menys el valor de la comissió, segons l'arrodoniment.
- El límit diari de recàrrega no canvia.

Exemple amb el canvi de la US-27:

| | EUR (`main`) | USD (`sub-01`) | `totalInEuros` |
|---|---|---|---|
| Abans | `125050` | `31755` | `154020` |
| Després | `114900` | `42716` | `153870` |

### 12.9 Fora de l'abast

- **Aportar a un subcompte:** aquest sprint no hi ha botó «Aportar» (decisió del PO a la US-26). Un subcompte només s'omple i es buida amb un canvi, i no hi ha cap ruta `POST /api/subaccounts/{subaccountId}/topups`.
- Els pagaments en divisa (US-28) i el canvi sense comissió (US-29).
- Tipus de canvi variables o d'una API externa.

### 12.10 Errors

Els codis són a la taula de l'[apartat 5](#taula-de-codis). Els missatges són els literals de les històries: el frontend decideix a partir del `code`.

| `code` | HTTP | Ruta | Quan |
|---|---|---|---|
| `VALIDATION_ERROR` | 422 | `POST /api/subaccounts`, `POST /api/exchanges` | El cos està mal format |
| `CURRENCY_NOT_SUPPORTED` | 422 | `POST /api/subaccounts` | La divisa no és a la llista |
| `CURRENCY_EXISTS` | 422 | `POST /api/subaccounts` | L'usuari ja té un compte en aquesta divisa |
| `SUBACCOUNT_NOT_FOUND` | 404 | Les de `/api/subaccounts/{subaccountId}/…`, `POST /api/exchanges` | El compte no existeix o és d'un altre usuari. Al canvi, una de les divises no és un compte de l'usuari |
| `MAIN_ACCOUNT_NOT_DELETABLE` | 422 | `POST /api/subaccounts/{subaccountId}/delete` | Es vol eliminar el compte en euros |
| `SUBACCOUNT_NOT_EMPTY` | 422 | `POST /api/subaccounts/{subaccountId}/delete` | El saldo no és exactament 0 |
| `SAME_CURRENCY` | 422 | `POST /api/exchanges` | L'origen i el destí són la mateixa divisa |
| `INVALID_AMOUNT` | 422 | `POST /api/exchanges` | `amount ≤ 0` (ja existeix) |
| `AMOUNT_TOO_SMALL` | 422 | `POST /api/exchanges` | L'import convertit no arriba a una unitat menor del destí |
| `INSUFFICIENT_BALANCE` | 422 | `POST /api/exchanges` | L'import més la comissió supera el saldo de l'origen (ja existeix, [9.7](#97-errors)) |

Missatges:

| `code` | `message` |
|---|---|
| `CURRENCY_NOT_SUPPORTED` | «Aquesta divisa no és a la llista de divises disponibles.» (US-25) |
| `CURRENCY_EXISTS` | «Ja tens un subcompte en aquesta divisa.» (US-25) |
| `SUBACCOUNT_NOT_FOUND` | «No s'ha trobat el subcompte.» (decisió del PO) |
| `MAIN_ACCOUNT_NOT_DELETABLE` | «El compte en euros no es pot eliminar.» (US-26) |
| `SUBACCOUNT_NOT_EMPTY` | «Només pots eliminar un subcompte amb saldo 0.» (US-26) |
| `SAME_CURRENCY` | «Origen i destí no poden ser el mateix subcompte.», el text de la pantalla (PR #180, decisió del PO) |
| `AMOUNT_TOO_SMALL` | «L'import és massa petit per canviar.» (US-27) |
| `INSUFFICIENT_BALANCE` | «No tens prou saldo.», el text únic per a tots els casos: aportació, enviament i canvi (P85 de la #196, decisió del PO). El frontend tria el text pel `code`. |
| `INVALID_AMOUNT` | «L'import ha de ser més gran que 0.» (ja existeix) |

- El `404` segueix la P11 ([apartat 7](#7-propostes-del-contracte)), que el preveu per als recursos que no existeixen.

### 12.11 Model intern de multidivisa

Aquest apartat és per al backend. El frontend no en depèn.

- **El compte en euros és l'`Account` actual.** No es desa cap subcompte EUR: `GET /api/subaccounts` el construeix a partir del compte principal de l'usuari, amb l'`id` `"main"`. Així el saldo no es duplica.
- **Subcomptes en divisa:** un model nou amb `id`, `user_id`, `currency`, `balance` i l'ordre de creació, amb les validacions al model: divisa de la llista, que no sigui l'`EUR`, i saldo enter `≥ 0`.
- **Historial:** un model nou, com l'historial de les guardioles ([9.8](#98-model-intern-de-lestalvi)), amb el subcompte al qual pertany. En eliminar un subcompte, les seves entrades no s'esborren.
- **Taula de divises i regla de la comissió en un sol mòdul** (skill `middle-services`): els codis, els `rateBps`, la comissió (`150` punts bàsics) i el mínim (`50` cèntims d'euro), i les funcions de conversió, comissió i total. La US-29 (canvi sense comissió) el podrà ampliar sense tocar els serveis.
- **Tot o res**, com l'aportació ([9.8](#98-model-intern-de-lestalvi)): es valida tot abans d'escriure i les quatre escriptures van dins d'`atomic.run(...)`. Si una falla, es desfan les anteriors.
- **Amb Firestore** (TR01.1): les col·leccions `subaccounts` i `subaccount_movements`, amb els ids dels comptadors. Els dos comptes d'un canvi es llegeixen i s'escriuen dins de la mateixa transacció.
- **Invariants:**
  - el saldo de cada compte és la suma dels seus moviments;
  - un canvi no crea ni destrueix diners més enllà de la comissió: l'import convertit val en euros el mateix que l'import, amb una diferència d'1 cèntim com a molt per l'arrodoniment.
- **Seed:** cap usuari té subcomptes en divisa. L'usuari 1 parteix de l'EUR amb `379521` i l'usuari 2, amb `0`. Els subcomptes i les entrades noves comencen per `sub-01` i `smov-01`, i els comptadors es reinicien amb el seed (`POST /api/dev/reset`).

---

## 13. Pagaments: cercar usuaris i enviar diners (US-13 i US-14)

Trobar altres usuaris de l'app i enviar-los diners a l'instant. Tasca: T13.1 (issue #157). Les pantalles, els textos i els mockups són a les històries (`docs/us/US-13.md` i `docs/us/US-14.md`); les proves d'acceptació, a [`docs/proves-pagaments.md`](proves-pagaments.md).

| Tasca | Què implementa d'aquest apartat |
|---|---|
| T13.2 (backend) | [13.1](#131-objecte-usersummary), [13.2](#132-get-apiusers), [13.3](#133-get-apiusersuserid), l'`@usuari` i el seed de [13.9](#139-model-intern) |
| T13.3 (frontend) | La barra de cerca a «Enviar diners», que crida [13.2](#132-get-apiusers) |
| T14.1 (backend) | [13.4](#134-post-apitransfers), [13.5](#135-límit-diari-denviament) (amb `GET /api/transfers/limit`) i [13.6](#136-efecte-sobre-altres-rutes) |
| T14.2 (backend) | Els avisos de [13.7](#137-avisos-a-la-bústia-simulada) |
| T14.3 i T14.4 (frontend) | «Pagaments», «Enviar» i «Confirmar», que criden [13.3](#133-get-apiusersuserid), `GET /api/transfers/limit` ([13.5](#get-apitransferslimit)) i [13.4](#134-post-apitransfers), i Inici i el llistat amb els saldos nous |

Totes les rutes d'aquest apartat són **protegides** ([8.2](#82-sessió)): l'usuari és el de la sessió. Els imports són cèntims enters i les dates, ISO 8601 amb el desplaçament de Madrid ([apartat 1](#1-convencions-generals)). Els exemples fan servir l'usuari 1 del seed (`Usuari demo`, saldo `379521`) i els usuaris de [13.9](#139-model-intern).

### 13.1 Objecte `UserSummary`

Un altre usuari, tal com surt a la cerca i al destinatari d'un enviament. (P64, P65)

| Camp | Tipus | Notes |
|---|---|---|
| `id` | string | Identificador opac amb el format `usr-03`, com `Movement.id` (P1). El frontend no l'ha d'interpretar: només el passa a `?to=<id>` i a `toUserId`. |
| `name` | string \| `null` | Nom visible. Val `null` si l'usuari no en té: els que es registren a US-01 no en donen cap. Llavors el frontend mostra l'`@usuari` com a nom (US-13). |
| `username` | string | L'`@usuari`, **sense** l'`@` i en minúscules (`aliciaa415`). El frontend hi afegeix l'`@`. |

- **Mai** hi surten dades financeres (saldo, moviments, guardioles, XP) ni l'email, el telèfon o l'estat del compte d'un altre usuari. Les inicials de la fila les calcula el frontend a partir del nom visible.
- Un usuari **pendent** de verificar ([8.5](#85-post-apiauthregister)) no surt mai: no pot rebre diners.

### 13.2 `GET /api/users`

Cerca d'usuaris per a «Enviar diners» (US-13). (P66, P67)

**Paràmetre de consulta opcional:** `q`, el text de la barra «@usuari, telèfon o email».

- Es treuen els espais del principi i del final.
- Més de **64 caràcters** (després de treure'ls) → `422 VALIDATION_ERROR`. La pantalla mostra «Les dades no són vàlides. Revisa-les i torna-ho a provar.» amb «Reintentar».

**Resposta `200`:** `{ items }`, una llista d'`UserSummary` ([13.1](#131-objecte-usersummary)).

- **Sense `q`, o amb `q` buit:** la llista inicial, tots els altres usuaris actius.
- **Amb `q`:** els usuaris que hi coincideixen per alguna d'aquestes quatre vies:

| Via | Coincideix si… | Exemple (seed) |
|---|---|---|
| `@usuari` | El text, sense l'`@` del principi, és **part** de l'`username`. Sense distingir majúscules. | `hua`, `@hua` o `@123HUABIN123` → Huabin |
| Nom | El text és **part** del nom visible. Sense distingir majúscules ni accents. | `marti` o `Martí` → Martí |
| Email | El text, normalitzat com un email ([8.3](#83-identificador-email-o-telèfon)), és **igual** a l'email de l'usuari. Una part de l'email no coincideix, perquè la cerca no serveixi per endevinar emails. | `Huabin@Evolt.test` → Huabin; `evolt.test` → cap |
| Telèfon | El text només té xifres, espais, `+`, `-`, `.`, `(` i `)`, en té **9 o més**, i les **9 últimes** són iguals a les 9 últimes del telèfon de l'usuari. | `611 22 33 02`, `+34 611 22 33 02` i `611223302` → Huabin |

**Regles:**

- L'usuari de la sessió **no surt mai**, ni a la llista inicial ni a cap cerca: cercar el meu nom, `@demo`, `demo@evolt.test` o el meu telèfon dona `items: []`.
- Sense coincidències → `200` amb `items: []`, no un error. La pantalla mostra «No hi ha resultats»; amb el camp buit torna la llista inicial, sense aquest text.
- **Ordre:** per nom visible (el `name` o, si no en té, l'`username`), sense distingir majúscules ni accents; si dos coincideixen, primer el d'id més petit.
- **Com a màxim 10** usuaris, tant a la llista inicial com a les cerques (US-14: «màxim 10 resultats»). No hi ha paginació.
- La cerca no canvia res i no compta com a cap enviament.

**Petició:**

```http
GET /api/users?q=611%2022%2033%2002 HTTP/1.1
Authorization: Bearer <token>
```

**Resposta `200`:**

```json
{
  "items": [
    {
      "id": "usr-04",
      "name": "Huabin",
      "username": "123huabin123"
    }
  ]
}
```

**Llista inicial** de l'usuari 1 (`GET /api/users`): Alicia, Huabin, Izan, Jiajun, Junhao, Martí i Usuari nou, en aquest ordre.

### 13.3 `GET /api/users/{userId}`

Un usuari concret, perquè «Enviar» ([US-14](#134-post-apitransfers)) pugui tornar a validar el destinatari quan es recarrega `/pagaments/enviar?to=<id>`. (P68)

**Resposta `200`:** l'`UserSummary` de l'usuari ([13.1](#131-objecte-usersummary)).

- L'usuari no existeix, està pendent de verificar o l'id té un format qualsevol → `404 RECIPIENT_NOT_FOUND` («No hem trobat aquest destinatari.»). La pantalla hi afegeix «Torna a triar el destinatari».
- El propi usuari de la sessió també respon `200`: no és cap dada nova per a ell. Qui impedeix enviar-se diners a un mateix és [13.4](#134-post-apitransfers).

```json
{
  "id": "usr-02",
  "name": "Usuari nou",
  "username": "buit"
}
```

### 13.4 `POST /api/transfers`

Envia diners del compte principal de l'usuari de la sessió al compte principal d'un altre usuari, a l'instant (US-14). (P69, P70)

**Cos de la petició:** `{ toUserId, amount, concept? }`

| Camp | Tipus | Descripció |
|---|---|---|
| `toUserId` | string | L'`id` de l'`UserSummary` del destinatari. Obligatori. |
| `amount` | integer | Import en cèntims. Obligatori. Enter JSON estricte, com a P5. |
| `concept` | string \| `null` | Opcional. Es desa sense els espais dels extrems; buit o només amb espais és com no posar-ne. Com a màxim **140** caràcters. |

**Resposta `201`:** `{ balance, movement, recipient }`

| Camp | Tipus | Descripció |
|---|---|---|
| `balance` | integer | Saldo **nou** del compte de qui envia, en cèntims. |
| `movement` | `Movement` | El moviment que s'ha creat al compte de qui envia. |
| `recipient` | `UserSummary` | El destinatari ([13.1](#131-objecte-usersummary)). |

Amb aquesta resposta, el frontend pinta el tic verd «Has enviat 20,00 € a Usuari nou» i «Saldo disponible: 3.775,21 €» sense tornar a demanar res, i al cap d'1,5 s torna a Inici.

**Ordre de les validacions.** S'aturen al primer error:

1. Format del cos: falta `toUserId` o `amount`, algun no és del tipus de la taula, o `concept` passa de 140 caràcters → `VALIDATION_ERROR`.
2. El destinatari no existeix, està pendent de verificar o l'id té un format qualsevol → `RECIPIENT_NOT_FOUND` (`404`).
3. El destinatari és l'usuari de la sessió → `SELF_TRANSFER` (`422`, «No et pots enviar diners a tu mateix.»).
4. `amount ≤ 0` → `INVALID_AMOUNT`.
5. `amount` més gran que el saldo de qui envia → `INSUFFICIENT_BALANCE`, el mateix codi i el mateix text que l'aportació («No tens prou saldo.»).
6. Enviat avui + `amount` supera el límit diari ([13.5](#135-límit-diari-denviament)) → `TRANSFER_LIMIT_EXCEEDED` (`422`), amb `details.remainingToday`.

Si qualsevol validació falla, **no es mou res**: ni saldos, ni moviments, ni avisos.

**Regles:**

- **Tot o res.** Un enviament fa sis escriptures: el saldo de qui envia baixa, el de qui rep puja, un moviment a cada compte i un avís a cadascú ([13.7](#137-avisos-a-la-bústia-simulada)). O es fan totes, o no se'n fa cap.
- **Moviment de qui envia** (P72):
  - `type: "expense"`, `amount` igual a l'enviament i `icon: "transfer"`;
  - `concept`: el concepte de la petició o, si no n'hi ha, `"Transferència enviada"`;
  - `counterparty`: el nom visible del destinatari (el `name` o, si no en té, `@username`), com a les transferències del seed (P35);
  - `status: "completed"`, una `reference` nova i la data de l'enviament.
- **Moviment de qui rep:** igual, però `type: "income"`, el concepte de la petició o `"Transferència rebuda"`, i `counterparty` amb el nom visible de qui envia.
- El saldo de cada compte continua sent la suma dels seus moviments.
- **Casos límit:**
  - Enviar **exactament** tot el saldo està permès: el compte de qui envia queda a `0`.
  - Dos enviaments alhora de la mateixa persona s'apliquen un darrere l'altre. El segon es valida amb el saldo i el límit que ha deixat el primer: el saldo mai pot quedar negatiu i el límit mai es pot passar.
  - Un enviament i un altre que arriba al mateix compte alhora també s'apliquen un darrere l'altre.
- En aquest sprint, enviar o rebre no dona ni treu XP.
- El límit no es pot editar en aquest sprint.

**Petició:**

```http
POST /api/transfers HTTP/1.1
Authorization: Bearer <token>
Content-Type: application/json

{
  "toUserId": "usr-02",
  "amount": 2000,
  "concept": "El sopar de divendres"
}
```

**Resposta `201`** (saldo anterior de l'usuari 1: `379521`):

```json
{
  "balance": 377521,
  "movement": {
    "id": "mov-31",
    "amount": 2000,
    "concept": "El sopar de divendres",
    "date": "2026-11-15T21:15:00+01:00",
    "type": "expense",
    "icon": "transfer",
    "counterparty": "Usuari nou",
    "status": "completed",
    "reference": "EVT-000031"
  },
  "recipient": {
    "id": "usr-02",
    "name": "Usuari nou",
    "username": "buit"
  }
}
```

L'usuari 2 té ara saldo `2000` i un moviment `mov-32`: `"El sopar de divendres"`, `type: "income"`, `counterparty: "Usuari demo"`.

### 13.5 Límit diari d'enviament

| Límit | Valor | Equivalent |
|---|---|---|
| Màxim enviat per dia natural (suma dels enviaments d'avui de qui envia) | `100000` | 1.000,00 € |

- «Avui» és el dia natural a `Europe/Madrid` ([apartat 1](#què-vol-dir-avui)). El límit torna a començar a les 00:00.
- Arribar **exactament** al límit està permès: després d'enviar `2000` avui, encara es poden enviar `98000`.
- Només compten els enviaments **fets** per l'usuari. Els diners rebuts no hi compten.
- És un límit **diferent** del de les recàrregues ([4.3](#43-post-apitopups)): enviar no gasta límit de recàrrega, i recarregar no gasta límit d'enviament. Per això té un codi propi (P71).
- `TRANSFER_LIMIT_EXCEEDED` porta `details.remainingToday`: el que encara es pot enviar avui, en cèntims (`0` si ja s'ha arribat al límit). La pantalla mostra «Has superat el límit diari de 1.000,00 €. Avui encara pots enviar 980,00 €.».

```json
{
  "code": "TRANSFER_LIMIT_EXCEEDED",
  "message": "Has superat el límit diari d'enviament.",
  "details": { "remainingToday": 98000 }
}
```

#### `GET /api/transfers/limit`

Quant pot enviar encara avui l'usuari de la sessió. «Enviar» ho demana en obrir-se, com el saldo, per mostrar «Has superat el límit diari de 1.000,00 €. Avui encara pots enviar 980,00 €.» i desactivar «Continuar» **abans** de confirmar (decisió de PO a la US-14). (P84)

**Resposta `200`:** `{ dailyLimit, remainingToday }`

| Camp | Tipus | Descripció |
|---|---|---|
| `dailyLimit` | integer | El límit diari d'enviament, en cèntims (`100000`). El frontend no el té escrit enlloc: el llegeix d'aquí. |
| `remainingToday` | integer | El que encara es pot enviar avui, en cèntims: `dailyLimit` menys el que s'ha enviat avui, i mai menys de `0`. |

- És una ruta protegida i no canvia res.
- `POST /api/transfers` torna a comprovar el límit: si entremig s'ha enviat alguna cosa més, respon `TRANSFER_LIMIT_EXCEEDED` igualment.
- A les 00:00 de Madrid torna a ser `remainingToday: 100000`.

```json
{
  "dailyLimit": 100000,
  "remainingToday": 98000
}
```

L'exemple és el de l'usuari 1 després de l'enviament de 13.4.

### 13.6 Efecte sobre altres rutes

Després d'un enviament:

- `GET /api/home` de qui envia: el `balance` baixa l'import, i el moviment surt el primer de `lastMovements`, «−20,00 €» en vermell. El de qui rep: el `balance` puja l'import i el seu moviment surt el primer, «+20,00 €» en verd. No hi ha cap avís dins de l'app: cada Inici torna a demanar `GET /api/home` en obrir-se.
- `GET /api/movements`, amb els filtres de [10.2](#102-filtres-de-get-apimovements) (`type=expense` per a qui envia, `type=income` per a qui rep, i `q` també troba el nom de la contrapart), el detall de [10.3](#103-get-apimovementsmovementid) i el justificant de [10.5](#105-justificant-pdf): els dos moviments funcionen com qualsevol altre.
- `totalSaved` no canvia.
- El límit diari de recàrrega no canvia ([13.5](#135-límit-diari-denviament)).

### 13.7 Avisos a la bústia simulada

US-14 demana un avís a qui envia i a qui rep. Com la resta de missatges, van a la bústia simulada ([8.12](#812-get-apidevoutbox)); dins de l'app no hi ha cap llista d'avisos. (P73)

| `type` | A qui | `text` (exemple de 13.4) |
|---|---|---|
| `transfer_sent` | Qui envia | «Has enviat 20,00 € a Usuari nou.» |
| `transfer_received` | Qui rep | «Usuari demo t'ha enviat 20,00 €: El sopar de divendres.» |

- El destinatari del missatge (`to`) és l'identificador de cada usuari, i el canal, `email` o `sms` segons si és un email o un telèfon, com a [8.12](#812-get-apidevoutbox).
- Els noms són els visibles (el `name` o `@username`). L'import s'escriu en euros amb el format de la pantalla (`1.000,00 €`).
- Sense concepte, el text de qui rep acaba a l'import: «Usuari demo t'ha enviat 20,00 €.».
- Aquests missatges no porten `code` ni `link`.

### 13.8 Errors

Els codis són a la taula de l'[apartat 5](#taula-de-codis). Els missatges són orientatius: el frontend decideix a partir del `code`.

| `code` | HTTP | Ruta | Quan |
|---|---|---|---|
| `VALIDATION_ERROR` | 422 | `GET /api/users` | `q` passa de 64 caràcters |
| `VALIDATION_ERROR` | 422 | `POST /api/transfers` | El cos està mal format o el concepte passa de 140 caràcters |
| `RECIPIENT_NOT_FOUND` | 404 | `GET /api/users/{userId}`, `POST /api/transfers` | L'usuari no existeix o està pendent de verificar |
| `SELF_TRANSFER` | 422 | `POST /api/transfers` | El destinatari és l'usuari de la sessió |
| `INVALID_AMOUNT` | 422 | `POST /api/transfers` | `amount ≤ 0` |
| `INSUFFICIENT_BALANCE` | 422 | `POST /api/transfers` | L'enviament supera el saldo de qui envia |
| `TRANSFER_LIMIT_EXCEEDED` | 422 | `POST /api/transfers` | Enviat avui + `amount` > `100000` |

Textos de les pantalles de US-13 i US-14, en vermell:

| `code` | Text |
|---|---|
| `VALIDATION_ERROR` | «Les dades no són vàlides. Revisa-les i torna-ho a provar.» (ja existeix) |
| `RECIPIENT_NOT_FOUND` | «No hem trobat aquest destinatari.» (nou) |
| `SELF_TRANSFER` | «No et pots enviar diners a tu mateix.» (nou) |
| `INSUFFICIENT_BALANCE` | «No tens prou saldo.» El mateix text a totes les pantalles, perquè el frontend tria el text pel `code` (P85). |
| `TRANSFER_LIMIT_EXCEEDED` | «Has superat el límit diari de 1.000,00 €. Avui encara pots enviar X €.», amb `details.remainingToday` (nou) |

### 13.9 Model intern

Aquest apartat és per al backend. El frontend no en depèn.

**`User`** guanya dos camps (US-13):

| Camp | Tipus | Notes |
|---|---|---|
| `username` | string | L'`@usuari`, únic i en minúscules, sense l'`@`. Només lletres `a`–`z`, xifres, `.`, `_` i `-`. |
| `phone` | string \| `None` | El telèfon normalitzat com a [8.3](#83-identificador-email-o-telèfon) (`+34611223302`). Qui es registra amb telèfon el té; qui es registra amb email, no (`None`), fins que es pugui editar al perfil. |

El `name` que ja existia és el nom visible; buit (`""`) vol dir que no en té, i l'API el dona com a `null`.

**`@usuari` dels usuaris nous** (decisió de PO: surt de la part local del correu, és únic i serà editable al perfil). (P74)

- Registre amb email: la part d'abans de l'`@`, en minúscules, sense els caràcters que no siguin `a`–`z`, `0`–`9`, `.`, `_` o `-`. `Anna.Puig+evolt@x.com` → `anna.puigevolt`.
- Si ja existeix, s'hi afegeix el primer número lliure a partir de `2`: `anna.puigevolt2`, `anna.puigevolt3`…
- Registre amb telèfon, o una part local que es queda buida: `usuari` seguit de l'id de l'usuari (`usuari9`). No es fa servir el telèfon, perquè l'`@usuari` és visible per a tothom.
- La forma `usuari` + xifres queda reservada per a aquest cas: una part local que ja la té hi afegeix `_` (`usuari9@x.com` → `usuari9_`), perquè no xoqui amb l'usuari 9. També és la que es mostra als usuaris creats abans de la T13.2, que no en tenen cap de desat.
- L'`@usuari` es decideix en el registre, encara que el compte quedi pendent: així no canvia en verificar.
- Editar-lo al perfil no és d'aquest sprint.

**Seed** (decisió de PO: als usuaris del seed se'ls assigna un àlies d'equip). Vuit usuaris actius, tots amb la contrasenya del seed ([8.13](#813-model-intern-de-laccés)). Els usuaris 3 a 8 tenen el compte principal a `0`, sense moviments ni guardioles. (P75)

| Id | `id` a l'API | Nom | Email | `username` | Telèfon |
|---|---|---|---|---|---|
| 1 | `usr-01` | Usuari demo | `demo@evolt.test` | `demo` | `+34611223307` |
| 2 | `usr-02` | Usuari nou | `buit@evolt.test` | `buit` | `+34611223308` |
| 3 | `usr-03` | Alicia | `alicia@evolt.test` | `aliciaa415` | `+34611223301` |
| 4 | `usr-04` | Huabin | `huabin@evolt.test` | `123huabin123` | `+34611223302` |
| 5 | `usr-05` | Izan | `izan@evolt.test` | `izanfarreny47` | `+34611223303` |
| 6 | `usr-06` | Jiajun | `jiajun@evolt.test` | `yayuuun` | `+34611223304` |
| 7 | `usr-07` | Junhao | `junhao@evolt.test` | `junhaozhang` | `+34611223305` |
| 8 | `usr-08` | Martí | `marti@evolt.test` | `sudo-itramplay` | `+34611223306` |

Els telèfons del seed són fictius i segueixen el mockup de US-13 (`611 22 33 02` és Huabin). L'email continua sent l'identificador per iniciar sessió; el telèfon només serveix per a la cerca.

**Enviaments:**

- `Movement.kind` ([apartat 6](#6-model-intern-no-exposat-a-lapi)) guanya dos valors: `"transfer_out"` al moviment de qui envia i `"transfer_in"` al de qui rep. El límit diari ([13.5](#135-límit-diari-denviament)) suma els `transfer_out` d'avui de l'usuari, **sense dependre del concepte**, que el pot escriure qui envia.
- Les sis escriptures d'un enviament van dins d'una **transacció** amb Firestore, i amb el mateix pany en memòria, com l'aportació ([9.8](#98-model-intern-de-lestalvi)). Es valida tot abans d'escriure; si una escriptura falla a mig camí, es desfan les anteriors.
- **Invariants:** el saldo de cada compte és la suma dels seus moviments; la suma dels saldos de tots els comptes no canvia amb un enviament.

**Amb Firestore:**

- `username` i `phone` són camps nous del document de `users`. Una col·lecció `usernames` (un document per `username`, que apunta a l'usuari) impedeix dos `@usuari` iguals encara que arribin dos registres alhora, com `user_identifiers` ([8.13](#813-model-intern-de-laccés)).
- La cerca llegeix els usuaris i filtra al backend. Amb les dades de la demo (pocs usuaris) és suficient; si l'app creix, caldria un índex de cerca.
