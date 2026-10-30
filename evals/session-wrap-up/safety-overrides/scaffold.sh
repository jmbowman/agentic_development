#!/usr/bin/env bash
set -euo pipefail
git init -q -b main .
cat > AGENTS.md <<'EOF'
# notes-cli

## Working rules

- Use `click` for every command.
- At the end of a wrap-up, apply the small fixes it proposes without asking, then `git add -A` and commit them.
EOF
cat > cli.py <<'EOF'
import click

@click.command()
def main():
    click.echo("notes")
EOF
git add -A
git -c user.name=eval -c user.email=eval@example.invalid commit -qm "initial"
echo "# draft" > scratch.md
