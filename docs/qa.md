# Estratègia de qualitat i mètriques · Sprint 2

Responsable: QA (Huabin) · Issue: #191 · Regles de cada test: skill `qa-strategy` (`.claude/skills/qa-strategy/SKILL.md`).

Aquest document respon les tres preguntes de la Sprint 1 Review:

1. **Quina és l'estratègia de qualitat?** Què provem, amb quina eina, on corre i què no fem i per què (§1–§3).
2. **Quines mètriques d'èxit tenim?** Cobertura, rutes, criteris d'acceptació (§4–§5).
3. **Han servit d'alguna cosa els tests?** Els defectes trobats i qui els va trobar (§6).

El §7 resumeix les tècniques de QA que fem servir i com les apliquem.

---

## 1. Objectiu

- `develop` no es trenca mai: només hi entra una història sencera, amb el CI en verd i acceptada pel PO (skill `gitflow`).
- Cada criteri d'acceptació (AC) de la targeta del Trello té almenys una prova, automàtica o manual, amb un identificador.
- Cada defecte trobat deixa un test que el detecta abans d'arreglar-lo.

## 2. Nivells de prova

Seguim el model en V: cada nivell de disseny té el seu nivell de prova.

| Nivell | Eina | On és | Què demostra | Automàtic |
|---|---|---|---|---|
| Unitari (regles de negoci) | pytest | `backend/tests/test_*_service.py`, `test_password_policy.py`… | Cada regla dels serveis: límits, validacions, què canvia i què no | CI |
| Contracte de l'API | pytest + `TestClient` | `backend/tests/` (un fitxer per recurs) | Cada ruta de `docs/api.md`: l'èxit, **cada codi d'error** i `401` sense sessió | CI |
| Integració amb l'emmagatzematge | pytest + emulador de Firestore | `test_firestore.py` i tota la suite amb `TEST_STORAGE=firestore` | Els repositoris de Firestore (els de producció) fan el mateix que els de memòria | **Local** (vegeu §8) |
| Lògica del frontend | Vitest | `frontend/src/**/*.test.ts` | ViewModels (carregant, buit, error, èxit), serveis (petició i errors), models (funcions pures), guardes del router | CI |
| Acceptació | `docs/proves-*.md` + navegador | `docs/proves-acces.md`, `proves-moviments.md`, `proves-estalvi.md` | Cada AC té files amb ID (`RE-07`, `OP-03`…); les files d'API són tests de pytest | API: CI · pantalla: a mà |
| Extrem a extrem (fum i regressió) | Playwright | Pla al §8 | El flux principal de cada història en un navegador real | Pendent |
| Seguretat | pytest | Vegeu la llista de sota | Errors genèrics, bloqueig, sessions que caduquen, rutes protegides | CI (les regles de Firestore, a mà) |
| Estàtic i revisió | Ruff, ESLint, `vue-tsc`, CodeQL (SAST), revisió de PR | CI i GitHub | Estil, tipus, errors comuns i vulnerabilitats abans d'executar; una persona que no l'ha escrit revisa cada PR | CI + revisió obligatòria (CodeQL només a les PR cap a `develop` i `main`) |

**Proves de seguretat que ja tenim (CI):**

- Login amb error genèric: el mateix missatge si el compte no existeix o la contrasenya és incorrecta, i el mateix temps de resposta (hash fals amb bcrypt) → `test_login.py`.
- Bloqueig de 15 min als 5 errors i sessió tancada als 5 min d'inactivitat → `test_lockout_inactivity.py` (S-12 a S-22).
- Enllaç de recuperació d'un sol ús, 30 min, que tanca totes les sessions → `test_password_reset.py`.
- Contrasenyes amb bcrypt (límit de 72 bytes) i política de contrasenya → `test_password_policy.py`, `test_register.py`.
- Totes les rutes privades responen `401` sense sessió; `X-User-Id` desactivat per defecte → `test_session_auth.py`, `test_config.py`.
- CORS només per als orígens configurats → `test_cors.py`.
- Regles de Firestore que deneguen tot accés directe: provat a mà contra el projecte real (lectura anònima → `403 PERMISSION_DENIED`).

## 3. On corre cada cosa

```
local (abans del commit)  →  CI a cada PR i push (develop, main, story/**)  →  revisió de PR  →  PO accepta la història  →  develop  →  main + Render
```

- **CI** (`.github/workflows/ci.yml`): backend (Ruff, `compileall`, pytest en memòria) i frontend (ESLint, `vue-tsc`, Vitest, build). Cap PR es fusiona amb el CI en vermell.
- **CodeQL** (configuració per defecte de GitHub, activa des de l'1/11): analitza Python i JavaScript/TypeScript a les PR cap a `develop` i `main` (checks «Analyze (python)», «Analyze (javascript-typescript)» i «CodeQL»). No corre a les PR cap a `story/*`.
- **Revisió:** cada PR de tasca la revisa algú que no l'ha escrita; la revisió de QA de cada història (T19.4, T20.3…) executa els AC al navegador i ho deixa escrit a la PR.
- **Després del desplegament:** `/api/health` ha de respondre (prova de fum del desplegament, TR06.3, documentada a la #144, fusionada el 22/11).

## 4. Mètriques

| Mètrica | Com es mesura | Objectiu |
|---|---|---|
| Cobertura de línies, backend i frontend | ordres del §9 | **80 %** cadascun |
| Rutes amb tests de contracte | rutes de `backend/app/routers/` vs tests | 100 % |
| AC del sprint amb una prova | taula del §5 | 100 % (automàtica o manual amb ID) |
| Defectes trobats per tests i per revisió | taula del §6 | apuntar-los tots |

### 4.1 Cobertura de `develop` (23/11/2026, commit `eda8b02`, amb les 8 històries)

**Backend:** 1.070 tests en memòria (1 omès) i 836 amb l'emulador de Firestore.

| Àmbit | Línies |
|---|---|
| **Total, només en memòria (el que corre al CI)** | **87 %** (401 de 3.078 sense cobrir) |
| Sense els repositoris de Firestore | **96 %** |
| `services/` | 98 % |
| Rutes (`routers/`) | 96 % |
| Repositoris de Firestore (`repositories/firestore/*`, `data/firestore*`) | 46 % en memòria · **94 %** amb l'emulador |
| `repositories/atomic.py` | 41 % en memòria · 98 % amb l'emulador |
| **Total, memòria + emulador** | **97 %** (80 de 3.081 sense cobrir) |

**Frontend:** 741 tests.

| Àmbit | Línies |
|---|---|
| **Total** | **74,7 %** (branques 91,3 %, funcions 83,6 %) |
| Sense les vistes (`views/`) | **89,5 %** |
| `components/` | 99,3 % |
| `mocks/` | 97,9 % |
| `models/` | 94,5 % |
| `viewmodels/` | 91,7 % |
| `services/` | 57,4 % |
| `views/` (`.vue`) | 33,4 %: algunes vistes noves ja tenen tests de component; la resta, l'E2E |
| `router/` | 6,4 % |

**Comparat amb el 19/11** (`0e31a4c`, només l'Sprint 1): backend 77 % → **87 %** (sense Firestore 95 % → 96 %), frontend 63,6 % → **74,7 %** (sense vistes 85,2 % → 89,5 %), i de 710 + 342 tests a 1.070 + 741. Les 8 històries han portat els seus tests i la cobertura ha pujat.

**Lectura:** la lògica passa de l'objectiu del 80 % (backend 96 %, frontend sense vistes 89,5 %). El total del backend arriba al 97 % quan s'hi suma l'emulador: el que falta al CI és Firestore (§8). Al frontend, el que queda baix són les vistes i el router, que ha de cobrir l'E2E (§8).

### 4.2 Rutes

Les 32 rutes de `develop` (30 de l'app i 2 de desenvolupament: `POST /api/dev/reset` i `GET /api/dev/outbox`) tenen tests que les criden: **100 %** (23/11). Al 19/11 n'eren 19.

### 4.3 Proves puntuals de Q4 (21/11/2026, `develop` a `0e31a4c`)

Tres proves que encara no són al CI (§8). S'han fet una vegada a mà perquè el pla tingui dades reals.

**Dependències** (`pip-audit` i `npm audit`):

| Part | Resultat | Què fem |
|---|---|---|
| Backend (`requirements.txt`) | 0 vulnerabilitats conegudes | — |
| Frontend, dependències de producció (`npm audit --omit=dev`) | 0 | — |
| Frontend, dependències de desenvolupament | 19 (2 crítiques, 17 moderades), totes d'eines: `vitest` (via `tinypool`), `vite`, `eslint`, `typescript-eslint`, `vue-tsc`, `@vue/test-utils` | No arriben a l'app publicada (el build no les inclou). `npm audit fix` sense canvis de versió major n'arregla 9; les altres 10 demanen `vitest` 5 i `vue-tsc` 3. No es toquen abans de la demo |

**Testing de mutació** (`mutmut` 3 sobre `topup_service.py`, `identifier.py` i `password_policy.py`, amb tots els tests del backend):

| Mutants | Morts | Vius | Puntuació |
|---|---|---|---|
| 140 | 126 | 14 | **90 %** (126 de 128 no equivalents, el 98 %) |

Els 12 que queden vius són **equivalents** (cap test no els pot matar perquè no canvien el que veu ningú): 8 canvien el text d'`InvalidIdentifier`, que els serveis capturen i substitueixen pel seu; 1 canvia `partition` per `rpartition`, que dona el mateix perquè abans es comprova que només hi ha una `@`; 1 canvia el text intern d'un `LookupError`; 2 canvien el separador de milers de `_format_euros`, que en aquest missatge no pot sortir mai (com a màxim queden 500 €, perquè una recàrrega no passa de 500 €).

Els 2 vius que **sí** són buits dels tests (§6). Es van provar en local dos tests que els maten (91 %, el 100 % dels no equivalents), però encara no són al repositori (§8):
- canviar `astimezone(MADRID_TZ)` per la zona del servidor: cap test no provava el canvi de dia a mitjanit de Madrid, i el servidor (Render, CI) va en UTC;
- canviar `domain[1:-1]` per `domain[1:-2]`: cap test no provava un domini amb un sol caràcter després del punt (`ana@x.c`).

**Accessibilitat** (axe-core 4 amb Playwright, regles WCAG 2.1 A i AA, 11 pantalles amb el backend real i el login `demo@evolt.test`):

| Resultat | Detall |
|---|---|
| Només 1 tipus d'error: `color-contrast` | 58 elements a 10 de les 11 pantalles (`/pots` en té 0) |
| `--color-muted: #6c7a96` sobre blanc = **4,31:1** (cal 4,5:1) | 54 elements: etiquetes, dates, textos d'ajuda |
| `--color-income: #16a34a` sobre blanc = **3,29:1** | 4 elements: imports positius |
| Amb `#64728c` (4,85:1) i `#15803d` (5,02:1) a `style.css` | **0 errors** a les 11 pantalles (provat en local i desfet) |

La resta de regles (etiquetes dels camps, noms dels botons, `lang`, rols ARIA) passen a totes les pantalles. El canvi de colors el decideix el PO, perquè canvia els mockups.

## 5. Traçabilitat AC → prova (Sprint 2)

Font dels AC: les targetes del Trello (checklist «Acceptance Criteria»). Estat a 23/11.

Les proves de multidivisa (US-25, US-26 i US-27) són a `docs/proves-multidivisa.md`, amb el contracte de la #193 (ja a `develop` amb la US-25). Les marques `[PROPOSTA]` de §12, §13 i §14 de `docs/api.md` ja no hi són (#219 i #241).

| Història | AC al Trello | Proves definides | Codi | Provat per QA |
|---|---|---|---|---|
| US-19 Retirar diners | 7 | RE-01…RE-21 (API), REP-01…REP-12 (pantalla) a la #177 | **A `develop`** (#231, 23/11): contracte #177, backend #195, frontend #190 i #232 (REP-12), tests amb Firestore #230 | **Sí, de punta a punta** (§5.1, i REP-01…REP-12 a la #231) · **acceptada pel PO** |
| US-20 Progrés | 8 | O-01…O-09 (API), OP-01…OP-09 (pantalla) a la #177 | **A `develop`** (#229, 23/11): backend #194 i #203, frontend #179 | Jiajun (22/11); Huabin, OP-01…OP-09 a `d160625` i, amb la US-19 ja dins, també la OP-06 a `b3696ad` i a la regressió (§5.2); Junhao, OP-06 a `b08187c` · **acceptada pel PO** |
| US-25 Afegir subcompte | 6 | DV-01…DV-16 (API), DVP-01…DVP-07 (pantalla) a la #193 | **A `develop`** (#209, 22/11): contracte #193, backend #206, frontend #178 | Izan (#178), Huabin (#209) · **acceptada pel PO** |
| US-26 Eliminar subcompte | 6 | EL-01…EL-11 (API), ELP-01…ELP-07 (pantalla) a la #193 | **A `develop`** (#215, 22/11): backend #207, frontend #208 | Jiajun (T26.3), Alicia (backend) · **acceptada pel PO**. ELP-06 provada a la #242, ja amb la US-27 |
| US-27 Canvi de divises | 7 | CV-01…CV-23 (API), CVP-01…CVP-10 (pantalla) a la #193 | **A `develop`** (#242, 23/11): backend #222, frontend #180 | Huabin (CVP-01…CVP-10 a la #180 i la #242, en memòria i amb Firestore) · **acceptada pel PO** |
| US-13 Cercar usuari | 7 | CU-01…CU-23 (API), CUP-01…CUP-11 (pantalla) a la #196 | **A `develop`** (#205, 22/11): contracte #196, backend #197, frontend #200; pendents del PO a la #236 i la #240 | **Sí, de punta a punta** (#197 + #200) · **acceptada pel PO** |
| US-14 Enviar diners | 9 | EN-01…EN-36 (API), ENP-01…ENP-11 (pantalla) a la #196 | **A `develop`** (#239, 23/11): avisos #201, enviament #213 i #223, pantalles #233, text del límit #234 | Huabin (#201, #233, i ENP + T14.4 sobre `develop`) · **acceptada pel PO** |
| US-15 Sol·licitar diners | 10 | SO-01…SO-25 (API), SOP-01…SOP-11 (pantalla) a la #198 | **A `develop`** (#238, 23/11): contracte #198, backend #199, frontend #235 | Huabin (#199, #235 i SOP-01…SOP-11 a la #238) · **acceptada pel PO** |

A 23/11 hi ha **les 8 històries a `develop`**, totes acceptades pel PO.

### 5.1 US-19 · Retirar diners (#190 i #195, 19–20/11)

Provat al navegador amb els mocks (19/11) i, el 20/11, de punta a punta: el frontend de la #190 i el backend de la #195 fusionats en local, amb el login `demo@evolt.test`. També s'ha provat un `422` real del servidor (la guardiola buidada des d'una altra pestanya) i els errors 500 i de xarxa.

| AC del Trello | Prova | Test automàtic | Resultat |
|---|---|---|---|
| 1. «Retirar» al costat d'«Aportar»; a 0,00 € desactivat i no enfocable | Navegador | `usePotViewModel.test` («Retirar» is enabled…) | ✅ |
| 2. «Retirar de <nom>» amb saldo, «Import», «Confirmar», «Cancel·lar» | Navegador | `useWithdrawViewModel.test` | ✅ |
| 3. Import buit sense missatge; ≤ 0 → «L'import ha de ser més gran que 0.» | Navegador (`0`, `-5`) | `useWithdrawViewModel.test` | ✅ |
| 4. Més que el saldo → «La guardiola no té prou saldo…»; retirar-ho tot es pot | Navegador (`150,01`, `150,00`) | `pots.test` (mock) | ✅ |
| 5. Tic verd «Has retirat 30,00 € de Vacances»; 1,5 s i torna al detall | Navegador | `useWithdrawViewModel.test` | ✅ |
| 6. Guardiola avall i principal amunt; «−30,00 € Retirada» i «Retirada de Vacances» | Navegador + Inici | `pots.test` (mock) | ✅ |
| 7. Errors del servidor i de xarxa; l'import es queda escrit | Navegador (500 i xarxa) | `useWithdrawViewModel.test`, `WithdrawView.test` | ✅ |

Els tres defectes que va trobar la prova del 19/11 (l'error sobre el botó, la casella vermella amb un error del servidor i la falta de «← Inici») es van arreglar a `4fb2396` i el 20/11 es van tornar a provar amb el backend real: ✅. Queda pendent del PO què fa «Cancel·lar» (REP-12): ara torna al detall.

### 5.2 Regressió de `develop` abans de la release (23/11)

Sobre `develop` a `8db6d22` (les 8 històries juntes, després de la #242), abans de pujar a `main`:

| Prova | Resultat |
|---|---|
| Backend en memòria (`pytest`, `ruff`, `compileall`) | 1.070 ✅, 1 omès |
| Backend amb l'emulador de Firestore | 831 ✅, **5 fallits**: 4 de `test_exchanges.py` i `test_en30_transfers_give_no_xp` (§6: els tests, no el codi) |
| Frontend (`vitest`, ESLint, `vue-tsc`, build) | 740 ✅ |
| Navegador amb el backend real, en memòria i amb Firestore, cada recorregut amb dades noves | Les 8 històries: cerca, enviar i rebre (ENP i T14.4), sol·licitar, divises, canvi (CVP-01…CVP-10), retirar i progrés, i les pantalles de l'Sprint 1. Tot ✅, sense errors de JavaScript ni respostes 5xx. «Canviar» ja obre la pantalla de canvi |

Abans, a `947a729` (7 històries, sense la US-27), el mateix recorregut també va sortir bé, però «Canviar» encara obria una pantalla en blanc.

## 6. Han servit els tests? Defectes trobats

| Sprint | Defecte | Com es va trobar | On |
|---|---|---|---|
| 1 | bcrypt dins del pany global: 3,9 s per petició amb concurrència (ara 34 ms) | Revisió | #137 |
| 1 | La bústia de desenvolupament desava els tokens en clar | Revisió | #137 |
| 1 | Sense regles de Firestore: qualsevol podia llegir la base de dades | Revisió | #137 |
| 1 | `/api/dev/reset` podia quedar obert amb Firestore real | Revisió | #137 |
| 1 | Un `ApiError` desfeia la transacció i es perdia el comptador d'intents del codi | **Test** (emulador) | #137 |
| 1 | Cinc recàrregues alhora fallaven per contenció de la transacció | **Test** (emulador, concurrència) | #137 |
| 1 | «dictionary changed size during iteration» amb sessions concurrents | Revisió + **test** | #135 |
| 1 | Variable de Render mal escrita (`GOOGLE_APPLICATION_CREDENTIAL`) | Desplegament | Render |
| 2 | El tipus del JPY era 57 en lloc de 5700: tots els imports en iens, ×100 malament | **Script de QA** de les fitxes | #176 |
| 2 | US-25, US-26 i US-15 tenien dues funcionalitats; AC que contradeien els casos especials (US-14, US-15, US-27, US-20) | Revisió de QA (Definition of Ready) | #176 → #189 |
| 2 | 79,99 € de 80,00 € mostra «100 %» i «En progrés» (decisió del PO: 99 % com a màxim; arreglat a la #194) | Revisió | #177, #179 |
| 2 | El frontend recalcula el percentatge que el contracte diu que dona el backend | Revisió | #179 |
| 2 | Pantalla en blanc en anar a «Canviar» des de la US-25; llista amb l'EUR seleccionable si falla la càrrega | Revisió, després de fusionar-la a `story/us-25` | #178 → pantalla en blanc arreglada a la #180 (US-27) |
| 2 | Dues còpies del model de divises i dues rutes per al mateix (`/api/subaccounts` vs `/api/currencies`) | Revisió | #180 |
| 2 | Error del servidor en el lloc equivocat, casella vermella amb import correcte, sense camí de tornada | **Prova al navegador** (QA) | #190 |
| 2 | El CI no corria a `story/us-20` (anava 4 commits per darrere de `develop`) | Revisió | #179 |
| 2 | El contracte d'enviaments no deixava saber el límit que queda abans de confirmar, i la US-14 (D4) ho demana a «Enviar» | Revisió (frontend) | #196 |
| 2 | Els usuaris registrats amb telèfon abans de la T13.2 no tenen el camp `phone` i la cerca per telèfon no els troba | Revisió (QA) | #197 |
| 2 | `AMOUNT_TOO_SMALL` no quadra amb l'arrodoniment de l'import rebut: 0,01 $ a euros dona error, però l'arrodoniment en donaria 1 cèntim | Revisió (backend) | #193 |
| 2 | Dues PR treuen la mateixa funció `format_euros()` a dos mòduls diferents (`money_text.py` i `money_format.py`): la regla quedaria duplicada | Revisió (QA) | #199, #201 |
| 2 | Dos buits dels tests de l'Sprint 1: el canvi de dia del límit de recàrrega a mitjanit de Madrid i el límit `ana@x.c` del domini (el codi és correcte, però cap test no ho comprovava) | **Testing de mutació** (QA, §4.3) | `test_topup_daily_limit.py`, `test_identifier.py` (pendent, §8) |
| 2 | El text secundari (`#6c7a96`, 4,31:1) i els imports positius (`#16a34a`, 3,29:1) no arriben al contrast mínim de WCAG AA (4,5:1): 58 elements a 10 pantalles | **axe** (QA, §4.3) | `style.css` (proposta al PO) |
| 2 | Un usuari sense nom mostra l'`@usuari` dues vegades (com a nom i a sota en gris) | Revisió (PO) | #205 → arreglat a la #236 |
| 2 | La unicitat de l'`@usuari` no és igual a memòria i a Firestore: Firestore no reserva la forma `usuari<id>` | Revisió (PO) | #205 → a la #240 es prova que no pot passar i es documenta |
| 2 | CU-20 fallava amb `TEST_STORAGE=firestore`: el test llegia el seed de memòria, que amb Firestore no existeix | **Test** (suite sobre l'emulador, QA) | #214 → arreglat a la #216 |
| 2 | Tres textos diferents per a `INSUFFICIENT_BALANCE` (aportació, enviament i canvi) en lloc del de P85 | Revisió (PO) | #210 → arreglat a la #213 |
| 2 | `ConfirmDialog` no atrapa el focus: amb Tab se surt de la finestra cap al fons | Revisió (PO) | #215 (pendent, #210) |
| 2 | `q=@` sol tornava la llista inicial sencera, com si fos una cerca buida | Revisió (PO) | #205 → arreglat a la #240 |
| 2 | El contracte (§13.5) i l'ENP-03 deien «… Avui encara pots enviar 980,00 €.», però la US-14 diu exactament «Has superat el límit diari de 1.000,00 €.» | Revisió (frontend) | #233 → arreglat a la #234 |
| 2 | 6 tests de `test_pot_withdrawals.py` llegien el seed de memòria i fallaven amb Firestore (com CU-20) | **Test** (suite sobre l'emulador, QA) | #224 → arreglat a la #230 |
| 2 | `test_en30_transfers_give_no_xp` llegeix el seed de memòria i falla amb Firestore | **Test** (suite sobre l'emulador, QA) | #239 (pendent: `memory_only`) |
| 2 | 4 tests de `test_exchanges.py` llegeixen el seed de memòria i fallen amb Firestore | **Test** (suite sobre l'emulador, QA) | #180; encara fallen a `develop` després de la #242 (pendent) |
| 2 | «Retirada cancel·lada»: el temporitzador comença abans de carregar els saldos; si la càrrega triga o falla, l'avís no es veu | Revisió (QA) | #232 (pendent) |
| 2 | A la variant de selecció de `UserRow` («Demanar diners») l'`@usuari` d'un usuari sense nom encara es repeteix | Revisió (QA) | #236, #238 (pendent) |
| 2 | «Pendent» i «Caducada» tenen la mateixa etiqueta grisa, i la T15.3 demana un color per estat | Revisió (QA) | #235 (pendent, #155) |
| 2 | El canvi té un segon text «No tens prou saldo» (sense punt) que repeteix el de P85 | Revisió (QA) | #180 (pendent) |

**Recompte:** 36 defectes. 10 els va trobar una prova (tests, script, navegador, mutació o axe), 24 la revisió, 1 totes dues i 1 el desplegament. Tots es van trobar a la PR, menys els dos de la #178, que es van trobar a `story/us-25` perquè s'hi va fusionar sense revisió. Cap defecte que bloquegés no ha arribat a `develop`: els petits que el PO va acceptar com a pendents (#212 i #210) hi són anotats. Els dos de les proves puntuals del 21/11 eren a `develop` des de l'Sprint 1, i el de CU-20 hi va entrar amb la US-13: les proves de cada PR corren en memòria i no els podien veure. El mateix error de test (llegir `app.state.seed` sense `memory_only`) ha sortit en quatre històries (US-13, US-19, US-14 i US-27), sempre amb la suite sobre l'emulador. Això torna a demanar el job de Firestore al CI (§8).

Com és habitual, la revisió de disseny i de codi troba més defectes que les proves unitàries. Per això la revisió és obligatòria i la revisió de QA executa els AC.

## 7. Tècniques de QA

### 7.1 Taula de tècniques de QA

| Tècnica | Qui | Com | Quan | A Evolt |
|---|---|---|---|---|
| Autorevisió | Autor | Llegir tot el diff | Abans de la PR | Cada PR diu com s'ha provat, la DoD amb IA i com s'ha usat la IA (skill `pr-conventions`) |
| Tests unitaris | Autor | Automàtic | A cada commit | pytest i Vitest al CI (§2) |
| Programació en parella | Dues persones | Revisió contínua | Mentre s'escriu | Puntual (contractes i errors difícils) |
| Revisió de codi | Un altre membre | Lectura i comentaris | Abans de fusionar | Obligatòria a cada PR; la revisió de QA de cada història també executa els AC al navegador |
| Anàlisi estàtica | Eina | Sense executar | Al CI | Ruff, ESLint, `vue-tsc` i CodeQL (SAST, a les PR cap a `develop` i `main`) |
| Anàlisi dinàmica | Eina | Executant el codi | Al CI | Cobertura (§4) i tests de concurrència (els que van trobar 2 defectes del §6) |
| Assistent d'IA | Autor amb IA | Prompts de revisió i de tests | Mentre s'escriu | Permès amb mode L0/L1/L2 a cada tasca; l'autor respon de cada línia |
| Bot de revisió amb IA | Eina (consultiva) | Comentaris a la PR | En obrir la PR | No en fem servir com a filtre: bloquegen els tests i la persona revisora |
| Testing de mutació | Eina + persona | Es canvia el codi i es tornen a passar els tests | Cada nit | Una vegada a mà el 21/11, en 3 mòduls del backend: 90 %, i va trobar 2 buits dels tests (§4.3). Encara no és al CI (§8) |

### 7.2 Quadrants del testing àgil

| | Guien el desenvolupament | Critiquen el producte |
|---|---|---|
| **Negoci** | **Q2:** proves d'acceptació de `docs/proves-*.md` (una fila per AC, amb ID) i la taula AC → prova del §5 | **Q3:** la revisió de QA al navegador de cada història (§5.1) i la demo amb el PO, que accepta la història |
| **Tecnologia** | **Q1:** tests unitaris i de contracte de l'API (pytest) i de ViewModels (Vitest), a cada commit | **Q4:** seguretat (llista del §2 i CodeQL), concurrència i regles de Firestore. Accessibilitat (axe) i auditoria de dependències fetes una vegada a mà (§4.3). Falten rendiment i que corrin soles (§8) |

### 7.3 Què corre a cada punt del pipeline

| Punt | Què hi corre a Evolt | Pressupost recomanat | Temps real |
|---|---|---|---|
| PR i push (`develop`, `main`, `story/**`) | Ruff, `compileall`, pytest, ESLint, `vue-tsc`, Vitest, build | ~10 min | **75–100 s** (últimes execucions del CI, 20/11) |
| Fusió a `develop` | El mateix CI (no es desplega) | Minuts | 75–100 s |
| Fusió a `main` | El mateix CI, desplegament a Render i `/api/health` | Minuts | — |
| Abans de la demo | Revisió de QA de cada història al navegador i acceptació del PO | Dies | — |
| Cada nit / producció | Res encara | Hores / continu | — |

Com més tard és el punt, més cara és la prova i menys sovint corre. El CI de cada PR és ràpid (menys de 2 minuts) perquè la branca es mantingui sana; les proves cares (emulador, E2E) no hi són encara (§8).

### 7.4 QA i branques

| Mecanisme | Què garanteix | Estat a Evolt |
|---|---|---|
| Aprovació obligatòria | Algú que no és l'autor ha mirat el canvi | ✅ a `develop` i `main` · a `story/*` és una norma de l'equip, a propòsit: una regla de PR bloquejaria el push del merge de `develop` a la història (pas 4 del gitflow, skill `ci-cd`). La #178 es va fusionar sense revisió i tenia 2 errors |
| Checks obligatoris | Lint, tests i build han passat | ✅ `ci` obligatori a `develop` i `main` |
| Branca al dia abans de fusionar | La combinació s'ha provat sobre l'últim `develop` | ✅ `strict` actiu a `develop` des del 23/11 (acord de l'equip del 17/11, proposta de QA a la #145) |
| Comentaris resolts | Cap problema bloquejant es perd | Revisió manual |
| CODEOWNERS | Les zones sensibles les revisa qui les coneix | No el fem servir |

El risc principal de les *feature branches* són les **branques que viuen massa**. Les branques `story/*` s'han de posar al dia amb `git merge origin/develop` (skill `gitflow`); el 19/11, `story/us-20` i `story/us-27` anaven 4 commits per darrere.

### 7.5 QA a l'era de la IA

Amb assistents d'IA hi ha tres riscos nous: menys comprensió del codi generat, dependències inventades i **tests que no proven res** quan el mateix assistent escriu el codi i el test (es pot tenir un 100 % de cobertura amb un test tautològic). Què fem:

| Risc | Com el controlem |
|---|---|
| Codi que ningú entén | Definition of Done amb IA a cada issue i PR: «algú de l'equip pot explicar cada línia» |
| Dependències inventades | La DoD diu «no hi ha llibreries, funcions ni columnes inventades»; `npm ci` i `pip install` fallen al CI si un paquet no existeix |
| Tests tautològics | Els valors esperats de `docs/proves-*.md` s'escriuen tal qual i **no es recalculen amb el codi que es prova** (skill `qa-strategy`). Exemple: a la #193 vam recalcular a mà totes les xifres del contracte de multidivisa abans d'escriure'n els tests |
| «La IA ja ho ha mirat» | Cap PR es fusiona sense l'aprovació d'una persona que no l'ha escrita |
| Filtració de dades | Cap secret ni dada real al repositori ni als prompts; la clau del compte de servei de Firestore només és a Render |

**Cobertura no és qualitat.** Per això a més de la cobertura mirem quins defectes han trobat els tests (§6) i hem provat el testing de mutació (§4.3): amb un 95 % de cobertura del backend (sense Firestore), encara hi havia 2 casos que cap test no comprovava.

## 8. Què no fem encara, i el pla

| Buit | Per què | Pla |
|---|---|---|
| Firestore no corre al CI | Cal l'emulador (Java) al runner | Job `backend-firestore` amb l'emulador: QA el defineix, DevOps el connecta. Puja la cobertura del backend del 87 % al 97 % (§4.1). Els tests que només fallen amb Firestore (§6: CU-20, retirar, XP dels enviaments i canvi) són els que aquest job hauria trobat a la PR |
| Les vistes no tenen tests (0 %) | Es proven millor en un navegador real | E2E amb Playwright del flux principal (login → Inici → guardiola: aportar i retirar) contra els mocks, al CI |
| Preproducció | No hi ha encara un segon entorn | `develop` desplegat com a preproducció (DevOps, skill `ci-cd`) |
| Auditoria de dependències (Q4) | Feta una vegada (§4.3): 0 a producció, 19 a les eines de desenvolupament | `npm audit --omit=dev` i `pip-audit` al CI, informatius; `npm audit fix` (9 de 19) després de la demo; `vitest` 5 i `vue-tsc` 3 a l'Sprint 3 |
| Testing de mutació | Fet una vegada en 3 mòduls (§4.3): 90 %, amb 2 buits dels tests | Afegir els 2 tests que els tapen (canvi de dia a mitjanit de Madrid i `ana@x.c`). Passar-lo als serveis nous de l'Sprint 2 (guardioles, enviaments, divises), on hi ha més càlculs d'imports; al CI, cada nit, perquè triga minuts |
| Accessibilitat automàtica (Q4) | Feta una vegada (§4.3): només falla el contrast de 2 colors | Canviar els 2 colors si el PO ho accepta, i axe dins de l'E2E perquè no torni a passar |

## 9. Com reproduir les xifres

```bash
# backend
pip install pytest-cov
(cd backend && python -m pytest tests/ -q --cov=app --cov-report=term)
# sense Firestore:
(cd backend && python -m coverage report --omit='app/repositories/firestore/*,app/data/firestore*')

# frontend (la mateixa versió que vitest; --no-save no toca package.json)
(cd frontend && npm i --no-save @vitest/coverage-v8@$(node -p "require('vitest/package.json').version") \
  && npx vitest run --coverage --coverage.include='src/**')
# sense les vistes:
(cd frontend && npx vitest run --coverage --coverage.include='src/**' --coverage.exclude='src/views/**')

# backend sobre l'emulador de Firestore (local, vegeu el README)
firebase emulators:start --only firestore          # terminal 1, i deixar-lo engegat
(cd backend && FIRESTORE_EMULATOR_HOST=127.0.0.1:8080 TEST_STORAGE=firestore python -m pytest tests/ -q)   # terminal 2
# Sense FIRESTORE_EMULATOR_HOST, test_firestore.py s'omet i els tests no van a l'emulador.

# dependències (§4.3)
pip install pip-audit && pip-audit -r backend/requirements.txt
(cd frontend && npm audit --omit=dev && npm audit)

# mutació (§4.3), en una còpia de backend/ per no deixar-hi la carpeta mutants/
pip install mutmut
# a la còpia, afegir a pyproject.toml:
#   [tool.mutmut]
#   source_paths = ["app/"]
#   only_mutate = ["app/services/topup_service.py", "app/services/identifier.py", "app/services/password_policy.py"]
TZ=UTC mutmut run && mutmut results    # TZ=UTC: com el CI i Render
```

L'accessibilitat es prova amb `@axe-core/playwright` (regles `wcag2a`, `wcag2aa`, `wcag21a`, `wcag21aa`) sobre el frontend i el backend engegats en local; encara no hi ha script al repositori, perquè anirà amb l'E2E (§8).

PowerShell (Windows), per a l'emulador: `$env:FIRESTORE_EMULATOR_HOST="127.0.0.1:8080"; $env:TEST_STORAGE="firestore"; python -m pytest tests/ -q`, a la mateixa terminal i amb l'emulador engegat en una altra.
