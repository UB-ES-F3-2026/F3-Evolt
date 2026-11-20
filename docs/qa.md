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
| Estàtic i revisió | Ruff, ESLint, `vue-tsc`, revisió de PR | CI i GitHub | Estil, tipus i errors comuns abans d'executar; una persona que no l'ha escrit revisa cada PR | CI + revisió obligatòria |

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
- **Revisió:** cada PR de tasca la revisa algú que no l'ha escrita; la revisió de QA de cada història (T19.4, T20.3…) executa els AC al navegador i ho deixa escrit a la PR.
- **Després del desplegament:** `/api/health` ha de respondre (prova de fum del desplegament, TR06.3 a la #144).

## 4. Mètriques

| Mètrica | Com es mesura | Objectiu |
|---|---|---|
| Cobertura de línies, backend i frontend | ordres del §9 | **80 %** cadascun |
| Rutes amb tests de contracte | rutes de `backend/app/routers/` vs tests | 100 % |
| AC del sprint amb una prova | taula del §5 | 100 % (automàtica o manual amb ID) |
| Defectes trobats per tests i per revisió | taula del §6 | apuntar-los tots |

### 4.1 Cobertura de `develop` (19/11/2026, commit `0e31a4c`)

`develop` encara no té codi del Sprint 2 (les històries són a les branques `story/*`), així que les xifres són les mateixes que la base del 10/11.

**Backend:** 710 tests (1 omès).

| Àmbit | Línies |
|---|---|
| **Total** | **77 %** (455 de 2.012 sense cobrir) |
| Sense els repositoris de Firestore | **95 %** |
| Repositoris de Firestore (`repositories/firestore/*`) | 0 % al CI; provats a l'emulador (555 tests en verd) |
| Rutes (`routers/`) | 8 de 10 fitxers al 100 %; `dev.py` 94 % i `dependencies.py` 68 % (branques de Firestore i de la bústia) |
| `repositories/atomic.py` | 41 % (la transacció de Firestore només corre a l'emulador) |

**Frontend:** 342 tests.

| Àmbit | Línies |
|---|---|
| **Total** | **63,6 %** (branques 94,9 %, funcions 84,6 %) |
| Sense les vistes (`views/`) | **85,2 %** |
| `viewmodels/` | 91,8 % |
| `models/` | 94,5 % |
| `mocks/` | 96,9 % |
| `services/` | 60,2 % |
| `components/` | 55,5 % |
| `router/` | 12,5 % |
| `views/` (`.vue`) | 0 %: no tenen tests de component; les cobrirà l'E2E |

**Branques del Sprint 2 (frontend):** #190 US-19 378 tests, 62,8 % · #179 US-20 375 tests, 67,7 % · #180 US-27 441 tests, 65,4 %. El codi nou porta els seus tests i no baixa la cobertura.

**Lectura:** la lògica ja passa del 80 % (backend 95 %, frontend sense vistes 85 %). El que ens falta és:

- el codi de Firestore al CI, que és el que corre a producció → emulador al CI (§8);
- les pantalles → E2E (§8).

### 4.2 Rutes

Les 19 rutes de `develop` (17 de l'app i 2 de desenvolupament: `POST /api/dev/reset` i `GET /api/dev/outbox`) tenen tests de contracte (èxit, cada codi d'error de `docs/api.md` i `401`): **100 %**.

## 5. Traçabilitat AC → prova (Sprint 2)

Font dels AC: les targetes del Trello (checklist «Acceptance Criteria»). Estat a 20/11 a la nit.

Les proves de multidivisa (US-25, US-26 i US-27) són a `docs/proves-multidivisa.md`, amb el contracte de la #193 (cap a `story/us-25-currency-subaccounts`; alguns punts encara són proposta del PO).

| Història | AC al Trello | Proves definides | Codi | Provat per QA |
|---|---|---|---|---|
| US-19 Retirar diners | 7 | RE-01…RE-21 (API), REP-01…REP-12 (pantalla) a la #177 | Frontend #190 · backend #195 (totes dues aprovades) | **Sí, de punta a punta** (§5.1) |
| US-20 Progrés | 8 | O-01…O-08 (API), OP-01…OP-08 (pantalla) a la #177 | Frontend #179 · backend #194 | Yayun i Huabin (#179, #194) |
| US-25 Afegir subcompte | 6 | DV-01…DV-16 (API), DVP-01…DVP-07 (pantalla) a la #193 | Frontend a `story/us-25` (#178) · backend T25.2 pendent | Izan (#178) |
| US-26 Eliminar subcompte | 6 | EL-01…EL-09 (API), ELP-01…ELP-07 (pantalla) a la #193 | No començat (depèn de la T25.2) | — |
| US-27 Canvi de divises | 7 | CV-01…CV-23 (API), CVP-01…CVP-10 (pantalla) a la #193 | Frontend #180 (esborrany) · backend T27.1 pendent | — |
| US-13 Cercar usuari | 7 | CU-01…CU-23 (API), CUP-01…CUP-11 (pantalla) a la #196 | Backend #197 · frontend T13.3 pendent | Huabin (#197, l'API) |
| US-14 Enviar diners | 9 | EN-01…EN-32 (API), ENP-01…ENP-11 (pantalla) a la #196 | Backend T14.1 i T14.2 i frontend T14.3 pendents | — |
| US-15 Sol·licitar diners | 10 | SO-01…SO-25 (API), SOP-01…SOP-11 (pantalla) a la #198 | Backend #199 · frontend T15.3 pendent | Huabin (#199, l'API) |

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
| 2 | 79,99 € de 80,00 € mostra «100 %» i «En progrés» | Revisió | #177, #179 |
| 2 | El frontend recalcula el percentatge que el contracte diu que dona el backend | Revisió | #179 |
| 2 | Pantalla en blanc en anar a «Canviar» des de la US-25; llista amb l'EUR seleccionable si falla la càrrega | Revisió, després de fusionar-la a `story/us-25` | #178 |
| 2 | Dues còpies del model de divises i dues rutes per al mateix (`/api/subaccounts` vs `/api/currencies`) | Revisió | #180 |
| 2 | Error del servidor en el lloc equivocat, casella vermella amb import correcte, sense camí de tornada | **Prova al navegador** (QA) | #190 |
| 2 | El CI no corria a `story/us-20` (anava 4 commits per darrere de `develop`) | Revisió | #179 |
| 2 | El contracte d'enviaments no deixava saber el límit que queda abans de confirmar, i la US-14 (D4) ho demana a «Enviar» | Revisió (frontend) | #196 |
| 2 | Els usuaris registrats amb telèfon abans de la T13.2 no tenen el camp `phone` i la cerca per telèfon no els troba | Revisió (QA) | #197 |

**Recompte:** 18 defectes. 4 els va trobar una prova (tests, script o navegador), 12 la revisió, 1 totes dues i 1 el desplegament. Cap defecte de codi no ha arribat a `develop`. Tots es van trobar a la PR, menys els dos de la #178, que es van trobar a `story/us-25` perquè s'hi va fusionar sense revisió.

Com és habitual, la revisió de disseny i de codi troba més defectes que les proves unitàries. Per això la revisió és obligatòria i la revisió de QA executa els AC.

## 7. Tècniques de QA

### 7.1 Taula de tècniques de QA

| Tècnica | Qui | Com | Quan | A Evolt |
|---|---|---|---|---|
| Autorevisió | Autor | Llegir tot el diff | Abans de la PR | Cada PR diu com s'ha provat, la DoD amb IA i com s'ha usat la IA (skill `pr-conventions`) |
| Tests unitaris | Autor | Automàtic | A cada commit | pytest i Vitest al CI (§2) |
| Programació en parella | Dues persones | Revisió contínua | Mentre s'escriu | Puntual (contractes i errors difícils) |
| Revisió de codi | Un altre membre | Lectura i comentaris | Abans de fusionar | Obligatòria a cada PR; la revisió de QA de cada història també executa els AC al navegador |
| Anàlisi estàtica | Eina | Sense executar | Al CI | Ruff, ESLint i `vue-tsc` |
| Anàlisi dinàmica | Eina | Executant el codi | Al CI | Cobertura (§4) i tests de concurrència (els que van trobar 2 defectes del §6) |
| Assistent d'IA | Autor amb IA | Prompts de revisió i de tests | Mentre s'escriu | Permès amb mode L0/L1/L2 a cada tasca; l'autor respon de cada línia |
| Bot de revisió amb IA | Eina (consultiva) | Comentaris a la PR | En obrir la PR | No en fem servir com a filtre: bloquegen els tests i la persona revisora |
| Testing de mutació | Eina + persona | Es canvia el codi i es tornen a passar els tests | Cada nit | No el tenim (§8) |

### 7.2 Quadrants del testing àgil

| | Guien el desenvolupament | Critiquen el producte |
|---|---|---|
| **Negoci** | **Q2:** proves d'acceptació de `docs/proves-*.md` (una fila per AC, amb ID) i la taula AC → prova del §5 | **Q3:** la revisió de QA al navegador de cada història (§5.1) i la demo amb el PO, que accepta la història |
| **Tecnologia** | **Q1:** tests unitaris i de contracte de l'API (pytest) i de ViewModels (Vitest), a cada commit | **Q4:** seguretat (llista del §2), concurrència i regles de Firestore. Falten rendiment, accessibilitat automàtica i auditoria de dependències (§8) |

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
| Branca al dia abans de fusionar | La combinació s'ha provat sobre l'últim `develop` | ⚠️ acordat per l'equip el 17/11 (proposta de QA a la #145), però `docs/branch-protection.md` encara diu `strict: false` |
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

**Cobertura no és qualitat.** Per això a més de la cobertura mirem quins defectes han trobat els tests (§6) i proposem el testing de mutació (§8).

## 8. Què no fem encara, i el pla

| Buit | Per què | Pla |
|---|---|---|
| Firestore no corre al CI | Cal l'emulador (Java) al runner | Job `backend-firestore` amb l'emulador: QA el defineix, DevOps el connecta. Puja la cobertura del backend (les 455 línies sense cobrir són sobretot de Firestore) |
| Les vistes no tenen tests (0 %) | Es proven millor en un navegador real | E2E amb Playwright del flux principal (login → Inici → guardiola: aportar i retirar) contra els mocks, al CI |
| Preproducció | No hi ha encara un segon entorn | `develop` desplegat com a preproducció (DevOps, skill `ci-cd`) |
| Auditoria de dependències i de secrets (Q4, SAST) | No és al CI | `npm audit` i `pip-audit` al CI, informatius; més endavant CodeQL |
| Testing de mutació | La cobertura no diu si els tests detecten errors | Provar `mutmut` en un servei del backend (p. ex. les recàrregues) i donar el % de mutants morts |
| Accessibilitat automàtica (Q4) | Els tests miren `aria-*` a mà | axe o Lighthouse amb l'E2E |

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
```

PowerShell (Windows), per a l'emulador: `$env:FIRESTORE_EMULATOR_HOST="127.0.0.1:8080"; $env:TEST_STORAGE="firestore"; python -m pytest tests/ -q`, a la mateixa terminal i amb l'emulador engegat en una altra.
