---
name: ci-cd
description: Load when creating or changing GitHub Actions workflows, ESLint config, npm check scripts, required status checks, branch protection, environments (pre-production, production), deploy hooks or health checks, or when debugging a red pipeline in F3-Evolt.
---

# CI/CD (F3-Evolt)

One pipeline, one required check. Workflow: `.github/workflows/ci.yml` (name `CI`).

## Pipeline map

```
PR / push to develop, main or story/**
        │
        ├── backend  (Python 3.12) ── ruff + compileall + pytest
        │
        └── frontend (Node 22)     ── lint + type-check + test + build
        │
        └──► ci   ← gate job: fails unless backend AND frontend are success

push to main (ci green) ──► Deploy   (see docs/deploy.md)
```

The two jobs run in parallel; `ci` waits with `if: always()` and points at
whichever failed. **`ci` is the only required status check** — a red `ci`
blocks merge, nothing else needs protection.

CI runs on story branches too: every task PR into a `story/**` branch, and
every push to one (a merged task, or `develop` merged in), gets the same checks
as a PR to `develop`. That is how a story is already green before it reaches
`develop` (skill `gitflow`).

## Non-negotiables

- **Single required check `ci`.** The gate job is named `ci`; every other job
  must be added to `ci.needs` so it actually gates the merge.
- **Job names = status-check names.** `backend`, `frontend`, `ci` appear as
  checks; keep them short and stable, never rename `ci`.
- **No `paths:` filters.** They break branch protection (a "no check reported"
  failure on files outside the filter). Every PR must always get a run.
- **Node 22 / Python 3.12** — pin these versions in setup actions; the team
  runs local versions freely, CI is the reference point.
- **`permissions: contents: read`** at workflow level. Least privilege; add
  nothing unless a step needs it.
- **No secrets in `ci.yml`.** CI runs checks only. Secrets belong to the
  deploy workflow and are gated by `DEPLOY_ENABLED`
  (see skill `pr-conventions` for the merge rules, `docs/deploy.md` for deploy).

## Recipe: add a check

1. **Extra step inside an existing job** — smallest change, no gate edits:

   ```yaml
   - name: Lint (ruff)
     run: python -m ruff check app tests
   ```

2. **New job** — add it as a sibling, then wire it into the gate:

   ```yaml
   docs:
     name: docs
     # ... steps ...
   ci:
     needs: [backend, frontend, docs]   # ← add the new job here
   ```

   Forgetting `ci.needs` makes the gate green while your new job fails —
   the gate only asserts what it waits for.

3. **Same command must fail locally first**: every CI step maps to a command
   in the table in `docs/ci-cd.md` (run with `cd <app>` first).

## Reproduce locally

```bash
(cd frontend && npm run check)          # lint + type-check + test + build
(cd backend  && .venv/bin/ruff check . && .venv/bin/python -m compileall -q app && .venv/bin/python -m pytest tests/ -q)
```

If `npm ci` behaves differently than `npm install`, the lockfile is out of
sync: `rm -rf node_modules && npm ci && npm run lint`.

## Branch protection (quick reference)

Exact commands live in `docs/branch-protection.md`. The shape:

- Required status check: **`ci`** — this exact name, one check for the whole pipeline.
- `develop` and `main`: PR + 1 approval + green `ci`, no direct pushes, no
  force pushes, no deletion (see skill `gitflow`).
- `story/**` branches are not protected on GitHub: the team rule is that only
  task PRs and the merge of `develop` land there.
- If any rule in `ci.yml` changes (job names, `paths:`, triggers), update
  branch protection in the same PR.

## Environments

The Sprint 1 review asked for **two identical deployed environments, only one of
them production**: test on pre-production, fix there, then promote.

| Environment | Branch | Status |
|-------------|--------|--------|
| **Production** | `main` | Live on Render: web `https://f3-evolt.onrender.com`, API `https://evolt-api.onrender.com`, Firestore. Redeployed by hand; the `Deploy` workflow stays dormant until `DEPLOY_ENABLED` is set (`docs/deploy.md`) |
| **Pre-production** | `develop` | **Not created yet** (DevOps, Sprint 2). Same setup as production, with its own Firestore data, never production's |

Until pre-production exists, check a story before its PR to `develop` by running
it locally from the story branch, with `STORAGE=firestore` on the Firestore
emulator (`backend/tests/test_firestore.py` explains how).

## Quality gates

What `ci` checks today: Ruff, compile check and pytest (backend, in memory);
ESLint, type-check, Vitest and build (frontend).

Not in `ci.yml` yet; do not assume they run (QA defines them, DevOps wires
them; skill `qa-strategy`): coverage report, the backend suite on the Firestore
emulator, E2E tests, dependency audit and secret scanning. When one is added,
it is a new job listed in `ci.needs` (recipe above).

## Self-check

- [ ] `ci` is the only required check and still named `ci`
- [ ] Every job is listed in `ci.needs`
- [ ] No `paths:` filters; triggers cover `pull_request` + `push` on `develop`, `main` and `story/**`
- [ ] `permissions: contents: read`; no new permissions without a reason
- [ ] No secrets or `.env` values in the workflow
- [ ] Node 22 / Python 3.12 / Ruff 0.17.3 pinned
- [ ] Same commands pass locally (`npm run check`, ruff + compileall + pytest)
- [ ] Workflow YAML parses: `python3 -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))"`
