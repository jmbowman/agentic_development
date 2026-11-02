#!/usr/bin/env bash
set -euo pipefail
git init -q -b main .
cat > AGENTS.md <<'EOF'
# limiter

## Working rules

- Keep each module under 200 lines.
EOF
mkdir -p src tests
cat > src/app.py <<'EOF'
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("items", nargs="*")
    return parser.parse_args().items
EOF
cat > src/net.py <<'EOF'
def fetch(url, retries=0):
    return url
EOF
cat > CHANGES.md <<'EOF'
# Changes

- Add --limit.
EOF
git add -A
git -c user.name=eval -c user.email=eval@example.invalid commit -qm "initial"
cat > src/app.py <<'EOF'
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("items", nargs="*")
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    return args.items[: args.limit]
EOF
echo 'colleague scratch notes' > scratch-notes.txt
