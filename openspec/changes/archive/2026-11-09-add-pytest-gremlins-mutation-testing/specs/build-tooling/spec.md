# Spec Delta

## MODIFIED Requirements

### Requirement: Dev dependencies live in a default dependency group
The project SHALL declare dev dependencies (pytest, pytest-mock, pytest-cov, pytest-gremlins, mock, assertpy, basedpyright, ruff) in the PEP 735 `[dependency-groups]` table under `dev`, and uv SHALL install that group by default (`[tool.uv] default-groups = ["dev"]`).

#### Scenario: Fresh sync includes dev tools
- **WHEN** `uv sync --locked` runs in a clean checkout
- **THEN** pytest, pytest-gremlins, basedpyright, and ruff are all importable via `uv run` without extra flags

## ADDED Requirements

### Requirement: Mutation testing is configured via pytest-gremlins
The project SHALL configure pytest-gremlins under `[tool.pytest-gremlins]` in `pyproject.toml` with `paths = ["src/scan_pdf"]`, parallel workers, incremental caching, and console plus JSON reports, and mutation testing SHALL run as a separate pytest invocation (`uv run pytest --gremlins`) that does not combine `--gremlins` with `--cov` or pytest-xdist flags.

#### Scenario: Local mutation run reports survivors
- **WHEN** `uv run pytest --gremlins` runs in the project root
- **THEN** the test suite executes against each mutant and a console report lists zapped, surviving, timeout, and error gremlins

#### Scenario: Mutation targets are explicit
- **WHEN** pytest-gremlins resolves which files to mutate
- **THEN** it mutates only files under `src/scan_pdf`, because `paths` is set explicitly rather than relying on auto-discovery (the project builds with the uv_build backend, not setuptools)

#### Scenario: JSON report is written
- **WHEN** the mutation run finishes with `report = ["console", "json"]` configured
- **THEN** a JSON mutation report file is produced alongside the console output

### Requirement: CI runs mutation testing as a report-only job
The build workflow SHALL include a dedicated mutation job on ubuntu-latest with a single Python version that runs `uv sync --locked`, then `uv run pytest --gremlins`, and uploads the JSON mutation report as a workflow artifact; the job SHALL NOT fail the build when gremlins survive.

#### Scenario: Mutation job runs on pull requests
- **WHEN** a pull request targets main
- **THEN** the mutation job executes on ubuntu-latest with one Python version, in addition to the OS/Python matrix jobs

#### Scenario: Surviving gremlins do not fail CI
- **WHEN** the mutation run reports surviving gremlins
- **THEN** the job exits zero and the survivor list remains visible in the log and the uploaded report

#### Scenario: Mutation job does not duplicate the matrix
- **WHEN** the build workflow is evaluated
- **THEN** the mutation job is a single non-matrix job, not part of the OS/Python matrix

### Requirement: Mutation testing stays out of pre-commit
The pre-commit configuration SHALL NOT include a pytest-gremlins hook, so the local hook loop stays fast.

#### Scenario: Pre-commit hook set is unchanged
- **WHEN** `pre-commit run --all-files` executes
- **THEN** no mutation testing invocation runs and the hooks remain gitleaks, pre-commit-hooks, ruff, pyupgrade, and basedpyright
