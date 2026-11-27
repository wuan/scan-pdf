# Tasks

## 1. CLI parser refactor and tests (`cli.py`, `tests/test_cli.py`)

- [x] 1.1 Extract `build_parser()` from `parse_args()` (which now calls `build_parser().parse_args()`) and verify the existing `TestParseArgs` tests pass unchanged
- [x] 1.2 Remove redundant argparse kwargs (`dest=` equal to the derived name, `type=str`, `default=None`, `action="store"`), keeping `dest="debug"` on `-d`; verify `uv run pytest tests/test_cli.py` and `uv run basedpyright` pass
- [x] 1.3 Add a test asserting `parser.description` and the exact help text per option (`{action.dest: action.help}` table); verify it fails if any help string is altered
- [x] 1.4 Add parametrized tests accepting every `--color-mode` (`bw`, `gray`, `color`) and every `--paper-format` (`A3`–`A7`), plus tests that `--color-mode sepia` and `--paper-format Letter` raise `SystemExit` with a non-zero code; verify with `uv run pytest tests/test_cli.py`
- [x] 1.5 Add a test that `run()` without `-d` calls `basicConfig(level=logging.INFO)` (patched); verify it passes alongside the existing `test_debug`
- [x] 1.6 Tighten `test_no_pages_found` to assert `caplog.record_tuples == [("scan_pdf.cli", logging.WARNING, "no pages found")]`; verify it passes

## 2. Scanner (`scan.py`, `tests/test_scan.py`)

- [x] 2.1 Convert `PaperFormat` to `@dataclass(frozen=True)` with fields `left, width, top, height` in the same order; verify existing scanner tests and `uv run basedpyright` pass
- [x] 2.2 Fix the log typo `"call retured %d"` → `"call returned %d"`, and add a test asserting the scanner's DEBUG records `call <full command>` and `call returned 0` on logger `scan_pdf.scan`; verify it passes
- [x] 2.3 Add a test that an unsupported `paper_format` (e.g. `"Letter"`) yields `-l 0 -x 210 -t 0 -y 297`; verify it passes
- [x] 2.4 Add a test with string overrides `paper_left="5"`, `paper_width="200"`, `paper_top="7"`, `paper_height="280"` asserting `-l 5 -x 200 -t 7 -y 280`; verify it passes

## 3. Converter (`tests/test_convert.py`)

- [x] 3.1 Add a parametrized test for `gray` and `color` with `color_depth=4` asserting `-depth 4` in the command; verify it passes
- [x] 3.2 Assert the mocked `os.path.exists` is called with `"base.pdf"`; verify the test passes
- [x] 3.3 Replace the substring log checks with exact `caplog.record_tuples` assertions for `convert base` (INFO), `call: <full command>` (DEBUG), `convert failed: <full command>` (ERROR), and `target file 'base.pdf' does not exist` (ERROR); verify with `uv run pytest tests/test_convert.py`

## 4. Combiner (`tests/test_combine.py`)

- [x] 4.1 Assert `caplog.record_tuples` contains `("scan_pdf.combine", logging.INFO, "combine 2 pages into output.pdf")`; verify it passes

## 5. TempDir (`tests/test_util.py`)

- [x] 5.1 Assert the temp directory base name starts with `scanpdf_`; verify it passes
- [x] 5.2 Add a test that removes the directory inside the `with` block and verify leaving the block raises nothing
- [x] 5.3 Add a test that `TempDir().__exit__(None, None, None)` with `shutil.rmtree` patched does not call it; verify it passes

## 6. Verification

- [x] 6.1 Run `uv run pytest`, `uv run basedpyright`, and `pre-commit run --all-files`; verify all pass
- [x] 6.2 Run `uv run mutmut run` and `uv run mutmut results`; verify 0 survivors. For any remaining survivor, either add a killing test or, only if it is proven equivalent, add `# pragma: no mutate` with a justification comment and re-run until 0 survive

## Workflow follow-up

- Sync specs (`scan-to-pdf` is new, `build-tooling` gains a requirement) and archive the change after review.
