#!/usr/bin/env bash
set -euo pipefail
export GIT_AUTHOR_NAME=Fixture GIT_AUTHOR_EMAIL=fixture@example.invalid
export GIT_COMMITTER_NAME=Fixture GIT_COMMITTER_EMAIL=fixture@example.invalid
export GIT_AUTHOR_DATE=2026-01-15T12:00:00Z GIT_COMMITTER_DATE=2026-01-15T12:00:00Z
commit_all() { git -C "$1" add -A && git -C "$1" commit -qm "$2"; }

git init -q -b main .
cat > AGENTS.md <<'EOF'
# Platform config

Record decisions in docs/decisions/ as numbered ADRs.
EOF
mkdir -p docs/decisions research
echo "# Decisions" > docs/decisions/README.md
cat > research/2025-03-02-shared-config-overrides.md <<'EOF'
# Prior art: shared config with per-repo overrides (2025-03-02)

## Need and criteria

Share config files across repos, with per-repo overrides.

## Verdict

**Build:** a small fetch script that copies the shared files into each repo.
EOF
commit_all . "Initial commit"
