---
name: qa-strategy
description: Load when writing or reviewing tests, deciding what and how to test, writing acceptance tests (docs/proves-*.md), measuring coverage, fixing a bug (regression test), or preparing the quality part of a sprint review in F3-Evolt — pytest, Vitest, Firestore emulator, E2E, security tests, coverage and quality metrics.
---

# Quality strategy (F3-Evolt)

At the Sprint 1 review we could not answer "**what is our quality strategy, and
what do these tests prove?**". Running hundreds of tests without knowing what
they check is not a strategy. Everyone tests by these rules; the QA role owns
this file and changes it when the team agrees.

## 1. What we test, and with what

| Level | Tool | Where | Must prove | In CI |
|-------|------|-------|------------|-------|
| Business rules | pytest | `backend/tests/` | Every rule of each service: limits, validations, what changes | yes |
| API contract | pytest + `TestClient` | `backend/tests/` | Every route in `docs/api.md`: the success answer, **each error `code` listed for it**, and `401` without a session | yes |
| Storage | pytest + Firestore emulator | `tests/test_firestore.py`, and the whole suite with `TEST_STORAGE=firestore` | The Firestore repositories behave like the in-memory ones (that is what production runs) | **no**, local only |
| Frontend logic | Vitest | `*.test.ts` next to the file | ViewModels: every state (loading, empty, error, success) and every AC they own. Services: the request and the error mapping. Models: pure functions. Router guards | yes |
| Acceptance | `docs/proves-*.md` | one table per story | Every AC has rows with an ID (`D-03` API, `DP-10` screen); the API rows become pytest tests | by hand |
| End to end | Playwright (proposal; QA decides) | — | The main flow of each story in a real browser against the real backend | **no**, not yet |
| Security | pytest + tooling | API tests; dependency audit and secret scanning to add | Generic login error, lockout, sessions that expire, protected routes. No vulnerable dependency, no secret in the repo | partly |

## 2. Rules for every test

1. **Its name says what it proves**, with the AC or acceptance-test ID:
   `it('keeps the real amount with the amounts hidden on screen (DP-10)')`.
   If you cannot name it, you do not know what it tests.
2. **One behaviour per test.** Expected values come from the seed, written out
   (`379521`), not recomputed with the code under test.
3. **New route** → its contract tests (success, each error code, `401`) in the
   same PR.
4. **New screen** → ViewModel tests for every state, plus its rows in
   `docs/proves-*.md`.
5. **Bug found** → first a test that fails because of it, then the fix. Say in
   the PR that a test found it, or that it slipped past the tests.
6. Test behaviour, not implementation: no test that only checks a mock returned
   what the same test told it to return.
7. Each AC of a story maps to at least one test (pytest, Vitest or E2E);
   the story PR lists that mapping (skill `pr-conventions`).

## 3. Metrics (report them at every sprint review)

| Metric | How | Target |
|--------|-----|--------|
| Line coverage, backend and frontend | commands below | **80 %** each (the figure the professor gave) |
| Routes with contract tests | routes in `backend/app/routers/` vs tests | 100 % |
| ACs with an automated test | the story PRs' AC mapping | every AC of the sprint |
| What the tests caught | bugs found by a test vs found by a person (PRs and issues) | write it down; it answers "did the tests help?" |

Baseline, `develop` on 2026-11-10:

- **Backend 77 %** (710 tests). All 18 routes have tests. The Firestore
  repositories are at 0 % because CI runs in memory; without them, 95 %.
- **Frontend 63.6 %** (342 tests): viewmodels 92 %, models 94 %, services 60 %,
  components 55 %, router 12.5 %, views 0 % (views are for E2E).

Measure locally. Neither coverage tool is a project dependency yet; install it
in your own environment:

```bash
# backend
pip install pytest-cov
(cd backend && python -m pytest tests/ -q --cov=app --cov-report=term)

# frontend (same version as vitest; --no-save leaves package.json alone)
(cd frontend && npm i --no-save @vitest/coverage-v8@$(node -p "require('vitest/package.json').version") \
  && npx vitest run --coverage --coverage.include='src/**')
```

## What went wrong in Sprint 1, and how we avoid it

| What happened | Now |
|---------------|-----|
| No answer to "what is the quality strategy?" | Section 1 is the answer; QA presents it at the review |
| "It should be tested": tests ran without anyone knowing what they proved | Every test names its AC or rule (rule 1) |
| No metric for success | Coverage, routes, ACs and bugs caught, reported every sprint |
| The Firestore code that production runs was never tested in CI | Emulator job in CI (QA defines, DevOps wires); meanwhile run it before every story PR that touches storage |
| Screens were only checked by hand | E2E for the main flow of each story (QA decides the tool) |

## Self-check

- [ ] Every new rule, route and screen has its tests in the same PR
- [ ] Test names say what they prove, with the AC or test ID
- [ ] Every AC of the story maps to a test
- [ ] A bug fix comes with the test that would have caught it
- [ ] Coverage did not go down
