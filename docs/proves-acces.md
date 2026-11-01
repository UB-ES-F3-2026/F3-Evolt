# Proves d'acceptació · Accés (US-01 a US-04)

Proves d'acceptació de les històries d'accés, escrites a partir dels criteris de [`docs/P1/trello-backlog.md`](P1/trello-backlog.md) i del contracte de l'[apartat 8 de `docs/api.md`](api.md#8-accés-us-01-a-us-04). Tasca: T01.1 (issue #56).

## Índex

1. [Com fer servir aquest document](#com-fer-servir-aquest-document)
2. [Dades de partida](#dades-de-partida)
3. [US-01 · Registre](#us-01--registre)
4. [US-02 · Verificació del codi](#us-02--verificació-del-codi)
5. [US-03 · Inici de sessió](#us-03--inici-de-sessió)
6. [US-04 · Recuperació de contrasenya](#us-04--recuperació-de-contrasenya)
7. [Sessió i rutes protegides](#sessió-i-rutes-protegides)
8. [Criteris d'acceptació i proves](#criteris-dacceptació-i-proves)

---

## Com fer servir aquest document

Cada història té dues taules:

- **API:** proves del backend. Cada fila es converteix en un test de pytest a la tasca indicada. Les que depenen del temps fixen el rellotge (`now`), com els tests de recàrrega de l'Sprint 0.
- **Pantalla:** proves del frontend. Es comproven a mà amb l'app arrencada (com a [`docs/prueba-sprint0.md`](prueba-sprint0.md)) i, quan es pugui, amb un test de Vitest del ViewModel.

Per llegir el codi o l'enllaç que «arriba» a l'usuari, es fa servir la bústia simulada: `GET /api/dev/outbox?to=<identifier>` ([`api.md` §8.12](api.md#812-get-apidevoutbox)).

## Dades de partida

- Seed acabat de carregar (`POST /api/dev/reset` o un client nou de pytest).
- Usuaris del seed: `demo@evolt.test` i `buit@evolt.test`, contrasenya `Evolt2026`, tots dos actius.
- Rellotge fixat a **T0 = `2026-11-03T10:00:00+01:00`** a les proves que depenen del temps. «T0 + 9:59» vol dir 9 minuts i 59 segons després de T0.
- Contrasenya vàlida de les proves: `Platja2026`.

---

## US-01 · Registre

### API (T01.2)

| Id | Situació inicial | Acció | Resultat esperat |
|---|---|---|---|
| **R-01** | `ana@x.com` no existeix | `POST /api/auth/register` amb `ana@x.com`, `Platja2026`, `acceptedTerms: true` | `201` `{ identifier: "ana@x.com", status: "pending" }`. L'usuari existeix en estat `pending`, amb compte de saldo `0`. |
| **R-02** | R-01 fet | Mirar la resposta de R-01 | **No** hi ha `token`: el registre no obre sessió. |
| **R-03** | R-01 fet | `GET /api/dev/outbox?to=ana@x.com` | Un missatge `verification_code` pel canal `email`, amb un `code` de 6 xifres. |
| **R-04** | R-01 fet | Registrar `ANA@x.com` | `409 ALREADY_REGISTERED`. No es crea cap usuari nou. |
| **R-05** | R-01 fet | Registrar `ana@x.com` amb una altra contrasenya | `409 ALREADY_REGISTERED`, també amb el compte encara pendent. |
| **R-06** | — | Registrar amb `curta1A` (7 caràcters) | `422 WEAK_PASSWORD`. |
| **R-07** | — | Registrar amb `platja2026` (sense majúscula) | `422 WEAK_PASSWORD`. |
| **R-08** | — | Registrar amb `PlatjaNova` (sense número) | `422 WEAK_PASSWORD`. |
| **R-09** | — | Registrar amb `Àlgebra26` | `201`: la majúscula accentuada compta. |
| **R-10** | — | Registrar amb `acceptedTerms: false`, o sense el camp | `422 VALIDATION_ERROR`. |
| **R-11** | — | Registrar amb `identifier` `ana@` o `12ab` | `422 VALIDATION_ERROR`. |
| **R-12** | — | Registrar amb `612 34 56 78` | `201` amb `identifier: "+34612345678"`. El missatge de la bústia surt pel canal `sms`. |
| **R-13** | R-12 fet | Registrar `0034612345678` | `409 ALREADY_REGISTERED`: és el mateix telèfon un cop normalitzat. |
| **R-14** | — | Registrar `demo@evolt.test` | `409 ALREADY_REGISTERED`. |
| **R-15** | — | Registrar `ana@x.com` amb `WEAK` i `acceptedTerms: false` | `422 VALIDATION_ERROR`: el format es comprova abans que la política. |
| **R-16** | — | Registrar `demo@evolt.test` amb `curta` | `422 WEAK_PASSWORD`: la política es comprova abans que el duplicat. |
| **R-17** | R-01 fet | Mirar l'usuari desat i els logs | La contrasenya no apareix en clar enlloc: només el hash. |

### Pantalla (T01.3)

| Id | Què fas | Què has de veure |
|---|---|---|
| **RP-01** | Obre «Crear compte». | Tres caselles, una sota l'altra: «Email o telèfon», «Contrasenya» i «Repeteix la contrasenya»; a sota, la casella dels termes i el botó lila «Crear compte». |
| **RP-02** | Escriu `platja2026` a «Contrasenya». | La casella es posa vermella i a sota surt en vermell «La contrasenya ha de tenir 8 caràcters, una majúscula i un número». |
| **RP-03** | Escriu `Platja2026` i, a la segona casella, `Platja2025`. | Sota la segona casella surt en vermell «Les contrasenyes no coincideixen» i «Crear compte» queda desactivat. |
| **RP-04** | Omple-ho bé però no marquis els termes. | «Crear compte» surt desactivat (gris clar). |
| **RP-05** | Marca els termes i envia amb `demo@evolt.test`. | Surt en vermell «Aquest email o telèfon ja té un compte» i l'enllaç lila «Inicia sessió». |
| **RP-06** | Envia un registre correcte amb un email nou. | L'app passa sola a «Verifica el teu compte». |

---

## US-02 · Verificació del codi

### API (T02.1)

Totes les proves parteixen d'`ana@x.com` registrada a **T0** (R-01) i del seu codi, llegit de la bústia.

| Id | Situació inicial | Acció | Resultat esperat |
|---|---|---|---|
| **V-01** | Codi de T0 | `POST /api/auth/verify` amb el codi correcte a T0 + 5:00 | `200` `{ token }`. El compte passa a `active`. |
| **V-02** | V-01 fet | `GET /api/home` amb `Authorization: Bearer <token>` | `200`, saldo `0`, sense moviments: el token de la verificació ja és una sessió. |
| **V-03** | V-01 fet | Tornar a verificar amb el mateix codi | `422 INVALID_CODE`: el codi ja s'ha fet servir i el compte ja no és pendent. |
| **V-04** | Codi de T0 | Codi correcte a T0 + 9:59 | `200`. |
| **V-05** | Codi de T0 | Codi correcte a T0 + 10:00 | `422 CODE_EXPIRED`. |
| **V-06** | Codi de T0 | Un codi incorrecte | `422 INVALID_CODE`, amb el missatge «El codi no és correcte o ha caducat.». |
| **V-07** | Codi de T0 | 4 codis incorrectes i després el correcte | Els 4 primers `INVALID_CODE`; el correcte, `200`. |
| **V-08** | Codi de T0 | 5 codis incorrectes | Els 4 primers `INVALID_CODE`; el 5è, `429 TOO_MANY_ATTEMPTS`. |
| **V-09** | V-08 fet | El codi correcte | `429 TOO_MANY_ATTEMPTS`: cal demanar-ne un de nou. |
| **V-10** | V-08 fet | `POST /api/auth/resend-code` i verificar amb el codi nou | `200` al reenviament i `200` a la verificació. |
| **V-11** | Codi de T0 | Reenviar a T0 + 2:00 i verificar amb el codi **antic** | `422 INVALID_CODE`: l'anterior deixa de servir. |
| **V-12** | V-11 fet | Verificar amb el codi nou a T0 + 11:00 | `200`: els 10 minuts compten des del reenviament. |
| **V-13** | — | Reenviar a `ningu@x.com` i a `demo@evolt.test` (actiu) | `200` `{ status: "ok" }` en tots dos casos, i cap missatge nou a la bústia. |
| **V-14** | — | Verificar `ningu@x.com` amb `123456` | `422 INVALID_CODE`, sense revelar que el compte no existeix. |
| **V-15** | Codi de T0 | Verificar amb `"12345"`, `"12a456"` o `123456` (número) | `422 VALIDATION_ERROR`. No compta com a intent. |
| **V-16** | Codi de T0 | 4 codis incorrectes abans de T0 + 10:00 i un altre codi a T0 + 10:00 | Els 4 primers `INVALID_CODE`; el 5è `CODE_EXPIRED`, no `TOO_MANY_ATTEMPTS`: un codi caducat no compta com a intent. |
| **V-17** | V-08 fet | Reenviar i escriure 4 codis incorrectes amb el codi nou | Tots 4 `INVALID_CODE`: el reenviament posa el comptador a zero. |

### Pantalla (T02.2)

| Id | Què fas | Què has de veure |
|---|---|---|
| **VP-01** | Després d'RP-06, mira la pantalla. | «Verifica el teu compte» amb 6 caselles, una per número. |
| **VP-02** | Escriu el codi de la bústia. | El compte s'activa i l'app obre «Inici». |
| **VP-03** | Escriu un codi incorrecte. | Les caselles es posen vermelles i surt en vermell «El codi no és correcte o ha caducat». |
| **VP-04** | Toca l'enllaç lila «Envia'm un codi nou». | Arriba un codi nou a la bústia; l'anterior ja no funciona. |
| **VP-05** | Escriu 5 codis incorrectes. | Les caselles es bloquegen i surt «Has fet massa intents. Demana un codi nou». |

---

## US-03 · Inici de sessió

### API (T03.1 i T03.2)

| Id | Tasca | Situació inicial | Acció | Resultat esperat |
|---|---|---|---|---|
| **S-01** | T03.1 | Seed | `POST /api/auth/login` amb `demo@evolt.test` i `Evolt2026` | `200` `{ token }`. |
| **S-02** | T03.1 | S-01 fet | `GET /api/home` amb el token | `200` amb les dades de l'usuari 1. |
| **S-03** | T03.1 | Seed | Login amb `DEMO@evolt.test` | `200`: l'email es normalitza. |
| **S-04** | T03.1 | Seed | Login amb `demo@evolt.test` i `Dolent2026` | `401 INVALID_CREDENTIALS`. |
| **S-05** | T03.1 | Seed | Login amb `ningu@x.com` i qualsevol contrasenya | `401 INVALID_CREDENTIALS`, amb **el mateix cos** que S-04. |
| **S-06** | T03.1 | Seed | Login amb `identifier` `12ab` | `401 INVALID_CREDENTIALS`: no diu quina casella falla. |
| **S-07** | T03.1 | `ana@x.com` pendent (R-01) | Login amb `Platja2026` | `403 ACCOUNT_NOT_VERIFIED`. |
| **S-08** | T03.1 | `ana@x.com` pendent | Login amb una contrasenya incorrecta | `401 INVALID_CREDENTIALS`. |
| **S-09** | T03.1 | S-01 fet | `POST /api/auth/logout` amb el token, i després `GET /api/home` amb el mateix token | `200` `{ status: "ok" }`, i després `401 UNAUTHENTICATED`. |
| **S-10** | T03.1 | — | Logout sense capçalera i amb un token inventat | `200` `{ status: "ok" }` en tots dos casos. |
| **S-11** | T03.1 | Dues sessions de l'usuari 1 | Logout amb la primera | La segona continua funcionant. |
| **S-12** | T03.2 | Seed, T0 | 5 logins seguits amb una contrasenya incorrecta | Els 4 primers `401 INVALID_CREDENTIALS`; el 5è, `423 ACCOUNT_LOCKED` amb `details.lockedUntil = "2026-11-03T10:15:00+01:00"`. |
| **S-13** | T03.2 | S-12 fet | Login amb la contrasenya **correcta** a T0 + 1:00 | `423 ACCOUNT_LOCKED`. |
| **S-14** | T03.2 | S-12 fet | Bústia de `demo@evolt.test` | Un missatge `account_locked` pel canal `email`. |
| **S-15** | T03.2 | S-12 fet | Login correcte a T0 + 14:59 i a T0 + 15:00 | `423` i després `200`. |
| **S-16** | T03.2 | Seed | 4 errors, 1 login correcte, 4 errors més | Cap bloqueig: un login correcte posa el comptador a zero. |
| **S-17** | T03.2 | Seed | 5 errors amb `ningu@x.com` | Sempre `401 INVALID_CREDENTIALS`: no hi ha compte per bloquejar. |
| **S-18** | T03.2 | Login a T0 | `GET /api/home` a T0 + 4:59 | `200`. |
| **S-19** | T03.2 | S-18 fet | `GET /api/home` a T0 + 9:58 | `200`: l'activitat de T0 + 4:59 ha renovat els 5 minuts. |
| **S-20** | T03.2 | Login a T0 | `GET /api/home` a T0 + 5:01 | `401 SESSION_EXPIRED`. |
| **S-21** | T03.2 | S-20 fet | `GET /api/home` amb el mateix token | `401 UNAUTHENTICATED`: la sessió ja s'ha tancat. |
| **S-22** | T03.2 | Login a T0 | `POST /api/topups` amb `60000` a T0 + 4:00, i `GET /api/home` a T0 + 8:30 | `422 AMOUNT_OVER_LIMIT` i després `200`: una petició amb error de negoci també compta com a activitat. |

### Pantalla (T03.3 i T03.5)

| Id | Què fas | Què has de veure |
|---|---|---|
| **SP-01** | A «Inicia sessió», entra amb `demo@evolt.test` i `Evolt2026` i toca el botó lila «Entrar». | S'obre «Inici» amb el saldo de l'usuari 1. |
| **SP-02** | Entra amb una contrasenya incorrecta. | Surt en vermell «L'email, el telèfon o la contrasenya no són correctes», sense marcar cap casella en concret. |
| **SP-03** | Falla 5 vegades seguides. | Surt en vermell «Compte bloquejat durant 15 minuts» i a la bústia hi ha l'avís per email. |
| **SP-04** | Entra i no facis res durant 5 minuts. | L'app torna a «Inicia sessió» i surt «La sessió s'ha tancat per inactivitat». |
| **SP-05** | Al menú, toca «Tancar sessió». | L'app torna a «Inicia sessió». Amb el botó enrere del navegador no es pot tornar a «Inici». |
| **SP-06** | Sense sessió, escriu a mà l'adreça d'«Inici». | L'app et porta a «Inicia sessió». |
| **SP-07** | (T03.5) Mira les peticions a les eines del navegador. | Cap petició porta `X-User-Id`; totes les rutes protegides porten `Authorization: Bearer`. |

---

## US-04 · Recuperació de contrasenya

### API (T04.1)

| Id | Situació inicial | Acció | Resultat esperat |
|---|---|---|---|
| **C-01** | Seed, T0 | `POST /api/auth/forgot-password` amb `demo@evolt.test` | `200` `{ status: "ok" }`. A la bústia, un missatge `password_reset` amb un `link`. |
| **C-02** | Seed | `forgot-password` amb `ningu@x.com` | `200` amb **el mateix cos** que C-01, i cap missatge a la bústia. |
| **C-03** | C-01 fet | `POST /api/auth/reset-password` amb el token de l'enllaç i `NovaClau2026` | `200`. Login amb `NovaClau2026`: `200`. Login amb `Evolt2026`: `401 INVALID_CREDENTIALS`. |
| **C-04** | C-03 fet | Tornar a fer servir el mateix token | `422 RESET_LINK_EXPIRED`: és d'un sol ús. |
| **C-05** | C-01 fet | `reset-password` a T0 + 29:59 | `200`. |
| **C-06** | C-01 fet | `reset-password` a T0 + 30:00 | `422 RESET_LINK_EXPIRED`. |
| **C-07** | C-01 fet | `reset-password` amb `novaclau` | `422 WEAK_PASSWORD`. Després, amb el **mateix** token i `NovaClau2026`: `200`. |
| **C-08** | Dues sessions obertes de l'usuari 1, i C-01 | `reset-password` correcte, i després `GET /api/home` amb les dues sessions | `401 UNAUTHENTICATED` a totes dues. |
| **C-09** | C-01 a T0, segon `forgot-password` a T0 + 1:00 | `reset-password` amb el token del **primer** enllaç | `422 RESET_LINK_EXPIRED`: l'anterior deixa de servir. |
| **C-10** | — | `reset-password` amb un token inventat | `422 RESET_LINK_EXPIRED`. |
| **C-11** | Usuari 1 bloquejat (S-12) | `forgot-password` i `reset-password` correcte | Login amb la contrasenya nova: `200`. El compte s'ha desbloquejat. |
| **C-12** | `+34612345678` registrat (R-12) | `forgot-password` amb `612 34 56 78` | `200` i un missatge `password_reset` pel canal `sms`. |
| **C-13** | `FRONTEND_URL=https://f3-evolt.onrender.com` | `forgot-password` amb `demo@evolt.test` | El `link` de la bústia comença per `https://f3-evolt.onrender.com/nova-contrasenya?token=`. Sense la variable, per `http://localhost:5173/nova-contrasenya?token=`. |

### Pantalla (T04.2)

| Id | Què fas | Què has de veure |
|---|---|---|
| **CP-01** | A «Inicia sessió», mira sota el botó «Entrar». | L'enllaç lila «He oblidat la contrasenya». |
| **CP-02** | Escriu `demo@evolt.test` i toca «Enviar». | Surt «Si l'email és correcte, rebràs un enllaç per canviar la contrasenya». A la bústia hi ha l'enllaç. |
| **CP-03** | Repeteix-ho amb `ningu@x.com`. | Surt exactament el mateix missatge. |
| **CP-04** | Obre l'enllaç de la bústia i escriu `novaclau`. | Surt el mateix error en vermell que al registre: «La contrasenya ha de tenir 8 caràcters, una majúscula i un número». |
| **CP-05** | Escriu `NovaClau2026`. | Surt un tic verd amb «Contrasenya canviada». |
| **CP-06** | Torna a obrir el mateix enllaç i intenta-ho de nou. | Surt «Aquest enllaç ha caducat» i el botó lila «Demanar-ne un de nou». |
| **CP-07** | Amb una sessió oberta en una altra pestanya, canvia la contrasenya. | A la primera petició, l'altra pestanya torna a «Inicia sessió». |

---

## Sessió i rutes protegides

Proves comunes del backend (T03.1), amb `ALLOW_X_USER_ID=0` excepte on es diu el contrari.

| Id | Acció | Resultat esperat |
|---|---|---|
| **G-01** | `GET /api/home`, `GET /api/movements` i `POST /api/topups` sense capçalera | `401 UNAUTHENTICATED` a les tres. |
| **G-02** | `GET /api/health` sense capçalera | `200`: és pública. |
| **G-03** | `GET /api/home` amb `Authorization: Bearer inventat` | `401 UNAUTHENTICATED`. |
| **G-04** | Amb `ALLOW_X_USER_ID=1`, `GET /api/home` amb `X-User-Id: 2` i sense token | `200` amb les dades de l'usuari 2 (comportament de l'Sprint 0). |
| **G-05** | Amb `ALLOW_X_USER_ID=1`, `GET /api/home` amb el token de l'usuari 1 i `X-User-Id: 2` | `200` amb les dades de l'**usuari 1**: el token mana. |
| **G-06** | Amb `ALLOW_X_USER_ID=1`, `GET /api/home` amb `Authorization: Bearer inventat` i `X-User-Id: 1` | `401 UNAUTHENTICATED`: amb token, `X-User-Id` s'ignora. |
| **G-07** | Preflight `OPTIONS /api/home` des de `http://localhost:5173` amb `Access-Control-Request-Headers: authorization` | `200` i la capçalera `Authorization` permesa. |
| **G-08** | Tots els tests de Home, moviments i recàrrega de l'Sprint 0 | Continuen passant (amb `ALLOW_X_USER_ID=1` o amb un token). |
| **G-09** | `POST /api/dev/reset` amb una sessió oberta | La sessió es tanca i la bústia queda buida. |
| **G-10** | Amb Firestore (o l'emulador): registrar `ana@x.com`, fer login, **reiniciar el backend** i fer `GET /api/home` amb el mateix token | `200`: l'usuari i la sessió continuen existint després del reinici. |
| **G-11** | Amb `ENABLE_DEV_ROUTES=false` i sense `ENABLE_DEV_OUTBOX`: `GET /api/dev/outbox` i `POST /api/dev/reset` | Totes dues responen com una ruta no definida: la bústia segueix `ENABLE_DEV_ROUTES`. |
| **G-12** | Amb `ENABLE_DEV_ROUTES=false` i `ENABLE_DEV_OUTBOX=true`: `GET /api/dev/outbox` i `POST /api/dev/reset` | La bústia respon `200`; el reinici continua sense existir. |
| **G-13** | Amb `DEV_OUTBOX_KEY` definida: `GET /api/dev/outbox` sense `X-Dev-Key` i amb una clau incorrecta | `401 UNAUTHENTICATED` en tots dos casos. |
| **G-14** | Amb `DEV_OUTBOX_KEY` definida: `GET /api/dev/outbox` amb `X-Dev-Key` correcta | `200` amb els missatges. |

---

## Criteris d'acceptació i proves

| Criteri d'acceptació | Proves |
|---|---|
| US-01 · Pantalla «Crear compte» amb tres caselles i botó lila | RP-01 |
| US-01 · Contrasenya feble: casella vermella i missatge | R-06, R-07, R-08, R-09, RP-02 |
| US-01 · Les contrasenyes no coincideixen | RP-03 |
| US-01 · Email o telèfon ja registrat, amb l'enllaç «Inicia sessió» | R-04, R-05, R-13, R-14, RP-05 |
| US-01 · Cal acceptar els termes | R-10, RP-04 |
| US-01 · El compte es crea en estat «pendent de verificació» | R-01, R-02, R-12 |
| US-01 · Després passa sola a «Verifica el teu compte» | RP-06 |
| US-02 · Arriba un codi de 6 números i la pantalla té 6 caselles | R-03, VP-01 |
| US-02 · Passats 10 minuts el codi ja no serveix | V-04, V-05, V-12, V-16 |
| US-02 · Amb el codi correcte el compte s'activa i s'obre «Inici» | V-01, V-02, VP-02 |
| US-02 · Codi incorrecte o caducat: caselles vermelles i missatge | V-05, V-06, VP-03 |
| US-02 · «Envia'm un codi nou»: arriba un codi nou i l'anterior no serveix | V-10, V-11, VP-04 |
| US-02 · Després de 5 codis incorrectes, bloqueig i missatge | V-07, V-08, V-09, V-17, VP-05 |
| US-03 · Amb dades correctes s'obre «Inici» | S-01, S-02, S-03, SP-01 |
| US-03 · Dades incorrectes: missatge genèric | S-04, S-05, S-06, SP-02 |
| US-03 · 5 errors seguits: bloqueig de 15 minuts i avís per email | S-12, S-13, S-14, S-15, S-16, SP-03 |
| US-03 · 5 minuts sense activitat: la sessió es tanca | S-18, S-19, S-20, S-21, S-22, SP-04 |
| US-03 · «Tancar sessió» torna a «Inicia sessió» | S-09, S-10, S-11, SP-05 |
| US-04 · Enllaç «He oblidat la contrasenya» sota «Entrar» | CP-01 |
| US-04 · Arriba un enllaç que funciona 30 minuts | C-01, C-05, C-06, C-12, C-13, CP-02 |
| US-04 · El mateix missatge tant si l'email existeix com si no | C-02, CP-03 |
| US-04 · La contrasenya nova compleix la mateixa política | C-07, CP-04 |
| US-04 · Es tanquen les altres sessions i surt «Contrasenya canviada» | C-03, C-08, CP-05, CP-07 |
| US-04 · Enllaç caducat: missatge i «Demanar-ne un de nou» | C-04, C-06, C-09, C-10, CP-06 |
