---
name: arch-structure
description: Load when designing or changing project structure, folders, architecture layers, SOLID, DRY, Clean Architecture, dependency rules, or where a new piece of code should live. Use for any non-trivial feature start or refactor of folder layout.
---

# Architecture & Structure (F3-Evolt)

Standards for the **project layout**, **Clean Architecture** layers, **SOLID** and **DRY**.
Full context: repo `AGENTS.md`.

## Layout

Two apps in one repo. Inside each one, folders are named after the **layer**.

```
backend/
  app/
    main.py
    models/         # data classes
    repositories/   # access to the in-memory data
    services/       # business logic
    routers/        # endpoints
    data/seed.py    # hardcoded data
  tests/

frontend/src/
  models/        # Model: data and JSON mapping
  services/      # Model: API calls
  viewmodels/    # ViewModel: state and logic of each screen
  views/         # View: screens
  components/    # View: reusable pieces
  router/
  mocks/
```

- No feature folders (`features/<x>/`) and no `shared/` folder: `components/`, `models/` and `services/` are already shared by every screen.
- Do not add another top-level folder to `frontend/src/` or `backend/app/` without agreeing it in the team.

## Dependency rule (Clean Architecture)

```
Frontend:  View  →  ViewModel  →  Service  →  apiClient  →  API
Backend:   Router  →  Service  →  Repository  →  Data
```

| May depend on | Must not depend on |
|---------------|--------------------|
| View → its ViewModel, `components/` | View → services, `fetch` |
| ViewModel → `services/`, `models/` | ViewModel → templates, views |
| Frontend service → `apiClient.ts`, `models/`, `mocks/` | Frontend service → ViewModels, views |
| Router → services | Router → repositories, `data/seed.py` |
| Backend service → repositories, models | Backend service → `data/seed.py`, routers |
| Repository → data, models | Repository → services, routers |

## SOLID (practical)

- **S** — a ViewModel serves one screen; a service function solves one use case (not “home + top-up + limits”).
- **O** — add a new service function or ViewModel instead of growing a giant switch.
- **L** — a mock returns exactly what the real service returns: same shape, same errors as `docs/api.md`.
- **I** — small modules: one service file per resource, one function per endpoint.
- **D** — each layer talks only to the next one; services never read `seed.py`, views never call `fetch`.

## DRY

- Same **business rule** in 2+ places → one module both import (skill `middle-services`).
- Different UI copies that look similar → do **not** extract yet.

## Where does new code go?

| Code | Location |
|------|----------|
| Screen | `frontend/src/views/XxxView.vue` |
| State and actions of a screen | `frontend/src/viewmodels/useXxxViewModel.ts` |
| Reusable UI piece | `frontend/src/components/Xxx.vue` |
| API call | `frontend/src/services/xxxService.ts` (through `apiClient.ts`) |
| Type of a contract object, API JSON → app object | `frontend/src/models/` |
| Example data for mocks | `frontend/src/mocks/` |
| Route | `frontend/src/router/` |
| Endpoint | `backend/app/routers/` |
| Business rule | `backend/app/services/` |
| Data access | `backend/app/repositories/` |
| Data class | `backend/app/models/` |
| Hardcoded data | `backend/app/data/seed.py` |
| Backend test | `backend/tests/` |

## Self-check before you finish

- [ ] The file is in the folder of its layer
- [ ] No `fetch` or service call in a View; no template in a ViewModel
- [ ] Backend services read data only through repositories
- [ ] SOLID: no god service, no god ViewModel
- [ ] DRY: each business rule lives in one place
