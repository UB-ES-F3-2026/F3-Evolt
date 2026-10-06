# AGENTS.md — F3-Evolt AI & Engineering Standards

> Team AI workflow. Humans own architecture, product and final decisions.
> AI accelerates implementation, tests, docs and refactors **inside these rules**.

Product context lives in `docs/P1/` (backlog, US, roles).
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

### 2.1 Screaming Architecture

Folders are named after **business features**, not technical layers.

```
src/
  features/                 # SCREAMS what the product is
    auth/
    account/
    transfers/
    savings/
    gamification/
    multidivisa/
    movements/
  shared/                   # true cross-feature code only
    services/
    models/
    components/
    utils/
  app/                      # shell, routing, composition root
```

**Bad (technical layers first):**

```
src/
  components/
  services/
  models/
  utils/
```

**Good (features first):** `features/savings/`, `features/transfers/`, …

### 2.2 MVVM inside every feature (Model · ModelView · View)

Team naming: **ModelView** = ViewModel, implemented in Vue 3 as a **composable**.

**Stack:** Vue 3 + TypeScript (frontend) · Firebase (backend: Functions + Firestore + Auth)

```
features/savings/
  model/          # entities, value types, pure helpers
  modelview/      # useXxxModelView.ts — state, commands, derived UI data
  view/           # *.vue screens & components (dumb-ish)
  services/       # feature services (orchestration + Firebase adapters)
```

| Layer | Vue piece | Does | May import |
|-------|-----------|------|------------|
| **View** | `*.vue` | Render UI, forward user events | ModelView, shared UI |
| **ModelView** | `useXxxModelView.ts` | UI state, commands, derived values | Model, Services (via interfaces) |
| **Model** | pure `.ts` | Domain data, pure logic | nothing domain-external |
| **Services** | plain TS | Use cases, orchestration, adapters | Model, shared services, data sources |

**Rules:**

1. View (`.vue`) does **not** call repositories/Firebase directly.
2. ModelView does **not** render templates or know layout.
3. Model is pure data + pure functions (no Firebase, no Vue reactivity in domain models).
4. Services are the only place that talks to shared services / Firebase / APIs.

Full Vue rules: skill `mvvm-patterns`.

### 2.3 Clean Architecture (layers + dependency rule)

```
View  →  ModelView  →  Services (use cases)  →  Ports  →  Adapters (Firebase/API)
                ↘              ↙
                  Shared services / shared models
```

**Dependency rule:** outer layers depend on inner layers. Inner layers never depend on outer.

Clean layers mapped to our tree:

| Clean layer | Lives in | Example |
|-------------|----------|---------|
| Entities | `features/*/model/`, `shared/models/` | `SavingPot`, `Transaction` |
| Use cases / application | `features/*/services/`, `shared/services/` | `ContributeToPot` |
| Interface adapters | `features/*/modelview/`, Firebase adapters under services | `useSavingsModelView` |
| Frameworks/drivers | Vue 3, Firebase (Auth/Firestore/Functions) | SFC, callable functions, Firestore SDK |

### 2.4 Shared Services (middle layer)

- **Shared services** = business logic used by more than one feature.
- Lives in `shared/services/` (or `src/middle/services/` if we prefer a named middle folder).
- Feature services **compose** shared services; they do not copy-paste them.
- Shared services must not import features, views, or modelviews.

**Middle layer** = the glue between UI presentation and data backends:

- Shared domain services (XP rules, limits, currency conversion)
- API / Firestore repositories behind ports
- Cross-cutting policies (daily limits, atomic balance moves)

### 2.5 SOLID — how we apply it (junior-friendly)

| Principle | Practical rule |
|-----------|----------------|
| **S**ingle Responsibility | One class/function = one reason to change. A service that both validates password rules AND creates users = split. |
| **O**pen/Closed | Prefer adding a new use case over editing a huge switch in ModelView. |
| **L**iskov | Any `AuthRepository` implementation must behave like `AuthRepository` (same contract, same failure modes). |
| **I**nterface Segregation | Small ports: `createUser`, `login`, not one mega `UserService` with 20 methods. |
| **D**ependency Inversion | ModelView/Services depend on **ports** (interfaces), not on Firestore classes directly. |

### 2.6 DRY — how we apply it

- Extract when the **same business rule** appears in 2+ places (e.g. password policy, daily XP cap).
- Do **not** extract prematurely for two similar-but-different UI copies.
- Shared logic → `shared/services` or `shared/models`. Never duplicate in `auth/` and `transfers/`.

---

## 3. Code quality bar

### Must

- Traceable flow: View event → ModelView command → Service → Model update
- One public entry per use case (easy to find, easy to test)
- Errors handled at the right layer; UI shows user-safe messages
- Business rules live in services/models, not scattered in widgets
- Tests for use cases and critical pure model logic

### Must not

- “Quick” business logic inside a widget/event handler
- Direct Firestore/HTTP calls from View or ModelView
- God-classes / god-files
- Copy-paste of the same rule across features
- Clever one-liners that need a comment to understand

### Naming (clear)

- Features: `savings`, `transfers`, `auth` (business words)
- Model: nouns (`SavingPot`, `Money`)
- ModelView (Vue): `useXxxModelView` composables; commands as verbs (`submitContribution`)
- Vue views: `XxxView.vue`
- Services / use cases: `XxxService` or `CreateXxx`
- Ports: `XxxRepository` / `XxxGateway`
- Adapters: `FirebaseXxxAdapter` / `FirestoreXxxAdapter`
- Files: match main type (`savingPot.ts`, `useContributeModelView.ts`)

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
   - Vue UI state / screens / composables → `mvvm-patterns`
   - Firebase backend / use cases / Functions → `backend-clean`
   - Firebase Auth/Firestore/rules/config/adapters → `firebase-stack`
   - Shared business logic → `middle-services`
   - Cross-cutting types/utils → `shared-module`
   - Vue + TS naming/style → `code-style`
   - Comments → `comments-docs`
   - Branches / gitflow → `gitflow`
   - PR → `pr-conventions`
   - Commit → `commit-conventions`
3. **Implement** inside the feature folder; follow dependency rule.
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
| `hotfix/<slug>` | Urgent fix on `main` |

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

**Scopes:** `auth`, `account`, `transfers`, `savings`, `gamification`, `multidivisa`, `movements`, `shared`, `firebase`, `ci`, `docs`, `app`

Examples:

```
feat(savings): create pot with target US-17
fix(auth): show generic error on bad login US-03
refactor(shared): extract password policy service US-01
docs: update AI workflow in AGENTS.md
```

Rules:

- Imperative mood (“add”, not “added” / “adds”)
- One logical change per commit
- Scope = feature area when possible
- Reference US when the change maps to a story
- No secrets, no build junk

Full rules: skill `commit-conventions`.

### Pull Requests

- Title: same shape as commit: `feat(savings): create pot with target US-17`
- **One US / one technical task per PR**
- Branch: `feature/<slug>` from `develop`; PR base **`develop`**
- Body: what, why, AC mapping, screenshots if UI
- Checklist: DoD + architecture checklist
- ≥1 teammate review (per course DoD proposal)
- CI green before merge
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
9. **Architecture checklist** (layers respected, no UI→Firebase shortcut, shared logic not duplicated)

---

## 7. Sprint / product docs

| Doc | Role |
|-----|------|
| `docs/P1/AGENTS.md` | course, roles, Scrum, backlog rules |
| `docs/P1/MEMORY.md` | decisions, workflow memory |
| `docs/P1/backlog.md` / `trello-backlog.md` | US + AC |
| `README.md` | project + AI workflow overview |
| `AGENTS.md` (this file) | coding + AI standards |

---

## 8. Quick anti-patterns

| Anti-pattern | Do instead |
|--------------|------------|
| Firestore call in a widget | Service → port → adapter |
| Business rule in ModelView only | Put rule in model/service; ModelView orchestrates |
| `utils.ts` with 50 unrelated helpers | Feature service or `shared/` named module |
| Same password check in 2 files | `shared/services/passwordPolicy` |
| Mega PR with 5 stories | One US per PR |
| “It works, don’t ask” hack | Real structure, even if slower to type |
