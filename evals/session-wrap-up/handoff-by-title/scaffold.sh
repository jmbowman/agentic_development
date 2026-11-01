#!/usr/bin/env bash
set -euo pipefail
git init -q -b main .
cat > AGENTS.md <<'EOF'
# importer

## Working rules

- `docs/STATUS.md` is the record of current state.
EOF
mkdir -p docs src
cat > docs/where-we-are.md <<'EOF'
# Current state

- Importer: in progress.
EOF
cat > src/importer.py <<'EOF'
def load(rows):
    return [row for row in rows if row]
EOF
git add -A
git -c user.name=eval -c user.email=eval@example.invalid commit -qm "initial"
