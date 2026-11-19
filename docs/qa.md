# Estratègia de qualitat i mètriques · Sprint 2

Responsable: QA (Huabin) · Issue: #191 · Regles de cada test: skill `qa-strategy` (`.claude/skills/qa-strategy/SKILL.md`).

Aquest document respon les tres preguntes de la Sprint 1 Review:

1. **Quina és l'estratègia de qualitat?** Què provem, amb quina eina, on corre i què no fem i per què (§1–§3).
2. **Quines mètriques d'èxit tenim?** Cobertura, rutes, criteris d'acceptació (§4–§5).
3. **Han servit d'alguna cosa els tests?** Els defectes trobats i qui els va trobar (§6).

---

## 1. Objectiu

- `develop` no es trenca mai: només hi entra una història sencera, amb el CI en verd i acceptada pel PO (skill `gitflow`).
- Cada criteri d'acceptació (AC) de la targeta del Trello té almenys una prova, automàtica o manual, amb un identificador.
- Cada defecte trobat deixa un test que el detecta abans d'arreglar-lo.

## 2. Nivells de prova

Seguim el model en V de la classe 6: cada nivell de disseny té el seu nivell de prova.

| Nivell | Eina | On és | Què demostra | Automàtic |
|---|---|---|---|---|
| Unitari (regles de negoci) | pytest | `backend/tests/test_*_service.py`, `test_password_policy.py`… | Cada regla dels serveis: límits, validacions, què canvia i què no | CI |
| Contracte de l'API | pytest + `TestClient` | `backend/tests/` (un fitxer per recurs) | Cada ruta de `docs/api.md`: l'èxit, **cada codi d'error** i `401` sense sessió | CI |
| Integració amb l'emmagatzematge | pytest + emulador de Firestore | `test_firestore.py` i tota la suite amb `TEST_STORAGE=firestore` | Els repositoris de Firestore (els de producció) fan el mateix que els de memòria | **Local** (vegeu §7) |
| Lògica del frontend | Vitest | `frontend/src/**/*.test.ts` | ViewModels (carregant, buit, error, èxit), serveis (petició i errors), models (funcions pures), guardes del router | CI |
| Acceptació | `docs/proves-*.md` + navegador | `docs/proves-acces.md`, `proves-moviments.md`, `proves-estalvi.md` | Cada AC té files amb ID (`RE-07`, `OP-03`…); les files d'API són tests de pytest | API: CI · pantalla: a mà |
| Extrem a extrem (fum i regressió) | Playwright | Pla al §7 | El flux principal de cada història en un navegador real | Pendent |
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
| Cobertura de línies, backend i frontend | ordres del §8 | **80 %** cadascun |
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

- el codi de Firestore al CI, que és el que corre a producció → emulador al CI (§7);
- les pantalles → E2E (§7).

### 4.2 Rutes

Les 18 rutes de `develop` (17 de l'app i 1 de desenvolupament) tenen tests de contracte (èxit, cada codi d'error de `docs/api.md` i `401`): **100 %**.

## 5. Traçabilitat AC → prova (Sprint 2)

Font dels AC: les targetes del Trello (checklist «Acceptance Criteria»). Estat a 19/11.

| Història | AC al Trello | Proves definides | Codi | Provat per QA |
|---|---|---|---|---|
| US-19 Retirar diners | 7 | RE-01…RE-21 (API), REP-01… (pantalla) a la #177 | Frontend #190 · backend T19.2 pendent | **Sí** (§5.1) |
| US-20 Progrés | 8 | OP-01…OP-08 a la #177 | Frontend #179 · backend T20.1 pendent | Yayun (#179) |
| US-25 Afegir subcompte | 6 | Pendent del contracte T25.1 (#166) | Frontend a `story/us-25` (#178) | Izan (#178) |
| US-26 Eliminar subcompte | 6 | Pendent de #166 | No començat | — |
| US-27 Canvi de divises | 7 | Pendent de #166 | Frontend #180 (esborrany) | — |
| US-13 Cercar usuari | 7 | Pendent del contracte T13.1 (#157) | No començat | — |
| US-14 Enviar diners | 9 | Pendent de #157 | No començat | — |
| US-15 Sol·licitar diners | 10 | Pendent del contracte T15.1 (#153) | No començat | — |

### 5.1 US-19 · Retirar diners (#190, 19/11)

Provat al navegador amb els mocks (flux sencer) i amb el backend real (login `demo@evolt.test`, errors 500 i de xarxa).

| AC del Trello | Prova | Test automàtic | Resultat |
|---|---|---|---|
| 1. «Retirar» al costat d'«Aportar»; a 0,00 € desactivat i no enfocable | Navegador | `usePotViewModel.test` («Retirar» is enabled…) | ✅ |
| 2. «Retirar de <nom>» amb saldo, «Import», «Confirmar», «Cancel·lar» | Navegador | `useWithdrawViewModel.test` | ✅ |
| 3. Import buit sense missatge; ≤ 0 → «L'import ha de ser més gran que 0.» | Navegador (`0`, `-5`) | `useWithdrawViewModel.test` | ✅ |
| 4. Més que el saldo → «La guardiola no té prou saldo…»; retirar-ho tot es pot | Navegador (`150,01`, `150,00`) | `pots.test` (mock) | ✅ |
| 5. Tic verd «Has retirat 30,00 € de Vacances»; 1,5 s i torna al detall | Navegador | `useWithdrawViewModel.test` | ✅ |
| 6. Guardiola avall i principal amunt; «−30,00 € Retirada» i «Retirada de Vacances» | Navegador + Inici | `pots.test` (mock) | ✅ |
| 7. Errors del servidor i de xarxa; l'import es queda escrit | Navegador (500 i xarxa) | `useWithdrawViewModel.test` | ✅ text · ❌ posició |

Defectes oberts a la #190: l'error surt sobre el botó (ha d'anar a sota), la casella es posa vermella amb un error del servidor, i falta el camí de tornada «← Inici». «Cancel·lar» no està definit al Trello (decisió del PO pendent).

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
| 2 | Pantalla en blanc en anar a «Canviar» des de la US-25; llista amb l'EUR seleccionable si falla la càrrega | Revisió | #178 |
| 2 | Dues còpies del model de divises i dues rutes per al mateix (`/api/subaccounts` vs `/api/currencies`) | Revisió | #180 |
| 2 | Error del servidor en el lloc equivocat, casella vermella amb import correcte, sense camí de tornada | **Prova al navegador** (QA) | #190 |
| 2 | El CI no corria a `story/us-20` (anava 4 commits per darrere de `develop`) | Revisió | #179 |

**Recompte:** 16 defectes. 4 els va trobar una prova (tests, script o navegador), 10 la revisió, 1 totes dues i 1 el desplegament. Cap defecte de codi no ha arribat a `develop`: tots es van trobar a la PR.

Coincideix amb la classe 6: la revisió de disseny i de codi troba més defectes que les proves unitàries. Per això la revisió és obligatòria i la revisió de QA executa els AC.

## 7. Què no fem encara, i el pla

| Buit | Per què | Pla |
|---|---|---|
| Firestore no corre al CI | Cal l'emulador (Java) al runner | Job `backend-firestore` amb l'emulador: QA el defineix, DevOps el connecta. Puja la cobertura del backend (les 455 línies sense cobrir són sobretot de Firestore) |
| Les vistes no tenen tests (0 %) | Es proven millor en un navegador real | E2E amb Playwright del flux principal (login → Inici → guardiola: aportar i retirar) contra els mocks, al CI |
| Preproducció | No hi ha encara un segon entorn | `develop` desplegat com a preproducció (DevOps, skill `ci-cd`) |
| Auditoria de dependències i de secrets | No és al CI | `npm audit` i `pip-audit` al CI, informatius |

## 8. Com reproduir les xifres

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

# backend sobre l'emulador de Firestore (local)
(cd backend && TEST_STORAGE=firestore python -m pytest tests/ -q)
```
