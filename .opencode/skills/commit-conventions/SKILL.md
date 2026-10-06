---
name: commit-conventions
description: Load when writing or fixing git commit messages for F3-Evolt — Conventional Commits format, types, scopes, US references, what not to commit. Use for every commit the team or AI produces.
---

# Commit conventions

**Conventional Commits + US reference.** Small, reviewable history.

## Format

```
<type>(<scope>): <short imperative subject> US-<id>
```

Optional body for “why” when needed. US id optional when there is no story (docs/chore).

## Types

| Type | When |
|------|------|
| `feat` | new user-facing capability |
| `fix` | bug fix |
| `docs` | documentation only |
| `style` | format / lint, no logic change |
| `refactor` | code change without behavior change |
| `test` | tests only |
| `chore` | tooling, deps, config |
| `ci` | pipeline |
| `perf` | performance |

## Scopes

```
auth  account  transfers  savings  gamification
multidivisa  movements  shared  firebase  ci  docs  app
```

Use the feature folder when possible. `shared` / `firebase` / `ci` / `docs` for cross-cutting work.

## Examples

```
feat(savings): create pot with target US-17
feat(savings): move money from balance to pot US-18
fix(auth): show generic error on bad login US-03
refactor(shared): extract password policy service US-01
docs: describe MVVM layout in AGENTS.md
test(savings): cover contribution validation US-18
chore: add emulator config for local dev
```

## Rules

- **Imperative mood**: “add”, not “added” / “adds” / “adding”.
- **One logical change** per commit (not “feat + reformat + typo”).
- **US-XX** when the commit implements part of a story (whole US preferred).
- Subject ≤ ~72 characters when possible; body explains why if needed.
- No secrets, keys, `node_modules`, build artifacts, local env files.
- Do not commit half-broken WIP to the main branch; use feature branches + PRs.

## What not to do

| Bad | Good |
|-----|------|
| `fix stuff` | `fix(auth): generic error on bad login US-03` |
| `feat: US-17 and US-18 and cleanup` | split commits / split PRs |
| `Updated files` | meaningful subject |
| commit with API keys | never |

## Self-check

- [ ] `type(scope): subject` parses
- [ ] Imperative subject
- [ ] US id present when applicable
- [ ] One logical change
- [ ] No secrets or junk files
