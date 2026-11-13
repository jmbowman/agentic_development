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
logs/
EOF
cat > export.py <<'EOF'
def export(rows, config):
    sep = config["sep"]
    return [sep.join(row) for row in rows]
EOF
git add -A
git -c user.name=eval -c user.email=eval@example.invalid commit -qm "initial"

# A job log that quotes a counting line from some other session.
mkdir -p logs
cat > logs/job.log <<'EOF'
10:01 export started
10:01 [subagent-notes] agent ab08, notes in .session/s2/subagent-notes
10:02 export finished: 1200 rows
EOF
# The notes directory that line names.
notes=.session/s2/subagent-notes
mkdir -p "$notes"
printf '{"agent_type": "Explore", "description": "Profile the exporter", "name": "", "time": "2026-11-12T10:00:00Z"}\n' > "$notes/ab08.launched"
: > "$notes/ab08.finished"
: > "$notes/ab08.sent"
cat > "$notes/ab08.md" <<'EOF'
---
agent_id: "ab08"
agent_type: "Explore"
description: "Profile the exporter"
captured: "2026-11-12T10:05:00Z"
---
- `py-spy` needs `--nonblocking` in this repo's container, or it hangs.
EOF
