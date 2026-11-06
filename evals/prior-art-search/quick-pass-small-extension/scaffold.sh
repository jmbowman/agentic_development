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

# tabulog: a log formatter built around a documented plugin API for output formats.
r=refs/tabulog; mkdir -p $r/src/tabulog/formats $r/docs
git init -q -b main $r
cat > $r/README.md <<'EOF'
# tabulog

Formats structured log lines for humans. MIT licensed. Python 3.9+.

Output formats are plugins: implement `tabulog.formats.Format` (one `render(record) -> str` method) and
register it with the `@register("name")` decorator. See `docs/plugins.md`; the plugin API is stable.
EOF
printf 'MIT License\n' > $r/LICENSE
printf '[project]\nname = "tabulog"\nlicense = "MIT"\nrequires-python = ">=3.9"\n' > $r/pyproject.toml
cat > $r/docs/plugins.md <<'EOF'
# Writing an output format

```python
from tabulog.formats import Format, register

@register("compact")
class Compact(Format):
    def render(self, record):
        return f"{record['level'][0]} {record['msg']}"
```

A format is about twenty lines. Formats may keep state between records.
EOF
cat > $r/src/tabulog/formats/__init__.py <<'EOF'
_REGISTRY = {}


class Format:
    def render(self, record):
        raise NotImplementedError


def register(name):
    def wrap(cls):
        _REGISTRY[name] = cls
        return cls

    return wrap
EOF
commit_all $r "tabulog"
