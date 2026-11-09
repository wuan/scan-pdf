# Proposal

## Why

mypy is the odd one out in an otherwise modern toolchain: it is a second type checker with its own config dialect, and the project already runs everything through uv and pre-commit. basedpyright is a drop-in, strictly-typed pyright fork distributed on PyPI with a bundled runtime, so it slots into the existing `uv run` flow with no extra system dependencies and no third-party CI action. Switching also upgrades strictness for free: based mode ("all") is a superset of the current `disallow_untyped_defs` + `warn_return_any` posture, so the type-checking bar goes up instead of sideways.

## What Changes

- `pyproject.toml`: the dev dependency `mypy>=2.3,<3` is replaced with `basedpyright` (pinned `<2`), and the `[tool.mypy]` section is replaced with a `[tool.basedpyright]` section using full based mode (`typeCheckingMode = "all"`), `pythonVersion = "3.11"`, and an execution environment rooted at `src` so only `src/scan_pdf` is checked (parity with today's `packages = ["scan_pdf"]`; tests stay unchecked).
- `.pre-commit-config.yaml`: the local hook entry changes from `uv run mypy` to `uv run basedpyright`, keeping `language: system`, `types: [python]`, and `pass_filenames: false`.
- `uv.lock`: regenerated via `uv lock` after the dependency swap.
- `openspec/specs/build-tooling/spec.md`: the five requirements that name mypy (Python floor tooling config, dev dependency list, src-layout path config, CI provisioning, pre-commit hook) are updated to name basedpyright and its config keys.
- No CI workflow changes: mypy is only exercised through `pre-commit.yml`, which runs `pre-commit run --all-files` after `uv sync --locked` and needs no edit.
- Source code may need small adjustments if based mode's stricter rules (`reportAny`, `reportExplicitAny`, etc.) surface new diagnostics in the 5-module package; any such fixes are part of this change.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `build-tooling`: the static type checker named in the dev dependency group, tooling config, and pre-commit hook requirements changes from mypy to basedpyright in full based mode, scoped to `src/`.

## Impact

- `pyproject.toml` — dev group dependency swap; `[tool.mypy]` → `[tool.basedpyright]`.
- `.pre-commit-config.yaml` — one hook entry swapped.
- `uv.lock` — regenerated.
- `openspec/specs/build-tooling/spec.md` — mypy mentions updated (applied via delta spec + sync).
- `.github/workflows/*.yml` — untouched.
- `src/scan_pdf/*.py` — only touched if based mode reports new errors that require code fixes.
- `tests/`, `README.rst`, `sonar-project.properties` — untouched.
