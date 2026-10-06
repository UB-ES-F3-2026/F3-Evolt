---
name: firebase-stack
description: Load when touching Firebase product APIs and config — Auth, Firestore, security rules, Hosting, emulators, Firebase config, client SDK adapters, Cloud Functions wiring, env/secrets for F3-Evolt. Use for setup, adapters, rules, and Firebase project config (not Vue UI).
---

# Firebase stack (platform & adapters)

Firebase is the **driver** at the outer edge of Clean Architecture.  
Business rules live in services/use cases; Firebase appears in **adapters**, **functions entries**, and **config**.

Related skill: `backend-clean` (use cases, ports, atomic money on the Firebase backend).

## Boundary

```
ModelView / use case
        ↓ port (interface)
Firebase adapter     ← ONLY place with Firestore/Auth SDK for that rule
```

**Never:** `getFirestore()` / `getAuth()` inside a `.vue` file or ModelView composable.

## Project layout (Firebase)

```
firebase.json          # config (per repo policy)
functions/             # Cloud Functions (Node + TS)
  src/...
firestore.rules        # security rules
firestore.indexes.json
```

Respect existing `.gitignore` (no secrets, no emulator junk, no `functions/.env`).

## Auth (client + rules)

| Concern | Pattern |
|---------|---------|
| Session | `onAuthStateChanged` in one auth service/gateway → session state for ModelView |
| Register / login / reset | Feature services + shared password policy |
| Route guards | Vue Router guard using auth service — not inside every component |
| Ownership | Always `auth.currentUser.uid`; never trust uid from form data |

Client adapter example shape:

```ts
// features/auth/services/adapters/firebaseAuthGateway.ts
export class FirebaseAuthGateway implements AuthGateway {
  onAuthStateChanged(cb) { ... }
  signIn(email, password) { ... }
}
```

## Firestore (adapters)

- Collection paths documented per feature, e.g. `users/{uid}/pots/{potId}`.
- Adapters map **documents ↔ domain models** (no business rules in mappers).
- Prefer explicit fields; avoid nested blobs juniors cannot trace.
- Queries: filter in the query when possible.
- **Money:** adapter methods that mutate balances **must** use transactions/batches (see `backend-clean`).

```ts
export class FirestoreSavingPotAdapter implements SavingPotRepository {
  // only this file imports firestore SDK for pots
}
```

## Security rules

- Deny by default; allow only what the feature needs.
- Check `request.auth.uid` on every user-scoped path.
- Rules gate **access**; domain invariants stay in use cases when client-side rules are not enough.
- Ship rules with the feature that needs them — not a giant unreadable file without comments for “why”.
- Verify with **emulators** before demo.

## Cloud Functions wiring

- Deployable from `functions/`; handlers stay thin (`backend-clean`).
- Callable for commands with server trust; triggers only for async side effects.
- Config via Functions env / config — **never commit secrets**.
- Local: Firebase emulators for Auth + Firestore + Functions when possible.

## Emulators & local dev

- Prefer emulators for Auth + Firestore while iterating.
- Do not point demo clients at production data casually.

## Hosting / app shell

- Hosting (if used) serves the Vue build; app shell still owns routing and DI.
- Client Firebase config (public keys) is OK; **service account / private keys are not** in the repo.

## Self-check

- [ ] Firebase SDK only in adapters + functions + config
- [ ] Auth ownership uses authenticated uid
- [ ] Money mutations in adapters/functions use transactions
- [ ] Rules match feature access needs; tested with emulators
- [ ] No secrets committed
- [ ] Vue views/composables clean of `firebase/*`
