#!/usr/bin/env bash
set -euo pipefail
git init -q -b main .
cat > AGENTS.md <<'EOF'
# tiler

## Working rules

- Format with `ruff format` before handing back a change.
- Run the full test suite before every commit.
- Write new modules with type hints.
EOF
mkdir -p src
cat > src/tiles.py <<'EOF'
def tile(width, height, size, margin=0):
    step = size + margin
    return [(x, y) for x in range(0, width, step) for y in range(0, height, step)]
EOF
mkdir -p docs
echo '# Tiler' > docs/index.md
cat > mise.toml <<'EOF'
[tasks.docs-check]
run = "mdformat --check docs"
EOF
mkdir -p tests
cat > tests/test_tiles.py <<'EOF'
from src.tiles import tile


def test_margin():
    assert tile(4, 4, 2, margin=1)


class EdgeCases:
    def test_zero_margin(self):
        assert tile(4, 4, 2, margin=0)
EOF
git add -A
git -c user.name=eval -c user.email=eval@example.invalid commit -qm "initial"
