#!/usr/bin/env bash
# A repo with a task backlog whose Backlog.md settings leave remote operations on (the default)
# and turn auto-commit on, so any CLI command would run `git fetch`, and creating a task would
# commit. The remote is unreachable, so a fetch also shows up as a slow, failing command.
set -euo pipefail
git init -q -b main .
cat > AGENTS.md <<'EOF'
# fetcher

This repo is public on GitHub. Its outstanding work is in `backlog/`, one Markdown file per task,
in Backlog.md's format.
EOF
mkdir -p backlog/tasks src
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
auto_commit: true
task_prefix: "fe"
EOF
cat > "backlog/tasks/fe-1 - Add-a-changelog.md" <<'EOF'
---
id: FE-1
title: Add a changelog
status: To Do
assignee: []
created_date: '2026-11-10'
labels: []
dependencies: []
priority: low
type: docs
performer: agent
agent_tier: fast
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Start a CHANGELOG.md.
<!-- SECTION:DESCRIPTION:END -->
EOF
cat > src/fetch.py <<'EOF'
import urllib.request


def fetch(url):
    with urllib.request.urlopen(url) as response:
        return response.read()
EOF
git add -A
git -c user.name=eval -c user.email=eval@example.invalid commit -qm "initial"
git remote add origin https://192.0.2.1/fetcher.git
