# CLAUDE.md

Read **[`AGENTS.md`](AGENTS.md)** — it is the source of truth for architecture, MVVM, Clean Architecture, SOLID/DRY, skills, commits and PRs.

## Always

- Follow `AGENTS.md` for code structure and quality bar.
- Follow `docs/api.md` for every route, field name and error code.
- Load the matching lazy skill from `.claude/skills/` (or `.opencode/skills/`) when the task needs it.
- Prefer clear, traceable solutions over clever shortcuts.
- Never bypass layers (no API call from a View, no `seed.py` access from a backend service).

## Stack

- **Frontend:** Vue 3 + JavaScript (SFC `<script setup>`), Vite, Vue Router, Vitest — in `frontend/`
- **Backend:** Python + FastAPI, pytest, data in memory — in `backend/`
- **MVVM:** Model · ViewModel (composable `useXxxViewModel`) · View, in folders by layer

## Skills index

| Skill | Use for |
|-------|---------|
| `arch-structure` | folders, layers, SOLID/DRY |
| `mvvm-patterns` | Vue 3 Model / ViewModel / View |
| `backend-clean` | FastAPI routers, services, repositories |
| `middle-services` | business rules used in more than one place |
| `shared-module` | reusable models, components, helpers |
| `code-style` | naming and file shape |
| `comments-docs` | comments policy |
| `gitflow` | branches, develop/main, PR base |
| `pr-conventions` | pull requests |
| `commit-conventions` | commit messages |

Product/backlog context: `docs/P1/`.
