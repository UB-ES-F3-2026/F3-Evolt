# F3-Evolt

Evolt is an app to manage your accounts — a neobank inspired by Revolut/N26 with a gamification layer (XP, levels, badges, challenges).

Product, backlog and course context: [`docs/P1/`](docs/P1/).

---

## Team AI workflow

We use AI as a **co-pilot** (AI-SDLC). Humans own architecture, product and final decisions.

### How we work

1. Write / refine the **User Story + acceptance criteria** first.
2. Pick the smallest slice that is independently testable (INVEST).
3. Let AI implement **inside our architecture rules** (load the matching skill).
4. Human reviews structure and trade-offs — not only “does it work”.
5. Commit + PR with our conventions.

### Architecture in one screen

| Concept | What it means for us |
|---------|----------------------|
| **Stack** | Frontend: Vue 3 + JavaScript, Vite, Vue Router, Vitest. Backend: Python + FastAPI, pytest, data in memory. |
| **Layout** | Two apps, `frontend/` and `backend/`, each with folders named after the layer. |
| **MVVM** | The frontend uses **Model · ViewModel · View**; a ViewModel is a composable `useXxxViewModel`. |
| **Clean Architecture** | View → ViewModel → Service → API, and Router → Service → Repository → Data. Each layer knows only the next one. |
| **Business rules live once** | Enforced in the backend services; a ViewModel repeats a check only for faster feedback. |
| **SOLID** | Small services, small ViewModels, one reason to change. |
| **DRY** | Extract shared **business rules**; do not copy-paste them. |
| **Contract** | [`docs/api.md`](docs/api.md) fixes routes, fields and error codes for both sides. |

```
backend/app/     # models · repositories · services · routers · data/seed.py
backend/tests/
frontend/src/    # models · services · viewmodels · views · components · router · mocks
```

Flow: **View event → ViewModel action → Service → API → View re-render.**

### AI skills (lazy)

Skills live in the repo and load only when the task matches:

| Skill | Use when |
|-------|----------|
| `arch-structure` | folder layout, layers, SOLID/DRY, dependencies |
| `mvvm-patterns` | Vue 3 Model / ViewModel (composables) / View |
| `backend-clean` | FastAPI backend: routers, services, repositories |
| `middle-services` | business rules used in more than one place |
| `shared-module` | reusable models, components, helpers |
| `code-style` | naming, file shape, design consistency |
| `comments-docs` | when and how to comment |
| `gitflow` | branches, develop/main, hotfix, PR base |
| `pr-conventions` | pull request format and checklist |
| `commit-conventions` | Conventional Commits + US reference |

Locations (same content, for different tools):

- `.claude/skills/` — Claude Code
- `.opencode/skills/` — OpenCode

Full standards: [`AGENTS.md`](AGENTS.md).

### Branches (GitFlow)

```
main        ← demo / release
develop     ← sprint integration (PR target)
  feature/<slug>   fix/<slug>   hotfix/<slug>
```

### Commits

```
feat(savings): create pot with target US-17
```

`type(scope): short imperative subject US-XX`

### PRs

- One US or one technical task per PR
- Branch `feature/<slug>` → PR base **`develop`**
- Title mirrors the commit
- Body maps work to acceptance criteria
- Architecture checklist + DoD before request for review
- Tests pass; ≥1 teammate review

---

## Docs map

| Path | Content |
|------|---------|
| `AGENTS.md` | Engineering + AI standards (source of truth for code style) |
| `docs/api.md` | API contract shared by backend and frontend |
| `docs/P1/AGENTS.md` | Course context, Scrum, roles, backlog rules |
| `docs/P1/MEMORY.md` | Decisions and workflow memory |
| `docs/P1/Team Specification.md` | Product catalog + team |
| `docs/P1/backlog.md` | Product backlog |
| `docs/P1/trello-backlog.md` | Cards to copy into Trello |

---

## Frontend

Vue 3 + JavaScript + Vite SPA, in [`frontend/`](frontend/).

```bash
cd frontend
cp ../.env.example .env   # optional: VITE_* vars are read from frontend/.env
npm install
npm run dev               # dev server on http://localhost:5173
npm run build             # production build
npm run preview           # serve the production build
```

Copying `.env.example` is optional for a first run: the in-memory mocks are
**on by default**. Set `VITE_USE_MOCKS=false` in `frontend/.env` to call the
real API (and `VITE_API_URL` to point at it).

Layout (`frontend/src/`, folders by layer):

```
models/       # data and JSON mapping (pure)
services/     # API calls, one function per endpoint (services/apiClient.js)
viewmodels/   # useXxxViewModel composables: state and actions of each screen
views/        # screens (XxxView.vue)
components/   # reusable pieces
router/
mocks/        # in-memory data used unless VITE_USE_MOCKS=false
```
