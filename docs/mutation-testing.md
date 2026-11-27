# Mutation Testing: A Short Overview

## What it is

Mutation testing checks how well a test suite catches bugs. A tool makes many small, deliberate changes to the production code, one at a time, and runs the tests against each changed version. If the tests still pass, the change went unnoticed, which means a real bug in that spot would go unnoticed too.

Line coverage shows which code the tests *execute*. Mutation testing shows which behaviour the tests actually *check*.

## Nomenclature

| Term | Meaning |
|---|---|
| **Mutant** | A copy of the code with exactly one small change, e.g. `<` → `<=`, `+` → `-`, `True` → `False`, a string replaced with `"XX…XX"`, an argument replaced with `None`. |
| **Mutation operator** | A rule that produces mutants, e.g. "swap comparison operator" or "negate condition". |
| **Killed** | At least one test failed against the mutant. The tests detected the change. ✅ |
| **Survived** | All tests passed against the mutant. Either an assertion is missing or the mutant is equivalent. ❌ |
| **No coverage** | No test executes the mutated line, so the mutant survives automatically. |
| **Timeout** | The mutant made the tests hang, e.g. an endless loop. Usually counted as killed. |
| **Suspicious** | The mutant made the tests noticeably slower but not slow enough to time out. Needs a manual look. |
| **Equivalent mutant** | A change that cannot alter observable behaviour, e.g. passing an argument that already equals the library default. No test can kill it, so delete the redundant code or exclude the mutant with a justification. |
| **Mutation score** | Killed ÷ total mutants. The main headline metric. |
| **Pragma / exclusion** | An inline marker (e.g. `# pragma: no mutate`) that tells the tool not to mutate a line. |

## How a run works

1. Run the test suite once and record which tests cover which code.
2. Generate mutants for the target source files.
3. For each mutant, run the tests that cover it and stop at the first failure.
4. Report the killed and surviving mutants. Investigate each survivor: add or tighten a test, remove redundant code, or exclude it with a documented reason.

## Benefits

- Shows tests that execute code without asserting anything ("assertion-free coverage").
- Finds dead and redundant code. Mutants that can never be killed often point at it.
- Gives a stronger quality signal than coverage, which is easy to game.
- Turns implicit behaviour (log messages, error texts, defaults) into explicit, tested contracts.

## Risks and pitfalls

- **Cost.** Every mutant needs another test run, so the run time grows with code size × test time. Keep the suite fast, use coverage-guided test selection and caching, and run it as its own CI job rather than on every matrix cell. Put it in pre-commit only while a full run stays fast.
- **Equivalent mutants cause noise.** They can never be killed. Time spent proving that a mutant is equivalent is real effort, and a 100% score can be out of reach without exclusions.
- **Exclusions get abused.** Pragmas can hide real gaps. Allow them only with a written justification and review them like code.
- **Brittle tests.** Killing string mutants means asserting exact texts (help, logs, errors), so every wording change breaks tests. That's fine for user-visible contracts but costly for internal details. Decide deliberately what counts as a contract.
- **Testing the implementation, not the behaviour.** Chasing the score can lead to tests that mirror the code line by line. A mutant is worth killing only if its change would matter to a user or caller.
- **Goodhart's law.** Once the mutation score becomes a target, it stops being a good measure. Use survivors as prompts for investigation, not as a KPI to optimise.
- **Stale caches.** Incremental tools can reuse old results after test-only changes and report false survivors (or false kills). Clear the cache before trusting the numbers.
- **Blind spots.** Mutation operators are simple, syntactic changes. They don't simulate integration failures, concurrency bugs, or missing features, and code that runs at import or start-up may not be mutated at runtime at all.
- **Gating too early.** Failing CI on survivors before the baseline is clean blocks every change. Start report-only, reach a clean baseline, then decide whether to gate.

## Recommended adoption path

1. Close obvious coverage gaps first.
2. Add mutation testing as a separate, report-only CI job.
3. Triage the survivors: kill them with meaningful tests, delete redundant code, and exclude provably equivalent mutants with a reason.
4. Once the baseline is clean, treat each new survivor as a review signal. Optionally gate on "no new survivors" rather than on an absolute score.

## In this project

The tool is mutmut, which mutates the code under `src/scan_pdf/`. The README section "Mutation testing" explains how to run it locally. The baseline is zero surviving mutants, and it is enforced: `scripts/mutation_check.py` runs as a pre-commit hook and in CI, and fails on any survivor. A mutant that is provably equivalent may be excluded with `# pragma: no mutate`, but only with an adjacent comment that explains why.

mutmut keeps results in `mutants/`. After a change that only touches tests, run `rm -rf mutants` before re-running, otherwise it can report stale survivors. The gate script always starts from a clean cache.
