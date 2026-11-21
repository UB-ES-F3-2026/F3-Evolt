---
name: pr-conventions
description: Load when creating, updating, or reviewing a pull request for F3-Evolt — task PRs into a story branch, story PRs into develop, release PRs into main, title format, body structure, scope, DoD checklist, architecture checklist, review rules. Use before opening any PR.
---

# Pull request conventions

PRs are how we deliver **one clear change** with a review trail. Since the
Sprint 1 review there are three kinds, one per level of the branch model
(skill `gitflow`):

| Kind | Head → base | Holds | Merges when |
|------|-------------|-------|-------------|
| **Task PR** | `feature/<layer>/<tNN-N-slug>` → `story/us-<id>-<slug>` | One task of the story | CI green + 1 review |
| **Story PR** | `story/us-<id>-<slug>` → `develop` | The whole story, frontend + backend | Everything in the story checklist below |
| **Release PR** | `develop` → `main` | The sprint | Pre-production checked + 1 review |

Technical tasks and docs outside any story (`feature/devops/…`, `docs/…`) and
fixes open a task PR straight into `develop`, and only if the change is
complete on its own.

## Title

Same shape as commits:

```
feat(savings): pot detail endpoint US-19                    ← task PR
feat(savings): see the detail of a pot US-19                ← story PR (the story itself)
fix(auth): generic error on bad login US-03
ci: run CI on story branches
```

- Conventional type + scope
- Imperative mood
- US id when the change maps to a story

## Scope

| Allowed | Not allowed |
|---------|-------------|
| One task (task PR) or one whole story (story PR) | A task PR into `develop` while its story is still open |
| Related tests for that change | Half a story in `develop` ("the backend comes next week") |
| | Five stories in one PR |
| | Unrelated formatting of other files |

## Body: task PR

```markdown
## What
Short description of the change.

## Why
Story and task: US-XX, TXX.X (issue #N).

## How
Layers touched (View / ViewModel / Model, or Router / Service / Repository).

## AC mapping
- [ ] AC 1 … → test that proves it
- [ ] AC 2 … → test that proves it

## Screenshots
UI: next to the story's mockup; empty / loading / error states.

## Checklist
- [ ] Base is the story branch (not `develop`)
- [ ] Commits follow commit-conventions
- [ ] Architecture: correct layers (no API call from a View, no `seed.py` access from a service)
- [ ] Shared rules not duplicated
- [ ] Tests added per skill `qa-strategy` (each AC or rule has a test that names it)
- [ ] Nothing invented: every screen element, message and button comes from the story or its mockup
- [ ] Tests pass (`vitest` / `pytest`)
- [ ] Self-review: I read the whole diff and ran the tests before asking for review
```

## Body: story PR

```markdown
## Story
US-XX: value statement. Trello card / issue #N. Mockup: link.

## Task PRs in this story
- #… backend: …
- #… frontend: …

## Acceptance
- Acceptance tests run on the story branch: `docs/proves-….md` IDs …, all pass
- Automated tests per AC: AC 1 → test …, AC 2 → test …
- PO acceptance: link to the comment on the story issue

## Sync
`develop` merged into the story branch at <sha>; every test passes after it.

## Bugs
Found while integrating, and the test that now covers each one.
```

Story PR checklist (all must be true before it merges):

- [ ] Every task PR of the story is merged into the story branch
- [ ] Latest `develop` merged into the story branch; CI green after that
- [ ] The whole flow works from the story branch, and its acceptance tests pass
- [ ] The PO accepted the story on the story branch
- [ ] No critical bug open for the story
- [ ] Merged with a merge commit (no squash), so every task stays traceable

## Review

- **Self-review first.** Before asking for review, the author reads the whole
  diff, runs the tests and ticks the self-review line of the checklist.
- **One reviewer.** One teammate, never the author, reviews the PR, approves it
  and merges it. No second approval is needed, contracts included: pick the
  teammate who will use the change most (e.g. frontend for a backend contract).
- Reviewer checks **architecture + AC**, not only syntax. On a story PR, the
  reviewer also checks the story checklist above.
- A screen that does not match the story or its mockup is a review comment,
  even if it looks good: the fix is to refine the story with the PO (skill
  `user-stories`), not to keep the invention.
- AI may draft the PR body; **humans** approve merges.

## DoD reminder (course + tech)

1. Code committed
2. Dev tests pass
3. AC verified
4. Help/doc if user-facing
5. PO accepts (on the story branch)
6. PR self-reviewed, then reviewed, approved and merged by one teammate
7. CI green; the story reaches `develop` whole, and `develop` stays deployable
8. No critical open bugs for that story
9. Architecture checklist respected

## Self-check before requesting review

- [ ] Right kind of PR, right base branch
- [ ] Title + body follow the template for that kind
- [ ] Exactly one task (task PR) or one story (story PR)
- [ ] AC mapped to tests
- [ ] Architecture checklist done
- [ ] No secrets, no build junk in the diff
- [ ] Self-review done: whole diff read, tests run, said in the PR
