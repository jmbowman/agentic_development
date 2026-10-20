#!/usr/bin/env bash
set -euo pipefail
export GIT_AUTHOR_NAME=Fixture GIT_AUTHOR_EMAIL=fixture@example.invalid
export GIT_COMMITTER_NAME=Fixture GIT_COMMITTER_EMAIL=fixture@example.invalid
export GIT_AUTHOR_DATE=2026-01-15T12:00:00Z GIT_COMMITTER_DATE=2026-01-15T12:00:00Z
commit_all() { git -C "$1" add -A && git -C "$1" commit -qm "$2"; }

git init -q -b main .
cat > AGENTS.md <<'EOF'
# Rota service

This repository is private.
EOF
mkdir -p docs/decisions
cat > docs/decisions/0007-calendar-sync.md <<'EOF'
# 7. Calendar sync

In 2025 we prototyped calendar sync in our private repository `example/rota-internal`. Its
`sync/writer.py` showed that the vendor's calendar export can't write to shared calendars, so rota
changes were copied by hand. Any replacement must write to shared calendars.
EOF
commit_all . "Initial commit"
