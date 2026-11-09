# Design

## Context

Current state and motivation are in proposal.md. mypy is wired in exactly
three places: the `dev` dependency group and `[tool.mypy]` section in
`pyproject.toml`, and a local pre-commit hook (`entry: uv run mypy`,
`pass_filenames: false`). CI never calls mypy directly — `pre-commit.yml`
runs it via `pre-commit run --all-files` after `uv sync --locked`. The
package has no `py.typed` marker, which is why `mypy_path = "src"` +
`packages = ["scan_pdf"]` checks the sources directly instead of the
installed package. The codebase is small (5 modules, 11 functions) and fully
annotated.

## Goals / Non-Goals

**Goals:**

- One static type checker — basedpyright in full based mode — enforced by
  the existing pre-commit hook, locally and in CI, with no new system
  dependencies.
- Strictness goes up, not sideways: based mode is a superset of the current
  `disallow_untyped_defs` + `warn_return_any` posture.
- Check scope stays identical: only `src/scan_pdf`, tests excluded.

**Non-Goals:**

- No changes to GitHub Actions workflows (mypy/basedpyright only run through
  the pre-commit workflow).
- No `py.typed` marker added to the package; the src-rooted execution
  environment replaces the need for one.
- No changes to `tests/`, `README.rst`, or `sonar-project.properties`.
- No switch of pre-commit to an isolated hook environment; the local
  `language: system` hook shape is kept.

## Decisions

### D1 — basedpyright replaces mypy as the single type checker

- **Choice**: swap the dev dependency `mypy>=2.3,<3` for
  `basedpyright>=1,<2` in `[dependency-groups] dev` and delete
  `[tool.mypy]`.
- **Rationale**: basedpyright ships on PyPI with a bundled Node runtime, so
  `uv run basedpyright` works in CI (ubuntu-latest) and locally with no
  system Node. It is a pyright fork, so it reads standard
  `pyproject.toml` config and has first-class editor integration. Keeping
  mypy alongside would preserve the second-toolchain cost this change exists
  to remove.
- **Alternatives**: (a) keep mypy — rejected, that is the status quo this
  change removes; (b) upstream `pyright` — basedpyright is the same engine
  with strictly-typed defaults, which matches the project's existing strict
  config better than pyright's "standard" default mode.

### D2 — Configuration lives in `[tool.basedpyright]` in pyproject.toml

- **Choice**: replace `[tool.mypy]` with:

  ```toml
  [tool.basedpyright]
  pythonVersion = "3.11"
  typeCheckingMode = "all"
  executionEnvironments = [{ root = "src" }]
  ```

- **Rationale**: one config file, same as ruff and the old mypy block.
  Mapping from the old mypy config:

  | mypy | basedpyright |
  |---|---|
  | `python_version = "3.11"` | `pythonVersion = "3.11"` |
  | `disallow_untyped_defs = true` | `reportMissingParameterType` / `reportUnknownParameterType` (on in "all") |
  | `warn_return_any = true` | `reportAny` / `reportReturnType` (on in "all") |
  | `mypy_path = "src"` + `packages = ["scan_pdf"]` | `executionEnvironments = [{ root = "src" }]` |

- **Alternatives**: a standalone `pyrightconfig.json` — rejected, the
  project keeps all tool config in `pyproject.toml`; `typeCheckingMode =
  "recommended"` — rejected, the user explicitly chose full based mode.

### D3 — Check scope is pinned to `src/` via an execution environment

- **Choice**: `executionEnvironments = [{ root = "src" }]` so basedpyright
  resolves and checks `src/scan_pdf` directly.
- **Rationale**: parity with mypy's `packages = ["scan_pdf"]` — tests stay
  unchecked — and no dependence on the installed package, which lacks
  `py.typed`. Rooting the execution environment at `src` makes
  `scan_pdf.*` resolve to the sources under check.
- **Alternatives**: `extraPaths = ["src"]` at the project root — rejected,
  it would also pull `tests/` into the checked file set when basedpyright
  is invoked without arguments.

### D4 — Pre-commit hook keeps the local `language: system` shape

- **Choice**: in `.pre-commit-config.yaml`, change only the hook id/name and
  entry:

  ```yaml
  - id: basedpyright
    name: basedpyright
    entry: uv run basedpyright
    language: system
    types: [python]
    pass_filenames: false
  ```

- **Rationale**: basedpyright reads its own config and needs the whole
  package for cross-module analysis, so `pass_filenames: false` stays.
  `language: system` + `uv run` guarantees it executes in the uv-managed
  environment where basedpyright and pypdf are installed — the same reason
  the mypy hook was local (see the archived pre-commit-harness design).
- **Alternatives**: the community `basedpyright` pre-commit repo hook with
  an isolated env — rejected, the isolated env would not have pypdf/`scan_pdf`
  importable the way the project venv does.

### D5 — Lockfile regenerated with `uv lock`

- **Choice**: after editing `pyproject.toml`, run `uv lock` (then
  `uv sync --locked` to verify) so `uv.lock` drops mypy and pins
  basedpyright.
- **Rationale**: CI installs with `uv sync --locked`; a stale lockfile fails
  the build, so the lock must be committed in the same change.

## Risks / Trade-offs

- [Based mode is stricter than mypy's config — `reportAny`,
  `reportExplicitAny`, `reportUnknown*` may flag pypdf interactions or
  untyped spots mypy tolerated] → Run `uv run basedpyright` first and fix
  what surfaces in the 5-module package; prefer small code fixes over
  disabling rules, and keep any `report*` disables narrowly scoped and
  commented in pyproject.
- [basedpyright bundles a Node runtime, adding venv weight] → Acceptable:
  CI runners and dev machines already carry Node; no system-level install
  is required.
- [Config key drift between pyright/basedpyright versions] → Pin
  `basedpyright>=1,<2` and let Dependabot's uv ecosystem bumps drive
  upgrades, same as every other dev tool.

## Migration Plan

1. Edit `pyproject.toml`: swap the dev dependency and replace `[tool.mypy]`
   with `[tool.basedpyright]` per D2/D3.
2. Run `uv lock` and `uv sync --locked`.
3. Edit `.pre-commit-config.yaml` per D4.
4. Run `uv run basedpyright`; fix any new strict-mode diagnostics in
   `src/scan_pdf/`.
5. Run `uv run pre-commit run --all-files` to verify the hook end to end.
6. Sync the build-tooling spec delta into `openspec/specs/` (openspec sync).

Rollback: revert the single commit — no runtime behavior, database, or API
surface is affected; the type checker is a dev-only tool.

## Open Questions

- None blocking. The exact basedpyright minor version pinned in `uv.lock`
  is an implementation detail resolved by `uv lock` at apply time.
