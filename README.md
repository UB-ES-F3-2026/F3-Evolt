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
| **Screaming Architecture** | Folders named by business features (`savings`, `transfers`, `auth`…), not by technical layers. |
| **MVVM** | Each feature uses **Model · ModelView · View** (ModelView = ViewModel). |
| **Clean Architecture** | View → ModelView → Services → ports → Firebase/API. Outer depends on inner. |
| **Shared Services** | Cross-feature business logic lives once in `shared/services` (middle layer). |
| **SOLID** | Small services, small ports, depend on interfaces, one reason to change. |
| **DRY** | Extract shared **business rules**; do not copy-paste them across features. |

```
src/
  features/<feature>/   # model · modelview · view · services
  shared/               # services · models · components · utils
  app/                  # shell, routing, composition root
```

Flow: **View event → ModelView command → Service → Model update → View re-render.**

### AI skills (lazy)

Skills live in the repo and load only when the task matches:

| Skill | Use when |
|-------|----------|
| `arch-structure` | folder layout, layers, SOLID/DRY, dependencies |
| `mvvm-patterns` | Vue 3 Model / ModelView (composables) / View |
| `backend-clean` | Firebase backend: use cases, ports, Cloud Functions |
| `firebase-stack` | Firebase Auth, Firestore, rules, adapters, config |
| `middle-services` | shared business services / middle layer |
| `shared-module` | cross-cutting models, utils, contracts |
| `code-style` | Vue + TS naming, SFC shape, design consistency |
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
- CI green; ≥1 teammate review

---

## Docs map

| Path | Content |
|------|---------|
| `AGENTS.md` | Engineering + AI standards (source of truth for code style) |
| `docs/P1/AGENTS.md` | Course context, Scrum, roles, backlog rules |
| `docs/P1/MEMORY.md` | Decisions and workflow memory |
| `docs/P1/Team Specification.md` | Product catalog + team |
| `docs/P1/backlog.md` | Product backlog |
| `docs/P1/trello-backlog.md` | Cards to copy into Trello |
