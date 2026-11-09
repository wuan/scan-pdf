# Proposal

## Why

Poetry adds a second toolchain (its own lock format, resolver, and virtualenv management) on top of Python packaging standards, while uv is a single fast tool that covers locking, syncing, running, and building using standard `pyproject.toml` metadata. The project's dependency surface is tiny (one runtime dep, seven dev deps), so the migration is low-risk and removes the `abatilo/actions-poetry` third-party action, the Poetry-specific Dependabot ecosystem, and every `poetry run` indirection in CI and pre-commit. This also lets us fully commit to uv's native build backend (`uv_build`) instead of keeping a second backend alive for PyPI compatibility.

## What Changes

- **BREAKING**: `pyproject.toml` is rewritten from `[tool.poetry]` to PEP 621 `[project]`, PEP 735 `[dependency-groups]`, and `[build-system]` with `uv_build`; `poetry.lock` is deleted and replaced by a committed `uv.lock`.
- **BREAKING**: the package moves to src layout — `scan_pdf/` becomes `src/scan_pdf/` via `git mv` (module name and entry point unchanged), so mypy gains `mypy_path = "src"` and `sonar-project.properties` points `sonar.sources` at `src/scan_pdf/`.
- Python floor is promoted from 3.10 to 3.11 (`requires-python = ">=3.11"`); ruff `target-version`, mypy `python_version`, and the pyupgrade pre-commit arg follow to `py311`; the CI matrix drops 3.10.
- CI workflows (`build.yml`, `analysis.yml`, `pre-commit.yml`) replace `abatilo/actions-poetry` with SHA-pinned `astral-sh/setup-uv` (with cache enabled) and use `uv sync --locked` / `uv run` / `uv build`.
- `.github/dependabot.yml` switches `package-ecosystem: poetry` to `uv`.
- `.pre-commit-config.yaml` local mypy hook entry changes from `poetry run mypy` to `uv run mypy` (keeps `language: system`).
- `.gitignore` gains `/.venv/` (uv creates the environment in-project by default).

## Capabilities

### New Capabilities
- `build-tooling`: The project is packaged, locked, tested, and built with uv (`uv_build` backend, PEP 621 metadata, PEP 735 dev group, committed `uv.lock`) on a Python >= 3.11 floor, in local development, pre-commit, and CI alike.

### Modified Capabilities
- None (no existing specs).

## Impact

- `pyproject.toml` — full rewrite of the Poetry sections; `[tool.pytest.ini_options]`, `[tool.ruff]` stay, `[tool.mypy]` gains `mypy_path = "src"` and both ruff/mypy version targets bump to 3.11.
- `scan_pdf/` → `src/scan_pdf/` (pure move, no file contents edited).
- `sonar-project.properties` — `sonar.sources=src/scan_pdf/`.
- `poetry.lock` deleted; `uv.lock` added.
- `.github/workflows/build.yml`, `.github/workflows/analysis.yml`, `.github/workflows/pre-commit.yml` — uv setup + uv commands.
- `.github/dependabot.yml` — ecosystem swap.
- `.pre-commit-config.yaml` — mypy hook entry + pyupgrade arg.
- `.gitignore` — add `/.venv/`.
- No changes to test code, README, or `.coveragerc`; `--cov=scan_pdf` keeps working because the module name is unchanged.
