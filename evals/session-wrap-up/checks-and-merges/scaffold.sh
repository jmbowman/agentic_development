#!/usr/bin/env bash
set -euo pipefail
git init -q -b main .
cat > AGENTS.md <<'EOF'
# reporter

## Code

- Keep functions short.

## Docs

- Link every new page from the docs index.

## Checks

- `ruff check .` runs in CI, with the rules selected in `pyproject.toml`.
EOF
cat > pyproject.toml <<'EOF'
[project]
name = "reporter"
version = "0.1.0"

[tool.ruff.lint]
select = ["E", "F"]
EOF
mkdir -p src
cat > src/report.py <<'EOF'
def report(rows):
    return f"{len(rows)} rows"
EOF
cat > CHANGELOG.md <<'EOF'
# Changelog

- Added the rows count.
- Added a summary line.
EOF
git add -A
git -c user.name=eval -c user.email=eval@example.invalid commit -qm "initial"
