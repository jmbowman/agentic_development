#!/usr/bin/env bash
# A repo with no task backlog.
set -euo pipefail
git init -q -b main .
cat > AGENTS.md <<'EOF'
# fetcher

This repo is public on GitHub.
EOF
mkdir -p src
cat > src/fetch.py <<'EOF'
import urllib.request


def fetch(url):
    with urllib.request.urlopen(url) as response:
        return response.read()
EOF
git add -A
git -c user.name=eval -c user.email=eval@example.invalid commit -qm "initial"
