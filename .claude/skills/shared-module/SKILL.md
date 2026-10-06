---
name: shared-module
description: Load when creating or changing cross-cutting models, value types, utilities, DTOs, error types, or shared UI used by more than one feature in F3-Evolt. Use for Money, User refs, movement types, shared enums, mappers, small pure helpers.
---

# Shared module — models, types, utils

`shared/` holds code that is **genuinely cross-feature**. Keep it small, pure, and stable.

## What belongs in `shared/`

| Kind | Examples | Folder |
|------|----------|--------|
| Domain models | `Money`, `UserRef`, `MovementType` | `shared/models/` |
| Shared services | XP cap, password policy | `shared/services/` |
| Shared UI | Button, empty state, error banner | `shared/components/` |
| Small pure utils | date format for display, clamps | `shared/utils/` (named modules) |

## What does NOT belong

- Feature-only entities → `features/<f>/model/`
- Feature-only services → `features/<f>/services/`
- Screen-specific widgets → `features/<f>/view/`
- A random `utils.ts` kitchen sink

## Model rules

- **Money**: represent amounts carefully (integer cents or explicit `Money` value type — pick one convention for the team and document it in the model).
- Prefer value objects over raw `number`/`string` for money and currency.
- Models are **pure**: no Firebase, no UI, no async I/O.
- Mappers (domain ↔ Firestore/DTO) live next to adapters or in `shared/models/` if used everywhere — **no business rules inside mappers**.

## Utils rules

- One concept per file: `shared/utils/moneyFormat.ts`, not `misc.ts`.
- Export pure functions only.
- If a util encodes a **business rule**, it is a **service**, not a util.

## Shared UI rules

- Presentational components only.
- Props-driven; no Firestore or ModelView imports inside shared UI.

## Dependency direction

```
features/*  →  shared/*
shared/*    →  (other shared or nothing)
shared/*    ↛  features/*
```

## DRY vs premature extraction

- Two features need the **same entity shape** → `shared/models/`.
- Two screens look similar but rules differ → **keep separate**; extract later if the rule unifies.

## Self-check

- [ ] Imported by more than one feature (or clearly will be)
- [ ] No feature imports from `shared` that create cycles
- [ ] Models pure; utils pure; shared UI presentational
- [ ] Named modules, not a junk drawer
- [ ] Money/currency conventions consistent project-wide
