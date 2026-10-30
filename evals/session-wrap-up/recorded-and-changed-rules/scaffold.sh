#!/usr/bin/env bash
set -euo pipefail
git init -q -b main .
cat > AGENTS.md <<'EOF'
# tiler

## Working rules

- Format with `ruff format` before handing back a change.
- Run the full test suite before every commit.
- Write new modules with type hints.
EOF
mkdir -p src
cat > src/tiles.py <<'EOF'
def tile(width, height, size):
    return [(x, y) for x in range(0, width, size) for y in range(0, height, size)]
EOF
git add -A
git -c user.name=eval -c user.email=eval@example.invalid commit -qm "initial"
