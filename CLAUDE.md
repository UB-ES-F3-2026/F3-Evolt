# CLAUDE.md

Read **[`AGENTS.md`](AGENTS.md)** — it is the source of truth for architecture, MVVM, Clean Architecture, SOLID/DRY, skills, commits and PRs.

## Always

- Follow `AGENTS.md` for code structure and quality bar.
- Load the matching lazy skill from `.claude/skills/` (or `.opencode/skills/`) when the task needs it.
- Prefer clear, traceable solutions over clever shortcuts.
- Never bypass layers (no Firebase in View/ModelView).

## Stack

- **Frontend:** Vue 3 + TypeScript (SFC `<script setup lang="ts">`)
- **Backend:** Firebase (Cloud Functions + Firestore + Auth) — no separate custom server
- **MVVM:** Model · ModelView (composable) · View inside each feature

## Skills index

| Skill | Use for |
|-------|---------|
| `arch-structure` | folders, layers, SOLID/DRY |
| `mvvm-patterns` | Vue 3 Model / ModelView / View |
| `backend-clean` | Firebase use cases, Functions, atomic money |
| `firebase-stack` | Auth, Firestore, rules, adapters |
| `middle-services` | shared business services |
| `shared-module` | cross-feature models/utils |
| `code-style` | Vue + TS naming and SFC shape |
| `comments-docs` | comments policy |
| `gitflow` | branches, develop/main, PR base |
| `pr-conventions` | pull requests |
| `commit-conventions` | commit messages |

Product/backlog context: `docs/P1/`.
