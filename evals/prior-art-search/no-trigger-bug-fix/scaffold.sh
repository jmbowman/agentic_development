#!/usr/bin/env bash
set -euo pipefail
cat > pager.py <<'EOF'
def paginate(items, size):
    """Split items into pages of at most size items."""
    pages = len(items) // size
    return [items[i * size : (i + 1) * size] for i in range(pages)]
EOF
