# Proposal

## Why

The first full `uv run mutmut run` reports 576 mutants with 411 killed and **165 survived** (~71% score). The survivors show that large parts of the CLI and pipeline behaviour are executed by tests but never asserted: argument definitions, `choices` validation, log level selection, paper-format fallback and overrides, `TempDir` cleanup semantics, and every log message. Some survivors are equivalent mutants caused by redundant code (argparse arguments that restate defaults, a hand-written `PaperFormat.__init__` evaluated at import time) that no test can ever kill. Closing these gaps now, while the suite is small, establishes a zero-survivor baseline so new survivors in CI are meaningful signal rather than noise.

## What Changes

- `src/scan_pdf/cli.py`: extract `build_parser()` from `parse_args()`; drop redundant argparse keyword arguments that restate argparse defaults (`dest=` equal to the derived name, `type=str`, `default=None`, `action="store"`), keeping `dest="debug"` on `-d`. No change to parsed values or CLI interface.
- `src/scan_pdf/scan.py`: turn `PaperFormat` into a frozen dataclass with the same fields; fix the log message typo `"call retured %d"` → `"call returned %d"` (log text change only).
- Tests (`tests/test_cli.py`, `test_scan.py`, `test_convert.py`, `test_combine.py`, `test_util.py`) gain assertions for:
  - parser description and per-option help texts (exact match),
  - rejection of invalid `--color-mode` / `--paper-format` values and acceptance of every valid value,
  - INFO log level when `-d` is not given,
  - `-depth <color_depth>` for gray/color modes and the existence check on the converted target file,
  - A4 fallback for unknown paper formats and explicit `--paper-left/-width/-top/-height` overrides,
  - `TempDir` prefix, tolerant cleanup of an already-removed directory, and no cleanup when never entered,
  - exact logger name, level, and message for every log call.
- Any mutant still surviving after this work that is proven equivalent is marked `# pragma: no mutate` with a short justification.

## Capabilities

### New Capabilities
- `scan-to-pdf`: the user-facing behaviour of the `scan-pdf` tool: CLI options and their validation, scanner/converter command construction, paper format handling, PDF combination, temporary working directory lifecycle, and logging.

### Modified Capabilities
- `build-tooling`: the mutmut requirement gains a zero-surviving-mutant baseline and a rule for documenting equivalent mutants. CI stays report-only.

## Impact

- `src/scan_pdf/cli.py`, `src/scan_pdf/scan.py`: behaviour-neutral refactors plus one log-text typo fix.
- `src/scan_pdf/convert.py`, `combine.py`, `util.py`: unchanged unless an equivalent mutant needs a pragma.
- `tests/*`: new and tightened tests.
- `.github/workflows/build.yml`: untouched (mutation job remains report-only).
- No dependency, packaging, or CLI interface changes.
