# Backend — FastAPI

In-memory backend for F3-Evolt. The API contract is [`../docs/api.md`](../docs/api.md).
Layers: **Router → Service → Repository → Models**; data is seeded at start-up.
Architecture rules live in [`../AGENTS.md`](../AGENTS.md).

## Requirements

- Python **3.12** (same version as CI; see [`../docs/ci-cd.md`](../docs/ci-cd.md))
- `pip`

## Setup

```bash
cd backend
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload
```

`POST /api/dev/reset` restores the in-memory seed without restarting the server.
Stateful manual tests should call it first (see the root README).

## Tests

```bash
python -m pytest tests/ -q
```

CI runs exactly this command with Python 3.12.

## Lint — Ruff

Ruff is the Python **linter**. It analyses code without running it and catches
unused imports, undefined names, import order, likely bugs and outdated syntax.
It is a **dev tool**, not a runtime dependency: it is **not** in
`requirements.txt`; CI installs it separately.

### Config

[`pyproject.toml`](pyproject.toml) is the only Ruff configuration:

```toml
[tool.ruff]
line-length = 120
target-version = "py312"

[tool.ruff.lint]
select = ["E4", "E7", "E9", "F", "I", "B", "UP"]
```

| Code | What it checks | Example |
|------|----------------|---------|
| `E4` | import conventions | two imports on one line, import after code |
| `E7` | statement rules | bare `except:`, `== None`, `lambda` assigned to a name |
| `E9` | syntax/runtime errors | file that cannot be parsed |
| `F` | pyflakes | undefined name, unused import/variable |
| `I` | isort | import order and grouping |
| `B` | flake8-bugbear | likely bugs (e.g. `zip()` without `strict=`) |
| `UP` | pyupgrade | modern syntax for the target version (e.g. `datetime.UTC`) |

`E501` (line length) is **not** selected: it is style only. The `line-length`
value is still useful if we ever run `ruff format`.

### Commands

```bash
cd backend

uvx ruff check .              # same check as CI
uvx ruff check . --fix        # apply only safe fixes
uvx ruff check . --statistics # errors grouped by rule
uvx ruff rule B905            # explain one rule
uvx ruff check . --show-files # which files are linted
```

`uvx` downloads Ruff temporarily. To keep it in the venv:

```bash
.venv/bin/pip install ruff==0.17.3
.venv/bin/ruff check .
```

### Reading the output

```
tests/test_seed.py:99:32: B905 `zip()` without an explicit `strict=` parameter
```

- `file:line:column`
- rule code (`B905`)
- message; often followed by a `help:` block with the suggested fix

Any error makes Ruff exit with code 1, so CI fails. Warnings do not exist in
Ruff: every finding is an error.

### What Ruff does not do

| Tool | Checks |
|------|--------|
| Ruff | static style/bug rules (this document) |
| `compileall` | only that the file can be compiled |
| `pytest` | behaviour |
| `mypy` / `pyright` | types (not configured) |

### In CI

The `backend` job installs **Ruff 0.17.3** and runs `ruff check .` before
`compileall` and `pytest`. The version is pinned in
[`../.github/workflows/ci.yml`](../.github/workflows/ci.yml).

### Changing the rules

1. Edit `select` in [`pyproject.toml`](pyproject.toml).
2. Run `uvx ruff check .` and fix or explicitly ignore findings.
3. Update this table and the step list in [`../docs/ci-cd.md`](../docs/ci-cd.md)
   if the CI behaviour changes.

Do not add `ruff format --check` yet: it would reformat the whole backend and
create a large diff. Add it as a separate, agreed task.

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `ruff: command not found` | Not installed in the venv | `uvx ruff check .` or `pip install ruff==0.17.3` |
| Ruff passes locally, fails in CI | Local version differs | CI pins 0.17.3; run `uvx ruff@0.17.3 check .` |
| `pytest` cannot import `app` | Wrong working directory | Run from `backend/` |
| `ZoneInfo("Europe/Madrid")` fails | Missing `tzdata` (Windows) | `pip install -r requirements.txt` |

## Related docs

- [`../docs/api.md`](../docs/api.md) — API contract
- [`../docs/ci-cd.md`](../docs/ci-cd.md) — pipeline, local commands, troubleshooting
- [`../AGENTS.md`](../AGENTS.md) — layers and code standards
