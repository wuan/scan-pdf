# Design

## Context

The project is a small CLI package (`src/scan_pdf`, 5 modules, ~330 lines) with a
9-test suite (~0.3s) at 87% line coverage, driven entirely through uv: PEP 735
`dev` dependency group, `uv sync --locked` in CI, `uv_build` backend, src layout.
CI lives in `.github/workflows/build.yml` (3 OS x 3 Python matrix running
`pytest --cov` + `uv build`), plus main-only analysis and pre-commit workflows.
See proposal.md for motivation.

## Goals / Non-Goals

**Goals:**
- Mutation testing available locally via one command and enforced-as-report in CI on every PR.
- Base coverage raised first so the mutation score starts from a fair baseline.
- No slowdown of the pre-commit loop.

**Non-Goals:**
- No gating on a mutation-score threshold in this change; survivors are reported, not failed.
- No mutation runs on macOS/Windows or on every Python version — one ubuntu/Python cell is enough.
- No pre-commit hook, no changes to runtime code in `src/scan_pdf`.

## Decisions

**D1: pytest-gremlins as a pytest plugin, added to the `dev` group.**
`uv add --dev pytest-gremlins` keeps the single-toolchain (uv) discipline of the
project and makes the run `uv run pytest --gremlins`. Alternative: a separate
mutation tool (mutmut, cosmic-ray) — rejected because those are separate CLIs
with slower, file-rewriting mutation loops; pytest-gremlins mutates in memory,
runs coverage-guided test selection, parallel workers, and content-hash caching,
which suits a suite this small.

**D2: Explicit `paths = ["src/scan_pdf"]` in `[tool.pytest-gremlins]`.**
Auto-discovery reads setuptools metadata first and falls back to `src/`; this
project uses `uv_build`, so discovery is not guaranteed. Setting `paths`
explicitly removes the ambiguity and covers `cli.py` too, per scope.

**D3: Separate pytest invocation from the coverage run.**
`uv run pytest --gremlins` must not be combined with `--cov` (pytest-gremlins
does its own coverage pre-scan for test selection) nor with `-n` (incompatible
with its worker model). So the CI mutation job runs pytest twice in effect:
the existing matrix job keeps `--cov`, the new job runs only `--gremlins`.

**D4: Dedicated non-matrix job in `build.yml` on ubuntu-latest, Python 3.13.**
Mutation results are platform-independent; multiplying across the 3x3 matrix
would triple CI cost for nothing. Keeping it in `build.yml` (not `analysis.yml`)
gets PR feedback, since `analysis.yml` runs on main only. Alternative: a
separate `mutation.yml` workflow — rejected to avoid another file for one job.

**D5: Report-only gating; JSON report uploaded as artifact.**
`cli.py` sits at 60% coverage today, so survivors are guaranteed initially;
failing the build on them would block all PRs. The job therefore exits zero
regardless of survivors, writes `report = ["console", "json"]` with the JSON
under `reports/` and uploads it via `actions/upload-artifact`. Survivors get
triaged later (fix the test or `# gremlin: pardon[reason]`), and gating can be
added as a follow-up once the baseline is clean.

**D6: New tests land before the first mutation run.**
Coverage-guided selection maps each mutant to the tests covering its line, so
raising coverage of `cli.py` (untested `parse_args()` body lines 14-86, the
"no pages found" branch line 130) and `convert.py` (flip, non-zero returncode,
missing target file) directly raises the number of mutants that can be killed.
Tests use the existing style: `tests/__init__.py` `Options` namespace plus
`unittest.mock.patch`, as in `test_cli.py`.

**D7: No pre-commit hook.**
Mutation testing re-runs the suite once per mutant; even fast, that is slower
than the hook loop should be, and the pre-commit CI job would duplicate the
dedicated mutation job.

## Risks / Trade-offs

- **[Risk]** The plugin's exit code on surviving gremlins is not documented
  conclusively; if it exits non-zero on survivors, the report-only job would
  fail. → Mitigation: verify empirically on the first local run during
  implementation; if it fails on survivors, either accept gating or wrap the
  invocation so the job stays report-only.
- **[Risk]** Equivalent mutants (e.g. `util.py` `__exit__` guard) will survive
  legitimately. → Mitigation: triage with `# gremlin: pardon[reason]` and the
  `--gremlin-audit-pardons` flag; enforcement flags (`--strict-pardons`,
  `--gremlin-max-pardons-pct`) are available for a later gating change.
- **[Risk]** Gremlin cache directory in CI is ephemeral; `cache = true` mainly
  helps local runs. → Mitigation: harmless in CI; do not wire cache restore.
- **[Risk]** New tests could be flaky if they touch the real filesystem. →
  Mitigation: follow the existing pattern — `run()` already executes inside a
  real `TempDir`; only `sys.argv` and the collaborator classes are patched.

## Migration Plan

No migration: purely additive tooling. Rollback = remove the `mutation` job and
the `[tool.pytest-gremlins]` section and drop the dependency (`uv remove --dev
pytest-gremlins`).

## Open Questions

- Does `pytest --gremlins` exit non-zero when gremlins survive? (Answered
  empirically during implementation; affects only whether report-only needs a
  wrapper.)
- What mutation-score threshold, if any, should gate CI later? (Deferred until
  survivors are triaged; does not change this change's specs or tasks.)
