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
backend/app/     # middleware · models · repositories · services · routers · data/seed.py
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
| `ci-cd` | GitHub Actions, lint, branch protection, deploy |

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
cp .env.example .env      # optional: VITE_* vars are read from frontend/.env
npm install
npm run dev               # dev server on http://localhost:5173
npm run lint              # ESLint (flat config)
npm run type-check        # TypeScript check (vue-tsc)
npm run build             # type-check + production build
npm run check             # lint + type-check + tests + build (what CI runs)
npm run preview           # serve the production build
```

Copying `.env.example` is optional for a first run: the in-memory mocks are
**on by default**. Set `VITE_USE_MOCKS=false` in `frontend/.env` to call the
real API (and `VITE_API_URL` to point at it).

---

## Backend

Python + FastAPI, in [`backend/`](backend/). Data lives in memory (seed). Run every command from `backend/`.
Backend-specific setup, Ruff and troubleshooting: [`backend/README.md`](backend/README.md).

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

### Request collection & manual testing (T09.6)

[`docs/api.http`](docs/api.http) is an example request collection — one request
per endpoint plus every documented error case (invalid amount, over 500 €,
daily limit exceeded, user without movements, …). Open it with the **REST
Client** extension in VS Code or the **HTTP Client** in IntelliJ/JetBrains and
run the requests one by one; uvicorn must be running
(`uvicorn app.main:app --reload`).

`POST /api/dev/reset` restores the in-memory seed without restarting the
server. Run it before any stateful sequence — e.g. the daily-limit chain in the
collection — so the results are reproducible. The collection can be combined
with the T08.2 simulation env vars (set them when starting uvicorn).

When `ENABLE_DEV_ROUTES=false` (see [Deploy](#deploy-tr061)) this endpoint does
not exist.

### Environment variables

Every backend setting comes from the environment. With nothing set, the backend
runs exactly as in local development.

| Variable | Default | Effect | Secret |
|----------|---------|--------|--------|
| `FRONTEND_ORIGINS` | `http://localhost:5173` | Comma-separated origins allowed by CORS (no trailing slash needed) | No |
| `ENABLE_DEV_ROUTES` | `true` | `false` removes `/api/dev/*`; a misspelled value also disables them | No |
| `SIMULATE_DELAY_MS` | off | See [Simulating delay and failure](#simulating-delay-and-failure-t082) | No |
| `SIMULATE_ERROR_RATE` | off | See [Simulating delay and failure](#simulating-delay-and-failure-t082) | No |

**Adding a variable or a secret?** Add a row here in the same PR and tell the
person in charge of the deploy, so it is set on Render too. Secrets go only in
the Render dashboard, never in the repo. **Adding a request header** in the
frontend (e.g. `Authorization`)? Add it to `allow_headers` in
`backend/app/main.py`, or the browser will block the request.

### Deploy (TR06.1)

The backend runs on [Render](https://render.com) (free plan) as a Web Service:

- **Public URL:** https://evolt-api.onrender.com (e.g. [`/api/health`](https://evolt-api.onrender.com/api/health))
- **Branch:** `main` (the demo line); redeploy manually from the Render
  dashboard until automatic deploys exist (TR06.3)

| Render setting | Value |
|----------------|-------|
| Root directory | `backend` |
| Runtime | Python (version pinned in `backend/.python-version`) |
| Build command | `pip install -r requirements.txt` |
| Start command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Health check path | `/api/health` |

| Variable on Render | Value |
|--------------------|-------|
| `ENABLE_DEV_ROUTES` | `false` — nobody can reset the demo data |
| `FRONTEND_ORIGINS` | `https://f3-evolt.onrender.com` (the deployed frontend, TR06.2) |

Quick check: `curl https://evolt-api.onrender.com/api/health` → `{"status":"ok"}`.
The root URL `/` has no route, so it answers `500 INTERNAL_ERROR` like any unknown path.

Things to know about the free plan:

- After ~15 minutes without requests the service sleeps; the next request
  wakes it up and takes 30–60 s. Open the URL a couple of minutes before a demo.
- Data still lives in memory: every restart or sleep resets it to the seed.

---

## CI/CD

![CI](https://github.com/UB-ES-F3-2026/F3-Evolt/actions/workflows/ci.yml/badge.svg)

GitHub Actions pipeline in [`.github/workflows/ci.yml`](.github/workflows/ci.yml): every PR (and push) to `develop` or `main` runs two parallel jobs and a gate:

| Job | Runs | Version |
|-----|------|---------|
| `backend` | Ruff + compile check + pytest | Python 3.12 |
| `frontend` | ESLint + type-check + Vitest + build | Node 22 |
| `ci` | gate: both jobs must succeed | — |

**`ci` is the required status check: a PR can only merge when it is green.**

### Triggers

`ci.yml` listens to four events. Several triggers are **OR**; the filters inside
one trigger are **AND**.

| Trigger | When it runs | Notes |
|---------|--------------|-------|
| `pull_request` → `develop`, `main` | PR opened, updated (new push) or reopened | Default types: `opened`, `synchronize`, `reopened`. Runs on the synthetic merge commit. Merging does not re-run it (`closed` is not included). |
| `push` → `develop`, `main` | A commit lands on the branch (e.g. a merge) | It does not allow direct pushes; branch protection blocks those. Feature-branch pushes are covered by the PR's `synchronize` event. |
| `workflow_dispatch` | Manual run from *Actions* → *Run workflow*, or `gh workflow run ci.yml --ref develop` | Dormant until the workflow exists on the default branch (`main`). `pull_request`/`push` already work from `develop`. |
| `workflow_call` | Another workflow calls this one | `deploy.yml` calls it so deploy reuses this CI instead of duplicating it. |

No `paths:` filters on purpose: a required check that is skipped (e.g. a
docs-only PR) stays pending and blocks the PR forever.

How to read green/red: `gh pr checks` in a PR, or the repo's *Actions* tab →
click the failing job → read the red step's logs. Locally, run the same
commands (frontend: `npm run check`; backend: Ruff + compile check + pytest).

Full guide: [`docs/ci-cd.md`](docs/ci-cd.md).

---

## Docs map

The only complete list of documents; the others link here.

| Path | Content |
|------|---------|
| `README.md` | Project + AI workflow overview (this file) |
| `AGENTS.md` | Engineering + AI standards (source of truth for code style) |
| `CLAUDE.md` | Entry point for Claude Code; points to `AGENTS.md` |
| `.claude/skills/` · `.opencode/skills/` | The 11 lazy AI skills (same content in both) |
| `docs/api.md` | API contract shared by backend and frontend |
| `docs/api.http` | Example request collection for manual API testing (T09.6) |
| `docs/ci-cd.md` | CI/CD pipeline: jobs, how to read runs, how to edit |
| `backend/README.md` | Backend setup, Ruff config/commands and troubleshooting |
| `docs/branch-protection.md` | Rules on develop/main, how to apply/roll back |
| `docs/deploy.md` | Auto-deploy from main: gate, secrets/variables, Render example |
| `docs/demo-review.md` | Post-deploy demo script and secret audit (#95) |
| `docs/P1/AGENTS.md` | Course context, Scrum, roles, backlog rules |
| `docs/P1/MEMORY.md` | Team decisions, US and epic index |
| `docs/P1/Team Specification.md` | Product catalog + team |
| `docs/P1/trello-backlog.md` | Cards to copy into Trello (all US and epics) |
| `docs/P1/backlog.md` | Detailed backlog of block P2 (Savings) |
| `docs/P1/plantejament.md` | Notes from the first class |
| `docs/P1/PDFs/` | Class material |
