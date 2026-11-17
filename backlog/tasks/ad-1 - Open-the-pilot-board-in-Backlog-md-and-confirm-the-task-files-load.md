---
id: AD-1
title: Open the pilot board in Backlog.md and confirm the task files load
status: Done
assignee: []
created_date: '2026-11-16'
labels:
  - surfaced
milestone: m-1
dependencies: []
references:
  - docs/task-tracking-pilot.md
  - backlog/README.md
priority: high
type: review
ordinal: 1000
performer: human
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The pilot's task files were written by hand in Backlog.md 1.55.3's format, read from its source, because the agent session wasn't permitted to run the binary. Run `mise x npm:backlog.md@1.55.3 -- backlog board` and `backlog browser` in this repo and check: every task under `backlog/tasks/` appears; the custom keys (`performer`, `agent_tier`, `effort`, `external_blockers`) survive an edit made through the board; and the extra files in `backlog/` (`focus.yml`, `BOARD.md`, `README.md`, `outbox/`) don't confuse it. Then read `backlog/BOARD.md` and note what's wrong or missing. Done when the result is recorded in docs/task-tracking-pilot.md under 'Not verified'.

**Why it matters:** Every later task-tracking step assumes the files are valid Backlog.md tasks.
<!-- SECTION:DESCRIPTION:END -->
