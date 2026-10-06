---
name: pr-conventions
description: Load when creating, updating, or reviewing a pull request for F3-Evolt — PR title format, body structure, scope, DoD checklist, architecture checklist, branch targets, review rules. Use before opening any PR.
---

# Pull request conventions

PRs are how we deliver **one clear change** with a review trail.

## Title

Same shape as commits:

```
feat(savings): create pot with target US-17
fix(auth): generic error on bad login US-03
refactor(shared): extract daily XP cap US-23
```

- Conventional type + scope
- Imperative mood
- US id when the change maps to a story

## Scope of a PR

| Allowed | Not allowed |
|---------|-------------|
| One user story / AC slice | Five stories in one PR |
| One technical task (spike, refactor of one module) | “Cleanup of everything” |
| Related tests for that change | Unrelated formatting of other files |

**One US or one technical task per PR.**

## Body (template)

```markdown
## What
Short description of the change.

## Why
US ref / problem solved. Link backlog or US id (US-XX).

## How
Layers touched (View / ModelView / Service / shared / firebase).

## AC mapping
- [ ] AC 1 …
- [ ] AC 2 …

## Screenshots
UI: before/after or empty/loading/error states.

## Checklist
- [ ] Commits follow commit-conventions
- [ ] Architecture: correct layers (no UI→Firebase)
- [ ] Shared rules not duplicated
- [ ] Tests added/updated where required
- [ ] Help/doc text updated if user-facing
- [ ] CI green
- [ ] DoD ready for review
```

## Branch / target

- Branches: `feature/<slug>`, `fix/<slug>`, `refactor/<slug>` from `develop` (see skill `gitflow`).
- Target: **`develop`** for normal work; `main` only for hotfix/release paths per gitflow.
- Do not merge to `main` directly without review + green CI (per course rules).

## Review

- At least **1 teammate** reviews (course DoD proposal).
- Reviewer checks: **architecture + AC**, not only syntax.
- AI may draft the PR body; **humans** approve merge.

## DoD reminder (course + tech)

1. Code committed  
2. Dev tests pass  
3. AC verified  
4. Help/doc if user-facing  
5. PO accepts  
6. PR reviewed  
7. CI green; staging/demo deployable  
8. No critical open bugs for that story  
9. Architecture checklist respected  

## Self-check before request for review

- [ ] Title + body follow the template
- [ ] Exactly one US / technical task
- [ ] AC mapped
- [ ] Architecture checklist done
- [ ] No secrets, no build junk in the diff
