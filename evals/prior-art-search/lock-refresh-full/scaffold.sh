#!/usr/bin/env bash
set -euo pipefail
export GIT_AUTHOR_NAME=Fixture GIT_AUTHOR_EMAIL=fixture@example.invalid
export GIT_COMMITTER_NAME=Fixture GIT_COMMITTER_EMAIL=fixture@example.invalid
export GIT_AUTHOR_DATE=2026-01-15T12:00:00Z GIT_COMMITTER_DATE=2026-01-15T12:00:00Z
commit_all() { git -C "$1" add -A && git -C "$1" commit -qm "$2"; }

git init -q -b main .
cat > AGENTS.md <<'EOF'
# Example service

Rendered from a copier template and kept current by the hosted Renovate app.
EOF
cat > LICENSE <<'EOF'
MIT License

Copyright (c) 2026 Example
EOF
cat > mise.toml <<'EOF'
[tools]
python = "3.13.1"
uv = "0.9.0"
EOF
printf '[[tools]]\nversion = "3.13.1"\nbackend = "core:python"\n' > mise.lock
cat > .copier-answers.yml <<'EOF'
_commit: v1.4.0
_src_path: gh:example/copier-python
EOF
mkdir -p .github
echo '{"extends": ["github>example/renovate-config#v1.0.0"]}' > .github/renovate.json
commit_all . "Initial render"
