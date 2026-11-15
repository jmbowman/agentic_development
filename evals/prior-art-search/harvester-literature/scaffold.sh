#!/usr/bin/env bash
set -euo pipefail
export GIT_AUTHOR_NAME=Fixture GIT_AUTHOR_EMAIL=fixture@example.invalid
export GIT_COMMITTER_NAME=Fixture GIT_COMMITTER_EMAIL=fixture@example.invalid
export GIT_AUTHOR_DATE=2026-01-15T12:00:00Z GIT_COMMITTER_DATE=2026-01-15T12:00:00Z

git init -q -b main .
cat > AGENTS.md <<'EOF'
# Review assistant

A small tool that helps a human review changes that an AI coding agent made. Research and prior-art notes
go in `docs/prior-art/`.
EOF
printf 'Apache License\nVersion 2.0, January 2004\n' > LICENSE
mkdir -p docs/prior-art
printf '# Prior-art notes\n' > docs/prior-art/README.md
printf 'tmp/\n' > .gitignore
git add -A && git commit -qm "Initial commit"

# The eval's sandboxed shell can write only inside this workspace, so it has an ignored tmp/, and
# uv's cache is warmed there now, while this script runs outside the sandbox with network access.
# The agent still has to point UV_CACHE_DIR at it, as the skill's references/harvester.md says.
plugin="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
UV_CACHE_DIR="$PWD/tmp/prior-art-search/uv-cache" \
  uv sync --quiet --script "$plugin/skills/prior-art-search/scripts/harvest.py"
