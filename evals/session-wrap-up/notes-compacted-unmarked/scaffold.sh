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
cat > export.py <<'EOF'
def export(rows):
    return [",".join(row) for row in rows]
EOF
git add -A
git -c user.name=eval -c user.email=eval@example.invalid commit -qm "initial"
# The session's edit, uncommitted.
cat > export.py <<'EOF'
def export(rows, quiet=False):
    return [",".join(row) for row in rows]
EOF

# A transcript that marks the developer's turns but not hook-added context: the counting line
# sits in an entry with no origin, like a tool result.
mkdir -p .session/s6/subagent-notes
cat > .session/s6.jsonl <<'EOF'
{"type":"user","origin":{"kind":"human"},"promptSource":"typed","message":{"role":"user","content":"Add CSV export."}}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"tool_use","id":"t1","name":"Agent","input":{"subagent_type":"Explore","description":"Find the CSV writer","prompt":"Find where CSV is written."}}]}}
{"type":"user","message":{"role":"user","content":[{"type":"tool_result","tool_use_id":"t1","content":"Agent ab31 completed. Report: export.py joins with commas by hand."}]},"toolUseResult":{"status":"completed","agentId":"ab31","agentType":"Explore"}}
{"type":"user","message":{"role":"user","content":"[subagent-notes] agent ab31, notes in .session/s6/subagent-notes"}}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"Added CSV export."}]}}
{"type":"user","isCompactSummary":true,"message":{"role":"user","content":"This session is being continued from a previous conversation. Earlier in the session the agent added CSV export with the help of an Explore subagent."}}
{"type":"user","origin":{"kind":"human"},"promptSource":"typed","message":{"role":"user","content":"Add a --quiet flag to export.py."}}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"Done."}]}}
EOF
notes=.session/s6/subagent-notes
printf '{"agent_type": "Explore", "description": "Find the CSV writer", "name": "", "time": "2026-11-13T09:00:00Z"}\n' > "$notes/ab31.launched"
: > "$notes/ab31.finished"
: > "$notes/ab31.sent"
cat > "$notes/ab31.md" <<'EOF'
---
agent_id: "ab31"
agent_type: "Explore"
description: "Find the CSV writer"
captured: "2026-11-13T09:05:00Z"
---
- The csv module's `lineterminator` defaults to CRLF; the export tests compare against LF files.
EOF
