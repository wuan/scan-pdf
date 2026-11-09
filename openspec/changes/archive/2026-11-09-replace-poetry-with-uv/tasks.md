# Tasks

## 1. Move the package to src layout

- [x] 1.1 `git mv scan_pdf src/scan_pdf` (create `src/` first); do not edit any file contents. Verify: `git status` shows pure renames, `find src -name "*.py" | sort` lists the same 6 modules, and `uv run pytest` still collects all 9 tests (module name unchanged).

## 2. Rewrite pyproject.toml and generate uv.lock

- [x] 2.1 Rewrite `pyproject.toml`: replace `[tool.poetry]` sections with PEP 621 `[project]` (incl. `license = "Apache-2.0"`, `requires-python = ">=3.11"`, `dependencies = ["pypdf>=5.1,<7.0"]`), `[project.scripts]`, `[dependency-groups] dev` (caret ranges translated per design D4), `[build-system]` with `uv_build>=0.13.7,<0.14.0` (no `[tool.uv.build-backend]` override — src layout is the default), `[tool.uv]` (`package = true`, `default-groups = ["dev"]`); bump ruff `target-version` and mypy `python_version` to 3.11 and add `mypy_path = "src"` to `[tool.mypy]`. Verify: `uv lock` succeeds, `uv sync --locked` creates `.venv` with the project installed, and `uv build` produces a wheel containing `scan_pdf`.
- [x] 2.2 Delete `poetry.lock` and commit the generated `uv.lock`. Verify: `git status` shows `poetry.lock` deleted, `uv.lock` present; `uv sync --locked` exits 0 (lock in sync).
- [x] 2.3 Bump the Python floor in the rest of the tooling: pre-commit pyupgrade args `--py310-plus` → `--py311-plus`. Verify: `grep -rn "py310\|3\.10" pyproject.toml .pre-commit-config.yaml` returns nothing.
- [x] 2.4 Point SonarCloud at the moved sources: `sonar.sources=src/scan_pdf/` in `sonar-project.properties`. Verify: `grep "sonar.sources" sonar-project.properties` shows `src/scan_pdf/`.

## 3. Update local hooks and gitignore

- [x] 3.1 Change the local mypy hook in `.pre-commit-config.yaml` from `entry: poetry run mypy` to `entry: uv run mypy` (keep `language: system`, `types: [python]`, `pass_filenames: false`). Verify: `pre-commit run mypy --all-files` passes after `uv sync` and type-checks `src/scan_pdf` sources (no missing-`py.typed` warning).
- [x] 3.2 Add `/.venv/` to `.gitignore`. Verify: `git check-ignore .venv` exits 0.

## 4. Migrate CI workflows to uv

- [x] 4.1 In `.github/workflows/build.yml`: drop `"3.10"` from the Python matrix; replace the `POETRY_VERSION` env and `abatilo/actions-poetry` step with SHA-pinned `astral-sh/setup-uv` (tag in comment, `enable-cache: true`); replace `poetry install` with `uv sync --locked`, `poetry run pip list` with `uv pip list`, `poetry run pytest ...` with `uv run pytest ...` (the `--cov=scan_pdf` flag stays — it names the module), `poetry build` with `uv build`. Verify: `check-yaml` passes via `pre-commit run check-yaml --all-files` and every `uses:` is SHA-pinned.
- [x] 4.2 Apply the same setup-step and command swap in `.github/workflows/analysis.yml`. Verify: `pre-commit run check-yaml --all-files` passes; no `poetry` or `abatilo` references remain (`grep -rn poetry .github/workflows/analysis.yml` is empty).
- [x] 4.3 In `.github/workflows/pre-commit.yml`: replace the `abatilo/actions-poetry` step and `poetry install` with SHA-pinned `astral-sh/setup-uv` + `uv sync --locked`. Verify: `pre-commit run check-yaml --all-files` passes and `grep -rn poetry .github/workflows/pre-commit.yml` is empty.

## 5. Switch Dependabot to the uv ecosystem

- [x] 5.1 In `.github/dependabot.yml`, change `package-ecosystem: poetry` to `package-ecosystem: uv` (keep `github-actions` and `pre-commit`). Verify: `pre-commit run check-yaml --all-files` passes and the config is valid Dependabot YAML with three update entries.
- [x] 5.2 After merge, confirm Dependabot accepts the `uv` ecosystem (first scheduled run or manual dispatch produces a valid scan, not a config error). Verify: Dependabot logs/PRs show `uv` updates; if the ecosystem is rejected, fall back to removing the entry and note it in the PR.

## 6. Full local verification

- [x] 6.1 Run the complete harness: `uv sync --locked && uv run pytest --cov=scan_pdf --cov-report term && uv run mypy && uv run ruff check src tests && uv run ruff format --check src tests && uv build`. Verify: all 9 tests pass, mypy checks the src tree and exits 0, ruff exits 0, and `dist/` contains a wheel and sdist for `scan_pdf-0.4.10` whose wheel includes the `scan_pdf` package.
- [x] 6.2 Run `pre-commit install && pre-commit run --all-files`. Verify: every hook passes and git shows zero unexpected modifications.
- [x] 6.3 Confirm no stale references remain: `grep -rn -i "poetry" --include="*.yml" --include="*.yaml" --include="*.toml" --include="*.rst" --include="*.properties" .` (excluding `.git`, `.venv`, caches, and `openspec/changes/archive/`) returns nothing, and `grep -rn "scan_pdf/" --include="*.properties" --include="*.yml" .` shows only `src/scan_pdf/`-based paths.

## Workflow follow-up

- Archive the change after the project's review requirements are satisfied.
- Verify the archived result and that CI on main is green across the full matrix.
