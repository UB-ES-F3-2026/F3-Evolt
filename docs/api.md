# Contracte de l'API

Contracte compartit entre el backend (FastAPI) i el frontend per a les històries **US-07** (saldo a la pantalla principal), **US-08** (llistat de moviments) i **US-09** (recàrrega de prova) de l'Sprint 0, i **US-01 a US-04** (accés: registre, verificació, inici de sessió i recuperació de contrasenya) de l'Sprint 1.

- Tasques: T07.1 (issue #4) per a l'Sprint 0 i T01.1 (issue #56) per a l'[apartat 8](#8-accés-us-01-a-us-04).
- Qualsevol canvi en aquest contracte es fa amb una PR sobre aquest fitxer, revisada per almenys una persona de backend i una de frontend.
- Els punts marcats amb **[PROPOSTA — pendent de validar]** s'han de confirmar a la revisió. Hi ha la llista completa a l'[apartat 7](#7-punts-pendents-de-validar).

## Índex

1. [Convencions generals](#1-convencions-generals)
2. [Usuari actual i estat del servei](#2-usuari-actual-i-estat-del-servei)
3. [Objecte `Movement`](#3-objecte-movement)
4. [Endpoints](#4-endpoints)
5. [Errors](#5-errors)
6. [Model intern (no exposat a l'API)](#6-model-intern-no-exposat-a-lapi)
7. [Punts pendents de validar](#7-punts-pendents-de-validar)
8. [Accés (US-01 a US-04)](#8-accés-us-01-a-us-04)

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
- Precisió de segons, sense fraccions de segon. **[PROPOSTA — pendent de validar]**

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

Representa un moviment del compte principal. És el mateix objecte a `GET /api/home`, `GET /api/movements` i `POST /api/topups`.

| Camp | Tipus | Notes |
|---|---|---|
| `id` | string | Identificador opac. El frontend no l'ha d'interpretar. **[PROPOSTA — pendent de validar]** string, per no dependre de l'emmagatzematge. |
| `amount` | integer | Cèntims, sempre `> 0`. |
| `concept` | string | Text que es mostra a l'usuari. A les recàrregues val `"Recàrrega"`. |
| `date` | string | ISO 8601 amb desplaçament (vegeu l'[apartat 1](#dates)). |
| `type` | `"income"` \| `"expense"` | `income`: entren diners. `expense`: surten diners. |
| `icon` | string | Un dels valors de la llista tancada següent. |

Valors d'`icon` (llista tancada):

| Valor | Ús |
|---|---|
| `topup` | Recàrrega de prova |
| `salary` | Nòmina |
| `transfer` | Transferència |
| `shopping` | Compres |
| `food` | Menjar i restaurants |
| `transport` | Transport |
| `other` | Qualsevol altre moviment |

Exemple:

```json
{
  "id": "mov-20",
  "amount": 2350,
  "concept": "Restaurant La Plaça",
  "date": "2026-10-11T21:15:00+02:00",
  "type": "expense",
  "icon": "food"
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

A partir de la T03.1, `GET /api/home`, `GET /api/movements` i `POST /api/topups` són **rutes protegides**: necessiten una sessió ([apartat 8.2](#82-sessió)).

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
      "icon": "food"
    },
    {
      "id": "mov-19",
      "amount": 4590,
      "concept": "Supermercat",
      "date": "2026-10-10T18:42:00+02:00",
      "type": "expense",
      "icon": "shopping"
    },
    {
      "id": "mov-18",
      "amount": 1200,
      "concept": "Bitllet de tren",
      "date": "2026-10-09T08:05:00+02:00",
      "type": "expense",
      "icon": "transport"
    },
    {
      "id": "mov-17",
      "amount": 180000,
      "concept": "Nòmina d'octubre",
      "date": "2026-10-01T09:00:00+02:00",
      "type": "income",
      "icon": "salary"
    },
    {
      "id": "mov-16",
      "amount": 5000,
      "concept": "Transferència rebuda",
      "date": "2026-09-28T13:20:00+02:00",
      "type": "income",
      "icon": "transfer"
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
| `limit` | integer | `20` | `1`–`50` **[PROPOSTA — pendent de validar]** |

- Un `offset` negatiu, un `limit` fora de rang o un valor que no sigui enter retorna `422 VALIDATION_ERROR`.
- Un `offset` igual o més gran que el nombre total de moviments **no** és un error: retorna `200` amb `items: []` i `nextOffset: null`. **[PROPOSTA — pendent de validar]**

**Resposta `200`:** `{ items, nextOffset }`

| Camp | Tipus | Descripció |
|---|---|---|
| `items` | `Movement[]` | Com a màxim `limit` moviments, del més recent al més antic. |
| `nextOffset` | integer \| `null` | `offset + items.length` si encara queden moviments després d'aquesta pàgina. `null` si s'ha arribat al final. |

- El frontend continua demanant pàgines amb `offset = nextOffset` fins que rep `null`.
- Ordre: per `date` descendent. Si dos moviments tenen la mateixa `date`, va primer el que s'ha creat més tard, perquè l'ordre sigui estable entre pàgines. **[PROPOSTA — pendent de validar]**

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
      "icon": "food"
    },
    {
      "id": "mov-19",
      "amount": 4590,
      "concept": "Supermercat",
      "date": "2026-10-10T18:42:00+02:00",
      "type": "expense",
      "icon": "shopping"
    },
    {
      "id": "mov-18",
      "amount": 1200,
      "concept": "Bitllet de tren",
      "date": "2026-10-09T08:05:00+02:00",
      "type": "expense",
      "icon": "transport"
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
      "icon": "shopping"
    },
    {
      "id": "mov-01",
      "amount": 100000,
      "concept": "Ingrés inicial",
      "date": "2026-09-01T10:00:00+02:00",
      "type": "income",
      "icon": "other"
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

`amount` ha de ser un **enter JSON**. Valors com `"500"` (string) o `500.5` (decimal) retornen `422 VALIDATION_ERROR`. També `500.0` es considera no vàlid. **[PROPOSTA — pendent de validar]**

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
    "icon": "topup"
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

> **Sprint 1.** Si s'aprova la P20 i es fusiona la tasca de persistència (#106), les dades passen a Firestore ([apartat 8.13](#813-model-intern-de-laccés)) i aquest endpoint esborrarà les col·leccions i hi tornarà a escriure el seed. Llavors només es podrà fer servir amb l'**emulador de Firebase** o el projecte de desenvolupament, **mai** amb les dades del desplegament.

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
| `details` | object | **Opcional.** Dades addicionals de l'error. Quan un error no en té, la clau `details` no apareix a la resposta. **[PROPOSTA — pendent de validar]** |

> El frontend decideix què fa a partir del **`code`** (i de `details`), **mai** a partir del text de `message`. Els textos de `message` d'aquest document són orientatius i el backend els pot ajustar sense trencar el contracte.

### Taula de codis

| `code` | HTTP | Quan | `details` |
|---|---|---|---|
| `INVALID_AMOUNT` | 422 | `amount ≤ 0` | — |
| `AMOUNT_OVER_LIMIT` | 422 | `amount > 50000` | — |
| `DAILY_LIMIT_EXCEEDED` | 422 | Recàrregues d'avui + `amount > 100000` | `{ remainingToday }` (cèntims) |
| `VALIDATION_ERROR` | 422 | Paràmetres o cos mal formats: falta `amount`, no és un enter, o `offset`/`limit` fora de rang | — |
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

> Fins a l'Sprint 0 tots els errors eren `422` o `500`. Els codis d'accés fan servir també `401`, `403`, `409`, `423` i `429`, i els recursos que no existeixen (p. ex. una guardiola) faran servir `404` **[PROPOSTA — pendent de validar]**. El frontend continua decidint només amb el `code`: l'`apiClient` ja propaga qualsevol cos d'error del contracte, sigui quin sigui l'estat HTTP.

> Qualsevol ruta o mètode no definit es tracta com a error inesperat i retorna `500 INTERNAL_ERROR` (mateix cos que `INTERNAL_ERROR`).

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

### Seed

- El seed (T07.3) **no pot tenir cap recàrrega amb data d'avui**. Si en tingués, el límit diari no començaria a zero i les proves i la demo de US-09 no serien reproduïbles.
- A partir de la T01.2, els dos usuaris del seed tenen credencials fictícies per poder iniciar sessió ([apartat 8.13](#813-model-intern-de-laccés)).

---

## 7. Punts pendents de validar

Propostes d'aquest contracte que s'han de confirmar a la revisió de la PR:

| # | Apartat | Proposta |
|---|---|---|
| P1 | [3](#3-objecte-movement) | `Movement.id` és un string opac, per no dependre de l'emmagatzematge. |
| P2 | [4.2](#42-get-apimovements) | El rang vàlid de `limit` és `1`–`50`. |
| P3 | [4.2](#42-get-apimovements) | Un `offset` més gran o igual que el total retorna `200` amb `items: []` i `nextOffset: null`, no un error. |
| P4 | [4.2](#42-get-apimovements) | Si dues `date` coincideixen, va primer el moviment creat més tard. |
| P5 | [4.3](#43-post-apitopups) | `amount` ha de ser un enter JSON estricte: `"500"`, `500.5` i `500.0` retornen `VALIDATION_ERROR`. |
| P6 | [5](#5-errors) | Quan un error no té `details`, la clau no apareix a la resposta (en lloc de `"details": null`). |
| P7 | [1](#dates) | Les dates es donen amb precisió de segons, sense fraccions de segon. |

Propostes de l'accés (T01.1), per validar a la revisió de la PR de l'Sprint 1:

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
| P20 | [8.13](#813-model-intern-de-laccés) | Les dades es guarden a Cloud Firestore amb l'Admin SDK des del backend. El login és propi (no Firebase Auth) i el frontend no parla amb Firebase. |
| P34 | [8.12](#812-get-apidevoutbox) | La bústia simulada es pot activar al desplegament amb `ENABLE_DEV_OUTBOX`, independent d'`ENABLE_DEV_ROUTES`, però protegida amb la clau `DEV_OUTBOX_KEY` (capçalera `X-Dev-Key`). El número salta a P34 perquè P21–P33 són del contracte de guardioles (§9). |

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
| `ALLOW_X_USER_ID` | `1` fins a la T03.5; `0` després | Accepta la capçalera `X-User-Id` quan no hi ha token. | [8.2](#transició-des-dx-user-id) |
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
- Les sessions es guarden **en memòria**: reiniciar el backend o cridar `POST /api/dev/reset` les tanca totes. Si s'aprova la P20 i es fusiona la tasca de persistència (#106), passaran a Firestore ([8.13](#813-model-intern-de-laccés)) i sobreviuran als reinicis; `POST /api/dev/reset` les continuarà tancant.
- Com guarda el token el frontend i si també té un temporitzador propi d'inactivitat ho decideix la T03.3. La referència sempre és la resposta del backend.

#### Transició des d'`X-User-Id`

Perquè la resta de blocs (guardioles, filtres, detall) no quedin bloquejats mentre es fa el login, `X-User-Id` es manté darrere de la variable d'entorn **`ALLOW_X_USER_ID`** (`1` activada, `0` desactivada). **[PROPOSTA — pendent de validar]**

El backend resol l'usuari de cada ruta protegida en aquest ordre:

1. Si hi ha `Authorization: Bearer <token>`, fa servir el token, i els seus errors (`UNAUTHENTICATED`, `SESSION_EXPIRED`). `X-User-Id` s'ignora.
2. Si no hi ha token i `ALLOW_X_USER_ID=1`, aplica les regles de l'[apartat 2](#capçalera-x-user-id): sense capçalera, usuari 1.
3. Si no hi ha token i `ALLOW_X_USER_ID=0` → `401 UNAUTHENTICATED`.

| Moment | Valor per defecte d'`ALLOW_X_USER_ID` |
|---|---|
| Des de la T03.1 fins a la T03.5 | `1`: el frontend actual continua funcionant sense login. |
| Des de la T03.5 | `0`: el frontend ja no envia `X-User-Id`. Els tests de pytest que la fan servir activen la variable. |

El CORS ha d'acceptar la capçalera `Authorization` (T03.1).

### 8.3 Identificador (email o telèfon)

Les rutes d'accés reben un sol camp, **`identifier`**, que pot ser un email o un telèfon. Abans de comparar-lo o desar-lo, el backend el **normalitza**:

| Tipus | Com es reconeix | Normalització | Vàlid si | Exemple |
|---|---|---|---|---|
| Email | Conté `@` | Treu els espais del principi i del final i el passa a minúscules. | Té exactament una `@`, alguna cosa abans, i un domini amb almenys un punt, sense espais. | `" Ana@X.com "` → `"ana@x.com"` |
| Telèfon | No conté `@` | Treu espais, `-`, `.`, `(` i `)`. Un `00` inicial passa a ser `+`. Un número de 9 xifres sense prefix rep `+34`. | És `+` seguit de 8 a 15 xifres, i la primera no és `0`. | `"612 34 56 78"` → `"+34612345678"` |

- Un `identifier` que no és vàlid retorna `422 VALIDATION_ERROR`, excepte al login, que respon `INVALID_CREDENTIALS` per no dir quina casella falla ([8.8](#88-post-apiauthlogin)).
- Les respostes que retornen l'`identifier` el donen **normalitzat**.
- Els missatges a un email surten pel canal `email` de la bústia simulada; els d'un telèfon, pel canal `sms` ([8.12](#812-get-apidevoutbox)).

### 8.4 Política de contrasenya

- **Mínim 8 caràcters, almenys una lletra majúscula i almenys un número** (`0`–`9`). Qualsevol majúscula compta, també les accentuades (`À`, `É`...).
- És la mateixa regla al registre (US-01) i a la contrasenya nova (US-04). El backend la defineix en **un sol lloc** (T01.2) i la reutilitza la T04.1.
- Si no la compleix → `422 WEAK_PASSWORD`.
- Una contrasenya de més de 72 bytes en UTF-8 → `422 VALIDATION_ERROR`, perquè bcrypt no en fa servir més. **[PROPOSTA — pendent de validar]**
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

- Es crea l'usuari en estat `pending`, amb el seu compte principal amb saldo `0`, sense moviments ni guardioles i amb XP `0`. **[PROPOSTA — pendent de validar]**
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

Comprova el codi de 6 xifres, activa el compte i **obre la sessió** (US-02). **[PROPOSTA — pendent de validar]**

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
- Si hi ha un compte **pendent** amb aquest `identifier`: es genera un codi nou, l'anterior **deixa de servir**, el comptador d'intents torna a zero i els 10 minuts tornen a començar. **[PROPOSTA — pendent de validar]**
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
5. La contrasenya és correcta però el compte és pendent → `403 ACCOUNT_NOT_VERIFIED` **[PROPOSTA — pendent de validar]**. El comptador d'errors torna a zero. El frontend pot portar l'usuari a «Verifica el teu compte» i demanar un codi nou ([8.7](#87-post-apiauthresend-code)).
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
- Respon `200` **sempre**, també sense capçalera o amb un token ja caducat o tancat: l'usuari vol sortir i no té sentit mostrar-li un error. **[PROPOSTA — pendent de validar]**
- La resposta porta cos JSON (no `204`), perquè l'`apiClient` del frontend espera JSON a totes les respostes.

### 8.10 `POST /api/auth/forgot-password`

Demana un enllaç per canviar la contrasenya («He oblidat la contrasenya», US-04).

**Cos de la petició:** `{ identifier }`

- Accepta email **o** telèfon. **[PROPOSTA — pendent de validar]** La US-04 parla d'email, però així qui s'ha registrat amb telèfon també pot recuperar el compte, i l'enllaç li arriba per SMS.
- `identifier` mal format → `VALIDATION_ERROR`.
- **Resposta `200`:** `{ status }`, amb `status` sempre `"ok"`, **existeixi o no el compte**. El frontend mostra sempre «Si l'email és correcte, rebràs un enllaç per canviar la contrasenya».
- Si el compte existeix (pendent, actiu o bloquejat): es genera un enllaç d'**un sol ús** que caduca als 30 minuts, l'enllaç anterior **deixa de servir** **[PROPOSTA — pendent de validar]** i es deixa a la bústia simulada.
- L'enllaç és `<FRONTEND_URL>/nova-contrasenya?token=<token>`. `FRONTEND_URL` és una variable d'entorn ([8.1](#variables-dentorn-de-laccés)): en local val `http://localhost:5173` i a Render, l'URL del frontend desplegat. La T04.2 crea aquesta ruta del frontend, que llegeix el `token` de l'URL. **[PROPOSTA — pendent de validar]**

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
- El compte es desbloqueja i el comptador d'errors de login torna a zero. **[PROPOSTA — pendent de validar]**
- L'estat del compte (pendent o actiu) no canvia.

### 8.12 `GET /api/dev/outbox`

Bústia simulada: eina de **desenvolupament**, com `POST /api/dev/reset`. En lloc d'enviar emails o SMS de veritat, el backend desa aquí els missatges. **No l'usa l'app**: serveix per llegir el codi o l'enllaç a les proves manuals, a la demo i als tests.

**Disponibilitat i protecció** **[PROPOSTA — pendent de validar]**:

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

Textos dels altres dos tipus:

- `account_locked`: «Hem bloquejat el teu compte d'Evolt durant 15 minuts després de 5 intents fallits. Si no has estat tu, canvia la contrasenya.»
- `password_reset`: «Per canviar la contrasenya d'Evolt, obre aquest enllaç. Caduca en 30 minuts: <enllaç>»

`POST /api/dev/reset` buida la bústia.

### 8.13 Model intern de l'accés

Aquest apartat és per al backend. El frontend no en depèn.

**Emmagatzematge.** Si s'aprova la P20, les dades passen de la memòria a **Cloud Firestore** amb la tasca de persistència (#106) **[PROPOSTA — pendent de validar]**:

- Només el backend parla amb Firestore, amb l'Admin SDK de Python (`firebase-admin`). El frontend **no** usa Firebase: continua cridant només aquesta API.
- El login el fa el nostre backend tal com descriu aquest apartat. **No** es fa servir Firebase Auth.
- Les credencials del compte de servei es llegeixen d'una variable d'entorn i **mai** es pugen al repositori.
- En local i als tests s'usa l'**emulador de Firestore** o els repositoris en memòria; una variable d'entorn tria quin. Els serveis no canvien: només canvien els repositoris.
- Mentre no estigui fusionada la tasca de persistència, les dades d'aquest apartat viuen en memòria com a l'Sprint 0. El contracte de les rutes és el mateix en tots dos casos.

| Col·lecció | Contingut |
|---|---|
| `users`, `accounts`, `pots`, `movements` | Les dades de l'Sprint 0 (seed, saldos, moviments). |
| `sessions`, `verification_codes`, `password_reset_tokens` | Les dades de l'accés (taula següent). |
| `outbox` | La bústia simulada ([8.12](#812-get-apidevoutbox)). |

Les dates es desen com a `Timestamp` de Firestore (UTC) i el backend les converteix a `Europe/Madrid` en llegir-les, de manera que l'API continua donant-les com a l'[apartat 1](#dates). La recàrrega (`POST /api/topups`) es fa dins d'una **transacció** de Firestore, perquè la comprovació del límit diari, el moviment nou i el saldo nou siguin tot o res.

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

**Credencials del seed** **[PROPOSTA — pendent de validar]**. Són fictícies i serveixen per a la demo i les proves:

| Usuari | `identifier` | Contrasenya | Estat |
|---|---|---|---|
| 1 (compte amb moviments) | `demo@evolt.test` | `Evolt2026` | `active` |
| 2 (compte buit) | `buit@evolt.test` | `Evolt2026` | `active` |

El domini `.test` està reservat i no pot arribar a cap bústia real. Els mocks del frontend han de fer servir les mateixes credencials.

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
