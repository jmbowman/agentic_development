#!/usr/bin/env bash
set -euo pipefail
git init -q -b main .
cat > AGENTS.md <<'EOF'
# greeter

## Working rules

- Keep each module under 200 lines.
EOF
cat > greet.py <<'EOF'
def greet(name):
    return f"Helo, {name}!"
EOF
git add -A
git -c user.name=eval -c user.email=eval@example.invalid commit -qm "initial"
cat > greet.py <<'EOF'
def greet(name):
    return f"Hello, {name}!"
EOF
echo 'unrelated notes' > notes.txt
