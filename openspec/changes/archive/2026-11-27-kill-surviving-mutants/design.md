# Design

## Context

See proposal.md (Why) for motivation. These are the findings from analysing all 165 survivors (`uv run mutmut show <name>`):

| Root cause | Approx. count | Where |
|---|---|---|
| Equivalent mutants from argparse kwargs that restate defaults (`dest` = derived name, `type=str`, `default=None`, `action="store"`) | ~45 | `cli.parse_args` |
| Help/description strings only visible in `--help` | ~45 | `cli.parse_args` |
| Log calls not asserted, or asserted by substring only | ~50 | `convert`, `combine`, `scan`, `cli.run` |
| `choices` never exercised with invalid/explicit values | ~12 | `cli.parse_args` |
| Real behaviour gaps (debug-off level, depth in gray mode, `exists(target)`, A4 fallback, paper overrides, TempDir prefix/cleanup) | ~13 | `cli.run`, `convert`, `scan`, `util` |
| `PaperFormat.__init__` field assignments | 4 | `scan` |

Two mechanics of mutmut 3 / pytest shape the approach:

- mutmut switches mutants on at call time (trampolines). Code that runs at **import** time (the `Scanner.paper_formats` dict building `PaperFormat` instances) always uses the original code, so those mutants can only be killed by calling the constructor inside a test.
- `logging.basicConfig` is a no-op under pytest because the logging plugin already installs root handlers, so the level must be checked by patching `basicConfig`, as `test_debug` already does.
- A mutated format string such as `logger.info(None, x)` does not raise at the call site. `logging` swallows formatting errors in `handleError`. It only fails when `record.getMessage()` is evaluated, which `caplog.record_tuples` does.

## Goals / Non-Goals

**Goals:**
- Every current survivor is either killed by a test that asserts observable behaviour, or removed by a behaviour-neutral refactor of redundant code.
- Tests stay readable: one focused test per behaviour, with parametrization where several values exercise the same rule.

**Non-Goals:**
- Making the CI mutation job fail on survivors (it stays report-only).
- Changing CLI flags, defaults, or parsed value types (e.g. paper overrides stay strings).
- Reaching for `# pragma: no mutate` before trying a test or refactor.

## Decisions

1. **Remove redundant argparse kwargs instead of testing them.** These mutants are equivalent by construction, so no test can kill them. Deleting the kwargs removes the mutants and simplifies the code. `dest="debug"` on `-d` stays, because without it argparse would derive `d` (those mutants are already killed). *Alternative:* `# pragma: no mutate` on each line. Rejected as noisier than simply deleting dead code.

2. **Extract `build_parser()` and assert help texts exactly via the parser's actions.** Test `parser.description` and a `{action.dest: action.help}` mapping against an expected table. *Alternatives:* a substring check on `--help` output does not kill `"XX…XX"` mutants. A full `--help` snapshot is brittle across the 3.11–3.13 CI matrix, because argparse formatting changed between versions. Excluding help strings with pragmas was also considered; testing was preferred because the table documents the CLI. `_actions` is private but has been stable for many years. If that is ever a concern, the test can switch to `parser._option_string_actions` or parse `format_help()` at a fixed `COLUMNS`.

3. **`PaperFormat` becomes `@dataclass(frozen=True)`.** The generated `__init__` is not mutated, which removes the 4 import-time mutants. It also adds value equality and immutability, which suit a constant table. Attribute names and positional order (`left, width, top, height`) stay the same, so call sites are unchanged. *Alternative:* keep the class and add a direct construction test. That would also work but keeps boilerplate.

4. **Assert logs via `caplog.record_tuples` at DEBUG level with exact messages.** One assertion per call site gives `(logger name, level, message)`. This kills format-string, argument, `getLogger(None)` and `"XX…XX"` mutants together. Use `caplog.set_level(logging.DEBUG, logger="scan_pdf.<module>")` so only the module under test is captured.

5. **Fix the `"call retured %d"` typo** in the same change, since the new test pins that message. This is a log-text change only.

6. **Behaviour-gap tests mirror the spec scenarios** in `specs/scan-to-pdf/spec.md`. They reuse the existing fixtures (`subprocess` and `os_path_exists` mocks, the `options` fixture in `test_scan.py`, and the CLI patch fixtures). Paper override values are passed as strings, because that is what argparse produces.

## Risks / Trade-offs

- [Exact help/log assertions make wording changes require test updates] → Accepted. That is the point of pinning user-visible text, and the expected tables are kept in one place per test.
- [Reliance on private `argparse` `_actions`] → Isolated in a single test, with a fallback noted in Decision 2.
- [Dataclass changes `PaperFormat` semantics (equality, hashing, immutability)] → No code mutates or compares instances today (verified by reading `scan.py` and `cli.py`). basedpyright in "all" mode will flag any misuse.
- [New mutants may appear from the refactor, e.g. in `build_parser`] → The final `mutmut run` verification task covers them.
