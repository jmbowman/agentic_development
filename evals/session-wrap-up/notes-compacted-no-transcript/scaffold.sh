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

# A transcript-shaped file beside the notes directory, at a location nobody stated.
mkdir -p .session/s4/subagent-notes
cat > .session/s4.jsonl <<'EOF'
{"type":"user","origin":{"kind":"human"},"promptSource":"typed","message":{"role":"user","content":"Add CSV export. From now on, name branches feat/<topic>."}}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"tool_use","id":"t1","name":"Agent","input":{"subagent_type":"Explore","description":"Find the CSV writer","prompt":"Find where CSV is written."}}]}}
{"type":"user","message":{"role":"user","content":[{"type":"tool_result","tool_use_id":"t1","content":"Agent ab21 completed. Report: export.py joins with commas by hand."}]},"toolUseResult":{"status":"completed","agentId":"ab21","agentType":"Explore"}}
{"type":"attachment","attachment":{"type":"hook_additional_context","content":["[subagent-notes] agent ab21, notes in .session/s4/subagent-notes"],"hookName":"PostToolUse:Agent","toolUseID":"t1","hookEvent":"PostToolUse"}}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"tool_use","id":"t2","name":"Agent","input":{"subagent_type":"Explore","description":"List the export tests","prompt":"List the export tests."}}]}}
{"type":"user","message":{"role":"user","content":[{"type":"tool_result","tool_use_id":"t2","content":"Agent ab22 completed. Report: there are none."}]},"toolUseResult":{"status":"completed","agentId":"ab22","agentType":"Explore"}}
{"type":"attachment","attachment":{"type":"hook_additional_context","content":["[subagent-notes] agent ab22, notes in .session/s4/subagent-notes"],"hookName":"PostToolUse:Agent","toolUseID":"t2","hookEvent":"PostToolUse"}}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"Done."}]}}
EOF
notes=.session/s4/subagent-notes
for id in ab21 ab22; do
  printf '{"agent_type": "Explore", "description": "", "name": "", "time": "2026-11-13T09:00:00Z"}\n' > "$notes/$id.launched"
  : > "$notes/$id.finished"
  : > "$notes/$id.sent"
done
sed -i 's/"description": ""/"description": "Find the CSV writer"/' "$notes/ab21.launched"
sed -i 's/"description": ""/"description": "List the export tests"/' "$notes/ab22.launched"
cat > "$notes/ab21.md" <<'EOF'
---
agent_id: "ab21"
agent_type: "Explore"
description: "Find the CSV writer"
captured: "2026-11-13T09:05:00Z"
---
- The csv module's `lineterminator` defaults to CRLF; the export tests compare against LF files.
EOF
