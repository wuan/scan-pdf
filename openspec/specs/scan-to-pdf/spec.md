# scan-to-pdf Specification

## Purpose
Defines the user-facing behaviour of the `scan-pdf` command: how it parses and validates options, drives the scanner and converter, handles paper formats, combines pages into one PDF, manages its temporary working directory, and logs progress.

## Requirements

### Requirement: CLI options parse to documented values
The `scan-pdf` command SHALL accept one positional output file name and the options `--device`, `--resolution` (integer, default 300), `--flatbed`, `-d`, `--duplex`, `--color-mode` (default `gray`), `--threshold`, `--color-depth` (default 4), `--paper-format` (default `A4`), and `--paper-left/-top/-height/-width` (default 0), each exposed under its documented option name.

#### Scenario: Defaults apply when only the output file is given
- **WHEN** `scan-pdf output.pdf` is parsed
- **THEN** device and threshold are unset, resolution is 300, flatbed, debug and duplex are off, color mode is `gray`, color depth is 4, paper format is `A4`, and all paper overrides are 0

#### Scenario: Every option is honoured
- **WHEN** every option is passed with a non-default value
- **THEN** each parsed value equals the value given on the command line

### Requirement: Enumerated options reject unknown values
`--color-mode` SHALL accept exactly `bw`, `gray`, and `color`, and `--paper-format` SHALL accept exactly the supported paper format names (`A3`–`A7`); any other value SHALL make the command exit with a usage error.

#### Scenario: Each valid value is accepted
- **WHEN** `--color-mode` is given as `bw`, `gray`, or `color`, or `--paper-format` as any of `A3`, `A4`, `A5`, `A6`, `A7`
- **THEN** parsing succeeds with that value

#### Scenario: Invalid color mode is rejected
- **WHEN** `--color-mode sepia` is passed
- **THEN** the command exits with a non-zero usage error

#### Scenario: Invalid paper format is rejected
- **WHEN** `--paper-format Letter` is passed
- **THEN** the command exits with a non-zero usage error

### Requirement: CLI help documents every option
The `--help` output SHALL show the description "Produce PDF from Scanner with document-feeder" and the documented help text for the output file argument and each option.

#### Scenario: Help texts are exact
- **WHEN** the help for the command is generated
- **THEN** the description and each argument's help text match the documented wording exactly

### Requirement: Log level follows the debug flag
The command SHALL log at DEBUG level when `-d` is given and at INFO level otherwise.

#### Scenario: Debug enabled
- **WHEN** the command runs with `-d`
- **THEN** logging is configured at DEBUG level

#### Scenario: Debug disabled
- **WHEN** the command runs without `-d`
- **THEN** logging is configured at INFO level

### Requirement: Paper area falls back to A4 and honours overrides
The scan area SHALL use the selected paper format's left, width, top, and height, falling back to A4 for an unknown format; each non-zero `--paper-left/-width/-top/-height` value SHALL override the matching dimension.

#### Scenario: Unknown paper format uses A4
- **WHEN** the scanner is invoked with a paper format that is not supported
- **THEN** the scan area is left 0, width 210, top 0, height 297

#### Scenario: Explicit overrides win
- **WHEN** paper left, width, top, and height overrides are given
- **THEN** the scan area uses the override values instead of the paper format's values

### Requirement: Conversion uses the configured color depth
Converting a scanned page SHALL use depth 1 in `bw` mode and the configured color depth in every other mode, and SHALL check that the expected target PDF exists afterwards.

#### Scenario: Gray mode uses configured depth
- **WHEN** a page is converted in `gray` or `color` mode with color depth 4
- **THEN** the conversion is run with depth 4

#### Scenario: Missing target is detected
- **WHEN** conversion of `base` finishes but `base.pdf` does not exist
- **THEN** an error naming `base.pdf` is logged

### Requirement: Temporary working directory is isolated and always cleaned up
The command SHALL work in a fresh temporary directory whose name starts with `scanpdf_`, SHALL remove it on exit without failing if it is already gone, and SHALL attempt no removal if the directory was never created.

#### Scenario: Directory name has the tool prefix
- **WHEN** the temporary directory is created
- **THEN** its base name starts with `scanpdf_`

#### Scenario: Already-removed directory does not fail cleanup
- **WHEN** the temporary directory is deleted before the working context ends
- **THEN** leaving the context raises no error

#### Scenario: Never-created directory is not removed
- **WHEN** the working context is exited without having been entered
- **THEN** no directory removal is attempted

### Requirement: Progress is logged with stable messages
Each module SHALL log under its own logger name with these messages: `convert <basename>` (INFO), `call: <command>` (DEBUG, converter), `convert failed: <command>` (ERROR), `target file '<file>' does not exist` (ERROR), `combine <n> pages into <file>` (INFO), `call <command>` and `call returned <code>` (DEBUG, scanner), and `no pages found` (WARNING, CLI).

#### Scenario: Conversion messages
- **WHEN** a page `base` is converted and the command fails
- **THEN** the `scan_pdf.convert` logger emits `convert base` at INFO, `call: <full command>` at DEBUG, and `convert failed: <full command>` at ERROR

#### Scenario: Combination message
- **WHEN** two pages are combined into `output.pdf`
- **THEN** the `scan_pdf.combine` logger emits `combine 2 pages into output.pdf` at INFO

#### Scenario: Scanner messages
- **WHEN** the scanner command runs and returns 0
- **THEN** the `scan_pdf.scan` logger emits `call <full command>` and `call returned 0` at DEBUG

#### Scenario: No pages found
- **WHEN** a scan produces no pages
- **THEN** the `scan_pdf.cli` logger emits exactly `no pages found` at WARNING
