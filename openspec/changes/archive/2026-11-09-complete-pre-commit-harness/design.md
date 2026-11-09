# Design

## Context

Current state and motivation are in proposal.md. Constraints that shape the
approach: the repo standardizes on SHA-pinned GitHub Actions with
step-security/harden-runner; dependencies are managed by Poetry
(`pyproject.toml` + `poetry.lock`); the codebase is already clean under
`ruff check`, `ruff format`, and `mypy` (verified locally), so the new hooks
must not require reformatting or re-typing existing code. `scan_pdf` imports
`pypdf`, which matters for any hook running in a pre-commit isolated env.

## Goals / Non-Goals

**Goals:**

- One lint/format/type toolchain (ruff + mypy) enforced by pre-commit, locally
  and in CI.
- No stale config files that shadow correct ones (`pytest.ini`, `.travis.yml`).
- Hook versions and dependency manifests kept current automatically via
  Dependabot.
- Zero changes to `scan_pdf/` source, `tests/`, or the published package.

**Non-Goals:**

- No new runtime dependencies or changes to scanner behavior.
- No bandit hook (secrets covered by gitleaks, SAST by CodeQL).
- No README/documentation rewrite; a short contributor note about
  `poetry install && pre-commit install` may be added only if trivial.
- No changes to the existing GH Actions workflows beyond adding one new
  pre-commit workflow and extending dependabot config.

## Decisions

### D1 — Ruff is the single linter and formatter; pylint hook and flake8 dep are removed

- **Choice**: `astral-sh/ruff-pre-commit` with hooks `ruff` (args: `--fix`) and
  `ruff-format`. Remove the `pylint-dev/pylint` repo and the `flake8` dev
  dependency.
- **Rationale**: ruff is already a dev dep and the code passes it today, so
  adoption costs zero code changes. The pylint hook cannot pass as configured
  (isolated env lacks `pypdf` -> import-error on `scan_pdf/combine.py`; no
  `.pylintrc`; v2.17.2 predates Python 3.12/3.13 support). flake8 currently
  fails with 8x E501 and overlaps ruff. One tool, one config block in
  `pyproject.toml`.
- **Alternatives**: (a) keep pylint with a `.pylintrc` + `additional_dependencies: [pypdf]`
  — more config to maintain for a linter ruff supersedes; (b) keep flake8 and
  fix E501s — adds a third linter and code churn for no gain.
- **Ruff config in pyproject.toml**: add `target-version = "py310"` and an
  explicit `select = ["E4", "E7", "E9", "F", "I", "W"]` so behavior is pinned
  rather than default-shifted; keep formatter defaults (line-length 88, which
  the code already satisfies).

### D2 — mypy runs as a local hook against the project environment

- **Choice**: `repo: local` hook, `language: system`, `entry: poetry run mypy`,
  `types: [python]`, `pass_filenames: false` (mypy config uses
  `packages = ["scan_pdf"]`).
- **Rationale**: mypy must resolve `scan_pdf` and `pypdf`; a pre-commit
  isolated env would need `additional_dependencies` mirroring the project deps
  and can drift. The project venv already passes mypy today, and every
  contributor running pre-commit necessarily has the Poetry env installed.
- **Alternative**: mirror hook with `additional_dependencies: ["pypdf>=5.1,<7.0"]`
  — rejected because it duplicates the dependency spec and still cannot see
  the `scan_pdf` package itself without installing it.

### D3 — Delete `pytest.ini`; pytest config lives only in `pyproject.toml`

- **Choice**: remove the file. `[tool.pytest.ini_options]` already has
  `testpaths = ["tests"]`.
- **Rationale**: `pytest.ini` takes precedence over pyproject and points at the
  nonexistent `src/` layout, so every bare `pytest` run currently warns and
  falls back to recursion. One config file removes the whole class of bug.
- **Alternative**: fix `pytest.ini` to `testpaths = tests` — rejected; two
  pytest config locations is the original problem.

### D4 — Delete `.travis.yml`

- **Choice**: remove the file.
- **Rationale**: it references `requirements.txt` (absent since the Poetry
  migration), `PYTHONPATH=src`, and Python 3.5–3.9 while the project requires
  ^3.10. CI is GitHub Actions (`build.yml` et al.). Dead config that misleads
  readers and tools.
- **Alternative**: leave it — rejected; zero cost to remove, ongoing confusion
  cost to keep.

### D5 — Hygiene hooks from `pre-commit-hooks`, pyupgrade from `pre-commit/pyupgrade`

- **Choice**: add `check-yaml`, `check-merge-conflict`, `check-added-large-files`,
  `mixed-line-ending`, `debug-statements`, `end-of-file-fixer`,
  `trailing-whitespace` (last two already present), plus
  `pyupgrade --py310-plus`.
- **Rationale**: standard, zero-config hygiene; pyupgrade keeps syntax modern
  as the floor moves. All run in isolated envs with no project deps needed.

### D6 — CI enforcement via a new self-hosted workflow, not pre-commit.ci

- **Choice**: add `.github/workflows/pre-commit.yml` running
  `pre-commit run --all-files` on `pull_request` and push to `main`, using
  SHA-pinned `actions/checkout` and `step-security/harden-runner` with a Poetry
  setup step before the run (needed for the D2 mypy hook).
- **Rationale**: consistent with the repo's existing SHA-pinned, harden-runner
  convention; no external service dependency.
- **Alternative**: pre-commit.ci — rejected for consistency and because the
  mypy system hook needs the Poetry env, which a GH Actions workflow provides
  directly.

### D7 — Dependabot manages `poetry` and `pre-commit` ecosystems in addition to `github-actions`

- **Choice**: extend `.github/dependabot.yml` with `package-ecosystem: poetry`
  and `package-ecosystem: pre-commit`, both `directory: /`, daily.
- **Rationale**: `poetry.lock` is the real dependency manifest (currently
  unmanaged); pre-commit hook `rev`s are tags that Dependabot can bump.
- **Note**: keep hook revs as tags (pre-commit convention, Dependabot-managed),
  even though GH Actions are SHA-pinned — the two ecosystems have different
  pinning conventions and mixing them breaks `pre-commit autoupdate`-style tooling.

### D8 — Pre-commit config hygiene: `ci:` section and `default_language_version`

- **Choice**: add `default_language_version: python3` and a `ci:` block with no
  skips (all hooks can run in CI given Poetry is installed first).
- **Rationale**: pins the interpreter pre-commit uses for language:python hooks;
  keeps CI behavior explicit.

## Risks / Trade-offs

- **[Risk]** Contributors without the Poetry env installed will see the mypy
  system hook fail locally. → Mitigation: CI workflow installs Poetry first;
  the failure message is self-explanatory; documented order is
  `poetry install` then `pre-commit install`.
- **[Risk]** Deleting `pytest.ini` changes behavior for anyone who relied on the
  `src` fallback. → Mitigation: bare `pytest` must still collect all 9 tests
  from `tests/` with no warning after the change; verified as an acceptance
  check in tasks.
- **[Risk]** Dependabot's `poetry` ecosystem updates `poetry.lock`, which the
  auto-merge workflow (`pr_automation.yml`) may squash-merge — a bad bump
  could land untested. → Mitigation: existing `build.yml` matrix runs on PRs,
  so breakage surfaces before merge; auto-merge already applies to action bumps
  today.
- **[Risk]** Ruff's explicit `select` may flag new things as defaults expand. →
  Mitigation: `select` is pinned explicitly, so behavior is stable across ruff
  version bumps; Dependabot bumps are reviewed.
- **[Trade-off]** Tags (not SHAs) for pre-commit revs means a compromised tag
  could move — accepted, standard pre-commit practice, mitigated by Dependabot
  PR review.

## Migration Plan

1. Single PR implementing tasks.md in order (P0 -> P1 -> P2).
2. Locally: `poetry install`, `pre-commit install`, then
   `pre-commit run --all-files` — must pass with no file modifications (code is
   already ruff/mypy clean; only config files are deleted/added).
3. Verify bare `pytest` collects all tests without the testpaths warning.
4. Push; the new `pre-commit.yml` workflow must go green alongside `build.yml`.
5. Rollback: revert the PR — no runtime state exists, so rollback is trivial.

## Open Questions

- None blocking. Deferred by proposal: whether to add a bandit hook (P2 item 10,
  optional) and whether to add a short README note on `pre-commit install`.
