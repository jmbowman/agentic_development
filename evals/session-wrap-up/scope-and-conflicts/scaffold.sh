#!/usr/bin/env bash
set -euo pipefail
git init -q -b main .
mkdir -p docs/decisions
cat > AGENTS.md <<'EOF'
# invoice-api

## Where knowledge goes

- Record each decision in `DECISIONS.md` at the repo root.

## Working rules

- Return errors as JSON with `code` and `message` fields.
EOF
cat > DECISIONS.md <<'EOF'
# Decisions
EOF
cat > app.py <<'EOF'
def handler(event):
    return {"code": 200, "message": "ok"}
EOF
git add -A
git -c user.name=eval -c user.email=eval@example.invalid commit -qm "initial"
