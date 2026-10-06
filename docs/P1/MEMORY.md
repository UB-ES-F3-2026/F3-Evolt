# MEMORY — Projecte P1

> decisions i flux de treball. Font US: doc de l'equip. Trello: copiat a mà des de `trello-backlog.md`.

## Producte

- Neobanc inspirat en Revolut + gamificació (XP, nivells, insígnies, reptes)
- Compte, pagaments entre usuaris, estalvi (guardioles), multidivisa

## Curs

- Demo examen; sprints 0 → 3
- Class 3 (6-7 oct): Deliver Backlog + Start Sprint 0
- GitHub obligatori; Trello per backlog
- IA com a co-pilot; decisions humans

## Metodologia

- Format US: `AS A… I WANT TO… SO I CAN…` → a Trello: **COM / VULL / PER**
- AC: mínim 1/US, testables, Pass/Fall
- Granularitat: 20% fines / 20% mitjanes / 60% èpiques
- Estimació SP + VP a les US rellevants
- Backlog inclou: US, TR, spikes, tech debt, bugs

## Numeració

- **US-XX sencera** (US-01…US-29), sense decimals
- P1 Alta · P2 Estalvi · P3 Home+XP · P4 Moviments · P5 Social · P6 Transferències+Multidivisa
- Format complet de cada US: `trello-backlog.md`

## Trello

- Tauler: https://trello.com/b/LxXzo6NC/kanban
- **Sense import automàtic.** Copiat a mà des de `trello-backlog.md`
1. Backlog → **+ Afegeix una tarjeta** → títol
2. Card → **Descripció** (COM/VULL/PER)
3. **Checklist** → `Acceptance Criteria`
4. Labels

## Totes les US

### P1 — Alta i primers passos
| ID | Títol | Granularitat |
|----|-------|--------------|
| US-01 | Registre amb email o telèfon | Fina |
| US-02 | Verificació del codi de registre | Fina |
| US-03 | Inici de sessió amb contrasenya | Fina |
| US-04 | Recuperació de contrasenya | Fina |
| US-09 | Recàrrega de prova | Fina |

### P2 — Estalvi (teves)
| ID | Títol | Granularitat | SP/VP |
|----|-------|--------------|-------|
| US-17 | Crear guardiola | Fina | 5/8 |
| US-18 | Aportar diners a una guardiola | Fina | 5/8 |
| US-19 | Retirar diners d'una guardiola | Fina | 3/6 |
| US-20 | Progrés i objectiu assolit | Fina | 3/5 |

### P3 — Pantalla principal i XP
| ID | Títol | Granularitat |
|----|-------|--------------|
| US-07 | Saldo a la pantalla principal | Fina |
| US-23 | Guanyar XP per hàbits saludables | Mitjana |
| US-24 | Nivells i perfil de progrés | Mitjana |

### P4 — Moviments
| ID | Títol | Granularitat |
|----|-------|--------------|
| US-08 | Llistat de moviments | Fina |
| US-10 | Filtres i cerca de moviments | Mitjana |
| US-11 | Detall d'un moviment | Mitjana |

### P5 — Social
| ID | Títol | Granularitat |
|----|-------|--------------|
| US-13 | Cercar un usuari | Fina |
| US-15 | Sol·licitar diners | Mitjana |
| US-16 | Respondre a una sol·licitud | Mitjana |

### P6 — Transferències + Multidivisa
| ID | Títol | Granularitat |
|----|-------|--------------|
| US-12 | Dades del compte (IBAN) | Mitjana |
| US-14 | Enviar diners a un usuari | Fina |
| US-21 | Aportació periòdica automàtica | Mitjana |
| US-25 | Afegir subcompte en divisa | Fina |
| US-26 | Eliminar subcompte en divisa | Fina |
| US-27 | Canviar entre divises | Fina |
| US-28 | Pagaments en divisa | Mitjana |
| US-29 | Límit de canvi sense comissió | Mitjana |

**Total: 24 US** · Format COM/VULL/PER + AC a `trello-backlog.md`

## Èpiques i tech

| ID | Títol | Labels |
|----|-------|--------|
| EP-01 | Registre i accés | Èpica, P1 |
| EP-02 | Compte i moviments | Èpica, P3/P4 |
| EP-03 | Pagaments entre usuaris | Èpica, P5/P6 |
| EP-04 | Estalvi amb guardioles | Èpica, Estalvi, P2 |
| EP-05 | Gamificació: XP i nivells | Èpica, P3 |
| EP-06 | Multidivisa | Èpica, Multidivisa, P6 |
| EP-09 | Despeses compartides | Èpica, Social, P5 |
| EP-10 | Anàlisi de despeses | Èpica, Moviments, P4 |
| EP-11 | Insígnies i recompenses | Èpica |
| EP-12 | Reptes i ratxes | Èpica, P2 |
| EP-13 | Gamificació social | Èpica, Social, P5 |
| EP-14 | Perfil i preferències | Èpica |
| EP-15 | Administració de la gamificació | Èpica, P3 |
| TR-05 | CI/CD pipeline | Tech, DevOps, Sprint0 |
| TR-06 | Entorn demo desplegable | Tech, DevOps, Sprint0 |
| Spike-01 | Stack frontend/backend | Tech, Spike, Sprint0 |

## Fitxers

- `AGENTS.md` (arrel) — estàndards d'arquitectura + IA (font de veritat de codi)
- `CLAUDE.md` (arrel) — pointer cap a AGENTS.md
- `README.md` — resum del workflow AI
- `docs/P1/AGENTS.md` — visió + metodologia del curs
- `MEMORY.md` — aquest
- `plantejament.md` — notes curs
- `trello-backlog.md` — **24 US + èpiques** per copiar a Trello
- `PDFs/` — materials de classe
- `.claude/skills/` · `.opencode/skills/` — **11 skills lazy** (mateix contingut)

## Workflow AI (decisió d'equip)

- **Stack:** Vue 3 + TypeScript (frontend) · Firebase (backend: Functions + Firestore + Auth)
- **MVVM:** Model · ModelView (composable `useXxxModelView`) · View
- **Clean Architecture** + **shared services** (middle)
- **Screaming Architecture**, **SOLID**, **DRY**
- Solucions **clares i traciables** (no cutre, no sobre-enginyeria)
- Skills: arch-structure, mvvm-patterns (Vue), backend-clean (Firebase), firebase-stack, middle-services, shared-module, code-style, comments-docs, gitflow, pr-conventions, commit-conventions
- Commits: `type(scope): subject US-XX`
- Branches: `develop` = PR base · `feature/<slug>` · `main` = demo/release
- PR: una US / una tasca tècnica; checklist DoD + arquitectura
- Font: arrel `AGENTS.md`

## Pendents

- [ ] Les 24 US al tauler amb títol + AC + labels
- [ ] Renombrar US-2.x → US-17…20 si encara hi són
- [ ] Renombrar US-06.x → US-25…29 al tauler
- [ ] Èpiques EP-01…EP-15 al Backlog
- [ ] TR-05, TR-06, Spike-01 al Backlog
- [ ] GitHub repo + producte vs develop
- [ ] Class 3: PO accepta backlog; Sprint 0
