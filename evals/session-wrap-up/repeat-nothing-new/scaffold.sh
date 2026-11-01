#!/usr/bin/env bash
set -euo pipefail
git init -q -b main .
cat > AGENTS.md <<'EOF'
# greeter

## Working rules

- Keep each module under 200 lines.
EOF
cat > greet.py <<'EOF'
def hello(name):
    return f"Hello, {name}!"
EOF
git add -A
git -c user.name=eval -c user.email=eval@example.invalid commit -qm "initial"
