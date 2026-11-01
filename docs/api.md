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
9. [Guardioles (US-17 i US-18)](#9-guardioles-us-17-i-us-18)

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

Representa un moviment del compte principal. És el mateix objecte a `GET /api/home`, `GET /api/movements`, `POST /api/topups` i `POST /api/pots/{potId}/contributions` ([apartat 9.4](#94-post-apipotspotidcontributions)).

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
| `savings` | Aportació a una guardiola ([apartat 9.4](#94-post-apipotspotidcontributions)) **[PROPOSTA — pendent de validar]** |
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
| `GET /api/pots` | `200` | US-17 · [9.2](#92-get-apipots) |
| `POST /api/pots` | `201` | US-17 · [9.3](#93-post-apipots) |
| `POST /api/pots/{potId}/contributions` | `201` | US-18 · [9.4](#94-post-apipotspotidcontributions) |
| `GET /api/pots/{potId}/movements` | `200` | US-18 · [9.5](#95-get-apipotspotidmovements) |

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
| `INVALID_AMOUNT` | 422 | `amount ≤ 0`, a una recàrrega o a una aportació a una guardiola ([9.4](#94-post-apipotspotidcontributions)) | — |
| `AMOUNT_OVER_LIMIT` | 422 | `amount > 50000` | — |
| `DAILY_LIMIT_EXCEEDED` | 422 | Recàrregues d'avui + `amount > 100000` | `{ remainingToday }` (cèntims) |
| `VALIDATION_ERROR` | 422 | Paràmetres o cos mal formats: falta `amount`, no és un enter, o `offset`/`limit` fora de rang | — |
| `INTERNAL_ERROR` | 500 | Error inesperat, inclosos els que simula T08.2 | — |

> Qualsevol ruta o mètode no definit es tracta com a error inesperat i retorna `500 INTERNAL_ERROR` (mateix cos que `INTERNAL_ERROR`).

Codis de l'estalvi (Sprint 1, [apartat 9](#9-guardioles-us-17-i-us-18)):

| `code` | HTTP | Quan | `details` |
|---|---|---|---|
| `INVALID_POT_NAME` | 422 | El nom de la guardiola és buit o només té espais | — |
| `INVALID_TARGET` | 422 | L'objectiu de la guardiola és `≤ 0` | — |
| `INSUFFICIENT_BALANCE` | 422 | L'aportació supera el saldo del compte principal | — |
| `POT_NOT_FOUND` | 404 **[PROPOSTA — pendent de validar]** | La guardiola no existeix o és d'un altre usuari | — |

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

Propostes de l'estalvi (T17.1), per validar a la revisió de la PR de l'Sprint 1:

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
| P29 | [3](#3-objecte-movement), [9.4](#94-post-apipotspotidcontributions) | El moviment del compte principal d'una aportació té el concepte `"Aportació a <nom de la guardiola>"` i la icona nova `savings`. L'alternativa a la icona nova és `transfer`. |
| P30 | [9.4](#94-post-apipotspotidcontributions) | Es pot aportar a una guardiola que ja ha arribat a l'objectiu. Dues aportacions alhora s'apliquen una darrere l'altra. |
| P31 | [9.5](#95-get-apipotspotidmovements) | L'historial respon `{ items }`, del més recent al més antic i sense paginació. Cada entrada té `id` (`pmov-01`, `pmov-02`…), `amount`, `concept`, `date` i `type`. |
| P32 | [9.8](#98-model-intern-de-lestalvi) | Cada guardiola del seed té una entrada inicial «Saldo inicial» pel seu saldo, i el seed dona un color a cada guardiola i un objectiu a dues. |
| P33 | [9.7](#97-errors) | `POT_NOT_FOUND` respon `404`, seguint la P11 de l'accés. Si la P11 no s'aprova, l'estat el decideix l'equip. |

---

## 9. Guardioles (US-17 i US-18)

Crear guardioles, llistar-les, aportar-hi diners del compte principal i consultar-ne l'historial. Tasca: T17.1 (issue #71).

| Tasca | Què implementa d'aquest apartat |
|---|---|
| T17.2 (backend) | [9.1](#91-objecte-pot), [9.2](#92-get-apipots), [9.3](#93-post-apipots) i les guardioles del seed de [9.8](#98-model-intern-de-lestalvi) |
| T18.1 (backend) | [9.4](#94-post-apipotspotidcontributions), [9.5](#95-get-apipotspotidmovements), [9.6](#96-efecte-sobre-altres-rutes) i l'historial de [9.8](#98-model-intern-de-lestalvi) |
| T17.3, T17.4, T18.2, T18.4 (frontend) | Les pantalles que criden aquestes rutes |

Totes les rutes d'aquest apartat resolen l'usuari igual que la resta ([apartat 2](#2-usuari-actual-i-estat-del-servei)): cada usuari només veu i modifica les seves guardioles. Segueixen les convencions de l'[apartat 1](#1-convencions-generals): imports en cèntims enters, dates ISO 8601 amb el desplaçament de Madrid i claus en camelCase.

Els exemples d'aquest apartat fan servir les dades de l'usuari 1 del seed: compte principal amb `379521` (3.795,21 €) i tres guardioles que sumen `30000` (300,00 €). Les dates d'exemple són del 3/11/2026 (`+01:00`, horari d'hivern).

### 9.1 Objecte `Pot`

Una guardiola de l'usuari. És el mateix objecte a totes les respostes d'aquest apartat.

| Camp | Tipus | Notes |
|---|---|---|
| `id` | string | Identificador opac, com `Movement.id` (P1). El frontend no l'ha d'interpretar. Format `pot-01`, `pot-02`… **[PROPOSTA — pendent de validar]** |
| `name` | string | Mai buit: té almenys un caràcter que no és un espai. |
| `balance` | integer | Cèntims, `≥ 0`. Una guardiola nova té `0`. |
| `target` | integer \| `null` | Objectiu en cèntims, `> 0`. Val `null` si la guardiola no en té, perquè és opcional. |
| `color` | string | Un dels valors de la llista tancada següent. |

Valors de `color` (llista tancada) **[PROPOSTA — pendent de validar]**:

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

**Resposta `200`:** `{ items }` **[PROPOSTA — pendent de validar]**

| Camp | Tipus | Descripció |
|---|---|---|
| `items` | `Pot[]` | Totes les guardioles de l'usuari, en ordre de creació, de la més antiga a la més nova **[PROPOSTA — pendent de validar]**. Pot ser una llista buida. |

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
| `name` | string | Obligatori. Es desa sense els espais del principi i del final **[PROPOSTA — pendent de validar]**. |
| `target` | integer \| `null` | Opcional. Objectiu en cèntims. Si no s'envia, o val `null`, la guardiola no té objectiu. |
| `color` | string | Opcional. Un dels valors de [9.1](#91-objecte-pot). Si no s'envia, o val `null`, és `purple`. |

**Resposta `201`:** l'objecte `Pot` creat, sol **[PROPOSTA — pendent de validar]**.

- La guardiola neix amb `balance: 0`.
- Es retorna l'objecte sol perquè només hi ha una cosa a retornar, i és exactament el mateix objecte que surt a `GET /api/pots`. La recàrrega i l'aportació retornen un objecte amb diverses claus perquè canvien més d'una cosa (el saldo i el moviment).

**Ordre de les validacions.** S'aturen al primer error **[PROPOSTA — pendent de validar]**:

1. Format del cos → `VALIDATION_ERROR`:
   - falta `name` o no és un string;
   - `target` no és un enter JSON estricte, com a P5 (`"300"`, `300.5` i `300.0` no valen);
   - `color` no és de la llista tancada.
2. `name` buit o només amb espais → `INVALID_POT_NAME`.
3. `target ≤ 0` → `INVALID_TARGET`.

**Regles:**

- Si hi ha un error, no es crea res.
- No hi ha límit de guardioles (assumpte de US-17).
- Es poden repetir noms **[PROPOSTA — pendent de validar]**.
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

**Resposta `201`:** `{ balance, pot, movement }` **[PROPOSTA — pendent de validar]**

| Camp | Tipus | Descripció |
|---|---|---|
| `balance` | integer | Saldo **nou** del compte principal, en cèntims. |
| `pot` | `Pot` | La guardiola amb el saldo nou. |
| `movement` | `Movement` | El moviment que s'ha creat al compte principal. |

Amb aquesta resposta, el frontend pot pintar el tic verd «Has aportat X € a <nom>» i actualitzar els dos saldos sense tornar a demanar res.

**Ordre de les validacions.** S'aturen al primer error **[PROPOSTA — pendent de validar]**:

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
  - `concept: "Aportació a <nom de la guardiola>"`, p. ex. `"Aportació a Vacances"` **[PROPOSTA — pendent de validar]**;
  - `icon: "savings"`, un valor nou de la llista de l'[apartat 3](#3-objecte-movement) **[PROPOSTA — pendent de validar]**. Si el frontend rep una icona que no coneix, ja mostra `other` (`frontend/src/models/movement.ts`), així que la icona nova no trenca res. Per mostrar-la, però, s'ha d'afegir al frontend. L'alternativa és fer servir `transfer`;
  - `date`: el moment de l'aportació;
  - `kind` intern `"other"`, perquè no compti per al límit diari de recàrrega.
- **Casos límit** **[PROPOSTA — pendent de validar]**:
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
    "icon": "savings"
  }
}
```

### 9.5 `GET /api/pots/{potId}/movements`

L'historial d'una guardiola (US-18, criteri 6).

**Resposta `200`:** `{ items }` **[PROPOSTA — pendent de validar]**

| Camp | Tipus | Descripció |
|---|---|---|
| `items` | Entrada[] | Les entrades de l'historial, de la més recent a la més antiga, sense paginació. |

Cada entrada de l'historial **[PROPOSTA — pendent de validar]**:

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
| `POT_NOT_FOUND` | 404 **[PROPOSTA — pendent de validar]** | Les de `/api/pots/{potId}/…` | La guardiola no existeix o és d'un altre usuari |
| `INVALID_AMOUNT` | 422 | `POST /api/pots/{potId}/contributions` | `amount ≤ 0` |
| `INSUFFICIENT_BALANCE` | 422 | `POST /api/pots/{potId}/contributions` | L'aportació supera el saldo del compte principal |

- El `404` segueix la P11 de l'accés (PR #105), que ja proposa estats diferents de `422` i `500`. Si la P11 no s'aprova, l'estat el decideix l'equip.
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
  "message": "No tens prou saldo per fer aquesta aportació."
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
- **Seed** **[PROPOSTA — pendent de validar]**. Les tres guardioles de l'usuari 1 no canvien de nom ni de saldo, perquè en depenen els tests i els mocks del frontend. Guanyen:

  | `id` | `name` | `balance` | `target` | `color` | Entrada inicial de l'historial |
  |---|---|---|---|---|---|
  | `pot-01` | Vacances | `15000` | `100000` | `blue` | `pmov-01`, «Saldo inicial», `15000` |
  | `pot-02` | Emergències | `10000` | `null` | `orange` | `pmov-02`, «Saldo inicial», `10000` |
  | `pot-03` | Regal d'aniversari | `5000` | `8000` | `pink` | `pmov-03`, «Saldo inicial», `5000` |

  - Les entrades inicials tenen una data anterior a avui, com la resta del seed.
  - Les guardioles i les entrades noves continuen la numeració (`pot-04`, `pmov-04`…). Els comptadors es reinicien amb el seed (`POST /api/dev/reset`).
  - L'usuari 2 continua sense guardioles.
