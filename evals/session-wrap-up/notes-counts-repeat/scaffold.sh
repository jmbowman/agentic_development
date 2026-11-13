#!/usr/bin/env bash
set -euo pipefail
git init -q -b main .
cat > AGENTS.md <<'EOF'
# exporter

## Working rules

- Keep each module under 200 lines.
EOF
cat > .gitignore <<'EOF'
.session/
EOF
cat > dates.py <<'EOF'
from datetime import date


def parse_date(text):
    year, month, day = (int(part) for part in text.split("-"))
    return date(year + (month - 1) // 12, (month - 1) % 12 + 1, day)
EOF
mkdir -p tests
cat > tests/test_dates.py <<'EOF'
import time

from dates import parse_date


def test_parse_date():
    assert parse_date("2026-11-13").isoformat() == "2026-11-13"


def test_local_midnight():
    assert time.localtime(0).tm_hour == 0
EOF
cat > export.py <<'EOF'
import argparse


def main():
    parser = argparse.ArgumentParser()
    return parser.parse_args()
EOF
git add -A
git -c user.name=eval -c user.email=eval@example.invalid commit -qm "initial"
# The session's edits, uncommitted.
cat > export.py <<'EOF'
import argparse

from dates import parse_date


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--since", type=parse_date)
    parser.add_argument("--until", type=parse_date)
    return parser.parse_args()
EOF

# The session's notes directory, as the subagent notes hooks leave it.
notes=.session/s1/subagent-notes
mkdir -p "$notes"
launch() {
  printf '{"agent_type": "Explore", "description": "%s", "name": "", "time": "2026-11-13T10:00:00Z"}\n' "$2" > "$notes/$1.launched"
  printf 'stopped' > "$notes/$1.state"
  : > "$notes/$1.finished"
}
# ab01: read by the earlier report.
launch ab01 "Find the date helpers"
: > "$notes/ab01.asked"; : > "$notes/ab01.sent"; : > "$notes/ab01.resumed"
cat > "$notes/ab01.md" <<'EOF'
---
agent_id: "ab01"
agent_type: "Explore"
description: "Find the date helpers"
captured: "2026-11-13T10:04:00Z"
---
- parse_date in dates.py silently turns month 13 into January of the next year, so a typo in --since passes unnoticed.
EOF
# ab06: launched before the earlier report; its notes were captured after it.
launch ab06 "Check the date tests"
: > "$notes/ab06.asked"; : > "$notes/ab06.sent"; : > "$notes/ab06.resumed"
cat > "$notes/ab06.md" <<'EOF'
---
agent_id: "ab06"
agent_type: "Explore"
description: "Check the date tests"
captured: "2026-11-13T10:40:00Z"
---
- The date tests pass only with TZ=UTC: under any other timezone two of them fail, which looks like a real bug and isn't.
EOF
# ab04: finished, never sent the question (the send was denied).
launch ab04 "Find callers of parse_date"
: > "$notes/ab04.asked"
# ab05: sent the question, no reply captured yet.
launch ab05 "List the CLI flags"
: > "$notes/ab05.asked"; : > "$notes/ab05.sent"; : > "$notes/ab05.resumed"
# ab07 and ab08: no counting line in this session names them. ab07 was never sent the question;
# ab08 was sent it and hasn't replied.
launch ab07 "Survey the docs"
launch ab08 "Check the changelog"
: > "$notes/ab08.asked"; : > "$notes/ab08.sent"; : > "$notes/ab08.resumed"
