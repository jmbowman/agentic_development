#!/usr/bin/env bash
set -euo pipefail
git init -q -b main .
cat > AGENTS.md <<'EOF'
# paybatch

## Working rules

- Format YAML with two spaces.
- Squash every pull request.
- Every migration has a down step.
- Batch workers log their batch ID.
EOF
mkdir -p docs src
cat > docs/ops.md <<'EOF'
# Operations

Batches run under the `paybatch` service account.
EOF
cat > src/runner.py <<'EOF'
def run(batch, timeout=60):
    return batch.process(timeout=timeout)
EOF
git add -A
git -c user.name=eval -c user.email=eval@example.invalid commit -qm "initial"
