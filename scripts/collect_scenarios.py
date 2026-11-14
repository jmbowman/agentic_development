"""Collect every interactive scenario with pytest, without running any.

A scenario is a paid model run, so `check` never runs one. Collecting them still imports each
scenario module and applies the repo's pytest config (`--strict-markers` among it), which
catches a broken import, fixture or marker at no model cost.

Usage: `collect_scenarios.py [ROOT]`, where ROOT is the repo root (default: the current
directory). Exits 0 when there's nothing to collect or collection succeeds, and with pytest's
status otherwise.

Design: docs/intent/interactive-evals/interactive-evals-design.md (Layout and running)
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

# pytest's status when it collected no tests, which isn't a failure here.
NO_TESTS_COLLECTED = 5


# @spec IEVAL-CHK-001
def main(argv: list[str]) -> int:
    """Collect the scenarios under ROOT's `evals/*/interactive/` directories.

    Args:
        argv: The command-line arguments after the script's name.

    Returns:
        The exit status.
    """
    root = Path(argv[0] if argv else ".").resolve()
    if not (root / "evals").is_dir():
        sys.stderr.write(f"No evals directory in {root}: is that the repo root?\n")
        return 2
    directories = sorted(
        str(path.relative_to(root))
        for path in (root / "evals").glob("*/interactive")
        if any(path.glob("test_*.py"))
    )
    if not directories:
        sys.stdout.write("No interactive scenarios to collect.\n")
        return 0
    status = subprocess.run(  # noqa: S603
        [
            sys.executable,
            "-m",
            "pytest",
            "--collect-only",
            "-q",
            "-p",
            "no:cacheprovider",
            "--rootdir",
            str(root),
            *directories,
        ],
        cwd=root,
        check=False,
    ).returncode
    return 0 if status == NO_TESTS_COLLECTED else status


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
