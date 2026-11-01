#!/usr/bin/env bash
set -euo pipefail
git init -q -b main .
cat > AGENTS.md <<'EOF'
# exporter

## Working rules

- `docs/STATUS.md` is the record of current state.
EOF
mkdir -p docs src
cat > docs/STATUS.md <<'EOF'
# Status

- CSV export: in progress.
- Search: deferred until the index is rebuilt.
EOF
cat > README.md <<'EOF'
# exporter

## Status

Beta.
EOF
cat > src/export.py <<'EOF'
import csv


def export(rows, stream):
    csv.writer(stream).writerows(rows)
EOF
git add -A
git -c user.name=eval -c user.email=eval@example.invalid commit -qm "initial"
