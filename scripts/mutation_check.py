"""Run mutmut from a clean cache and fail if any mutant was not killed.

Used by the pre-commit hook and the CI mutation job.
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

MUTANTS_DIR = Path("mutants")
STATS_FILE = MUTANTS_DIR / "mutmut-cicd-stats.json"
# Timeouts count as killed. Everything else listed here means the tests missed it.
FAILING_STATUSES = ("survived", "no_tests", "suspicious", "segfault")


def main() -> int:
    # mutmut reuses cached results for unchanged source, which goes stale
    # after test-only changes. A clean run takes only a few seconds.
    shutil.rmtree(MUTANTS_DIR, ignore_errors=True)
    _ = subprocess.run(["mutmut", "run"], check=True, stdout=subprocess.DEVNULL)
    _ = subprocess.run(["mutmut", "export-cicd-stats"], check=True)

    stats: dict[str, int] = json.loads(STATS_FILE.read_text())
    failures = {status: stats[status] for status in FAILING_STATUSES if stats[status]}
    print(f"mutmut: {stats['killed']}/{stats['total']} killed", flush=True)
    if failures:
        print(f"mutmut: not killed: {failures}", file=sys.stderr, flush=True)
        _ = subprocess.run(["mutmut", "results"], check=False)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
