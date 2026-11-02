#!/usr/bin/env bash
set -euo pipefail
git init -q -b main .
cat > AGENTS.md <<'EOF'
# fetcher

## Working rules

- Keep each module under 200 lines.
EOF
mkdir -p src
echo 'def fetch(url): return url' > src/fetch.py
echo 'def store(row): return row' > src/store.py
echo 'def clean(row): return row' > src/clean.py
git add -A
git -c user.name=eval -c user.email=eval@example.invalid commit -qm "initial"
echo 'def fetch(url, retries=3): return url' > src/fetch.py
echo 'def store(row, timeout=10): return row' > src/store.py
echo 'def clean(row): return row.strip()' > src/clean.py
