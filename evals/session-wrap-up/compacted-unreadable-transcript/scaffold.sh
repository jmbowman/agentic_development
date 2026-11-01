#!/usr/bin/env bash
set -euo pipefail
git init -q -b main .
cat > AGENTS.md <<'EOF'
# exporter

## Working rules

- Keep each module under 200 lines.
EOF
cat > export.py <<'EOF'
def export(rows, quiet=False):
    return [",".join(row) for row in rows]
EOF
git add -A
git -c user.name=eval -c user.email=eval@example.invalid commit -qm "initial"
