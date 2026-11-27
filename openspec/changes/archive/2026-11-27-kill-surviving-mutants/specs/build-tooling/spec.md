# Spec Delta

## ADDED Requirements

### Requirement: Mutation suite keeps a zero-survivor baseline
A full `uv run mutmut run` on the main branch SHALL report zero surviving mutants. A mutant that is provably equivalent (no observable behaviour change) SHALL be excluded with `# pragma: no mutate` together with a comment stating why, rather than left surviving. CI SHALL stay report-only.

#### Scenario: Clean mutation run
- **WHEN** `uv run mutmut run` completes on main
- **THEN** the summary shows 0 survived and `uv run mutmut results` lists no surviving mutants

#### Scenario: Equivalent mutant is documented
- **WHEN** a source line carries `# pragma: no mutate`
- **THEN** an adjacent comment explains why mutating that line cannot change observable behaviour

#### Scenario: New survivor does not fail CI
- **WHEN** a later change introduces a surviving mutant
- **THEN** the CI mutation job still exits zero and lists the survivor in its log and report
