# Proposal

## Why

Line coverage (87%) only proves tests execute code, not that they assert on the
behavior — a test that runs a branch but never checks the result leaves bugs
invisible. Mutation testing closes that gap by injecting small faults (flipped
comparisons, changed arithmetic, negated booleans) and checking whether the test
suite kills them. The suite is tiny (9 tests, ~0.3s), so pytest-gremlins'
coverage-guided, parallel mutation run finishes in seconds and is practical to
run in CI on every PR.

## What Changes

- Add `pytest-gremlins` to the `dev` dependency group in `pyproject.toml` and
  update `uv.lock`.
- Add a `[tool.pytest-gremlins]` section to `pyproject.toml` targeting
  `src/scan_pdf` with parallel workers, incremental cache, and console + JSON
  reports.
- Add a dedicated `mutation` job to `.github/workflows/build.yml` (ubuntu-latest,
  Python 3.13 only) that runs `uv run pytest --gremlins` as its own invocation
  (no `--cov`, no xdist) and uploads the JSON report as a workflow artifact.
  The job is report-only: surviving mutants do not fail the build.
- Add tests that raise base coverage before the first mutation run, targeting
  the current gaps: the untested `parse_args()` body and the "no pages found"
  branch in `cli.py`, and the flip / non-zero-returncode / missing-target-file
  branches in `convert.py`.
- Document the local command (`uv run pytest --gremlins`) in `README.rst`.
- Pre-commit is intentionally unchanged: mutation testing stays out of the
  fast local hook loop.

## Capabilities

### New Capabilities
- (none)

### Modified Capabilities
- `build-tooling`: the dev-dependency requirement's enumerated package list
  gains `pytest-gremlins`, and a new requirement covers mutation testing
  configuration and its CI job.

## Impact

- `pyproject.toml` (dependency group + `[tool.pytest-gremlins]`), `uv.lock`
- `.github/workflows/build.yml` (new job + artifact upload)
- `tests/test_cli.py`, `tests/test_convert.py` (new coverage tests)
- `README.rst` (short usage note)
- No runtime code (`src/scan_pdf`) changes; no breaking changes.
