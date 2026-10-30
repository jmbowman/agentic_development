#!/usr/bin/env bash
set -euo pipefail
git init -q -b main .
cat > TODO.md <<'EOF'
# Tasks

- [ ] Rename `fetch_all` to `fetch_pages` in client.py
EOF
cat > client.py <<'EOF'
def fetch_all(session, url):
    return session.get(url).json()
EOF
