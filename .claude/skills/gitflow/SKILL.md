---
name: gitflow
description: Load when branching, merging, opening PRs, naming branches, targeting the right base branch, releasing, or hotfixing in F3-Evolt. Use for any git branch workflow question — feature branches, develop/main, hotfix, cleanup, and how commits map to PRs.
---

# GitFlow (F3-Evolt)

Course + team branch model. GitHub is mandatory; product docs vs develop stay separated.

## Branch map

| Branch | Role | Who merges |
|--------|------|------------|
| `main` | Demo / release-oriented line (course “product” branch) | After PR from `develop` or release |
| `develop` | Integration line for the current sprint work | Feature PRs target **this** |
| `feature/<slug>` | One US or one technical task | PR → `develop` |
| `fix/<slug>` | Bugfix for an open issue / AC failure | PR → `develop` |
| `refactor/<slug>` | Behavior-preserving cleanup (one module) | PR → `develop` |
| `hotfix/<slug>` | Urgent fix on `main` when demo is broken | PR → `main` (and cherry-pick / merge to `develop`) |
| `release/<version>` | Optional freeze before final demo (S3) | Team agreement |

`<slug>` = short kebab-case story or task: `savings-create-pot`, `auth-generic-login-error`, `ci-emulator`.

## Everyday flow

```
develop
  └── feature/savings-create-pot     ← create from develop
        commits: feat(savings): … US-17
        PR → develop (one US)
        review + CI green
        merge (squash or merge — team pick one and stay consistent)
```

1. `git switch develop && git pull`
2. `git switch -c feature/<slug>`
3. Small commits (`commit-conventions`)
4. Push + PR → **`develop`**
5. Reviewer checks AC + architecture (`pr-conventions`)
6. Merge; delete branch

## Naming rules

```
feature/savings-create-pot
fix/auth-generic-login-error
refactor/shared-extract-password-policy
hotfix/saldo-negative-transaction
```

- Lowercase, hyphens, no spaces.
- Optional: include US id — `feature/us17-savings-create-pot` if the team prefers.
- Do not use `feature/JIRA-123-Long description with spaces`.

## PR targeting

| Change | Base branch |
|--------|-------------|
| Normal US / tech task | `develop` |
| Demo-breaking bug on `main` | `hotfix/*` → `main`, then sync `develop` |
| Final release (end of course) | `release/*` → `main` after team check |

**One US / one technical task per PR** (see `pr-conventions`).

## Commit ↔ branch ↔ PR

| Piece | Example |
|-------|---------|
| Branch | `feature/savings-create-pot` |
| Commit | `feat(savings): create pot with target US-17` |
| PR title | `feat(savings): create pot with target US-17` |

## Rules

- Never commit directly to `develop` or `main` (except agreed hotfix path).
- Keep `feature/*` short-lived — merge within the sprint slice.
- No secrets, build junk, or personal `.env` on any branch (already gitignored).
- If `develop` moves under you: rebase or merge `develop` into your branch before PR review.
- Delete remote branch after merge.

## Cleanup

```sh
git branch -d feature/savings-create-pot
git push origin --delete feature/savings-create-pot
```

## Course note

- **Product definition** (backlog, US docs) lives under `docs/P1/` — not mixed into feature code PRs.
- **Sprint work** goes through `develop` → PR → demo on `main` per class schedule.
- Final pitch branch policy: confirm with the team in Sprint 3 (`release/` if needed).

## Self-check

- [ ] Branch name matches type + short slug
- [ ] Created from latest `develop` (or agreed base)
- [ ] Commits follow `commit-conventions`
- [ ] PR targets `develop` (unless hotfix/release)
- [ ] One US / one technical task
- [ ] Branch deleted after merge
