---
name: arch-structure
description: Load when designing or changing project structure, folders, architecture layers, SOLID, DRY, Clean Architecture, Screaming Architecture, dependency rules, or where a new piece of code should live. Use for any non-trivial feature start or refactor of folder layout.
---

# Architecture & Structure (F3-Evolt)

Standards for **Screaming Architecture**, **Clean Architecture**, **SOLID**, **DRY**.
Full context: repo `AGENTS.md`.

## Screaming Architecture

Folders scream **what the product is**, not which technical layer.

```
src/
  features/     # auth, account, transfers, savings, gamification, multidivisa, movements
  shared/       # services, models, components, utils (true cross-feature only)
  app/          # shell, routing, composition root
```

- New business capability → new folder under `features/`.
- Never create `src/components/` or `src/services/` as the top-level organization.

## Feature layout (MVVM + services)

```
features/<feature>/
  model/       # entities, value types, pure logic
  modelview/   # UI state + commands (ViewModel pattern)
  view/        # screens & components
  services/    # use cases / orchestration / data access for this feature
```

## Dependency rule (Clean Architecture)

```
View → ModelView → Services → Ports → Adapters (Firebase/API)
```

| May depend on | Must not depend on |
|---------------|--------------------|
| View → ModelView, shared UI | View → Firebase, repositories |
| ModelView → Model, service **interfaces** | ModelView → Firestore SDK |
| Services → Models, shared services, adapters | Services → View / ModelView |
| Shared services → nothing feature-specific | Shared → features/*, view/* |

**Adapters** live at the outer edge (Firebase). **Ports** are small interfaces owned by the feature or shared layer.

## SOLID (practical)

- **S** — one service = one use case or one policy (not “user manager + rules + Firebase”).
- **O** — add a new use case / adapter instead of growing a giant switch.
- **L** — all `XRepository` implementations honour the same contract and errors.
- **I** — small ports (`findUserById`, `sendMoney`), not mega interfaces.
- **D** — ModelView/Services depend on ports, never on concrete Firebase classes.

## DRY

- Same **business rule** in 2+ places → extract to `shared/services` or `shared/models`.
- Different UI copies that look similar → do **not** extract yet.
- Feature services **compose** shared services; they never copy-paste them.

## Where does new code go?

| Code | Location |
|------|----------|
| Entity / value type | `features/<f>/model/` or `shared/models/` if used everywhere |
| UI-only state | `features/<f>/modelview/` |
| Screen/widget | `features/<f>/view/` |
| Use case / orchestration | `features/<f>/services/` |
| Rule used by 2+ features | `shared/services/` |
| Firestore/Auth adapter | adapter next to services + port interface |
| Routing / DI wiring | `app/` |

## Self-check before you finish

- [ ] Path is under a **feature** or true **shared**, not a dump layer
- [ ] No Firebase/HTTP in View or ModelView
- [ ] Model has no UI or framework imports
- [ ] Shared code is not a dependency magnet for features
- [ ] SOLID: no god service; ports are small
- [ ] DRY: shared rules live in one place
