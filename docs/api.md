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
10. [Moviments: filtres, detall i informe (US-10 i US-11)](#10-moviments-filtres-detall-i-informe-us-10-i-us-11)

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
| `GET /api/movements/{movementId}` | `200` | US-11 · [10.3](#103-get-apimovementsmovementid) |
| `POST /api/movements/{movementId}/reports` | `201` | US-11 · [10.4](#104-post-apimovementsmovementidreports) |

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
| `limit` | integer | `20` | `1`–`50` **[PROPOSTA — pendent de validar]** |
| `dateFrom`, `dateTo`, `type`, `q` | — | Sense filtre | Filtres opcionals de US-10. Vegeu l'[apartat 10.2](#102-filtres-de-get-apimovements). |

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
| `VALIDATION_ERROR` | 422 | Paràmetres o cos mal formats: falta `amount`, no és un enter, `offset`/`limit` fora de rang, o filtres del llistat no vàlids (data mal formada, `type` desconegut o `dateFrom` posterior a `dateTo`, [10.2](#102-filtres-de-get-apimovements)) | — |
| `INTERNAL_ERROR` | 500 | Error inesperat, inclosos els que simula T08.2 | — |

> Qualsevol ruta o mètode no definit es tracta com a error inesperat i retorna `500 INTERNAL_ERROR` (mateix cos que `INTERNAL_ERROR`).

Codis dels moviments (Sprint 1, [apartat 10](#10-moviments-filtres-detall-i-informe-us-10-i-us-11)):

| `code` | HTTP | Quan | `details` |
|---|---|---|---|
| `MOVEMENT_NOT_FOUND` | 404 **[PROPOSTA — pendent de validar]** | El moviment no existeix o és d'un altre usuari | — |
| `INVALID_DESCRIPTION` | 422 **[PROPOSTA — pendent de validar]** | La descripció de l'informe és buida, només té espais o passa de 500 caràcters | — |

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

Propostes dels moviments (T10.1), per validar a la revisió de la PR de l'Sprint 1:

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
| P44 | [10.5](#105-justificant-pdf) | El justificant PDF es genera al navegador amb **jsPDF** (llicència MIT). S'ha de validar amb la Jiajun. |
| P45 | [10.7](#107-model-intern-dels-moviments) | Seed: els noms fictius de la contrapart de la taula de 10.7, i el moviment més recent de l'usuari 1 (`mov-30`) en estat `pending`. |

---

## 10. Moviments: filtres, detall i informe (US-10 i US-11)

Camps nous del moviment, filtres i cerca al llistat, detall d'un moviment, informe de problema i justificant. Tasca: T10.1 (issue #80).

| Tasca | Què implementa d'aquest apartat |
|---|---|
| T10.2 (backend) | [10.1](#101-camps-nous-de-movement) i el seed de [10.7](#107-model-intern-dels-moviments) |
| T10.3 (backend) | [10.2](#102-filtres-de-get-apimovements) |
| T11.1 (backend) | [10.3](#103-get-apimovementsmovementid) i [10.4](#104-post-apimovementsmovementidreports) |
| T10.4, T11.2, T11.3 (frontend) | Les pantalles que fan servir aquestes rutes, i el justificant de [10.5](#105-justificant-pdf) |

Totes les rutes d'aquest apartat resolen l'usuari igual que la resta ([apartat 2](#2-usuari-actual-i-estat-del-servei)): cada usuari només veu els seus moviments. Segueixen les convencions de l'[apartat 1](#1-convencions-generals).

Els exemples fan servir les dades de l'usuari 1 del seed, suposant que avui és el **3/11/2026**. Els ids són els del seed (`mov-01` és el més antic i `mov-30`, el més recent).

### 10.1 Camps nous de `Movement`

L'objecte `Movement` de l'[apartat 3](#3-objecte-movement) guanya tres camps. Com que l'objecte és el mateix a totes les respostes, els camps nous surten a la Home, al llistat, a la recàrrega, a l'aportació a una guardiola i al detall.

| Camp | Tipus | Notes |
|---|---|---|
| `counterparty` | string \| `null` | Qui paga o qui cobra (US-11). Mai és un text buit. **[PROPOSTA — pendent de validar]** el nom del camp, i que la clau sempre hi sigui amb `null` quan no n'hi ha. |
| `status` | `"completed"` \| `"pending"` | Llista tancada. La pantalla mostra «Completat» o «Pendent». |
| `reference` | string | Única entre tots els moviments i opaca: el frontend no l'ha d'interpretar. La genera el backend en crear el moviment, com l'`id`. Format `EVT-000031` **[PROPOSTA — pendent de validar]**. |

**Regla de `counterparty`** **[PROPOSTA — pendent de validar]**:

| Moviment | `counterparty` |
|---|---|
| Transferència o Bizum (`icon: "transfer"`) | El nom del contacte |
| Nòmina (`icon: "salary"`) | L'empresa que paga |
| Recàrrega i aportació a una guardiola | `null` |
| Compres, menjar, transport i altres pagaments | `null`: el concepte ja diu de què es tracta |

- L'alternativa, si es vol una contrapart a tots els pagaments, és posar-hi el nom del comerç. Caldria inventar un nom per a cada moviment del seed.
- Els noms són sempre inventats: cap dada personal real.

**Estat** **[PROPOSTA — pendent de validar]**:

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

Paràmetres de consulta nous (US-10), opcionals i combinables. Funcionen junt amb `offset` i `limit` ([4.2](#42-get-apimovements)). Noms **[PROPOSTA — pendent de validar]**:

| Paràmetre | Tipus | Què fa |
|---|---|---|
| `dateFrom` | string `YYYY-MM-DD` | Només moviments d'aquest dia o posteriors. |
| `dateTo` | string `YYYY-MM-DD` | Només moviments d'aquest dia o anteriors. |
| `type` | `"income"` \| `"expense"` | Només els moviments d'aquest tipus. Sense el paràmetre surten tots («Tots»). |
| `q` | string | Només els moviments que contenen aquest text al concepte o a la contrapart. |

**Regles:**

- **Dates:** dies naturals a `Europe/Madrid` ([apartat 1](#què-vol-dir-avui)), amb **els dos extrems inclosos**. El dia d'un moviment és el de la seva `date` a Madrid. Es pot fer servir només un dels dos extrems.
- **Text** **[PROPOSTA — pendent de validar]**:
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
- No hi ha cap ruta de PDF: el justificant es genera al navegador amb aquestes dades ([10.5](#105-justificant-pdf)).

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

**Resposta `201`:** `{ id, movementId, description, createdAt }` **[PROPOSTA — pendent de validar]**

| Camp | Tipus | Descripció |
|---|---|---|
| `id` | string | Identificador opac de l'informe. Format `rep-01`, `rep-02`… |
| `movementId` | string | El moviment al qual està vinculat. |
| `description` | string | La descripció desada, sense els espais dels extrems. |
| `createdAt` | string | Data ISO 8601 amb el desplaçament de Madrid. |

**Ordre de les validacions.** S'aturen al primer error **[PROPOSTA — pendent de validar]**:

1. Format del cos: falta `description` o no és un string → `VALIDATION_ERROR`.
2. El moviment no existeix o és d'un altre usuari → `MOVEMENT_NOT_FOUND`.
3. La descripció és buida, només té espais o passa de **500 caràcters** (un cop trets els espais dels extrems) → `INVALID_DESCRIPTION`.

**Regles:**

- Si hi ha un error, no es desa res.
- Es poden enviar diversos informes sobre el mateix moviment **[PROPOSTA — pendent de validar]**.
- L'informe es desa en memòria i **no s'envia enlloc**. `POST /api/dev/reset` l'esborra.
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

El justificant (US-11, criteri 2) es genera **al navegador** (T11.3), a partir de la resposta de [10.3](#103-get-apimovementsmovementid). El backend no té cap ruta de PDF.

- Llibreria: **jsPDF**, amb llicència MIT **[PROPOSTA — pendent de validar]**. S'ha de validar amb la Jiajun.
- El PDF porta les mateixes dades que la pantalla «Detall del moviment»: el concepte, l'import amb el signe, la data i l'hora, l'estat, la contrapart (o «—» si és `null`) i la referència. L'import i la referència han de coincidir exactament amb els del detall.

### 10.6 Errors

Els codis són a la taula de l'[apartat 5](#taula-de-codis). Els missatges són orientatius: el frontend decideix a partir del `code`.

| `code` | HTTP | Ruta | Quan |
|---|---|---|---|
| `VALIDATION_ERROR` | 422 | `GET /api/movements` | Filtres no vàlids ([10.2](#102-filtres-de-get-apimovements)) |
| `VALIDATION_ERROR` | 422 | `POST /api/movements/{movementId}/reports` | Falta `description` o no és un string |
| `MOVEMENT_NOT_FOUND` | 404 **[PROPOSTA — pendent de validar]** | Les de `/api/movements/{movementId}…` | El moviment no existeix o és d'un altre usuari |
| `INVALID_DESCRIPTION` | 422 **[PROPOSTA — pendent de validar]** | `POST /api/movements/{movementId}/reports` | La descripció és buida, només té espais o passa de 500 caràcters |

- El `404` segueix la P11 de l'accés (PR #105) i el `POT_NOT_FOUND` de l'estalvi (PR #119). Si la P11 no s'aprova, l'estat el decideix l'equip.
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
- **Seed** **[PROPOSTA — pendent de validar]**. Els 30 moviments de l'usuari 1 no canvien d'import, de data, de concepte ni d'ordre, perquè en depenen els tests i els mocks del frontend. Guanyen:
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
