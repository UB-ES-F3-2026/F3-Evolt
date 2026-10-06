---
name: middle-services
description: Load when creating shared business services or a middle layer between UI and data — XP rules, limits, currency conversion, password policy, atomic balance moves, cross-feature orchestration. Use when logic is needed by more than one feature or sits between ModelView and Firebase.
---

# Shared services / middle layer

**Middle layer** = business logic used by more than one feature, living **between** presentation and data backends.

Location: `src/shared/services/` (or `src/middle/services/` if the team names the folder `middle`).

## When to create a shared service

Create it when the **same business rule** appears in 2+ features, e.g.:

- Password policy (register + reset password)
- Daily XP cap (gamification + savings)
- Daily recharge / transfer limits (account + transfers)
- Currency conversion + fee rules (multidivisa + payments)
- Atomic principal↔pot move (savings + future shared pots)

Do **not** create it for one feature’s private logic.

## Placement rule

| Rule used by | Put it in |
|--------------|-----------|
| 1 feature only | `features/<f>/services/` |
| 2+ features | `shared/services/` |
| Pure data shared by all | `shared/models/` |

Feature services **call** shared services. Shared services never call features or views.

## Shape of a shared service

```ts
// shared/services/dailyXpCap.ts
export class DailyXpCap {
  // policy object or config
  check(userId: string, action: XpAction, amount: number): XpDecision
}
```

- **Pure policy** when possible (easy to unit test).
- **Side effects** (persistence, Firestore) stay in adapters / feature services — shared services expose the rule; adapters apply it.

## Layer responsibilities (middle)

| Piece | Role |
|-------|------|
| Shared domain services | XP rules, limits, conversion, password policy |
| Ports + adapters | Firestore/Auth behind interfaces |
| Cross-cutting policies | daily limits, atomic balance moves |
| DTO mappers | domain ↔ API/Firestore shape (no business rules) |

## Composition

```
SavingsModelView
  → SavingsService (feature)
      → DailyXpCap (shared)          # rule
      → SavingPotRepository (port)
          → FirestorePotAdapter      # data
```

Same `DailyXpCap` is reused by gamification without copying the cap logic.

## Anti-patterns

| Bad | Good |
|-----|------|
| XP cap logic pasted in `savings/` and `gamification/` | One `DailyXpCap` in `shared/services/` |
| Shared service imports a feature folder | Shared imports only models/ports |
| Shared service renders or knows screens | Pure business + ports only |
| “Utils” folder collecting random helpers | Named shared **services** with one responsibility |

## Self-check

- [ ] Used by (or clearly needed by) 2+ features, or is a true cross-cutting policy
- [ ] Lives under `shared/` (or `middle/`), not duplicated
- [ ] No imports from `features/*` or `view/*`
- [ ] Single responsibility; testable without UI
- [ ] Feature services compose it; they do not copy it
