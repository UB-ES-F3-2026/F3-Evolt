# Contracte de l'API · Sprint 0

Contracte compartit entre el backend (FastAPI) i el frontend per a les històries **US-07** (saldo a la pantalla principal), **US-08** (llistat de moviments) i **US-09** (recàrrega de prova).

- Tasca: T07.1 (issue #4).
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

Només existeix si la variable d'entorn `ENABLE_DEV_ROUTES` no és `false` (per defecte, sí). Al desplegament (TR06.1) està desactivada: la ruta no es registra i respon com qualsevol ruta inexistent, `500 INTERNAL_ERROR` (§5).

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
