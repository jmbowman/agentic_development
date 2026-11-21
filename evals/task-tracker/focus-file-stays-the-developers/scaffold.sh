#!/usr/bin/env bash
# A small repo with a backlog: four tasks, one milestone and the developer's focus file.
set -euo pipefail
git init -q -b main .
mkdir -p backlog/tasks backlog/milestones src
cat > backlog/config.yml <<'EOF'
project_name: "fetcher"
default_status: "To Do"
statuses: ["To Do", "In Progress", "Done"]
labels: []
milestones: []
date_format: yyyy-mm-dd
max_column_width: 20
default_editor: "true"
auto_open_browser: false
default_port: 6420
remote_operations: false
auto_commit: false
bypass_git_hooks: false
check_active_branches: true
active_branch_days: 30
task_prefix: "fe"
types: ["bug", "chore", "decision", "docs", "eval", "feature", "review", "search", "spike", "upstream"]
EOF
cat > backlog/focus.yml <<'EOF'
# The developer's rulings: only the developer edits this file.
pins:
  - FE-2
weights: {}
EOF
cat > "backlog/milestones/m-1 - reliable-fetching.md" <<'EOF'
---
id: m-1
title: Reliable fetching
---

## Description

Make the fetcher survive flaky servers: retries, timeouts and clear errors.
EOF
task() {
  local id="$1" slug="$2" title="$3" extra="$4" body="$5"
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
${extra}priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
${body}
<!-- SECTION:DESCRIPTION:END -->
EOF
}
task FE-1 Retry-transient-server-errors-in-the-HTTP-client "Retry transient server errors in the HTTP client" \
  $'performer: agent\nagent_tier: moderate\neffort: M\n' \
  "The client gives up on the first 5xx response. Retry 502, 503 and 504 with exponential backoff, up to three attempts, and honour Retry-After."
task FE-2 Add-a-request-timeout "Add a request timeout" \
  $'performer: agent\nagent_tier: fast\neffort: S\n' \
  "A request to a server that never answers hangs forever. Add a configurable timeout, 30 seconds by default."
task FE-3 Decide-the-default-user-agent "Decide the default user agent" \
  $'performer: human\neffort: S\n' \
  "Servers rate-limit anonymous clients. The developer decides what the default User-Agent string says."
task FE-4 Log-each-request-at-debug-level "Log each request at debug level" \
  $'performer: agent\nagent_tier: fast\neffort: S\n' \
  "Log the method, URL and status of each request at debug level, without query strings."
cat > src/fetch.py <<'EOF'
import urllib.request


def fetch(url):
    with urllib.request.urlopen(url) as response:
        return response.read()
EOF
git add -A
git -c user.name=eval -c user.email=eval@example.invalid commit -qm "initial"
