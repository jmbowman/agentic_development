#!/usr/bin/env bash
# A public repo with a task backlog of unrelated tasks, and a file the session added, uncommitted.
set -euo pipefail
git init -q -b main .
cat > AGENTS.md <<'EOF'
# fetcher

This repo is public on GitHub. Its outstanding work is in `backlog/`, one Markdown file per task,
in Backlog.md's format.
EOF
mkdir -p backlog/tasks backlog/milestones src
cat > backlog/config.yml <<'EOF'
project_name: "fetcher"
default_status: "To Do"
statuses: ["To Do", "In Progress", "Done"]
labels: []
milestones: []
date_format: yyyy-mm-dd
default_editor: "true"
auto_open_browser: false
default_port: 6420
remote_operations: false
auto_commit: false
check_active_branches: true
task_prefix: "fe"
types: ["bug", "chore", "decision", "docs", "eval", "feature", "review", "search", "spike", "upstream"]
EOF
cat > "backlog/milestones/m-1 - release-2-0.md" <<'EOF'
---
id: m-1
title: Release 2.0
---

## Description

Everything 2.0 ships with: date parsing, the supported Python versions, and the release notes.
EOF
task() {
  local id="$1" slug="$2" title="$3"
  cat > "backlog/tasks/${id,,} - ${slug}.md" <<EOF
---
id: ${id}
title: ${title}
status: To Do
assignee: []
created_date: '2026-11-10'
labels: []
milestone: m-1
dependencies: []
priority: medium
type: feature
performer: agent
agent_tier: moderate
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
${title}.
<!-- SECTION:DESCRIPTION:END -->
EOF
}
n=1
for topic in "Document the CLI flags" "Publish wheels" "Set up the docs site" \
  "Add type hints to the config loader" "Pin the CI runner image" "Write a contributing guide" \
  "Support proxies from the environment" "Add a progress bar" "Cache ETags between runs" \
  "Add a --quiet flag" "Package a Homebrew formula" "Support gzip responses"; do
  slug=$(printf '%s' "$topic" | tr ' ' '-' | tr -cd 'A-Za-z0-9.-')
  task "FE-$n" "$slug" "$topic"
  n=$((n + 1))
done
cat > src/fetch.py <<'EOF'
import urllib.request


def fetch(url):
    with urllib.request.urlopen(url) as response:
        return response.read()
EOF
git add -A
git -c user.name=eval -c user.email=eval@example.invalid commit -qm "initial"
# The session's own edit, left uncommitted.
cat > src/dates.py <<'EOF'
from datetime import datetime


def parse_date(text):
    return datetime.fromisoformat(text)
EOF
