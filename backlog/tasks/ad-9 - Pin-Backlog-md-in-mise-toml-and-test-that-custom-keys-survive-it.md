---
id: AD-9
title: Pin Backlog.md in mise.toml and test that custom keys survive it
status: Done
assignee: []
created_date: '2026-11-16'
updated_date: '2026-11-17T23:51:00Z'
labels:
  - prior-art
milestone: m-1
dependencies:
  - AD-1
references:
  - docs/prior-art/2026-11-16-cross-repo-task-coordination.md
  - docs/tool-feedback/backlog-md.md
priority: medium
type: feature
ordinal: 2000
performer: agent
agent_tier: moderate
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Backlog.md 1.55.3 is pinned in `mise.toml` and the lock (done 2026-11-17). What remains: add a test that creates a task with the pilot's custom keys in a temporary directory, edits it through the Backlog.md CLI and asserts the keys are unchanged, so an automated upgrade can't silently drop them. Document `remote_operations: false` and `--agent-instructions none`. Done when `mise run check` passes with the tool installed in CI.

**Why it matters:** Makes the board a one-word command and guards the schema against upgrades.
<!-- SECTION:DESCRIPTION:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-11-17: the pin, the lock files, `tests/test_backlog_md.py` (the pinned CLI edits a task in a temporary repo; every custom key, a nested one included, and the body must come back as written; the repo's `config.yml` must keep remote operations and auto-commit off) and the setup notes in `backlog/README.md` are written, and `mise run check` passes locally. Left: the same check passing in CI on the pull request, which also shows that CI installs Backlog.md from the lock.

2026-11-17: merged as #265 (30f3423); CI passed on main, which installed Backlog.md from the lock and ran tests/test_backlog_md.py.
<!-- SECTION:NOTES:END -->
