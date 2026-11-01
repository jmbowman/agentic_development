#!/usr/bin/env bash
set -euo pipefail
git init -q -b main .
cat > AGENTS.md <<'EOF'
# exporter

## Working rules

- Keep each module under 200 lines.
EOF
mkdir -p docs
cat > docs/cli.md <<'EOF'
# CLI

- `--quiet`: print nothing.
EOF
cat > docs/dev-notes.md <<'EOF'
# Developer notes

Session transcripts are kept at `.session/transcript.jsonl`.
EOF
mkdir -p .session
cat > .session/transcript.jsonl <<'EOF'
{"type":"user","origin":{"kind":"human"},"promptSource":"typed","message":{"role":"user","content":"Add CSV export. In this repo, name exports after their date."}}
EOF
cat > export.py <<'EOF'
def export(rows, quiet=False):
    return [",".join(row) for row in rows]
EOF
git add -A
git -c user.name=eval -c user.email=eval@example.invalid commit -qm "initial"
