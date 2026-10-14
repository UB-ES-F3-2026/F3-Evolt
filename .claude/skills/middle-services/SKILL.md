---
name: middle-services
description: Load when adding or changing a business rule that more than one place needs — top-up and transfer limits, daily caps, XP rules, password policy, currency conversion, money parsing. Use to decide where the single owner of the rule lives and who may repeat it.
---

# Business rules live once

A **business rule** is something the product decides: “at most 500 € per top-up”, “at most 1.000 € per day”, “top-ups give no XP”. Each rule has **one owner**.

## Who owns a rule

| Rule | Owner | May repeat it |
|------|-------|---------------|
| Limits, balances, XP, anything about money | A backend service (`backend/app/services/`) | A ViewModel, only for faster feedback on screen |
| How an amount typed by the user becomes cents | A frontend model (`frontend/src/models/`) | Nobody — ViewModels import it |
| How an error code becomes a Catalan message | The ViewModel of that screen | Nobody |

The backend's answer always wins. A ViewModel check never replaces the service check.

## When to extract a module

Extract when the **same rule** is needed in 2+ places, e.g.:

- Daily limit (top-ups now, transfers later)
- Daily XP cap (gamification + savings)
- Password policy (register + reset password)
- Euros → cents parsing (top-up + contribute to pot)

Do **not** extract logic that only one service or one ViewModel uses.

## Placement rule

| Rule used by | Put it in |
|--------------|-----------|
| 1 backend service | That service |
| 2+ backend services | Its own module in `backend/app/services/`, imported by both |
| 1 ViewModel | That ViewModel |
| 2+ ViewModels | A pure module in `frontend/src/models/` |

## Shape of a shared rule

```python
# backend/app/services/daily_limit.py
DAILY_TOPUP_LIMIT_CENTS = 100_000

def remaining_today(topped_up_today_cents: int) -> int:
    return max(0, DAILY_TOPUP_LIMIT_CENTS - topped_up_today_cents)
```

- **Pure** when possible: values in, value out — easy to unit test.
- Reading and writing data stays in the service that calls it, through its repository.
- Limits are named constants, never numbers typed in the middle of a function.

## Anti-patterns

| Bad | Good |
|-----|------|
| The 500 € limit typed in two services | One named constant, imported |
| A limit enforced only in the ViewModel | The backend service enforces it; the ViewModel repeats it for UX |
| A shared rule that reads `seed.py` or calls a repository on its own | Pure function; the calling service passes the data in |
| A `utils` file collecting random helpers | A named module with one responsibility |

## Self-check

- [ ] The rule has one owner
- [ ] Money rules are enforced in a backend service
- [ ] Shared rule modules are pure
- [ ] Limits are named constants
- [ ] No copy of the rule elsewhere
