# Tasks

## 1. Remove stale config (P0)

- [x] 1.1 Delete `pytest.ini` so `[tool.pytest.ini_options]` in pyproject.toml is the single pytest config. Verify: bare `pytest` collects all 9 tests from `tests/` with no "No files were found in testpaths" warning.
- [x] 1.2 Delete `.travis.yml` (dead CI referencing nonexistent `requirements.txt` and Python 3.5-3.9). Verify: `grep -ri travis --exclude-dir=.git --exclude-dir=openspec .` returns no remaining references.

## 2. Rework `.pre-commit-config.yaml` (P0/P1)

- [x] 2.1 Remove the `pylint-dev/pylint` repo entry and bump `gitleaks` and `pre-commit-hooks` revs to current stable tags. Verify: `pre-commit run --all-files` passes with no import errors.
- [x] 2.2 Add `astral-sh/ruff-pre-commit` with `ruff` (args `--fix`) and `ruff-format` hooks. Verify: both hooks run and leave zero file modifications (code is already ruff-clean).
- [x] 2.3 Add hygiene hooks (`check-yaml`, `check-merge-conflict`, `check-added-large-files`, `mixed-line-ending`, `debug-statements`) from pre-commit-hooks and `pyupgrade` with `--py310-plus`. Verify: clean `pre-commit run --all-files`.
- [x] 2.4 Add local mypy hook (`repo: local`, `language: system`, `entry: poetry run mypy`, `types: [python]`, `pass_filenames: false`). Verify: hook passes after `poetry install` (mypy resolves `scan_pdf` + `pypdf` from the project env).
- [x] 2.5 Add `default_language_version: python3` and an explicit `ci:` section. Verify: `pre-commit run --all-files` still passes and config loads without warnings.

## 3. Consolidate tooling config in `pyproject.toml` (P1)

- [x] 3.1 Remove `flake8` from dev dependencies (`poetry remove --group dev flake8`) to end the three-linter overlap. Verify: `poetry install` succeeds and `poetry run flake8` no longer exists in the env.
- [x] 3.2 Add explicit ruff config: `target-version = "py310"` and pinned `lint.select = ["E4", "E7", "E9", "F", "I", "W"]`. Verify: `poetry run ruff check scan_pdf tests` and `poetry run ruff format --check scan_pdf tests` both pass.

## 4. Dependabot and CI enforcement (P1/P2)

- [x] 4.1 Extend `.github/dependabot.yml` with `poetry` and `pre-commit` ecosystems (directory `/`, daily) alongside `github-actions`. Verify: file passes the `check-yaml` hook and Dependabot config is valid YAML with three update entries.
- [x] 4.2 Add `.github/workflows/pre-commit.yml` running `pre-commit run --all-files` on pull requests and pushes to main, using SHA-pinned `actions/checkout` + `step-security/harden-runner` (matching existing workflows) and a Poetry setup step before the run (needed by the mypy system hook). Verify: YAML is valid (check-yaml) and every `uses:` is SHA-pinned like the other workflows.

## 5. Integration verification

- [x] 5.1 Run the full local harness `poetry install && pre-commit install && pre-commit run --all-files`. Verify: every hook passes and git shows zero unexpected modifications.
- [x] 5.2 Run `poetry run pytest`. Verify: all 9 tests pass and no testpaths warning is emitted.
- [x] 5.3 Run `poetry run mypy` and `poetry run ruff check scan_pdf tests`. Verify: both exit 0.
- [x] 5.4 Push the branch and open a PR. Verify: the new `pre-commit` workflow and the existing `build` workflow both pass in GitHub Actions.

## Workflow follow-up

- Archive the change after the project's review requirements are satisfied.
- Verify the archived result.
