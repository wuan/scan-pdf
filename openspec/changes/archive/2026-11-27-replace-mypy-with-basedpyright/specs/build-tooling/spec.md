# Spec Delta

## ADDED Requirements

### Requirement: Static type checking runs in basedpyright full based mode
The project SHALL configure basedpyright in the `[tool.basedpyright]` table of `pyproject.toml` with `typeCheckingMode = "all"` (full based mode), `pythonVersion = "3.11"`, and checking scoped to `src/` only, so that `src/scan_pdf` is type-checked in the strictest rule set while `tests/` remains unchecked.

#### Scenario: Type check passes on the package
- **WHEN** `uv run basedpyright` runs in the project root with the `[tool.basedpyright]` configuration
- **THEN** it exits zero and reports no errors for the `src/scan_pdf` sources

#### Scenario: Type errors in src fail the check
- **WHEN** a type error is introduced in a file under `src/scan_pdf/`
- **THEN** `uv run basedpyright` exits non-zero and reports the error against that source file

#### Scenario: Tests are outside the checked scope
- **WHEN** `uv run basedpyright` runs with the execution environment scoped to `src/`
- **THEN** files under `tests/` are not type-checked and produce no diagnostics, matching the previous mypy `packages = ["scan_pdf"]` scope

### Requirement: Path-based tooling follows the src layout with basedpyright
Tooling that addresses the package by filesystem path SHALL use the new location: basedpyright SHALL scope checking to `src` via an execution environment rooted there, and `sonar-project.properties` SHALL set `sonar.sources=src/scan_pdf/`.

#### Scenario: basedpyright type-checks the source tree
- **WHEN** `uv run basedpyright` runs with checking scoped to `src/`
- **THEN** basedpyright checks the `src/scan_pdf` sources directly instead of resolving the installed package (which lacks a `py.typed` marker)

#### Scenario: SonarCloud scans the moved source root
- **WHEN** SonarCloud analyzes the project
- **THEN** `sonar.sources=src/scan_pdf/` covers the package at its new location

### Requirement: Local hooks and Dependabot follow uv with the basedpyright hook
The pre-commit basedpyright hook SHALL use `entry: uv run basedpyright` (still `language: system`), and `.github/dependabot.yml` SHALL track the `uv` ecosystem for `/` instead of `poetry`.

#### Scenario: Pre-commit hook runs basedpyright through uv
- **WHEN** `pre-commit run --all-files` executes the local basedpyright hook
- **THEN** basedpyright runs in the uv-managed project environment via `uv run basedpyright`

#### Scenario: Dependabot scans uv manifests
- **WHEN** Dependabot evaluates the repository
- **THEN** it checks `pyproject.toml`/`uv.lock` under the `uv` ecosystem and no longer watches a Poetry manifest

## MODIFIED Requirements

### Requirement: Python floor is 3.11
The project SHALL require Python >= 3.11 via `requires-python = ">=3.11"`, and all tooling configuration (ruff `target-version`, basedpyright `pythonVersion`, pyupgrade pre-commit args) and the CI test matrix SHALL target 3.11 and newer only.

#### Scenario: Older Python is rejected
- **WHEN** `uv sync` runs with Python 3.10 selected
- **THEN** resolution fails because `requires-python` excludes 3.10

#### Scenario: CI does not test 3.10
- **WHEN** the build workflow matrix is evaluated
- **THEN** it contains 3.11, 3.12, and 3.13 but not 3.10

### Requirement: Dev dependencies live in a default dependency group
The project SHALL declare dev dependencies (pytest, pytest-mock, pytest-cov, mock, assertpy, basedpyright, ruff) in the PEP 735 `[dependency-groups]` table under `dev`, and uv SHALL install that group by default (`[tool.uv] default-groups = ["dev"]`).

#### Scenario: Fresh sync includes dev tools
- **WHEN** `uv sync --locked` runs in a clean checkout
- **THEN** pytest, basedpyright, and ruff are all importable via `uv run` without extra flags

### Requirement: CI provisions uv instead of Poetry
The build, analysis, and pre-commit workflows SHALL install uv via the SHA-pinned `astral-sh/setup-uv` action (with cache enabled), run `uv sync --locked`, execute tests and tools via `uv run`, and build via `uv build`; the third-party `abatilo/actions-poetry` action SHALL be removed everywhere.

#### Scenario: Tests run in CI
- **WHEN** the build workflow runs on any matrix OS/Python combination
- **THEN** pytest executes through `uv run pytest` in the uv-managed environment and `uv build` produces the distribution artifacts

#### Scenario: Pre-commit workflow prepares the environment
- **WHEN** the pre-commit workflow runs
- **THEN** `uv sync --locked` completes before `pre-commit run --all-files`, so the system-level basedpyright hook resolves `uv run basedpyright`

## REMOVED Requirements

### Requirement: Path-based tooling follows the src layout
**Reason**: mypy is replaced by basedpyright, which scopes checking via an execution environment rooted at `src` instead of `mypy_path`/`packages`.
**Migration**: configure `[tool.basedpyright]` with `executionEnvironments = [{ root = "src" }]` and run `uv run basedpyright`; see the ADDED requirement "Path-based tooling follows the src layout with basedpyright".

### Requirement: Local hooks and Dependabot follow uv
**Reason**: the pre-commit hook entry changes from `uv run mypy` to `uv run basedpyright`.
**Migration**: update the local hook in `.pre-commit-config.yaml` to `entry: uv run basedpyright`; see the ADDED requirement "Local hooks and Dependabot follow uv with the basedpyright hook".
