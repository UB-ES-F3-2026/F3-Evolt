---
name: backend-clean
description: Load when writing backend code in Python with FastAPI — routers, services, repositories, models, seed data, validation, error responses, pytest tests for F3-Evolt (home, movements, top-ups and later auth, transfers, savings, gamification).
---

# Backend on FastAPI — Clean layers

Backend = **Python + FastAPI**, tested with **pytest**. During Sprint 0 the data lives **in memory**, loaded from `data/seed.py` at start-up; a real database comes in a later sprint.

Every route, field and error code is fixed by `docs/api.md`. Read it before writing an endpoint.

## Layering

```
backend/app/
  routers/        endpoints
      ↓
  services/       business logic
      ↓
  repositories/   access to the data
      ↓
  models/  +  data/seed.py
```

Each layer calls only the one below it.

| Layer | Does | Must not |
|-------|------|----------|
| **Router** (`routers/home.py`) | Read the request, call one service, return the contract's JSON | Hold business rules; touch repositories |
| **Service** (`services/topup_service.py`) | Validate, apply limits, decide what changes | Read `seed.py`; know about HTTP |
| **Repository** (`repositories/`) | Read and write the in-memory data | Decide business rules |
| **Model** (`models/`) | Data classes with the contract's fields | Import FastAPI |

Services reach the data **only** through repositories. Swapping memory for a database later must mean rewriting `repositories/` and nothing else.

## Service style

One function = one use case = one clear outcome.

| Use case | Responsibility |
|----------|----------------|
| Home summary | balance + sum of all pots + 5 most recent movements |
| List movements | newest first, `offset`/`limit`, compute `nextOffset` |
| Top up | validate → check limits → add to balance → create the movement |

## Validation order (top-up, from the contract)

Stop at the first error:

1. Body shape: `amount` missing or not an integer → `VALIDATION_ERROR`
2. Per-top-up limits: `amount ≤ 0` → `INVALID_AMOUNT`; `amount > 50000` → `AMOUNT_OVER_LIMIT`
3. Daily limit: today's top-ups + `amount > 100000` → `DAILY_LIMIT_EXCEEDED` with `details.remainingToday`

## All or nothing

If a request ends in an error, **nothing changes**: neither the balance nor the movements. Validate everything first, write last.

## Money and dates

- Amounts are **integer cents**, always positive. `type` (`income` / `expense`) gives the direction, never the sign.
- Dates are ISO 8601 with the `Europe/Madrid` offset.
- “Today” is the calendar day in `Europe/Madrid`, whatever the server's time zone.
- A top-up is found by the internal field `kind == "topup"`, never by its concept text. `kind` is not returned by the API.

## Current user

There is no login in Sprint 0: user 1 by default, or the one in the `X-User-Id` header. Resolve it in one dependency; services receive the user id as a parameter.

## Errors

| Layer | Style |
|-------|-------|
| Service | Reports the failure with a stable code (`INVALID_AMOUNT`, …) |
| Global handler | Turns it into `{ code, message, details? }` with the contract's HTTP status |
| Unexpected failure | `INTERNAL_ERROR` (500), never a stack trace |

`message` is Catalan text for people. `details` appears only when the error has some.

## Tests

- pytest, in `backend/tests/`.
- Reset the in-memory data before each test so the order does not matter.
- Cover the edges the contract names: exactly 500 €, 500,01 €, the third top-up of the day, a user with no movements, invalid `offset`/`limit`.

## Self-check

- [ ] The router is thin (read request → call service → respond)
- [ ] The service reads and writes only through repositories
- [ ] Response keys, types and error codes match `docs/api.md`
- [ ] On error nothing was modified
- [ ] Amounts are integer cents; “today” uses `Europe/Madrid`
- [ ] Tests reset the data and pass
