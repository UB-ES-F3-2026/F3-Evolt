# Branch protection

Branch protection makes the GitHub rules we agreed on **real, not just a habit**:
nobody can push straight to `develop` or `main`, and a PR can only merge when
**one teammate has approved** it and the **`ci` check is green**.

Protection applies to both protected branches: **`develop`** (the PR target for
sprint work) and **`main`** (the demo/release line).

---

## The rules at a glance

| Rule | Value | What it means in practice |
|------|-------|---------------------------|
| Pull request required | `true` | No direct pushes to `develop` or `main`; every change arrives via PR |
| Approving reviews | 1 | A PR needs at least one teammate's approval before the merge button unlocks |
| Required status check | `ci` | The gate job `ci` must be green on the latest commit |
| `enforce_admins` | `true` | Admins follow the same rules — no "works on my machine because I'm admin" |
| Force pushes | blocked | Nobody can rewrite history on a protected branch by accident |
| Deletion | blocked | `develop`/`main` cannot be deleted, ever |
| `strict` (up-to-date requirement) | `false` | A PR does **not** need to be rebased onto the latest `develop` to merge |

That `strict: false` is a deliberate trade-off: for a small team it avoids the
churn of rebasing a PR every time someone else merges first; the cost is that a
PR can merge without being up to date, so read the diff against the branch
before reviewing.

---

## Prerequisites (do these before applying anything)

1. **`.github/workflows/ci.yml` must exist on `develop`.** This happens when
   the TR05.1 PR (#110) merges into `develop` (issue #89). If you apply
   protection before that, PRs from
   branches that predate the workflow never report a `ci` check and stay blocked
   with no way to merge them.
2. **At least one CI run must exist** so the check name is a real, selectable
   check. If no run has happened yet, the "required check" you type might not
   match what GitHub actually receives.

## Verify the exact check name

Check the names GitHub reports from a real run on `develop`:

```bash
gh api repos/UB-ES-F3-2026/F3-Evolt/commits/$(git rev-parse origin/develop)/check-runs \
  -q '.check_runs[].name'
```

You should see three names:

```
backend
frontend
ci
```

The required one is **`ci`** (the gate job that goes red whenever `backend` or
`frontend` fails).

---

## Apply the protection

Both branches get the **same payload**. Write it once:

```bash
cat <<'EOF' > /tmp/protection.json
{
  "required_status_checks": { "strict": false, "contexts": ["ci"] },
  "enforce_admins": true,
  "required_pull_request_reviews": { "dismiss_stale_reviews": false, "required_approving_review_count": 1 },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
EOF
```

Then apply it — first `develop`, then `main`:

```bash
gh api -X PUT repos/UB-ES-F3-2026/F3-Evolt/branches/develop/protection \
  --input /tmp/protection.json
gh api -X PUT repos/UB-ES-F3-2026/F3-Evolt/branches/main/protection \
  --input /tmp/protection.json
```

GitHub answers with the whole protection settings as JSON — check that
`contexts` says `["ci"]` and `required_approving_review_count` is `1`.

---

## Verify the acceptance criteria

Two things must be true after applying:

1. **A direct push to `develop` is rejected.**
   GitHub rejects it with `GH006: Protected branch update failed` (and says
   which rules fired — e.g. required reviews or required status check).
2. **A PR without approval cannot merge.**
   On the PR page the merge button shows a **"Review required"** message until
   one teammate approves.

To rehearse #1 safely from your terminal:

```bash
git commit --allow-empty -m "tmp: protection check"
git push origin develop        # expected to FAIL with GH006
git reset --hard origin/develop
```

> ⚠️ Run this **only on a throwaway clone**, or after confirming nobody else is
> mid-push: the local temp commit exists only in your clone, and the last line
> resets your clone back to `origin/develop`. The push itself is expected to
> fail — that *is* the test. If it succeeds, protection is **not** applied:
> revert the temp commit immediately (`git revert HEAD && git push origin
> HEAD:develop`, allowed because the branch is still unprotected) and apply
> the protection before anybody else pushes.

## Emergency rollback (lockout only)

If protection blocks urgent work and you need to lift it immediately:

```bash
gh api -X DELETE repos/UB-ES-F3-2026/F3-Evolt/branches/develop/protection
gh api -X DELETE repos/UB-ES-F3-2026/F3-Evolt/branches/main/protection
```

⚠️ This **immediately reopens direct pushes** with no PR and no review. Use it
only if you are genuinely locked out (e.g. the required check is broken and
cannot be fixed), and re-apply the protection right after.

---

## When the CI workflow changes

The required check and the workflow must move **in the same PR**:

- **If you rename the `ci` job**, the old check name never appears again and
  every PR stays blocked — update `required_status_checks.contexts` in the
  same PR that renames it.
- **If you add `paths:` filters**, unrelated PRs no longer report `ci`, so they
  stay blocked forever — either don't add filters, or update the required
  check in the same PR.
- **If you change triggers** (branches the workflow runs on), a PR to a branch
  that no longer triggers a run never reports `ci` — keep `develop` and `main`
  triggering.

Rule of thumb: whatever a `ci.yml` edit changes about *when and with what name*
checks are reported, branch protection needs the same change in the same PR.

---

## Current status

**Not applied yet.** The TR05.1 workflow has to land first.

- [ ] PR #110 (`feature/devops/t05-1-ci-pipeline`, issue #89) merges into `develop`
- [ ] At least one CI run exists on `develop` (happens automatically on merge)
- [ ] Check names verified with the `gh api` command above
- [ ] `develop` and `main` protected with the payload above (owner: team, per issue #90)
- [ ] Announced at daily stand-up (per issue #90)
