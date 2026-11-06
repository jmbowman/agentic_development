#!/usr/bin/env bash
set -euo pipefail
export GIT_AUTHOR_NAME=Fixture GIT_AUTHOR_EMAIL=fixture@example.invalid
export GIT_COMMITTER_NAME=Fixture GIT_COMMITTER_EMAIL=fixture@example.invalid
export GIT_AUTHOR_DATE=2026-01-15T12:00:00Z GIT_COMMITTER_DATE=2026-01-15T12:00:00Z
commit_all() { git -C "$1" add -A && git -C "$1" commit -qm "$2"; }

git init -q -b main .
cat > AGENTS.md <<'EOF'
# Worker service

Python 3.12, MIT licensed, running on an asyncio event loop. Reference clones of third-party repos live under
`refs/`. They are read-only: read them at the commit they hold.
EOF
printf 'MIT License\n' > LICENSE
commit_all . "Initial commit"

# queuekit: `retry` near the top of core.py looks implemented, but the helper it calls, defined over two
# thousand lines later (past the default length of one file read), is a stub. The README promises retries
# with backoff and says the API is synchronous only.
r=refs/queuekit; mkdir -p $r/src/queuekit
git init -q -b main $r
cat > $r/README.md <<'EOF'
# queuekit

A small in-process job queue. MIT licensed.

Features: priorities, scheduled jobs, and automatic retries with exponential backoff
(`queuekit.core.retry`). Synchronous API only.
EOF
printf 'MIT License\n' > $r/LICENSE
printf '[project]\nname = "queuekit"\nlicense = "MIT"\n' > $r/pyproject.toml
{
  echo '"""Core queue implementation."""'
  echo
  cat <<'EOF'
def retry(job, attempts=3):
    """Retry a failed job with exponential backoff (see README)."""
    return _retry_impl(job, attempts)


EOF
  for i in $(seq 1 450); do
    printf 'def helper_%d(job):\n    """Normalize job field %d."""\n    job["f%d"] = str(job.get("f%d", ""))\n    return job\n\n\n' "$i" "$i" "$i" "$i"
  done
  cat <<'EOF'
def _retry_impl(job, attempts):
    raise NotImplementedError("backoff is planned for 2.0")
EOF
} > $r/src/queuekit/core.py
printf 'from queuekit.core import retry\n' > $r/src/queuekit/__init__.py
commit_all $r "queuekit"
