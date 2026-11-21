#!/usr/bin/env bash
# A public repo with a task backlog: one open task the session adds to, one it adds nothing to, a
# finished task that Backlog.md has archived, an open task missing required keys, and unrelated
# tasks around them.
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
cat > "backlog/milestones/m-1 - reliable-fetching.md" <<'EOF'
---
id: m-1
title: Reliable fetching
---

## Description

Make the fetcher survive flaky servers and leak nothing: retries, timeouts, clear errors and safe logs.
EOF
task() {
  local id="$1" slug="$2" title="$3" status="$4" keys="$5" body="$6"
  cat > "backlog/tasks/${id,,} - ${slug}.md" <<EOF
---
id: ${id}
title: ${title}
status: ${status}
assignee: []
created_date: '2026-11-10'
labels: []
milestone: m-1
dependencies: []
priority: medium
type: feature
${keys}---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
${body}
<!-- SECTION:DESCRIPTION:END -->
EOF
}
agent=$'performer: agent\nagent_tier: moderate\neffort: M\npriority_set_by: agent\n'
task FE-1 Retry-transient-server-errors-in-fetch "Retry transient server errors in fetch()" "To Do" "$agent" \
  "fetch() gives up on the first 502, 503 or 504. Retry them with exponential backoff, up to three attempts."
task FE-2 Add-a-request-timeout "Add a request timeout" "To Do" "$agent" \
  "A request to a server that never answers hangs forever. Add a configurable timeout, 30 seconds by default."
task FE-3 Log-each-request-at-debug-level "Log each request at debug level" "Done" "$agent" \
  "Log the method, URL and status of each request at debug level."
task FE-4 Support-gzip-responses "Support gzip responses" "To Do" "" \
  "Decode gzip-encoded response bodies."
mkdir -p backlog/archive/tasks
mv "backlog/tasks/fe-3 - Log-each-request-at-debug-level.md" backlog/archive/tasks/
n=5
for topic in "Document the CLI flags" "Add a changelog" "Publish wheels" "Set up the docs site" \
  "Add type hints to the config loader" "Pin the CI runner image" "Write a contributing guide" \
  "Support proxies from the environment" "Add a progress bar" "Cache ETags between runs" \
  "Add a --quiet flag" "Package a Homebrew formula"; do
  slug=$(printf '%s' "$topic" | tr ' ' '-' | tr -cd 'A-Za-z0-9.-')
  task "FE-$n" "$slug" "$topic" "To Do" "$agent" "$topic."
  n=$((n + 1))
done
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
