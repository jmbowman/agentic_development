#!/usr/bin/env bash
set -euo pipefail
git init -q -b main .
mkdir -p docs/design src
cat > AGENTS.md <<'EOF'
# ledger-sync

Agent instructions for this repo.

## Where knowledge goes

- How agents should work here: this file, under "Working rules".
- What the system should do, and why: `docs/design/`, one file per component. Never in agent memory.
- Agent memory holds only facts about the developer and how they like to work.

## Working rules

- Keep functions under 30 lines.
EOF
cat > docs/design/importer.md <<'EOF'
# Importer

Reads bank CSV exports and writes ledger entries.
EOF
cat > src/importer.py <<'EOF'
def parse_amount(text):
    return float(text.replace(",", ""))
EOF
git add -A
git -c user.name=eval -c user.email=eval@example.invalid commit -qm "initial"
