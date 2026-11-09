# Proposal

## Why

The pre-commit harness only runs locally (no CI enforcement), is pinned to 2023-era
hook versions, and its one linter (pylint) cannot actually pass on this codebase —
while the project's declared dev tools (ruff, mypy) that do pass are not wired in
at all. Meanwhile two config files are stale leftovers that actively mislead:
`pytest.ini` shadows the correct pyproject pytest config and points at a
nonexistent `src/` layout, and `.travis.yml` references a `requirements.txt` that
no longer exists. The harness needs to be completed and made trustworthy before it
can be relied on.

## Review of Current State

### `.pre-commit-config.yaml` (only local enforcement, nothing in CI)

| Hook | Status | Finding |
|---|---|---|
| gitleaks v8.16.3 | OK, but old | Secret scanning present; version from 2023 |
| end-of-file-fixer, trailing-whitespace (pre-commit-hooks v4.4.0) | OK, but old | Basic hygiene only |
| pylint v2.17.2 | **Broken** | Runs in an isolated env without `pypdf`, so `scan_pdf/combine.py` fails with import-error; no `.pylintrc` exists, so defaults apply; v2.17.2 does not support Python 3.12/3.13 which CI builds with |

Missing entirely: formatter, ruff check, mypy, YAML/merge/large-file checks,
pyupgrade, a `ci:` section, and any pinned `default_language_version`.

### Dev dependencies vs. enforcement (pyproject.toml)

- `ruff` is a dev dep and the code is fully `ruff check` + `ruff format` clean —
  but neither is a hook. Near-zero cost to enforce.
- `mypy` is a dev dep with `disallow_untyped_defs` and currently passes —
  but is not a hook.
- `flake8` is a dev dep and currently **fails** with 8x E501 line-too-long —
  and is not a hook. Three overlapping linters (pylint, flake8, ruff) with no
  single source of truth.

### Stale files

- `pytest.ini`: sets `pythonpath = src` / `testpaths = src/tests`, but `src/`
  does not exist. It takes precedence over the correct
  `[tool.pytest.ini_options]` in pyproject.toml, so every bare `pytest` run emits
  "No files were found in testpaths" and only passes by fallback recursion.
- `.travis.yml`: Travis CI config referencing `requirements.txt` (absent),
  Python 3.5–3.9 (project requires ^3.10), and `PYTHONPATH=src`. Dead — CI is
  GitHub Actions now.

### GitHub Actions (healthy, keep as-is)

`build.yml` (test matrix 3.10–3.13 x ubuntu/macos/windows), `analysis.yml`
(SonarCloud), `codeql-analysis.yml`, `dependency-review.yml`, `scorecard.yml`,
`pr_automation.yml` (dependabot auto-merge) — all pinned by SHA with harden-runner.
Gap: `dependabot.yml` only manages the `github-actions` ecosystem; the real
dependency manifest is `poetry.lock`, and pre-commit hook `rev`s are not
auto-updated either. No workflow runs `pre-commit run --all-files`, so hooks
drift undetected.

## What Changes

Prioritized; P0 = broken/stale today, P1 = close the enforcement gap at ~zero
cost, P2 = make it stick.

### P0 — Fix what is broken or misleading

1. Delete `pytest.ini` (or fix it to `testpaths = tests`); keep pytest config
   solely in `pyproject.toml` so there is one source of truth.
2. Delete `.travis.yml` (dead CI referencing nonexistent files).
3. Remove the pylint hook from `.pre-commit-config.yaml` (cannot pass as
   configured; superseded by ruff + mypy). Decide explicitly: ruff owns linting
   and formatting, mypy owns typing; drop flake8 from dev deps to end the
   three-linter overlap.

### P1 — Complete the hook set

4. Add `ruff` (check, with `--fix`) and `ruff-format` hooks — tools already in
   dev deps, code already clean.
5. Add a `mypy` hook (local hook using the project venv, or with
   `additional_dependencies`).
6. Add standard hygiene hooks: `check-yaml`, `check-merge-conflict`,
   `check-added-large-files`, `mixed-line-ending`, `debug-statements`,
   `pyupgrade` (target py310+).
7. Bump all hook `rev`s to current versions; add `pre-commit` and `poetry`
   ecosystems to `.github/dependabot.yml` so hook versions and `poetry.lock`
   get automated updates.

### P2 — Enforce and maintain

8. Add a GitHub Actions workflow (or pre-commit.ci) running
   `pre-commit run --all-files` on pull requests so the harness is actually
   gating, not just local.
9. Add a `ci:` section to `.pre-commit-config.yaml` (e.g. skip slow hooks in
   CI) and pin `default_language_version: python3`.
10. Optional, low value on this small codebase: `bandit` hook — secrets are
    already covered by gitleaks and SAST by CodeQL in CI.

## Capabilities

### New Capabilities

None. This is a pure tooling change — no runtime behavior of `scan-pdf` changes,
so no spec deltas are introduced (`skip_specs: true` is set in `.openspec.yaml`).

### Modified Capabilities

None.

## Impact

- `.pre-commit-config.yaml`: hook set replaced/extended, revs bumped, `ci:`
  section added.
- `.github/dependabot.yml`: add `poetry` and `pre-commit` ecosystems.
- New file `.github/workflows/pre-commit.yml` (P2) running
  `pre-commit run --all-files` on PRs.
- Deleted: `pytest.ini`, `.travis.yml`.
- `pyproject.toml`: remove `flake8` from dev deps; consolidate ruff config
  (line-length, select rules) as the single lint/format config.
- No changes to `scan_pdf/` source or `tests/`; no dependency changes for the
  published package.
