# Demo review checklist (T06.4)

Manual review to run **after every successful `Deploy` run on `main`** and
**before every class demo**. It checks two things:

1. The deployed app works end-to-end from the public URL (demo script).
2. No secrets or configuration leaked into the repo.

Current status: **blocked** until #92/#93 give us public `FRONTEND_URL` and
backend URLs. Everything below assumes a live deployment.

---

## 1. Demo script (from the public URL)

Open `FRONTEND_URL` (the deployed frontend, e.g.
`https://f3-evolt.onrender.com`) and walk through:

| # | Check | What "pass" looks like |
|---|-------|------------------------|
| 1 | Home | Balance matches the seed, list shows the **last 5 movements** |
| 2 | Balance visibility toggle | Eye button hides/reveals the balance amount |
| 3 | Movements list | Paging/`loadMore` works if there are more than one page |
| 4 | Loading state | Spinner/skeleton visible while the API answers; if the UI looks instant, load is too fast — see "demo knobs" below |
| 5 | Empty state | The seed's second user (no movements) shows the empty message. The deployed build always sends `X-User-Id: 1`, so verify this locally against the public API: `cd frontend && VITE_USE_MOCKS=false VITE_DEMO_USER=2 npm run dev` |
| 6 | Error state | UI shows a user-safe error message, not a raw red screen |
| 7 | Top-up — happy path | Valid amount (e.g. 50 €) increases balance, new movement appears in the list |
| 8 | Top-up — invalid amount | `0`, negative or non-numeric → inline validation, no request sent |
| 9 | Top-up — over 500 € limit | Error (`amount_over_limit` family) shown, balance unchanged |
| 10 | Daily limit | Successive top-ups up to the 1 000 € daily cap → daily-limit error once exceeded |
| 11 | Fresh state before stateful runs | `POST /api/dev/reset` restores the seed — **disabled on the Render demo** (`ENABLE_DEV_ROUTES=false`, #92), so only use it on a local/controlled backend |

**Demo knobs** (only in a *controlled* demo environment, never default on the
deployed instance): backend env vars `SIMULATE_DELAY_MS` and
`SIMULATE_ERROR_RATE` make loading and error states easy to show; both are
documented in [`README.md → Simulating delay and failure`](../README.md) and
affect every request including `/api/health` (which is why the Deploy health
poll has a 5-minute tolerance).

## 2. Secret audit

Run from the repo root / `gh` authenticated session:

```bash
# what is registered, nothing readable
gh secret list
gh variable list

# spot-check history for leaked-looking strings
git log --all -p | rg -i "deploy_hook|api[_-]?key|secret|token|password"

# .env hygiene
git check-ignore -v frontend/.env          # must match: ignored on purpose
git log --all --oneline -- '*.env'         # must print nothing: never committed
```

Also open [`frontend/.env.example`](../frontend/.env.example) and confirm it
contains **only placeholders** (`http://localhost:8000`, flags) — the values
advertised to teammates must be the same local dev defaults, never deployed
URLs or keys.

## 3. Record the result

Add a comment on issue #95 with:

- date + reviewer
- deployed commit SHA (`git rev-parse --short HEAD` / shown in the run)
- which checks passed / failed (table above)
- screenshots (optional)

## 4. Current status

- [ ] Public `FRONTEND_URL` available → **pending #93**
- [ ] Public backend + `/api/health` reachable → **pending #92**
- [ ] First full pass of this checklist after the first real deploy (`DEPLOY_ENABLED=true`)
