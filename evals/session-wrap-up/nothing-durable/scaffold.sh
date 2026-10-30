#!/usr/bin/env bash
set -euo pipefail
git init -q -b main .
cat > AGENTS.md <<'EOF'
# greeter

## Working rules

- Run tests with `pytest -q`.
EOF
cat > greet.py <<'EOF'
def greet(name):
    return f"Hello, {name}!"
EOF
git add -A
git -c user.name=eval -c user.email=eval@example.invalid commit -qm "initial"
