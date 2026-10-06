---
name: backend-clean
description: Load when writing backend logic on Firebase — Cloud Functions, use cases, repositories/ports, atomic Firestore transactions, callable functions, security rules enforcement, server-side validation for F3-Evolt (auth, transfers, savings, gamification, multidivisa).
---

# Backend on Firebase — Clean Architecture

There is **no custom Node server** in this project. Backend = **Firebase** (Functions + Firestore + Auth).

Rules live in **use cases**; Firebase only appears in **adapters** and thin **function entries**.

## Layering

```
[Cloud Function entry]           callable / https / trigger
        ↓
[Use case / feature service]     features/<f>/services/ or shared/services
        ↓
[Port — interface]               e.g. SavingPotRepository, UserGateway
        ↓
[Adapter — Firebase]             Firestore / Auth / Messaging adapters
```

Dependency rule still holds: outer → inner; use cases never import `firebase/*` directly.

## Where logic runs

| Kind of logic | Where |
|---------------|--------|
| Pure domain (money math, progress %) | model / shared services — **can run client or Functions** |
| Authorization + atomic money moves | **Cloud Functions** (server) |
| Read-heavy UI queries | Client via adapter + **security rules** |
| Admin / config (XP values) | Functions + Firestore config docs |
| Password policy check | Shared service used by Auth flows (client UX + server if enforced server-side) |

**Client** may validate for UX; **Functions** enforce the real invariants (balance, limits, ownership).

## Use-case style

One use case = one public entry = one clear outcome.

| Use case | Responsibility |
|----------|----------------|
| `ContributeToPot` | authz → validate → **transaction** principal↓ pot↑ → movements → XP policy hook |
| `SendMoney` | authz → balance → atomic transfer → notify |
| `CreateSavingPot` | authz → validate → create doc |

Public entry on the function: `execute(...)` or a thin callable wrapper.

## Ports

Small, business-named; implemented only by Firebase adapters:

```ts
interface SavingPotRepository {
  create(pot: SavingPot): Promise<void>
  findById(userId: string, potId: string): Promise<SavingPot | null>
  moveFunds(tx: ContributeTx): Promise<void> // adapter uses Firestore tx
}
```

## Cloud Functions patterns

### Callable (preferred for app commands)

```ts
// functions/contributeToPot.ts  (shape — not production glue)
export const contributeToPot = onCall(async (request) => {
  const uid = request.auth?.uid
  if (!uid) throw new HttpsError('unauthenticated', 'Sign in required')
  const result = await contributeToPotUseCase.execute(uid, request.data)
  return result
})
```

- **Thin handler:** parse input → auth uid → use case → return DTO.
- No business rules in the handler beyond input shaping.
- Use **callable** for commands that need trusted server logic.

### Triggers (secondary)

- Firestore triggers only for true async side effects (notifications, denormalized counters) **after** the money path succeeds.
- Do not move the money mutation into a random trigger without a clear reason.

## Atomic money (TR-03)

Financial moves are **all or nothing**:

```ts
await db.runTransaction(async (tx) => {
  const account = await tx.get(accountRef)
  // check balance inside tx
  tx.update(accountRef, { balance: newBalance })
  tx.update(potRef, { balance: newPotBalance })
  tx.set(movementRef, movement)
})
```

- Contribute / transfer / pot withdraw: **one transaction**.
- On failure: no partial balances; typed error to the client.
- Design for **idempotency** where a retry could double-charge.

## Validation order (use case)

1. Authenticated `uid` (from `request.auth`, never from client body alone)
2. Domain invariants (amount > 0, limits, atomicity)
3. Authorization (resource belongs to caller)
4. Persistence (transaction)
5. Side effects (XP, push) only after success

## Security rules (must match use cases)

- Deny by default.
- User paths: `request.auth.uid == userId` (or documented admin claim).
- Rules are **not** a second copy of business logic — they gate access; use cases enforce domain rules when the client could bypass rules.
- Test with emulators before demo.

## Errors

| Layer | Style |
|-------|--------|
| Use case | Typed result / stable codes (`INSUFFICIENT_BALANCE`, …) |
| Function | Map to `HttpsError` / HTTP status |
| Client | User-safe messages in ModelView |

Never return raw Firestore errors to the UI.

## Composition

- Shared policies (`DailyXpCap`, `PasswordPolicy`, FX rules) → `shared/services/`.
- Feature services **call** shared services inside use cases.
- Adapters per aggregate (users, accounts, pots, movements) — not one mega-repo.

## Self-check

- [ ] Function entry is thin (auth + call use case + respond)
- [ ] Use cases depend on ports, not `firebase/*`
- [ ] Money moves use `runTransaction` / batch
- [ ] Authorization uses authenticated uid
- [ ] Shared rules not duplicated in Functions
- [ ] Errors typed; client messages safe
