# AGENTS.md — F3-Evolt AI & Engineering Standards

> Team AI workflow. Humans own architecture, product and final decisions.
> AI accelerates implementation, tests, docs and refactors **inside these rules**.

Product context lives in `docs/P1/` (backlog, US, roles).
The API contract shared by backend and frontend is `docs/api.md`.
This file is the **coding standard** every AI tool and teammate follows.

---

## 1. Who we are

Junior developers with real knowledge of patterns. We want:

- **Clear over clever** — code that is easy to trace
- **Real solutions** — not hacky / “cutre” shortcuts
- **Simple where possible, clear always**
- Backend + frontend experience on the team → shared contracts matter

---

## 2. Architecture (non-negotiable)

### 2.1 Stack

| Part | Technology |
|------|------------|
| **Frontend** | Vue 3 + TypeScript (strict), Vite, Vue Router, Vitest. No Pinia. |
| **Backend** | Python + FastAPI, pytest. Data lives in memory (seeded at start-up) during Sprint 0. |
| **Contract** | `docs/api.md`. It changes only through a PR reviewed by backend and frontend. |

### 2.2 Project layout

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

There are no feature folders (`features/<x>/`) and no `shared/` folder: `components/`, `models/` and `services/` are already shared by every screen.

### 2.3 MVVM in the frontend (Model · ViewModel · View)

A ViewModel is a Vue 3 **composable** named `useXxxViewModel` (`viewmodels/useHomeViewModel.ts`).

| Layer | Folders | Contains | Must not contain |
|-------|---------|----------|------------------|
| **Model** | `models/`, `services/` | Data, JSON mapping and API calls | Screen state |
| **ViewModel** | `viewmodels/` | State, validations and actions of each screen | HTML or styles |
| **View** | `views/`, `components/` | Template and styles; renders what the ViewModel exposes | Business logic or API calls |

**Rules:**

1. A `.vue` file never calls a service or `fetch`; it only uses its ViewModel.
2. A ViewModel has no template and knows nothing about layout.
3. `models/` is pure data + pure functions (no Vue reactivity, no HTTP).
4. `services/` is the only place that talks to the API, always through `services/apiClient.ts`.

Full Vue rules: skill `mvvm-patterns`.

### 2.4 Layers in the backend

```
Router  →  Service  →  Repository  →  Models / data
```

| Layer | Folder | Does | Must not |
|-------|--------|------|----------|
| **Router** | `routers/` | Read the request, call one service, return the contract's JSON | Hold business rules |
| **Service** | `services/` | Business rules: validations, limits, what changes | Read `data/seed.py` directly |
| **Repository** | `repositories/` | Read and write the in-memory data | Decide business rules |
| **Model** | `models/` | Data classes with the contract's fields | Import FastAPI |

Services reach the data **only** through repositories, so moving to a real database later means rewriting one folder.

Full rules: skill `backend-clean`.

### 2.5 Clean Architecture (dependency rule)

```
Frontend:  View  →  ViewModel  →  Service  →  API
Backend:   Router  →  Service  →  Repository  →  Data
```

**Dependency rule:** each layer knows only the next one. Inner layers never import outer ones.

### 2.6 Business rules live once

- A business rule (top-up limit, daily limit, XP) is **enforced in the backend** `services/`.
- A ViewModel may repeat a check only to answer faster on screen; the backend's answer always wins.
- A rule needed by 2+ services, or a helper needed by 2+ ViewModels, goes in **one** module that both import.

Details: skill `middle-services`.

### 2.7 SOLID — how we apply it (junior-friendly)

| Principle | Practical rule |
|-----------|----------------|
| **S**ingle Responsibility | One function = one reason to change. A ViewModel serves one screen; a service function solves one use case. |
| **O**pen/Closed | Prefer adding a new service function or ViewModel over growing a huge switch. |
| **L**iskov | A mock returns exactly what the real service returns: same shape, same errors as `docs/api.md`. |
| **I**nterface Segregation | Small modules: one service file per resource, one function per endpoint. |
| **D**ependency Inversion | Each layer talks only to the next one: services never read `seed.py`, views never call `fetch`. |

### 2.8 DRY — how we apply it

- Extract when the **same business rule** appears in 2+ places (e.g. top-up limits, daily XP cap).
- Do **not** extract prematurely for two similar-but-different UI copies.
- Never duplicate a rule in two services or two ViewModels.

---

## 3. Code quality bar

### Must

- Traceable flow: View event → ViewModel action → Service → API
- One public entry per use case (easy to find, easy to test)
- Errors handled at the right layer; UI shows user-safe messages
- The frontend decides what to do from the error `code` (and `details`), never from the `message` text
- Amounts are integer cents everywhere until the presentation layer; the ViewModel formats them for display
- Each contract object (`Movement`, error codes) has one type, declared in `models/`; no `any`
- Tests for backend services and for ViewModels

### Must not

- “Quick” business logic inside a template or event handler
- `fetch` or service calls from a View
- A backend service reading `seed.py` without a repository
- God-classes / god-files
- Copy-paste of the same rule in several places
- Clever one-liners that need a comment to understand

### Naming (clear)

- Views: `XxxView.vue` (`HomeView.vue`)
- Components: `Xxx.vue` (`MovementRow.vue`)
- ViewModels: `useXxxViewModel` composables; actions as verbs (`load`, `submit`, `loadMore`)
- Frontend services: `xxxService.ts`, one function per endpoint
- Frontend models: nouns (`movement.ts`)
- Backend: `xxx_service.py`, `XxxRepository`, routers named after the resource (`routers/home.py`)
- Files: match their main export (`useHomeViewModel.ts`, `home_service.py`)

### Comments policy (summary)

- Comment **why**, not **what**
- No comments that restate the code
- Document non-obvious business rules and financial invariants
- Full rules: skill `comments-docs`

---

## 4. AI workflow (how we use copilots)

1. **Read** the US / acceptance criteria first.
2. **Load the right skill** (lazy — only what the task needs):
   - Structure / layers → `arch-structure`
   - Vue screens / ViewModels / components → `mvvm-patterns`
   - FastAPI backend / services / repositories → `backend-clean`
   - A business rule used in more than one place → `middle-services`
   - Reusable models, components, helpers → `shared-module`
   - Naming/style → `code-style`
   - Comments → `comments-docs`
   - Branches / gitflow → `gitflow`
   - PR → `pr-conventions`
   - Commit → `commit-conventions`
3. **Implement** in the folder of the right layer; follow the dependency rule.
4. **Self-check** against the architecture checklist in the skill.
5. **Human reviews** architecture and trade-offs before merge.

AI is a co-pilot. **Humans own** architecture, product, security and final QA.

---

## 5. Git conventions

### Branches (GitFlow)

| Branch | Role |
|--------|------|
| `main` | Demo / release line |
| `develop` | Integration for sprint work — **PR target** |
| `feature/<slug>` | One US or one technical task |
| `fix/<slug>` | Bugfix |
| `refactor/<slug>` | Behavior-preserving cleanup (one module) |
| `hotfix/<slug>` | Urgent fix on `main` when the demo is broken |

Full rules: skill `gitflow`.

### Commits (Conventional Commits + US ref)

```
<type>(<scope>): <short imperative subject> US-<id>
```

| Type | When |
|------|------|
| `feat` | new user-facing capability |
| `fix` | bug fix |
| `docs` | documentation only |
| `style` | format, no logic change |
| `refactor` | code change without behavior change |
| `test` | tests only |
| `chore` | tooling, deps, config |
| `ci` | pipeline |
| `perf` | performance |

**Scopes:** `auth`, `account`, `transfers`, `savings`, `gamification`, `multidivisa`, `movements`, `backend`, `app`, `ci`, `docs`

Examples:

```
feat(savings): create pot with target US-17
fix(auth): show generic error on bad login US-03
refactor(account): extract top-up limits US-09
docs: update AI workflow in AGENTS.md
```

Rules:

- Imperative mood (“add”, not “added” / “adds”)
- One logical change per commit
- Scope = business area when possible
- Reference US when the change maps to a story
- No secrets, no build junk

Full rules: skill `commit-conventions`.

### Pull Requests

- Title: same shape as commit: `feat(savings): create pot with target US-17`
- **One US / one technical task per PR**
- Branch: `feature/<slug>`, `fix/<slug>` or `refactor/<slug>` from `develop`; PR base **`develop`**
- Only `hotfix/<slug>` starts from `main`; PR base `main`, then sync `develop`
- Body: what, why, AC mapping, screenshots if UI
- Checklist: DoD + architecture checklist
- ≥1 teammate review (per course DoD proposal)
- Tests pass before merge
- Target: `develop` (demo/release on `main` via agreed flow)

Full rules: skills `pr-conventions` + `gitflow`.

---

## 6. Definition of Done (from course + tech bar)

1. Code committed
2. Developer tests pass
3. Acceptance criteria verified
4. Help/doc text updated if user-facing
5. Product Owner accepts
6. PR reviewed by another member
7. CI green; staging/demo deployable
8. No critical open bugs for that story
9. **Architecture checklist** (layers respected, no API call from a View, shared rules not duplicated)

CI and deployment are out of Sprint 0. Until they exist, point 7 means: `vitest` and `pytest` pass locally, and the PR says so.

---

## 7. Sprint / product docs

| Doc | Role |
|-----|------|
| `docs/api.md` | API contract shared by backend and frontend |
| `docs/P1/AGENTS.md` | course, roles, Scrum, backlog rules |
| `docs/P1/MEMORY.md` | decisions, workflow memory |
| `docs/P1/backlog.md` / `trello-backlog.md` | US + AC |
| `README.md` | project + AI workflow overview |
| `AGENTS.md` (this file) | coding + AI standards |

---

## 8. Quick anti-patterns

| Anti-pattern | Do instead |
|--------------|------------|
| `fetch` in a `.vue` file | View → ViewModel → service → `apiClient` |
| Business rule only in a ViewModel | Enforce it in the backend service; the ViewModel repeats it for UX |
| Backend service reading `seed.py` | Go through a repository |
| `utils.ts` with 50 unrelated helpers | A named module in `models/` |
| Same limit check in 2 files | One module, imported by both |
| Mega PR with 5 stories | One US per PR |
| “It works, don’t ask” hack | Real structure, even if slower to type |
