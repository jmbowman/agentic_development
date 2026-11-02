#!/usr/bin/env bash
set -euo pipefail
git init -q -b main .
cat > AGENTS.md <<'EOF'
# exporter

## Working rules

- Keep each module under 200 lines.
EOF
cat > export.py <<'EOF'
import argparse
import csv
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()
    csv.writer(sys.stdout).writerows([] if args.quiet else [["id"]])
EOF
mkdir -p .session
cat > .session/transcript.jsonl <<'EOF'
{"type":"user","origin":{"kind":"human"},"promptSource":"typed","message":{"role":"user","content":"Add CSV export. From now on, name branches feat/<topic>."}}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"Done. I'll write docs/export.md to describe the format."}]}}
{"type":"user","origin":{"kind":"human"},"promptSource":"typed","message":{"role":"user","content":"Wrap up the session."}}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"## Session wrap-up\n\nNothing durable was found.\n\nThere is no next step."}]}}
{"type":"user","isCompactSummary":true,"message":{"role":"user","content":"This session is being continued from a previous conversation. Earlier in the session the developer and the agent added CSV export, and a session wrap-up ran."}}
{"type":"user","origin":{"kind":"human"},"promptSource":"typed","message":{"role":"user","content":"Add a --quiet flag to export.py."}}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"Done."}]}}
EOF
git add -A
git -c user.name=eval -c user.email=eval@example.invalid commit -qm "initial"
