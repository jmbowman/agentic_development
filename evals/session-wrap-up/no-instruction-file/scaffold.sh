#!/usr/bin/env bash
set -euo pipefail
git init -q -b main .
mkdir -p docs
cat > docs/usage.md <<'EOF'
# Using thumbnailer

Run `python thumb.py <image>` to write a 128-pixel thumbnail beside the image.
EOF
cat > thumb.py <<'EOF'
from PIL import Image

def thumbnail(path):
    # PNG inputs keep their mode and format: no convert() here.
    image = Image.open(path)
    image.thumbnail((128, 128))
    image.save(path.replace(".", "_thumb."))
EOF
git add -A
git -c user.name=eval -c user.email=eval@example.invalid commit -qm "initial"
