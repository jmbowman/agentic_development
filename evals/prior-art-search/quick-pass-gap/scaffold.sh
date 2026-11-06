#!/usr/bin/env bash
set -euo pipefail
export GIT_AUTHOR_NAME=Fixture GIT_AUTHOR_EMAIL=fixture@example.invalid
export GIT_COMMITTER_NAME=Fixture GIT_COMMITTER_EMAIL=fixture@example.invalid
export GIT_AUTHOR_DATE=2026-01-15T12:00:00Z GIT_COMMITTER_DATE=2026-01-15T12:00:00Z
commit_all() { git -C "$1" add -A && git -C "$1" commit -qm "$2"; }

git init -q -b main .
cat > AGENTS.md <<'EOF'
# Docs site

Our CI runs on Linux, macOS and Windows runners. Reference clones of third-party repos live under `refs/`.
They are read-only: read them at the commit they hold.
EOF
printf 'Apache License\nVersion 2.0, January 2004\n' > LICENSE
commit_all . "Initial commit"

# mdlinks: checks Markdown links well, but is built on POSIX file locking and does not run on Windows.
r=refs/mdlinks; mkdir -p $r/src/mdlinks
git init -q -b main $r
cat > $r/README.md <<'EOF'
# mdlinks

Checks every link in a tree of Markdown files, including anchors. MIT licensed.

Platforms: Linux and macOS. Windows is not supported: the link cache is guarded with `fcntl` file locks,
which Windows lacks, and the cache is not optional.
EOF
printf 'MIT License\n' > $r/LICENSE
printf '[project]\nname = "mdlinks"\nlicense = "MIT"\n' > $r/pyproject.toml
cat > $r/src/mdlinks/cache.py <<'EOF'
import fcntl


def locked_cache(path):
    handle = open(path, "a+")
    fcntl.flock(handle, fcntl.LOCK_EX)
    return handle
EOF
commit_all $r "mdlinks"

# anchorcheck: only checks in-page anchors, not links; it does run everywhere.
r=refs/anchorcheck; mkdir -p $r/src/anchorcheck
git init -q -b main $r
printf '# anchorcheck\n\nChecks `#anchor` fragments within one Markdown file only. Pure Python, runs on any platform. MIT licensed.\n' > $r/README.md
printf 'MIT License\n' > $r/LICENSE
printf '[project]\nname = "anchorcheck"\nlicense = "MIT"\n' > $r/pyproject.toml
printf 'def check(text):\n    return []\n' > $r/src/anchorcheck/__init__.py
commit_all $r "anchorcheck"
