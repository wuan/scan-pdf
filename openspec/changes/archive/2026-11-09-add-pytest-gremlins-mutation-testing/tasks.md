# Tasks

## 1. Raise base coverage with new tests

- [x] 1.1 Add `parse_args` tests to `tests/test_cli.py` that call the real `parse_args()` with patched `sys.argv` (one defaults case, one all-options case) and verify parsed values; verify `uv run pytest tests/test_cli.py --cov=scan_pdf --cov-report=term-missing -q` no longer lists cli.py lines 14-86 as missing
- [x] 1.2 Add a `run()` "no pages found" test to `tests/test_cli.py` (scanner returns `[]`) asserting the warning is logged and Converter/Combiner/shutil.move are never called; verify line 130 is covered
- [x] 1.3 Add `run()` tests for `duplex=True` (flip is True on even page numbers) and `debug=True` (logging level DEBUG); verify the remaining cli.py partial branches are covered
- [x] 1.4 Add `tests/test_convert.py` cases for `flip=True` (`-rotate 180` in args), non-zero returncode (error logged, returncode returned), and missing target file (error logged); verify `uv run pytest tests/test_convert.py --cov=scan_pdf --cov-report=term-missing -q` no longer lists convert.py lines 26, 34, 36->39 as missing

## 2. Add pytest-gremlins dependency and configuration

- [x] 2.1 Run `uv add --dev pytest-gremlins` and verify `pyproject.toml` `[dependency-groups] dev` includes it and `uv.lock` is updated (`uv lock --check` passes)
- [x] 2.2 Add `[tool.pytest-gremlins]` to `pyproject.toml` with `paths = ["src/scan_pdf"]`, `workers = "auto"`, `cache = true`, `report = ["console", "json"]`; verify the section parses via `uv run python -c "import tomllib; tomllib.load(open('pyproject.toml','rb'))"`
- [x] 2.3 Run `uv run pytest --gremlins -q` locally, confirm it completes and prints the mutation report, and record the exit code when gremlins survive (decides whether the CI job needs a wrapper to stay report-only)

## 3. CI mutation job

- [x] 3.1 Add a non-matrix `mutation` job to `.github/workflows/build.yml` on ubuntu-latest with Python 3.13 that runs `uv sync --locked` then `uv run pytest --gremlins` (no `--cov`, no `-n`), matching the hardened setup steps of the existing job; verify with `uv run python -c "import yaml; yaml.safe_load(open('.github/workflows/build.yml'))"` (or `check-yaml` pre-commit hook)
- [x] 3.2 Upload the JSON mutation report (reports/ output of `--gremlin-report=json`) as a workflow artifact in the mutation job; verify the workflow still parses and the artifact path matches the configured report output
- [x] 3.3 If task 2.3 showed pytest-gremlins exits non-zero on survivors, wrap the invocation so the job stays report-only; verify the job step would exit zero with survivors present (task 2.3 showed exit code 0 with survivors, so no wrapper needed)

## 4. Documentation and full verification

- [x] 4.1 Add a short "Mutation testing" section to `README.rst` documenting `uv run pytest --gremlins`; verify the documented command runs as written
- [x] 4.2 Run the full local verification: `uv run pytest --cov=scan_pdf -q`, `uv run pytest --gremlins -q`, `uv run ruff check`, `uv run basedpyright`, and `uv run pre-commit run --all-files`; verify all pass and pre-commit contains no gremlins hook
- [x] 4.3 Run `openspec validate add-pytest-gremlins-mutation-testing --strict` and verify it passes
