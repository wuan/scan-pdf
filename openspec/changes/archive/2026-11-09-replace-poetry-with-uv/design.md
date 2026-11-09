# Design

## Context

The project currently uses Poetry 2.1.1 for dependency management, locking (`poetry.lock`, 21 packages), virtualenv creation, running tools (`poetry run`), and building (`poetry build` with `poetry-core`). Poetry is referenced in `pyproject.toml`, three GitHub workflows, `.pre-commit-config.yaml`, and `.github/dependabot.yml`. The runtime dependency surface is a single package (`pypdf`); dev tools are pytest, pytest-mock, pytest-cov, mock, assertpy, mypy, ruff. Source layout is flat (`scan_pdf/` at repo root). See proposal.md for motivation.

uv 0.13.7 is installed locally; every pyproject shape below was verified against it (`uv lock`, `uv sync --locked`, `uv build`, `uv run` all exercised in a scratch project).

## Goals / Non-Goals

**Goals:**
- One toolchain: uv owns lock, sync, run, and build. No Poetry artifacts remain.
- Standard metadata: PEP 621 `[project]` + PEP 735 `[dependency-groups]` instead of `[tool.poetry]`.
- Fully commit to the uv-native build backend (`uv_build`), including its flat-layout knob.
- Python floor promoted to 3.11 everywhere (metadata, ruff, mypy, pyupgrade, CI matrix).

**Non-Goals:**
- No edits to the contents of `scan_pdf/` source files or tests — the move to `src/` is a pure `git mv`.
- No new dev tooling beyond what exists; README and `.coveragerc` unchanged.
- Archived OpenSpec changes that mention Poetry stay untouched (historical record).

## Decisions

### D1 — Build backend: `uv_build` (fully committed)
- **Choice**: `[build-system] requires = ["uv_build>=0.13.7,<0.14.0"]`, `build-backend = "uv_build"` (the exact stanza `uv init --package` generates on uv 0.13.7).
- **Rationale**: uv_build is PEP 517 compliant, so `pip install .` and PyPI uploads still work through any standard installer; but the project is managed end-to-end by uv, so uv's native backend removes a translation layer and is the fastest path.
- **Alternative considered**: `hatchling` — the ecosystem-default backend with the broadest familiarity. Rejected per explicit decision to fully commit to uv; it would keep a second backend's conventions alive for no functional gain here.

### D2 — Move the package to src layout (`src/scan_pdf/`)
- **Choice**: `git mv scan_pdf src/scan_pdf` and rely on `uv_build`'s default src module root — no `[tool.uv.build-backend]` override at all.
- **Rationale**: src layout is what `uv_build` expects out of the box (verified: flat layout fails with "Expected a Python module at: src/scan_pdf/__init__.py" unless `module-root = ""` is set, while src layout builds with zero config). It also prevents tests and scripts from accidentally importing the uninstalled package from the repo root. The module name `scan_pdf` is unchanged, so imports, `--cov=scan_pdf`, and the `scan-pdf` entry point are all unaffected.
- **Alternative considered**: keep flat layout via `module-root = ""`. Rejected — the user explicitly wants src layout, and it is the tool's default rather than a special case.

### D3 — Dev dependencies in PEP 735 `[dependency-groups]`
- **Choice**: `[dependency-groups] dev = [...]` with `[tool.uv] default-groups = ["dev"]` and `package = true`.
- **Rationale**: exact 1:1 mapping from Poetry's `dev` group; uv installs the `dev` group by default, so `uv sync` alone gives a complete environment (verified).
- **Alternative considered**: `[project.optional-dependencies]` — installable by end users via `pip install scan-pdf[dev]`, which we do not want; dev tools must not leak into the published distribution's extras.

### D4 — Poetry caret ranges translated to PEP 508
- **Choice**: `^9.1` → `>=9.1,<10`; `^3.14.0` → `>=3.14,<4`; `^7.1.0` → `>=7.1,<8`; `^5.1.0` → `>=5.1,<6`; `^1.1` → `>=1.1,<2`; `^2.3.0` → `>=2.3,<3`; `^0.16.0` → `>=0.16,<0.17` (zero-major caret pins the minor). `python = "^3.10"` → `requires-python = ">=3.11"` (floor promotion, not a direct translation).
- **Rationale**: preserves the exact upper bounds Poetry enforced, so the resolved dependency set is equivalent modulo the Python floor.

### D5 — Python floor 3.11
- **Choice**: `requires-python = ">=3.11"`; ruff `target-version = "py311"`; mypy `python_version = "3.11"`; pyupgrade `--py311-plus`; CI matrix `["3.11", "3.12", "3.13"]` (drops 3.10).
- **Rationale**: 3.10 is EOL-adjacent and the promotion was an explicit goal; uv will fetch a managed 3.11+ interpreter locally even where the system Python is older.

### D6 — CI provisions uv with `astral-sh/setup-uv`
- **Choice**: replace `abatilo/actions-poetry` with SHA-pinned `astral-sh/setup-uv` (latest release SHA at implementation time, tag in comment, matching the repo's pin-everything convention) with `enable-cache: true`; run `uv sync --locked`, `uv run pytest ...`, `uv run pip list`, `uv build`. The uv tool version itself floats; Dependabot bumps the action SHA.
- **Rationale**: removes a third-party action in favor of the tool vendor's official one; setup-uv's cache replaces Poetry's cache; `--locked` makes CI fail on a stale `uv.lock` instead of mutating it.
- **Alternative considered**: `pip install uv` — no pinning, no cache. Rejected.

### D7 — Commit `uv.lock`, delete `poetry.lock`
- **Choice**: `uv.lock` is committed; `poetry.lock` is deleted.
- **Rationale**: this is an application published to PyPI but developed as a repo; a committed lock makes CI reproducible (`--locked`) and Dependabot updates reviewable via PRs.

### D8 — Dependabot ecosystem `uv`
- **Choice**: `package-ecosystem: uv` in `.github/dependabot.yml` (replacing `poetry`), keeping `github-actions` and `pre-commit`.
- **Rationale**: uv's lockfile is the manifest Dependabot should watch. Verification that the `uv` ecosystem is enabled for this repo is a task-level check (see tasks).

### D9 — Pre-commit mypy hook stays `language: system`, entry becomes `uv run mypy`
- **Choice**: only the `entry` changes; `types: [python]`, `pass_filenames: false` stay.
- **Rationale**: preserves the deliberate design from the pre-commit-harness change (the hook must type-check against the project env, not a pre-commit-managed one); `uv run` resolves that env as long as `uv sync` ran.

### D10 — Target `pyproject.toml` shape
```toml
[project]
name = "scan-pdf"
version = "0.4.10"
description = "Tools for using scanners with document feeder"
authors = [{ name = "Andreas Würl", email = "andi@tryb.de" }]
license = "Apache-2.0"
readme = "README.rst"
requires-python = ">=3.11"
dependencies = ["pypdf>=5.1,<7.0"]

[project.scripts]
scan-pdf = "scan_pdf.cli:run"

[dependency-groups]
dev = [
    "pytest>=9.1,<10",
    "pytest-mock>=3.14,<4",
    "pytest-cov>=7.1,<8",
    "mock>=5.1,<6",
    "assertpy>=1.1,<2",
    "mypy>=2.3,<3",
    "ruff>=0.16,<0.17",
]

[build-system]
requires = ["uv_build>=0.13.7,<0.14.0"]
build-backend = "uv_build"

[tool.uv]
package = true
default-groups = ["dev"]

# no [tool.uv.build-backend] override — src layout is the default
# [tool.pytest.ini_options] unchanged; [tool.ruff] target py311 (src = ["src", "."] not needed — verified);
# [tool.mypy] python_version 3.11 + mypy_path = "src" + packages = ["scan_pdf"]
```

### D11 — Tooling path adjustments for src layout
- **Choice**: only three places address the package by filesystem path and need updating: mypy gains `mypy_path = "src"` (verified: without it, mypy resolves the installed editable package and warns about the missing `py.typed` marker; with it, mypy checks `src/scan_pdf` sources directly — "Success: no issues found in 1 source file"), and `sonar-project.properties` changes to `sonar.sources=src/scan_pdf/`. Ruff needs no `src` config: verified that with src layout and no `src` setting, ruff already classifies `scan_pdf` as first-party for the `I` rules. `--cov=scan_pdf` in the workflows stays valid because coverage measures the module name.
- **Rationale**: keep the diff to exactly the references that break; module-name-based references (`--cov`, entry point, test imports) must not change.
SPDX `license = "Apache-2.0"` verified to build with uv_build.

## Risks / Trade-offs

- **[Risk]** The `uv_build` upper bound `<0.14.0` must stay compatible with the uv version that builds the project. → Mitigation: `uv lock`/`uv build` fail loudly on mismatch, CI catches it, and Dependabot bumps both `uv.lock` and the setup-uv SHA in lockstep.
- **[Risk]** Dependabot's `uv` ecosystem may not be enabled for this repository yet. → Mitigation: task explicitly verifies the first Dependabot run after merge; fallback is removing the entry and relying on `uv lock --upgrade` PRs manually.
- **[Risk]** Contributors with a stale Poetry `VIRTUAL_ENV` active will see uv ignore it (warning observed locally). → Mitigation: migration task removes the old Poetry venv; uv always manages `./.venv` explicitly.
- **[Risk]** Contributors without uv installed cannot run the `language: system` mypy hook locally. → Mitigation: same exposure as the current Poetry setup; CI enforces the hook regardless.
- **[Risk]** Windows/macOS runners in the build matrix. → Mitigation: uv and `uv sync --locked` are cross-platform; no shell-specific commands are introduced (pytest invocation unchanged apart from the `uv run` prefix).

## Migration Plan

1. `git mv scan_pdf src/scan_pdf` (D2) — no file contents change.
2. Rewrite `pyproject.toml` (D10/D11), run `uv lock`, delete `poetry.lock`, add `uv.lock`; update `sonar-project.properties`.
3. Update `.gitignore` (`/.venv/`), `.pre-commit-config.yaml`, `.github/dependabot.yml`, and the three workflows.
3. Verify locally: `uv sync --locked`, `uv run pytest`, `uv run mypy`, `uv run ruff check scan_pdf tests`, `uv run ruff format --check scan_pdf tests`, `uv build`, `pre-commit run --all-files`.
4. Rollback: `git revert` of the merge commit restores Poetry state completely, since no source files change.

## Open Questions

None blocking. The Dependabot `uv`-ecosystem check is a verification step in tasks, not a design unknown.
