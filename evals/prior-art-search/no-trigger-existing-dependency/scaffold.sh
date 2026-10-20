#!/usr/bin/env bash
set -euo pipefail
printf '[project]\nname = "client"\ndependencies = ["requests>=2.32"]\n' > pyproject.toml
cat > client.py <<'EOF'
import requests


def fetch(url):
    return requests.get(url).json()
EOF
