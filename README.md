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
| **Stack** | Frontend: Vue 3 + TypeScript, Vite, Vue Router, Vitest. Backend: Python + FastAPI, pytest, data in memory. |
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
  feature/<slug>   fix/<slug>   refactor/<slug>   hotfix/<slug>
```

### Commits

```
feat(savings): create pot with target US-17
```

`type(scope): short imperative subject US-XX`

### PRs

- One US or one technical task per PR
- Branch `feature/<slug>`, `fix/<slug>` or `refactor/<slug>` → PR base **`develop`**
- Only `hotfix/<slug>` goes from `main` → PR base `main`
- Title mirrors the commit
- Body maps work to acceptance criteria
- Architecture checklist + DoD before request for review
- Tests pass; ≥1 teammate review

---

## Frontend

Vue 3 + TypeScript + Vite, in [`frontend/`](frontend/).

```bash
cd frontend
cp ../.env.example .env   # optional: VITE_* vars are read from frontend/.env
npm install
npm run dev               # dev server on http://localhost:5173
npm run type-check        # TypeScript check (vue-tsc)
npm run build             # type-check + production build
npm run preview           # serve the production build
```

Copying `.env.example` is optional for a first run: the in-memory mocks are
**on by default**. Set `VITE_USE_MOCKS=false` in `frontend/.env` to call the
real API (and `VITE_API_URL` to point at it).

---

## Backend

Python + FastAPI, in [`backend/`](backend/). Data lives in memory (seed). Run every command from `backend/`.

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload    # API on http://localhost:8000
python -m pytest tests/          # tests
```

Quick check: `curl http://localhost:8000/api/health` → `{"status":"ok"}`.
The frontend talks to this API when `frontend/.env` sets `VITE_USE_MOCKS=false`
(see [Frontend](#frontend)).

### Simulating delay and failure (T08.2)

Two optional environment variables make every response slower or fail, to
exercise the frontend's loading and error states. Both are **off** when unset
or empty; a malformed or out-of-range value is ignored with a server warning.

| Variable | Type | Effect |
|----------|------|--------|
| `SIMULATE_DELAY_MS` | integer ≥ 0 | Adds a fixed delay (milliseconds) to every response |
| `SIMULATE_ERROR_RATE` | float 0–100 | Percentage of requests answered with a 500 `INTERNAL_ERROR` |

```bash
SIMULATE_DELAY_MS=800 uvicorn app.main:app --reload          # every response +800 ms
SIMULATE_ERROR_RATE=25 uvicorn app.main:app --reload         # ~1 in 4 requests fails
SIMULATE_ERROR_RATE=100 uvicorn app.main:app --reload        # every request fails
```

The simulation affects **every** request, including `/api/health`.

---

## Docs map

The only complete list of documents; the others link here.

| Path | Content |
|------|---------|
| `README.md` | Project + AI workflow overview (this file) |
| `AGENTS.md` | Engineering + AI standards (source of truth for code style) |
| `CLAUDE.md` | Entry point for Claude Code; points to `AGENTS.md` |
| `.claude/skills/` · `.opencode/skills/` | The 10 lazy AI skills (same content in both) |
| `docs/api.md` | API contract shared by backend and frontend |
| `docs/P1/AGENTS.md` | Course context, Scrum, roles, backlog rules |
| `docs/P1/MEMORY.md` | Team decisions, US and epic index |
| `docs/P1/Team Specification.md` | Product catalog + team |
| `docs/P1/trello-backlog.md` | Cards to copy into Trello (all US and epics) |
| `docs/P1/backlog.md` | Detailed backlog of block P2 (Savings) |
| `docs/P1/plantejament.md` | Notes from the first class |
| `docs/P1/PDFs/` | Class material |
