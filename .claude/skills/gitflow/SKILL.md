---
name: gitflow
description: Load when branching, merging, opening PRs, naming branches, targeting the right base branch, starting or finishing a user story, syncing with develop, releasing, or hotfixing in F3-Evolt. Use for any git branch workflow question — story branches, task branches, develop/main, pre-production, hotfix, cleanup, and how commits map to PRs.
---

# GitFlow (F3-Evolt)

Rule number one, from the Sprint 1 review: **`develop` never breaks.** It
always builds, passes every test and works end to end. Anyone who starts new
work branches from `develop` and must get a version that works.

To get there, every user story has **its own branch**. The story's frontend and
backend tasks are integrated there, and the story reaches `develop` **only
when it is complete**: every task merged, tested on top of the latest
`develop`, and accepted by the PO.

## Branch map

| Branch | Starts from | PR into | Role |
|--------|-------------|---------|------|
| `main` | — | — | **Production.** Receives `develop` at the end of a sprint (release PR) or a `hotfix/*` |
| `develop` | — | — | **Integration, always working.** Receives whole stories, self-contained technical tasks and fixes. Will deploy to pre-production (DevOps, Sprint 2) |
| `story/us-<id>-<slug>` | `develop` | `develop` | **One user story.** Its frontend and backend tasks integrate here |
| `feature/<frontend\|backend\|devops>/<tNN-N-slug>` | the story branch | the story branch | **One task** of that story |
| `feature/devops/<trNN-N-slug>`, `docs/<slug>` | `develop` | `develop` | Technical task or doc change **outside any story**, only if it is complete on its own |
| `fix/<slug>` | `develop` (or the story branch if the bug is in an unmerged story) | where it started | Bug fix |
| `refactor/<slug>` | `develop` | `develop` | Behaviour-preserving cleanup of one module |
| `hotfix/<slug>` | `main` | `main`, then `develop` | Production is broken |

Examples for US-19:

```
story/us-19-pot-detail
  feature/backend/t19-1-pot-detail-endpoint
  feature/frontend/t19-2-pot-detail-screen
```

- Lowercase, hyphens, no spaces. The US id goes in the story branch; the T code
  goes in the task branch.
- The prefix is `story/`, not `feature/us-19`: git cannot have both a branch
  `feature/us-19` and branches under `feature/us-19/…`.

## Story flow

```
develop ──┬──────────────────────────────────────────────┬──► develop (still green)
          │ 1. create story branch                       │ 6. PR story → develop
          ▼                                              │
   story/us-19-pot-detail ──┬──── 3. task PRs ───────┬──►│ 4. sync with develop
                            │                        │   │ 5. PO accepts on the story branch
                            ├─ feature/backend/t19-1 ┤
                            └─ feature/frontend/t19-2┘
```

1. **Create the story branch** (whoever starts the story; first check the story
   is ready: skill `user-stories`):

   ```bash
   git switch develop && git pull
   git switch -c story/us-19-pot-detail
   git push -u origin story/us-19-pot-detail
   ```

2. **Contract first.** If the story changes `docs/api.md`, that is its first task
   PR into the story branch, reviewed by one teammate (whoever uses it most).
3. **Each task:** branch from the story branch, small commits, PR **into the
   story branch**. CI runs on it; the author self-reviews, then one teammate
   reviews, approves and merges.

   ```bash
   git switch story/us-19-pot-detail && git pull
   git switch -c feature/frontend/t19-2-pot-detail-screen
   ```

4. **Keep the story branch in sync with `develop`.** Every time `develop` moves,
   and always right before the story PR: merge `develop` into the story branch,
   run every test, and push.

   ```bash
   git switch story/us-19-pot-detail && git pull
   git merge origin/develop          # resolve conflicts here, not in develop
   (cd backend && python -m pytest tests/ -q) && (cd frontend && npm run check)
   git push
   ```

   The story branch is shared, so use **merge, not rebase**: a rebase rewrites
   commits that teammates' task branches are built on. Rebase only your own,
   unshared task branch.
5. **The whole story works on its branch:** run the app from the story branch,
   go through its acceptance tests (`docs/proves-*.md`), and the **PO accepts it
   there**, before it reaches `develop`.
6. **PR story → `develop`** (skill `pr-conventions`): CI green, one approval,
   merge with a merge commit (no squash, so each task stays traceable).
   `develop` deploys to pre-production; check it there (until pre-production
   exists, see skill `ci-cd` → Environments).
7. **End of sprint:** release PR `develop` → `main` after pre-production has
   been checked.

## What went wrong in Sprint 1, and how we avoid it

| What happened | Now |
|---------------|-----|
| Every task PR went straight to `develop`, so `develop` held half-built stories (screens on mocks before their endpoint existed) | Tasks go into the story branch; `develop` only gets whole stories |
| Integration was coordinated over WhatsApp ("have you finished that API?") | The story branch is the meeting point; the story PR lists what is in it |
| Code merged without being tested against the latest `develop` | Merge `develop` into the story branch and run every test before the story PR |
| The first time everything ran together on a server was the release to `main` | `develop` deploys to pre-production; `main` only gets what was checked there |

## Rules

- Never commit straight to `develop` or `main` (branch protection blocks it).
- Push straight to a story branch only to create it or to merge `develop`
  into it. Everything else arrives through a task PR.
- A task PR never targets `develop` while its story is open.
- A story branch lives for one sprint at most. A story that does not fit was
  too big; split it with the PO.
- No secrets, build junk or personal `.env` on any branch.
- Merged branches are deleted (the repo does it automatically).

## Self-check

- [ ] Task branch starts from its story branch, and its PR targets the story branch
- [ ] Story branch starts from `develop`, named `story/us-<id>-<slug>`
- [ ] Story branch has the latest `develop` merged in, and every test passes on it
- [ ] The PO accepted the story on its branch before the PR to `develop`
- [ ] Only whole stories, self-contained tasks and fixes reach `develop`
- [ ] Commits follow `commit-conventions`
