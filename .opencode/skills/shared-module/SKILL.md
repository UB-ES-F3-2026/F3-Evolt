---
name: shared-module
description: Load when creating or changing code that several screens or services reuse in F3-Evolt — frontend models, JSON mappers, reusable components, small pure helpers, backend data classes. Use for money amounts, the Movement model, movement types, icon lists, shared UI pieces.
---

# Reusable code — models, components, helpers

With folders by layer, `models/` and `components/` are used by every screen. Keep them small, pure and stable.

## What goes where

| Kind | Examples | Folder |
|------|----------|--------|
| Frontend types, models and mappers | `movement.ts` (the `Movement` type, API JSON → app object) | `frontend/src/models/` |
| Reusable UI | `MoneyAmount.vue`, `MovementRow.vue`, `EmptyState.vue` | `frontend/src/components/` |
| Small pure helpers | euros ↔ cents, date for display | `frontend/src/models/` (named modules) |
| Backend data classes | `User`, `Account`, `Pot`, `Movement` | `backend/app/models/` |

## What does NOT belong there

- State of one screen → its ViewModel
- Markup that belongs to one screen only → that view
- A random `utils.ts` kitchen sink

## Model rules

- **Money**: integer cents, always positive (`50000` = 500 €). The direction comes from `type` (`income` / `expense`), never from the sign.
- Each contract object has **one type**, declared in `models/` and imported everywhere. Field names and types are the ones in `docs/api.md`. Closed lists (the `icon` values) are copied from there, not invented.
- Models are **pure**: no Vue reactivity, no HTTP, no UI.
- Mappers only change shape — **no business rules inside mappers**.

## Helper rules

- One concept per file: `models/money.ts`, not `misc.ts`.
- Export pure functions only.
- If a helper encodes a **business rule**, see skill `middle-services`.

## Reusable component rules

- Presentational only: props in, events out.
- No ViewModel and no service call inside.
- Handle the unknown case (e.g. a default icon when an unknown `icon` arrives).

## Dependency direction

```
views → viewmodels → services → models
views → components
models → (nothing)
```

## DRY vs premature extraction

- Two screens need the **same piece** → `components/` or `models/`.
- Two screens look similar but behave differently → **keep them separate**; extract later if they converge.

## Self-check

- [ ] Used by more than one screen or service (or clearly will be)
- [ ] Models pure; helpers pure; components presentational
- [ ] Named modules, not a junk drawer
- [ ] Money is integer cents; names match `docs/api.md`
