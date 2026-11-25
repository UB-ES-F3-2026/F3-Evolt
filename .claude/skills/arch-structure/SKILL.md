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
    middleware/     # cross-cutting HTTP middleware (CORS, errors, simulation)
    models/         # data classes
    repositories/   # access to the in-memory data
    services/       # business logic
    routers/        # endpoints
    data/seed.py    # hardcoded data
  tests/

frontend/src/
  models/        # Model: data and JSON mapping
  services/      # Model: API calls — services/<domain>/ (single-domain) + shared at root
  viewmodels/    # ViewModel: state and logic of each screen — viewmodels/<domain>/ + shared composables at root
  views/         # View: screens, one folder per domain (views/<domain>/)
  components/    # View: reusable pieces
  router/        # accessGuard + routes/<domain>.ts
  mocks/
```

- No feature folders (`features/<x>/`) and no `shared/` folder: `components/`, `models/` and `services/` are already shared by every screen.
- Do not add another top-level folder to `frontend/src/` or `backend/app/` without agreeing it in the team.
- The domain subfolders **inside** the layers (`views/<domain>/`, `viewmodels/<domain>/`, `services/<domain>/`) are the team-agreed convention (recorded via the page-separation refactor); a domain folder may gain subfolders when the domain grows.
- `middleware/` wraps the HTTP stack (CORS, errors, simulation): it sits outside the Router → Service chain and holds no business rules.

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
| Screen | `frontend/src/views/<domain>/XxxView.vue` |
| State and actions of a screen | `frontend/src/viewmodels/<domain>/useXxxViewModel.ts` |
| Reusable UI piece | `frontend/src/components/Xxx.vue` |
| API call (single-domain service) | `frontend/src/services/<domain>/xxxService.ts` (through `apiClient.ts`) |
| API call (shared by 2+ domains) | `frontend/src/services/xxxService.ts` (root, through `apiClient.ts`) |
| Type of a contract object, API JSON → app object | `frontend/src/models/` |
| Example data for mocks | `frontend/src/mocks/` |
| Route | `frontend/src/router/routes/<domain>.ts` (lazy view import) |
| Endpoint | `backend/app/routers/` |
| Business rule | `backend/app/services/` |
| Data access | `backend/app/repositories/` |
| Data class | `backend/app/models/` |
| Cross-cutting HTTP middleware (CORS, errors, simulation) | `backend/app/middleware/` |
| Hardcoded data | `backend/app/data/seed.py` |
| Backend test | `backend/tests/` |

## Page separation

Pages (screens) are separated **by domain, inside the layers and in the router** — not in feature folders:

- One route module per domain: `frontend/src/router/routes/<domain>.ts`
  (`home.ts`, `movements.ts`, `topup.ts`, `exchange.ts`, `pots.ts`,
  `payments.ts`, `requests.ts`, `currencies.ts`, `auth.ts`). It exports the
  `RouteRecordRaw[]` for its domain.
- Inside each layer, files are grouped by domain: `views/<domain>/`,
  `viewmodels/<domain>/` (9 domains: `home`, `movements`, `topup`,
  `exchange`, `pots`, `payments`, `requests`, `currencies`, `auth`) and
  `services/<domain>/` (only the domains that own a single-domain service;
  `home` and `currencies` have none). Co-located tests move with their
  source files.
  This layout is the **team-agreed convention** (recorded via the
  page-separation refactor); `features/<x>/`, new top-level folders and
  `shared/` remain forbidden. A domain folder may gain subfolders when the
  domain grows.
- **Service placement:** a service used by exactly one domain lives in
  `services/<domain>/` (`authService`, `exchangeService`, `topupService`,
  `potsService`, `transfersService`, `moneyRequestsService`, plus
  `fileDownload`/`receiptPdf` in `services/movements/`). Services used by 2+
  domains or by shared infra stay at the `services/` root: `apiClient`,
  `session`, `homeService`, `usersService`, `subaccountsService`,
  `movementsService`.
- **Shared composables stay at `viewmodels/` root:** `useBalanceVisibility`,
  `useGoBack`, `usePasswordFields`, `useSessionMenuViewModel` (used across
  domains or by shared `components/`).
- Each view is lazy-loaded at the route level:
  `component: () => import('@/views/<domain>/XxxView.vue')`.
- Route paths and names are a **contract** (backend links like
  `/nova-contrasenya`, `router.push({ name })`) — never rename.
- `router/index.ts` only aggregates the `routes/*` modules and wires the
  guards and session hooks; never re-center routes there.
- Dependency rules are unchanged: a View never imports a service directly
  (View → ViewModel → Service → `apiClient`).

Page map (domain → route → view → ViewModel): `docs/pages.md`.

## Self-check before you finish

- [ ] The file is in the folder of its layer
- [ ] No `fetch` or service call in a View; no template in a ViewModel
- [ ] Backend services read data only through repositories
- [ ] SOLID: no god service, no god ViewModel
- [ ] DRY: each business rule lives in one place
