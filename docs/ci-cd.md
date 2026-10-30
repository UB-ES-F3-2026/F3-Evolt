# CI/CD

This repo has one GitHub Actions pipeline ([`.github/workflows/ci.yml`](../.github/workflows/ci.yml)).
It runs the backend and frontend checks on every PR and push to `develop`/`main`,
and a final gate job `ci` that is the **required status check for merging**.

- Workflows: GitHub Actions, defined in `.github/workflows/ci.yml` (job name `CI`).
- Environments: **Node 22** for the frontend, **Python 3.12** for the backend.
- Permissions: the workflow requests only `contents: read` (least privilege; no secrets needed).
- Deploy: `main` pushes trigger the deploy step (see `docs/deploy.md`, arrives in a later PR).

---

## Pipeline map

```
                            ┌──────────────┐
        PR / push ─────────►│    checkout  │
        to develop / main   └──────┬───────┘
                                   │
              ┌────────────────────┴─────────────────────┐
              ▼                                          ▼
        ┌───────────┐                            ┌───────────┐
        │  backend  │                            │ frontend  │
        │  (py3.12) │                            │ (node 22) │
        │ compileall│                            │   lint    │
        │   pytest  │                            │ type-check│
        │           │                            │   test    │
        │           │                            │   build   │
        └─────┬─────┘                            └─────┬─────┘
              └──────────────────┬──────────────────────┘
                                 ▼
                          ┌───────────┐
                          │    ci     │   ← gate: both must be green
                          └───────────┘

            push to main (green ci) ──► Deploy  (see docs/deploy.md)
```

- PR / push to `develop` or `main` → the two jobs `backend` and `frontend` run in parallel.
- Both finish → the **gate job `ci`** marks the whole pipeline pass/fail.
- Push to `main` → after green `ci`, the deploy flow takes over (later effort).
- Manual runs (`workflow_dispatch`) and reusable runs (`workflow_call`) are supported.

## How to read a run

- **In the browser:** repo → *Actions* tab → pick the run → the `ci` job shows
  the overall state; click the red step inside `backend` / `frontend` to see the logs.
- **From the terminal:**

```bash
gh pr checks                 # status of every check on the current PR
gh run list --limit 5        # recent runs
gh run view --log-failed     # only the failing steps of the last run
```

**What "green/red" means:** the required check is `ci`. If `backend` or
`frontend` fails, `ci` fails with it (it waits with `if: always()` and then
asserts both results are `success`). Merge is blocked while `ci` is red.

## Check ↔ local command

Every CI step maps to a command you run locally first:

| CI job | Step | Local command (run from repo root) |
|--------|------|------------------------------------|
| backend | Compile check | `cd backend && .venv/bin/python -m compileall -q app` |
| backend | pytest | `cd backend && .venv/bin/python -m pytest tests/ -q` |
| frontend | Lint | `cd frontend && npm run lint` |
| frontend | Type check | `cd frontend && npm run type-check` |
| frontend | Unit tests | `cd frontend && npm run test` |
| frontend | Build | `cd frontend && npm run build` |
| frontend | (all four above) | `cd frontend && npm run check` |
| ci | gate | everything above green |

If it works locally, it almost certainly works in CI — same commands, slightly
different versions (**CI pins Node 22 and Python 3.12; your local versions may
be newer** — a tiny local-only difference is possible but rare).

## Adding or editing a check

Rules for changing `.github/workflows/ci.yml`:

1. **Step vs job:** a *step* is one extra line inside an existing job
   (e.g. add `ruff` to the `backend` job before `pytest`). A *job* is a new
   parallel lane (e.g. a `docs` job).
2. **If you add a job, add it to `ci.needs`** — otherwise the gate can go green
   while your new job fails (it only asserts what it waits for).
3. **Never rename `ci`.** It is THE required status check name; renaming breaks
   branch protection silently.
4. **Never add `paths:` filters**, and if you must, update branch protection
   (with `paths:` filters, skipped-trigger runs report the check as failed on
   unrelated PRs — see `docs/branch-protection.md`).
5. Keep `permissions: contents: read`; add threat minimization, not power.
6. No secrets in `ci.yml`; secrets belong to deploy workflows only
   (see `docs/deploy.md`).

## Reproduce CI locally

Before pushing, run what CI runs:

```bash
# frontend — all four checks in one line
cd frontend && npm run check

# backend — compile check + pytest
cd backend
.venv/bin/python -m compileall -q app
.venv/bin/python -m pytest tests/ -q
```

Notes:

- `npm run check` = `npm run lint && npm run type-check && npm run test && npm run build`.
- CI installs with `npm ci` (clean, lockfile-driven). If your local run passes
  but CI fails right after `npm ci`, your `package-lock.json` is out of sync;
  `rm -rf node_modules && npm ci && npm run lint` reproduces it.
- CI pins **Node 22 / Python 3.12**; check your local versions with
  `node --version` / `python --version` if results differ.

## Failure triage

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `ci` red, `backend` green, `frontend` red | One frontend step failed | Red step in the run → same command locally |
| `Lint` fails only on CI | ESLint version differs (`~` vs `^`), or local uncommitted files | `npm ci`, re-run locally |
| `npm ci` fails in CI | `package-lock.json` out of sync | Re-install locally with the lock (`rm -rf node_modules && npm ci`), commit the lock |
| `pytest` fails only on CI | Local data state (in-memory seed) or Python version | Read the failing test; CI uses Python 3.12 |
| `ci` red although both jobs green | Gate run was from an older definition / manual skip | Re-run; never rename `ci` |
| Both jobs red right after checkout | YAML syntax broken | `python3 -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))"` |
| No run at all | Push touched only filtered paths — **must not happen**: the workflow has no `paths:` filters | Remove the filter |

## Related docs

- See `docs/branch-protection.md` (later PR): required status check `ci`, no pushes straight to `develop`/`main`.
- See `docs/deploy.md` (later PR): what runs after `main` is green, and `DEPLOY_ENABLED`.
