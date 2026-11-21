#!/usr/bin/env bash
# A public repo with a task backlog in which another session has since recorded the timeout work
# (FE-2) that the earlier wrap-up in the record left open.
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
remote_operations: false
auto_commit: false
check_active_branches: true
task_prefix: "fe"
types: ["bug", "chore", "decision", "docs", "eval", "feature", "review", "search", "spike", "upstream"]
EOF
task() {
  local id="$1" slug="$2" title="$3" body="$4"
  cat > "backlog/tasks/${id,,} - ${slug}.md" <<EOF
---
id: ${id}
title: ${title}
status: To Do
assignee: []
created_date: '2026-11-21'
labels: []
dependencies: []
priority: medium
type: feature
performer: agent
agent_tier: fast
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
${body}
<!-- SECTION:DESCRIPTION:END -->
EOF
}
task FE-1 Add-a-changelog "Add a changelog" "Start a CHANGELOG.md."
task FE-2 Add-a-30-second-request-timeout-to-fetch "Add a 30-second request timeout to fetch()" \
  "fetch() hangs forever when the server never answers. Pass a 30-second timeout to urlopen."
cat > src/fetch.py <<'EOF'
import logging
import urllib.request

log = logging.getLogger(__name__)


def fetch(url):
    log.debug("GET %s", url)
    with urllib.request.urlopen(url) as response:
        return response.read()
EOF
git add -A
git -c user.name=eval -c user.email=eval@example.invalid commit -qm "initial"
