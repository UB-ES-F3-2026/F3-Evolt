# Context compartit · especificacions de les 8 US del Sprint 2

> Document intern de treball. És el **context comú** que han de fer servir els vuit documents `docs/us/US-XX.md` del Sprint 2 (US-19, US-20, US-15, US-13, US-14, US-25, US-26, US-27), perquè cap escriptor hagi de tornar a buscar el mateix. Tot allò que no existeix encara al repositori es marca **`a crear`**; les decisions noves del PO es marquen **[PROPOSTA — pendent de validar]**. Fets verificats directament als fitxers del repo (branca `docs/us-sprint2`).

---

## 1. Les 8 US del Sprint 2

| US | Títol | Bloc | Punts | Hores | Tasques (ids) |
|---|---|---|---|---|---|
| US-19 | Retirar diners d'una guardiola | Estalvi | 3 | 9 | T19.1–T19.4 |
| US-20 | Veure progrés i objectiu assolit | Estalvi | 3 | 7 | T20.1–T20.3 |
| US-15 | Sol·licitar diners | Estalvi | 3 | 9 | T15.1–T15.4 |
| US-13 | Cercar un usuari | Pagaments | 2 | 9 | T13.1–T13.4 |
| US-14 | Enviar diners a usuaris | Pagaments | 5 | 15 | T14.1–T14.5 |
| US-25 | Afegir subcompte en divisa | Multidivisa | 4 | 12 | T25.1–T25.4 |
| US-26 | Eliminar subcompte en divisa | Multidivisa | 2 | 4 | T26.1–T26.3 |
| US-27 | Canviar entre divises | Multidivisa | 5 | 10 | T27.1–T27.3 |

**Totals per bloc** (tasca «Tasques del Sprint 2 · F3-Evolt»; 31 tasques en total, 90 h disponibles per a 6 persones × 15 h):

| Bloc | Històries | Punts | Hores | Hores disponibles |
|---|---|---|---|---|
| Estalvi | US-19, US-20 i US-15 | 9 | 25 | 30 (15 h × 2) |
| Pagaments | US-13 i US-14 | 7 | 24 | 30 (15 h × 2) |
| Multidivisa | US-25, US-26 i US-27 | 11 | 26 | 30 (15 h × 2) |
| Pendent del Sprint 1 | TR06.3 (desplegament automàtic, #144) | — | 1 | — |
| **Total** | **8 històries** | **27** | **76** | **90** |

Fases de les tasques: **E** contracte, **G** construir, **I** integrar, **R** revisar (les de revisió són sempre L0). Els punts són els del backlog; els del poker poden ser diferents.

**Nota crítica per a la US-15:** sense la US-16 (que **no** entra al sprint), una sol·licitud només pot quedar **Pendent**, **Caducada** o **Cancel·lada**. Els estats «Pagada» i «Rebutjada» arribaran amb la US-16; els documents de la US-15 han de reflectir-ho (els criteris del Trello els mencionen, però aquest sprint no s'implementen).

---

## 2. Value statements literals (COM/VULL/PER) per US

Tots vuit existeixen a [`docs/P1/trello-backlog.md`](../P1/trello-backlog.md); són **literals**, sense cap retoc (els documents han de copiar-los tal qual, indicant-ne les línies). Per a US-19 i US-20 hi ha a més la versió llarga «Com a… vull… per tal de…» a [`docs/P1/backlog.md`](../P1/backlog.md). **Cap de les vuit necessita un `[proposat]`: totes tenen el value statement al Trello.**

### US-19 · Retirar diners d'una guardiola

De `docs/P1/trello-backlog.md`, línies 496–498 (font: `trello-backlog.md`):

```
COM: client estàndard amb guardioles
VULL: retirar diners d'una guardiola al saldo principal
PER: fer servir els diners estalviats quan els necessiti.
```

Versió llarga de `docs/P1/backlog.md`, l.187–191 (font: `backlog.md`):

> Com a **usuari amb guardioles**, vull **retirar un import d'una guardiola al meu saldo principal**, per tal de **fer servir els diners estalviats quan els necessiti sense perdre el control de les metes**.

**Labels:** Fina, Alta, Estalvi, P2 · **Estimació:** SP 3 · VP 6 · Prioritat Alta (font: `trello-backlog.md`, l.491 i 508).

### US-20 · Veure progrés i objectiu assolit

De `docs/P1/trello-backlog.md`, línies 533–535 (font: `trello-backlog.md`):

```
COM: client estàndard amb guardioles amb objectiu
VULL: veure el progrés cap a cada objectiu i saber quan l'he assolit
PER: mantenir la motivació d'estalviar i celebrar les metes.
```

Versió llarga de `docs/P1/backlog.md`, l.255–259 (font: `backlog.md`):

> Com a **usuari amb guardioles amb objectiu**, vull **veure el progrés cap a cada objectiu i saber quan l'he assolit**, per tal de **mantenir la motivació d'estalviar i celebrar les metes**.

**Labels:** Fina, Alta, Estalvi, P2 · **Estimació:** SP 3 · VP 5 · Prioritat Alta (font: `trello-backlog.md`, l.528 i 545).

### US-13 · Cercar un usuari

De `docs/P1/trello-backlog.md`, línies 775–777 (font: `trello-backlog.md`):

```
COM: client estàndard
VULL: trobar altres usuaris de l'app
PER: poder enviar-los diners.
```

**Labels:** Fina, Alta, Social, P5 · **Estimació:** SP 2 · VP 6 · Prioritat Alta (font: `trello-backlog.md`, l.770 i 786).

### US-15 · Sol·licitar diners

De `docs/P1/trello-backlog.md`, línies 806–808 (font: `trello-backlog.md`):

```
COM: client estàndard
VULL: demanar diners a un contacte
PER: que em torni el que em deu.
```

**Labels:** Mitjana, Social, P5 · **Estimació:** SP 3 · VP 6 · Prioritat Mitjana (font: `trello-backlog.md`, l.801 i 816). *Vegeu la nota dels estats a la secció 1.*

### US-14 · Enviar diners a usuaris

De `docs/P1/trello-backlog.md`, línies 967–969 (font: `trello-backlog.md`; el títol de la card hi és «Enviar Diners a Usuaris», l.960):

```
COM: client estàndard
VULL: enviar diners a un altre usuari a l'instant
PER: saldar deutes de manera senzilla.
```

**Labels:** Fina, Alta, Transferències, P6 · **Estimació:** SP 5 · VP 8 · Prioritat Alta (font: `trello-backlog.md`, l.962 i 978).

### US-25 · Afegir subcompte en divisa

De `docs/P1/trello-backlog.md`, línies 1033–1035 (font: `trello-backlog.md`):

```
COM: client estàndard
VULL: afegir un subcompte en una nova divisa
PER: tenir saldo en aquesta moneda i gestionar-la per separat.
```

**Labels:** Fina, Mitjana, Multidivisa, P6 · **Estimació:** SP 4 · VP 6 · Prioritat Mitjana (font: `trello-backlog.md`, l.1028 i 1044). *Atenció: si un document ja escrit divergeix una paraula del literal («divisa nova» vs «nova divisa»), el literal del Trello és el que fa referència; copieu-lo exacte.*

### US-26 · Eliminar subcompte en divisa

De `docs/P1/trello-backlog.md`, línies 1067–1069 (font: `trello-backlog.md`):

```
COM: client estàndard amb subcomptes en divisa
VULL: eliminar un subcompte en divisa
PER: netejar la pantalla principal quan ja no necessito aquella moneda.
```

**Labels:** Fina, Mitjana, Multidivisa, P6 · **Estimació:** SP 2 · VP 4 · Prioritat Mitjana (font: `trello-backlog.md`, l.1062 i 1077).

### US-27 · Canviar entre divises

De `docs/P1/trello-backlog.md`, línies 1098–1100 (font: `trello-backlog.md`):

```
COM: client estàndard amb subcomptes en divisa
VULL: canviar diners entre les meves divises
PER: tenir saldo en la moneda que necessito en cada moment.
```

**Labels:** Fina, Mitjana, Multidivisa, P6 · **Estimació:** SP 5 · VP 7 · Prioritat Alta (font: `trello-backlog.md`, l.1093 i 1108).

---

## 3. API

### 3.1 Endpoints EXISTENTS (19, no cal crear-ne cap d'aquests)

Font: [`docs/api.md`](../api.md) i els routers de `backend/app/routers/` (`main` registra tots amb prefix `/api`; vegeu `backend/app/main.py`, línies dels `include_router`).

| # | Mètode + ruta | Per a què serveix | Router |
|---|---|---|---|
| 1 | `GET /api/health` | Estat del servei | `backend/app/routers/health.py` |
| 2 | `GET /api/home` | Resum d'Inici: saldo, guardioles, últims moviments | `backend/app/routers/home.py` |
| 3 | `GET /api/movements` | Llistat de moviments, amb filtres (§10.2) | `backend/app/routers/movements.py` |
| 4 | `GET /api/movements/{movementId}` | Detall d'un moviment | `backend/app/routers/movements.py` |
| 5 | `POST /api/movements/{movementId}/reports` | Informar d'un problema (justificant PDF) | `backend/app/routers/movements.py` |
| 6 | `POST /api/topups` | Recàrrega de saldo (US-09) | `backend/app/routers/topups.py` |
| 7 | `POST /api/dev/reset` | Tornar a carregar el seed | `backend/app/routers/dev.py` |
| 8 | `GET /api/dev/outbox` | Bústia simulada de notificacions | `backend/app/routers/dev.py` |
| 9 | `POST /api/auth/register` | Registre (US-01) | `backend/app/routers/auth.py` |
| 10 | `POST /api/auth/login` | Inici de sessió (US-03) | `backend/app/routers/auth.py` |
| 11 | `POST /api/auth/logout` | Tancar sessió | `backend/app/routers/auth.py` |
| 12 | `POST /api/auth/verify` | Verificar el codi (US-02) | `backend/app/routers/auth.py` |
| 13 | `POST /api/auth/resend-code` | Reenviar el codi | `backend/app/routers/auth.py` |
| 14 | `POST /api/auth/forgot-password` | Oblit de contrasenya (US-04) | `backend/app/routers/auth.py` |
| 15 | `POST /api/auth/reset-password` | Restablir contrasenya | `backend/app/routers/auth.py` |
| 16 | `GET /api/pots` | Llista de guardioles | `backend/app/routers/pots.py` |
| 17 | `POST /api/pots` | Crear guardiola (US-17) | `backend/app/routers/pots.py` |
| 18 | `POST /api/pots/{potId}/contributions` | Aportar diners a una guardiola (US-18) | `backend/app/routers/pots.py` |
| 19 | `GET /api/pots/{potId}/movements` | Historial d'una guardiola | `backend/app/routers/pots.py` |

**Convencions obligatòries** (`docs/api.md` §1, línies 24–58 — cap document pot contradir-les):

- Totes les rutes comencen per `/api`; peticions i respostes són JSON UTF-8.
- Les claus JSON van en **camelCase** (`totalSaved`, `remainingToday`, …).
- Els imports viatgen com a **enters en cèntims**: 500 € = `50000`; **1.250,50 € = `125050`**. L'`amount` és **sempre positiu**; el sentit el dona `type` (`income`/`expense`). El frontend converteix cèntims → euros només a la capa de presentació (`frontend/src/models/money.ts`).
- Dates en **ISO 8601 amb desplaçament de `Europe/Madrid`** (`2026-10-12T22:14:00+02:00`), precisió de segons; «avui» és el dia natural de Madrid.
- Límits de recàrrega existents (§1, US-09): màxim `50000` (500,00 €) per recàrrega i `100000` (1.000,00 €) per dia.
- Errors en format `{code, message, details}` (`docs/api.md` §5, l.498–508); el **frontend reacciona al `code`**, mai al text de `message`.
- L'usuari surt del token de sessió (`Authorization: Bearer`, §8.2); el `X-User-Id` només serveix per a proves manuals amb `ALLOW_X_USER_ID=true`.

### 3.2 Endpoints A CREAR (cap existeix: verificat contra la llista 3.1 i `rg` a `docs/api.md` i `backend/`)

Per a cada ruta nova, el camí és **proposat** fins que la tasca de contracte ho fixi a `docs/api.md` (T13.1, T15.1, T19.1, T25.1). Marqueu-los sempre **`a crear`** i citeu la tasca. **No toqueu `docs/api.md` des dels documents d'US**: el contracte és feina de la seva tasca E.

**US-19 (T19.1 contracte):** `a crear` **`POST /api/pots/{potId}/withdrawals`**, mirall de la contribució existent (§9.4): la guardiola baixa, el saldo principal puja, moviment registrat, tot o res (atòmic). A més, les respostes de `GET /api/pots` i del detall de guardiola han de passar a portar el **percentatge** i l'**estat** de progrés (per a la US-20). Camí *proposat, pendent del contracte de la tasca T19.1*.

**US-20 (T20.1):** no crea rutes noves; **modifica les respostes existents** de guardioles (`GET /api/pots`, i el detall que surti de la mateixa família) afegint `progressPercent` (enter, arrodonit) i `status` («En progrés» / «Objectiu assolit»; sense objectiu, cap dels dos). `a crear` com a camps, no com a endpoints. Depèn que el contracte de la T19.1 ho aproví.

**US-13 (T13.1 contracte):** `a crear` **`GET /api/users/search`** (cerca per @usuari, telèfon o email; **mai** retorna saldos ni cap dada financera; **mai** retorna l'usuari de la sessió; el telèfon ha de coincidir amb i sense `+34`). A més cal el camp **`@username` a l'usuari**: `backend/app/models/user.py` avui **NO té cap camp així** (només `id, name, identifier, identifier_type, password_hash, status, xp, failed_logins, locked_until`), i cal afegir-lo al seed (memòria i Firestore). Camí *proposat, pendent del contracte de la tasca T13.1*.

**US-14 (T13.1 contracte, mateixa PR):** `a crear` **`POST /api/transfers`**: enviament **atòmic** entre dos comptes (una sola transacció, també a Firestore), un moviment `transfer` a cadascú, límit diari d'enviaments de **1.000,00 €/dia = `100000` cèntims** (decisió NOVA del PO, vegeu §6: operació diferent del límit de recàrrega). A més, notificacions «Has enviat X € a <nom>» i «<nom> t'ha enviat X €» via **`backend/app/services/notifications.py`** (existeix; el patró és el de la bústia de `GET /api/dev/outbox`). Camí *proposat, pendent del contracte de la tasca T13.1*.

**US-15 (T15.1 contracte):** `a crear` **`GET /api/requests`** (les enviades), **`POST /api/requests`** i **`POST /api/requests/{id}/cancel`**. Quatre estats al model (Pendent/Pagada/Rebutjada/Caducada) però aquest sprint només se'n veuen tres: la **caducitat a 7 dies es calcula en llegir** (sense tasca de fons ni camp desat), només es cancel·la una **Pendent**, i la creació emet l'avís «<nom> et demana X €» a la bústia (visible per `GET /api/dev/outbox`). Camins *proposats, pendents del contracte de la tasca T15.1*.

**US-25 (T25.1 contracte):** `a crear` **`GET /api/subaccounts`** i **`POST /api/subaccounts`** (un subcompte **per divisa**, neix amb saldo `0`, i la llista de divises disponibles amb els seus codis, noms i símbols; el total de totes les divises es mostra **aproximat en euros** amb una **taula de tipus fixa** — `totalEurCents`). Error si la divisa ja té subcompte o no és a la llista. Camins *proposats, pendents del contracte de la tasca T25.1*.

**US-26 (T25.1 contracte, mateixa PR):** `a crear` **`DELETE /api/subaccounts/{subaccountId}`**: només es pot eliminar amb **saldo 0** (amb saldo, error i no s'elimina); el **compte principal en EUR mai no es pot eliminar**. Camí *proposat, pendent del contracte de la tasca T25.1*.

**US-27 (T25.1 contracte, mateixa PR):** `a crear` **`POST /api/exchanges`**: canvi **atòmic** entre dos subcomptes, amb tipus de canvi, **comissió d'1,5 % amb mínim de 0,50 €** (decisió NOVA del PO, §6) i arrodoniment en cèntims; error sense prou saldo, origen = destí o import que dona menys d'un cèntim al destí. Camí *proposat, pendent del contracte de la tasca T25.1*.

---

## 4. Frontend: existent vs a crear

### 4.1 Rutes EXISTENTS (font: `frontend/src/router/index.ts`, literals)

| Ruta | Nom | Component | Nota |
|---|---|---|---|
| `/` | `home` | `HomeView` | |
| `/movements` | `movements` | `MovementsView` | |
| `/movements/:movementId` | `movement` | `MovementDetailView` | `props: true` |
| `/movements/:movementId/report` | `report-movement` | `ReportProblemView` | `props: true` |
| `/topup` | `topup` | `TopUpView` | |
| `/pots` | `pots` | `PotsView` | |
| `/pots/new` | `create-pot` | `CreatePotView` | |
| `/pots/:potId` | `pot` | `PotView` | `props: true` |
| `/pots/:potId/contribute` | `contribute` | `ContributeView` | `props: true` |
| `/login` | `login` | `LoginView` | `meta.public` |
| `/register` | `register` | `RegisterView` | `meta.public` |
| `/verify` | `verify` | `VerifyView` | `meta.public` |
| `/forgot-password` | `forgot-password` | `ForgotPasswordView` | `meta.public` |
| `/nova-contrasenya` | `new-password` | `NewPasswordView` | `meta.public`; ruta de l'enllaç de recuperació (§8.10) |

`router.beforeEach(accessGuard)` redirigeix a `login` qualsevol ruta sense sessió; `afterEach` toca la sessió (amb mocks no hi ha peticions que la mantinguin viva).

### 4.2 Inventari rellevant (tot existeix)

- **14 views** a `frontend/src/views/`: `ContributeView`, `CreatePotView`, `ForgotPasswordView`, `HomeView`, `LoginView`, `MovementDetailView`, `MovementsView`, `NewPasswordView`, `PotsView`, `PotView`, `RegisterView`, `ReportProblemView`, `TopUpView`, `VerifyView`.
- **Components** a `frontend/src/components/`: `AppShell`, `PrimaryButton`, `MoneyAmount`, `MovementRow`, `PotRow`, `FormField`, `CodeInput`, `EmptyState`, `ErrorState`, `LoadingIndicator`.
- **Patró viewmodel:** `useXViewModel` a `frontend/src/viewmodels/` (p. ex. `useHomeViewModel`, `usePotViewModel`, `useContributeViewModel`, `useTopUpViewModel`) + servei a `frontend/src/services/` + model a `frontend/src/models/` + tests de Vitest al costat. **Mocks ON per defecte**: `frontend/src/mocks/` (`mocks/index.ts`) s'activa tret de `VITE_USE_MOCKS=false`; amb mocks cap petició arriba a `apiClient`.
- **Serveis** a `frontend/src/services/`: `apiClient`, `homeService`, `movementsService`, `topupService`, `potsService`, `authService` (i també `session`, `receiptPdf`, `fileDownload`).
- **Models:** `money.ts`, `date.ts`, `pot.ts`, `home.ts`, `movement.ts`, `apiError.ts`, `errorMessages.ts`, `auth.ts`, `password.ts`, `topup.ts`, `receipt.ts`, `movementReport.ts` — els nous (p. ex. subcomptes, sol·licituds) hi han de convivir amb aquests patrons.

### 4.3 A CREAR per US (rutes i vistes proposades, marcades sempre `a crear`)

Rutes noves proposades (pendents de fixar-se al document de cada US; el nom segueix el patró kebab-case de l'existents):

| US | Rutes i vistes `a crear` | Vistes EXISTENTS que toca |
|---|---|---|
| US-19 | `/pots/:potId/withdraw` → vista nova «Retirar de \<nom\>» (nom proposat: `withdraw`) | `PotView` (botó «Retirar» `a crear`, part de la US-19; desactivat amb saldo 0), `HomeView` (saldo principal), `PotsView`/`PotView` (historial) |
| US-20 | cap vista nova | `PotView` (barra, % i etiqueta), `PotsView` (mini-barra a la llista), `HomeView` |
| US-13 | cap vista pròpia: la cerca viu dins de les pantalles de la US-14/US-15 | `HomeView` i `MovementsView` com a punt de partida per navegar |
| US-14 | `/payments` (Pagaments), `/send` (Enviar), `/send/confirm` (Confirmar) | `HomeView` i `MovementsView` (integració: refrescar saldo i llistat després d'enviar) |
| US-15 | `/requests/new` (Demanar diners), `/requests` (Sol·licituds enviades) | «Demanar diners» fa servir la cerca de la US-13; sense vista pròpia d'Inici |
| US-25 | `/divises` (gestió de divises), `/divises/new` (Afegir divisa) | `HomeView` (botó «Divises», subcomptes amb símbol i total ≈ en euros) |
| US-26 | cap vista nova (finestres de confirmació sobre la vista del subcompte) | `HomeView` (el subcompte desapareix de la llista) |
| US-27 | `/exchange` (Canviar + resum) | `HomeView` (saldos actualitzats dels dos subcomptes) |

---

## 5. Tokens de disseny reals (perquè els mockups semblin el producte)

Tot el que segueix és **literal** de [`frontend/src/style.css`](../../frontend/src/style.css) i dels components; els mockups (`docs/us/_mockup/render.sh`, que renderitza HTML → PNG a 390×844 @2x amb Chromium headless) i la còpia d'UI dels documents han de fer servir aquests valors exactes.

| Token | Valor | Cita |
|---|---|---|
| `--color-bg` | `#f7f9fc` | `frontend/src/style.css:2` |
| `--color-surface` | `#ffffff` | `frontend/src/style.css:3` |
| `--color-text` | `#1a2233` | `frontend/src/style.css:4` |
| `--color-muted` | `#6c7a96` | `frontend/src/style.css:5` |
| `--color-border` | `#e6ebf4` | `frontend/src/style.css:6` |
| `--color-primary` (lila) | `#4f46e5` | `frontend/src/style.css:7` |
| `--color-income` (verd, amb «+») | `#16a34a` | `frontend/src/style.css:8` |
| `--color-expense` (vermell, amb «−») | `#dc2626` | `frontend/src/style.css:9` |
| `--color-error` | `#dc2626` | `frontend/src/style.css:10` |
| Colors de guardiola | purple `#4f46e5`, blue `#2563eb`, teal `#0d9488`, orange `#ea580c`, pink `#db2777`, yellow `#ca8a04` | `frontend/src/style.css:12–17` — **mai verd ni vermell per a guardioles** (signifiquen ingrés/despesa/error) |
| `--radius` | `0.75rem` | `frontend/src/style.css:18` |
| Tipografia | font del sistema (`system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif`) | `frontend/src/style.css:19` |
| Cos | 16 px / 1.5 | `frontend/src/style.css:35–36` |

Altres constants visuals:

- **Sense ombres decoratives**: les úniques `box-shadow` són anells de focus/estat (`0 0 0 1px var(--color-primary)` en focus i `0 0 0 1px var(--color-error)` en error, p. ex. `frontend/src/components/FormField.vue:66,74`).
- **`PrimaryButton`**: fons `--color-primary` i text `--color-surface`; **desactivat = fons `--color-border` + text `--color-muted`** (`frontend/src/components/PrimaryButton.vue:20–24`). Ús per als CTAs desactivats (import invàlid, guardiola buida, saldo insuficient).
- **Mides d'import**: text secundari `0.875rem`; saldos destacats `2rem` (`frontend/src/views/PotView.vue:99`, `frontend/src/views/HomeView.vue:119`, `frontend/src/views/MovementDetailView.vue:90`); resum intermedi `1.5rem` (`ContributeView.vue:164,175`, `TopUpView.vue:101,112`).
- **Botons tàctils ≈48 px** d'alçada (padding `0.75rem` + font 16 px, com a `PrimaryButton`).
- **Format de diners**: `frontend/src/models/money.ts` amb `Intl ca-ES` → `125050` → **`1.250,50 €`** (NBSP abans de €); `formatSignedCents` afegeix `+`/`−`; `eurosToCents` és l'única via euro → cèntims.
- **Format de dates**: `frontend/src/models/date.ts`, `Intl ca-ES` amb `Europe/Madrid` → `formatDateTime` dona **`11 d’oct. · 21:15`** (U+2019 a «d’», mig punt `·`), i `formatFullDateTime` dona `11/10/2026, 21:15` per al detall. **Aquests dos formats són l'única font de format**: cap document pot inventar-ne d'altres.

---

## 6. Decisions del PO (noves, sense contradicció amb els docs)

Totes són **[PROPOSTA — pendent de validar]** fins que el PO les confirmi; cap no contradiu `docs/api.md` ni el Trello:

1. **Límit diari d'ENVIAMENTS = 1.000,00 €/dia (`100000` cèntims)** — NOU. **No confondre** amb el límit de recàrrega existent (mateix import, `100000`, però és una altra operació: US-09 recàrregues vs US-14 enviaments). Ho decideix el PO abans de la T13.1.
2. **@usuari = part local de l'email, únic, editable al perfil** — NOU. Camp inexistent avui a `backend/app/models/user.py`; cal afegir-lo a User i al seed (memòria i Firestore), d'on surt el «@usuari» dels resultats de cerca (US-13) i de les sol·licituds (US-15). També cal decidir-ho abans de la T13.1.
3. **Comissió de canvi d'1,5 % amb mínim de 0,50 €** — NOU (US-27). El resum mostra la comissió o «Sense comissió» si no n'hi ha (p. ex. amb el tíquet just); arrodoniment en cèntims. Cal decidir-ho abans de la T25.1.
4. **Formats ja consistent amb els docs** (no són decisions noves): imports `1.250,50 €`, dates `11 d’oct. · 21:15`, color primari lila `#4f46e5` — tot coincideix amb `docs/P1/trello-backlog.md` §Guia d'estil, `docs/api.md` §1 i els tokens de `frontend/src/style.css`.

---

## 7. On trobar cada cosa

- **`docs/P1/trello-backlog.md`** — copies de Trello i **value statements literals de les vuit US** (US-19 l.489+, US-20 l.526+, US-13 l.768+, US-15 l.799+, US-14 l.960+, US-25 l.1026+, US-26 l.1060+, US-27 l.1091+), amb criteris d'acceptació a la mateixa card.
- **`docs/P1/AGENTS.md`** — format obligatori de la documentació d'US (l.78: plantilla i guia obligatòries; l.97: regla substitutiva del «com a mínim 1»; l.98: índex).
- **`docs/P1/backlog.md`** — versions llargues «Com a… vull… per tal de…» de la P2 Estalvi (US-19 l.187+, US-20 l.255+).
- **`docs/api.md`** — contracte vigent: §1 convencions, §5 errors `{code,message,details}`, §8 accés, §9 guardioles, §10 moviments. **No s'edita des dels documents d'US** (les tasques T19.1/T13.1/T15.1/T25.1 ho faran).
- **`docs/proves-estalvi.md`** — proves d'acceptació de US-17/US-18 (patró: taula API + taula Pantalla); la T19.1 hi **afegeix** les proves de US-19 i US-20.
- **Tasques del Sprint 2 · F3-Evolt.pdf** — tasques del Sprint 2 (les 31, per bloc, amb fases, hores i «fet quan»); el resum per bloc és a la secció 1 d'aquest document.
- **`docs/P1/trello-backlog.md`** — mateixes cards del Trello en format copiar-i-enganxar (labels, COM/VULL/PER, checklist), ja citades a la secció 2.
- **`docs/P1/backlog.md`** — detall de US-19/US-20 (assumptes, criteris numerats, INVEST, card Trello), citades a la secció 2.
- **`docs/api.md`**, **`backend/`** i **`frontend/`** — fonts dels endpoints (secció 3.1), l'inventari de frontend (secció 4) i els tokens de disseny (secció 5). *Nota: els primers extracts de treball d'aquests fets eren còpies temporals en un directori local; les fonts vàlides són les originals d'aquesta llista.*
- **`docs/us/_plantilla.md`** — plantilla obligatòria (existeix: 12 seccions + exemple farcit US-19) citada per `docs/P1/AGENTS.md` i `docs/us/_guia-escriptura.md`; la forma de referència és la de la plantilla, no la de cap US concreta.
- **`docs/us/_guia-escriptura.md`** — guia d'escriptura interna (existeix; remet a `_plantilla.md`, de la qual pren l'exemple farcit US-19 com a exemple de referència).
- **`docs/us/_mockup/render.sh`** — renderitza un mockup HTML a PNG amb Chromium headless (`./render.sh <input.html> <output.png>`, sortida 780×1688 per a un marc 390×844 @2x).
