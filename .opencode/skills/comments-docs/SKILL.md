---
name: comments-docs
description: Load when adding or reviewing code comments, docstrings, markdown help text, or user-facing documentation for features. Use when unsure how much to comment or how to document business rules in F3-Evolt code.
---

# Comments & documentation

We comment **why**, not **what**. Comments must help the next junior, not restate code.

## Rules

| Do | Don’t |
|----|-------|
| Explain a non-obvious **business rule** | `// increment counter` above `counter++` |
| Document a **financial invariant** | Restate the function name |
| Note a **workaround** and when to remove it | Leave “TODO: fix later” with no owner |
| Link to US / TR when relevant | Comment every import |
| Document public API of a service briefly | Wall of comments in view widgets |

## What deserves a comment

1. **Financial invariants** — e.g. “contributions move money atomically; never partial writes”.
2. **Hidden coupling** — e.g. “daily XP cap also enforced in gamification feature”.
3. **Security decisions** — e.g. “generic login error to avoid user enumeration” (see US-03).
4. **Limits from product** — recharge max 500€, 1000€/day, etc., if not obvious from constants.
5. **Workarounds** with a condition to delete.

## What does not

- Obvious assignments, getters, loops
- JSDoc that only copies the signature (useful API docs are OK when the contract is non-obvious)
- Decorative banner comments

## Example

```ts
// Password rules come from US-01 (min 8, one uppercase, one digit).
// Shared with password reset — do not duplicate in reset flow.
export function isPasswordStrong(pw: string): boolean { ... }
```

```ts
// counter += 1  ← unnecessary comment
```

## User-facing docs

- Help text / empty states / error strings live with the feature (copy or constants) — **clear wording**, no developer jargon in the UI.
- When a US is implemented, check whether help/doc text is part of DoD (course DoD).
- Product docs stay in `docs/P1/`; code comments stay in code.

## PR expectation

- Reviewer asks: “Could a teammate understand this without the author?”
- No comment noise on PRs that only restate code.

## Self-check

- [ ] Comments explain why / rule / risk
- [ ] No redundant “what” comments
- [ ] Business rules documented once (prefer service/model over UI)
- [ ] User-facing strings are product-clear
- [ ] DoD help/doc updated when user-facing
