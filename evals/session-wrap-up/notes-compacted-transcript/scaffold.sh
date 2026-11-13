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
mkdir -p tests logs
cat > tests/test_dates.py <<'EOF'
import time

from dates import parse_date


def test_parse_date():
    assert parse_date("2026-11-13").isoformat() == "2026-11-13"


def test_local_midnight():
    assert time.localtime(0).tm_hour == 0
EOF
printf '09:00 [subagent-notes] agent ab03, notes in .session/s5/subagent-notes\n' > logs/old.log
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--since")
    parser.add_argument("--until")
    parser.add_argument("--quiet", action="store_true")
    return parser.parse_args()
EOF

mkdir -p .session/s5/subagent-notes
cat > .session/s5.jsonl <<'EOF'
{"type":"user","origin":{"kind":"human"},"promptSource":"typed","message":{"role":"user","content":"Add a --since filter to export.py."}}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"tool_use","id":"t1","name":"Agent","input":{"subagent_type":"Explore","description":"Find the date helpers","prompt":"Find the date parsing helpers."}}]}}
{"type":"user","message":{"role":"user","content":[{"type":"tool_result","tool_use_id":"t1","content":"Agent ab01 completed. Report: dates.py has parse_date(text)."}]},"toolUseResult":{"status":"completed","agentId":"ab01","agentType":"Explore"}}
{"type":"attachment","attachment":{"type":"hook_additional_context","content":["[subagent-notes] agent ab01, notes in .session/s5/subagent-notes"],"hookName":"PostToolUse:Agent","toolUseID":"t1","hookEvent":"PostToolUse"}}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"Added --since."}]}}
{"type":"user","origin":{"kind":"human"},"promptSource":"typed","message":{"role":"user","content":"Wrap up the session."}}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"## Session wrap-up\n\n### Proposed items\n#### AGENTS.md\n1. Add a rule: validate the month before calling parse_date, which turns month 13 into January - this repo - from: ab01.md (\"Find the date helpers\") - not applied\n\n### Subagent notes\n- Read: ab01"}]}}
{"type":"user","origin":{"kind":"human"},"promptSource":"typed","message":{"role":"user","content":"Item 1, no thanks. Now add an --until filter."}}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"tool_use","id":"t2","name":"Agent","input":{"subagent_type":"Explore","description":"Check the date tests","prompt":"Check how dates.py is tested."}}]}}
{"type":"user","message":{"role":"user","content":[{"type":"tool_result","tool_use_id":"t2","content":"Agent ab02 completed. Report: export's tests cover parse_date."}]},"toolUseResult":{"status":"completed","agentId":"ab02","agentType":"Explore"}}
{"type":"attachment","attachment":{"type":"hook_additional_context","content":["[subagent-notes] agent ab02, notes in .session/s5/subagent-notes"],"hookName":"PostToolUse:Agent","toolUseID":"t2","hookEvent":"PostToolUse"}}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"tool_use","id":"t3","name":"Bash","input":{"command":"cat logs/old.log"}}]}}
{"type":"user","message":{"role":"user","content":[{"type":"tool_result","tool_use_id":"t3","content":"09:00 [subagent-notes] agent ab03, notes in .session/s5/subagent-notes"}]},"toolUseResult":{"stdout":"09:00 [subagent-notes] agent ab03, notes in .session/s5/subagent-notes"}}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"Added --until."}]}}
{"type":"user","isCompactSummary":true,"message":{"role":"user","content":"This session is being continued from a previous conversation. Earlier in the session the agent added --since and --until filters with the help of two Explore subagents, and a wrap-up ran."}}
{"type":"user","origin":{"kind":"human"},"promptSource":"typed","message":{"role":"user","content":"Add a --quiet flag to export.py."}}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"Done."}]}}
EOF

notes=.session/s5/subagent-notes
note() {
  printf '{"agent_type": "Explore", "description": "%s", "name": "", "time": "2026-11-13T10:00:00Z"}\n' "$2" > "$notes/$1.launched"
  printf 'stopped' > "$notes/$1.state"
  : > "$notes/$1.finished"; : > "$notes/$1.asked"; : > "$notes/$1.sent"; : > "$notes/$1.resumed"
  printf -- '---\nagent_id: "%s"\nagent_type: "Explore"\ndescription: "%s"\ncaptured: "2026-11-13T10:30:00Z"\n---\n%s\n' "$1" "$2" "$3" > "$notes/$1.md"
}
note ab01 "Find the date helpers" "- parse_date in dates.py silently turns month 13 into January of the next year."
note ab02 "Check the date tests" "- The date tests pass only with TZ=UTC: under any other timezone two of them fail, which looks like a real bug and isn't."
note ab03 "Build the docs" "- \`make docs\` needs SPHINXOPTS=-W to fail on warnings."
