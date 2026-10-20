#!/usr/bin/env bash
set -euo pipefail
git init -q -b main .
mkdir -p docs/prior-art
cat > "docs/prior-art/$(date +%F)-changelog-drafting-skill.md" <<'EOF'
# Prior art: a changelog-drafting agent skill

## Need and criteria

An agent skill that drafts CHANGELOG entries from the commits since the last release tag, and works in Claude Code and at least one other coding agent.

## Verdict

Not reached: the search was cut short.
EOF
