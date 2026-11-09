# Tasks

## 1. Swap the type checker dependency and config

- [x] 1.1 In `pyproject.toml`, replace `"mypy>=2.3,<3"` with `"basedpyright>=1,<2"` in `[dependency-groups] dev`, and replace the `[tool.mypy]` section with `[tool.basedpyright]` containing `pythonVersion = "3.11"`, `typeCheckingMode = "all"`, and `executionEnvironments = [{ root = "src" }]`. Verify: `uv lock` succeeds and `uv sync --locked` exits 0 with basedpyright importable via `uv run basedpyright --version`.
- [x] 1.2 Regenerate and commit `uv.lock` (mypy gone, basedpyright pinned). Verify: `git diff uv.lock` shows mypy removed and basedpyright added; `uv sync --locked` exits 0 (lock in sync).

## 2. Update the pre-commit hook

- [x] 2.1 In `.pre-commit-config.yaml`, change the local hook to `id: basedpyright`, `name: basedpyright`, `entry: uv run basedpyright`, keeping `language: system`, `types: [python]`, `pass_filenames: false`. Verify: `uv run pre-commit run basedpyright --all-files` passes after `uv sync` and type-checks the `src/scan_pdf` sources.

## 3. Make the package pass full based mode

- [x] 3.1 Run `uv run basedpyright` and fix every diagnostic it reports in `src/scan_pdf/` (based mode enables `reportAny`, `reportExplicitAny`, `reportUnknown*`, etc., which mypy did not enforce). Verify: `uv run basedpyright` exits 0 with no errors; any rule disable added to `[tool.basedpyright]` is narrowly scoped and commented.

## 4. Full local verification

- [x] 4.1 Run the complete harness: `uv sync --locked && uv run pytest --cov=scan_pdf --cov-report term && uv run basedpyright && uv run ruff check src tests && uv run ruff format --check src tests && uv build`. Verify: all tests pass, basedpyright checks the src tree and exits 0, ruff exits 0, and `dist/` contains a wheel and sdist containing the `scan_pdf` package.
- [x] 4.2 Run `uv run pre-commit run --all-files`. Verify: every hook passes, including basedpyright, and git shows zero unexpected modifications.
- [x] 4.3 Confirm no stale references remain: `grep -rn -i "mypy" --include="*.yml" --include="*.yaml" --include="*.toml" .` (excluding `.git`, `.venv`, `uv.lock`, and `openspec/changes/archive/`) returns nothing.

## 5. Sync the build-tooling spec

- [x] 5.1 Run `openspec sync` (or `/openspec-sync-specs`) to apply the delta in `openspec/changes/replace-mypy-with-basedpyright/specs/build-tooling/spec.md` to `openspec/specs/build-tooling/spec.md`. Verify: `openspec validate` passes and the main spec names basedpyright in the five modified requirements plus the new based-mode requirement.

## Workflow follow-up

- Archive the change after the project's review requirements are satisfied.
- Verify the archived result and that CI on main is green (pre-commit workflow runs the basedpyright hook).
