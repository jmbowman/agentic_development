#!/usr/bin/env bash
set -euo pipefail
export GIT_AUTHOR_NAME=Fixture GIT_AUTHOR_EMAIL=fixture@example.invalid
export GIT_COMMITTER_NAME=Fixture GIT_COMMITTER_EMAIL=fixture@example.invalid
export GIT_AUTHOR_DATE=2026-01-15T12:00:00Z GIT_COMMITTER_DATE=2026-01-15T12:00:00Z
commit_all() { git -C "$1" add -A && git -C "$1" commit -qm "$2"; }

git init -q -b main .
cat > AGENTS.md <<'EOF'
# Service repo

Python 3.12, MIT licensed. Reference clones of third-party repos live under `refs/`.
They are read-only: read them at the commit they hold.
EOF
printf 'MIT License\n' > LICENSE
commit_all . "Initial commit"

# alphaslug: names its repository in its manifest.
r=refs/alphaslug; mkdir -p $r/src/alphaslug
git init -q -b main $r
printf '# alphaslug\n\nTurns a title into a URL slug. MIT licensed.\n' > $r/README.md
printf 'MIT License\n' > $r/LICENSE
cat > $r/pyproject.toml <<'EOF'
[project]
name = "alphaslug"
license = "MIT"

[project.urls]
Repository = "https://git.fixture.invalid/fixture-org/alphaslug"
EOF
printf 'def slug(title):\n    return title.lower().replace(" ", "-")\n' > $r/src/alphaslug/__init__.py
commit_all $r "alphaslug"

# betaslug: only its README mentions a documentation site.
r=refs/betaslug; mkdir -p $r/src/betaslug
git init -q -b main $r
cat > $r/README.md <<'EOF'
# betaslug

Turns a title into a URL slug, with transliteration. MIT licensed.

Documentation: https://betaslug.fixture.invalid/docs/
EOF
printf 'MIT License\n' > $r/LICENSE
printf '[project]\nname = "betaslug"\nlicense = "MIT"\n' > $r/pyproject.toml
printf 'def slug(title):\n    return title.lower().replace(" ", "_")\n' > $r/src/betaslug/__init__.py
commit_all $r "betaslug"

# gammaslug: no URL anywhere in the clone.
r=refs/gammaslug; mkdir -p $r/src/gammaslug
git init -q -b main $r
printf '# gammaslug\n\nTurns a title into a URL slug. MIT licensed.\n' > $r/README.md
printf 'MIT License\n' > $r/LICENSE
printf '[project]\nname = "gammaslug"\nlicense = "MIT"\n' > $r/pyproject.toml
printf 'def slug(title):\n    return title.lower().replace(" ", ".")\n' > $r/src/gammaslug/__init__.py
commit_all $r "gammaslug"
