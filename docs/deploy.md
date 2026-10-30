# Deploy runbook (T06.3)

Auto-deploy to a hosting provider. The workflow lives in
[`.github/workflows/deploy.yml`](../.github/workflows/deploy.yml).

Hosting is **not decided yet** (issues #92 backend / #93 frontend, open). Until
then the workflow is **provider-agnostic** (driven by repository
secrets/variables) and **dormant**: it runs on every push to `main` and stays
green with all deploy jobs skipped.

---

## Trigger and order

```
push to main / manual (workflow_dispatch)
        │
        ▼
      ci            ← reusable CI (.github/workflows/ci.yml), must be green
        │
        ▼
deploy-backend    ← POST to the backend deploy hook (Render example)
        │
        ▼
verify-health     ← poll GET {BACKEND_HEALTH_URL}/api/health until 200
        │           (20 attempts × 15 s = 5 min budget)
        ▼
deploy-frontend   ← npm ci + build against the real API,
        │           POST to the frontend deploy hook (Netlify/Vercel example)
        ▼
(optional)        ← poll FRONTEND_URL until 200 (12 × 15 s),
                    runs only when FRONTEND_URL is set
```

- Deploy jobs never run on `develop` or PRs — only `push` to `main` and
  `workflow_dispatch`.
- `concurrency: deploy-<ref>` with `cancel-in-progress: false`: two rapid
  pushes to `main` queue up instead of interrupting a half-done deploy.

## The `DEPLOY_ENABLED` gate

Every deploy job has `if: vars.DEPLOY_ENABLED == 'true'`.

- **Unset or anything other than exactly `true`** → the three deploy jobs are
  skipped and the workflow run is **green**.
- **`true`** → the chain runs: hook → health poll → frontend build + hook.

This is **deliberate**: `main` gets pushes every sprint, but the hosting
providers only exist after #92/#93. Without the gate, every merge to `main`
would be red while hosting is missing. Only set the variable to `true` when
hosting is actually wired up.

## Secrets and variables

Set them in **repository** settings (Settings → Secrets and variables →
Actions).

| Name | Kind | Required to enable deploys | What it is |
|------|------|--------|------------|
| `BACKEND_DEPLOY_HOOK` | **secret** | yes | Render deploy hook URL — contains a token, never logged |
| `FRONTEND_DEPLOY_HOOK` | **secret** | yes | Netlify build hook URL — contains a token, never logged |
| `BACKEND_HEALTH_URL` | variable | yes | Base URL of the backend, e.g. `https://f3-evolt-api.onrender.com`; also the frontend API base |
| `PUBLIC_API_URL` | variable | no | Only if the public API base differs from the health URL; wins over `BACKEND_HEALTH_URL` when set |
| `FRONTEND_URL` | variable | no | Enables the final "public frontend responds" check |
| `DEPLOY_ENABLED` | variable | gate | `true` = deploy chain runs; unset = everything skips, workflow green |

Hook URLs are stored as **secrets** (they contain a token and can trigger a
deploy on anyone who knows them). Plain public URLs are **variables** so
they can be listed and audited without opening each secret.

## Example wiring: Render (backend) + Netlify (frontend)

**Backend — Render:**

1. New → *Web Service* → connect this repo → root `backend/`,
   environment **Python 3**.
2. Build command: `pip install -r requirements.txt`
   Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. Render injects `$PORT`; health check path `/api/health`.
4. Settings → *Deploy hook* → copy the URL (looks like
   `https://api.render.com/deploy/srv-XXXXXXXXXXXX?...` — **secret**).

**Frontend — Netlify:**

1. New site from this repo → base directory `frontend/`.
2. Build command: `npm run build`, publish directory `dist` (relative to the
   `frontend/` base).
3. Site settings → *Environment variables*: `VITE_API_URL` = backend public
   URL, `VITE_USE_MOCKS=false`.
4. Site configuration → *Build hooks* → copy the URL (**secret**).
5. Add a **SPA redirect** so deep links don't 404: in `frontend/` add
   `netlify.toml` with `/*  /index.html  200` (or set it in the Netlify UI
   under *Redirects*).

**Set everything from the CLI:**

```bash
# secrets (never printed back)
gh secret set BACKEND_DEPLOY_HOOK   # paste the Render hook URL
gh secret set FRONTEND_DEPLOY_HOOK  # paste the Netlify build hook URL

# variables
gh variable set BACKEND_HEALTH_URL -b "https://f3-evolt-api.onrender.com"
gh variable set FRONTEND_URL        -b "https://f3-evolt.netlify.app"
gh variable set DEPLOY_ENABLED      -b "true"
# only if the API base differs from the health URL:
# gh variable set PUBLIC_API_URL   -b "https://api.f3-evolt.example"
```

## First deploy checklist

1. Hosting live per the example above (#92/#93 done).
2. Set all secrets/variables (see table).
3. `gh variable set DEPLOY_ENABLED -b "true"` — **last**.
4. Open the release PR from `develop` to `main` and merge it (or run the
   workflow manually) so a push to `main` fires the deploy chain.
5. Watch it:

   ```bash
   gh run watch $(gh run list --workflow=Deploy --limit 1 --json databaseId -q '.[0].databaseId')
   ```

6. `curl https://<BACKEND_HEALTH_URL>/api/health` → `{"status":"ok"}`.
7. Open `FRONTEND_URL`, do a pass of [`docs/demo-review.md`](demo-review.md).

## Manual re-run

```bash
gh workflow run deploy.yml --ref main
# or in the browser: Actions → Deploy → Run workflow → main
```

Note: the reusable `ci` job always runs; the deploy chain only runs if
`DEPLOY_ENABLED == 'true'`.

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Deploy jobs show "skipped", run green | `DEPLOY_ENABLED` not exactly `true` | `gh variable set DEPLOY_ENABLED -b "true"` |
| `::error::BACKEND_DEPLOY_HOOK secret is not set` | Secret missing | `gh secret set BACKEND_DEPLOY_HOOK` |
| `::error::FRONTEND_DEPLOY_HOOK secret is not set` | Secret missing | `gh secret set FRONTEND_DEPLOY_HOOK` |
| `::error::BACKEND_HEALTH_URL variable is not set` | Variable missing | `gh variable set BACKEND_HEALTH_URL -b "https://…"` |
| Health poll times out (5 min) | Free tier **cold start** (first boot takes longer than the budget), wrong URL, or the app crashed | Cold start: rerun once; check the Render dashboard/logs; confirm the URL answers manually with `curl` |
| Frontend 404 on refresh / deep link | Missing SPA redirect | Add the `/* /index.html 200` redirect on the static host |
| CORS errors in the browser console | Backend allows only localhost | Configure the deployed frontend origin in the backend deploy environment (#92 owns backend config) |

## Security

- Hook URLs contain a **token** anyone could POST-to → they live in secrets,
  never in code, docs or logs. The workflow never echoes them.
- No `env:` block at workflow level: secrets exist only inside the step that
  uses them.
- If a hook leaks (in a screenshot, log, chat…): **rotate it** — Render/Netlify
  regenerate the URL on demand — then update `gh secret set`.
- Whether `/api/dev/*` routes (dev reset) are exposed in the deployed backend
  is a backend-deployment decision → issue #92. Default for the demo
  environment should be documented there.

## Status

Automation is **ready**; the gate keeps `main` green while hosting is missing.
The acceptance criterion of #94 ("merging to `main` produces a real deploy")
can only be **verified** after #92 and #93 provide the public URLs.
